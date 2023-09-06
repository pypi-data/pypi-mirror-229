from copy import deepcopy as clone

import click
import os
from convisoappsec.flowcli import help_option
from convisoappsec.flowcli.common import DeployFormatter, project_code_option, asset_id_option
from convisoappsec.flowcli.deploy.create.context import pass_create_context
from convisoappsec.flowcli.deploy.create.with_.values import values
from convisoappsec.flowcli.sast import sast
from convisoappsec.flowcli.sca import sca
from convisoappsec.logger import LOGGER
from convisoappsec.flowcli.projects.ls import Projects
from convisoappsec.flowcli.companies.ls import Companies
from convisoappsec.flow.graphql_api.v1.models.asset import CreateAssetInput
from convisoappsec.flow.graphql_api.v1.models.project import CreateProjectInput, UpdateProjectInput
from convisoappsec.flow.graphql_api.v1.client import ConvisoGraphQLClient
from convisoappsec.common import safe_join_url
from convisoappsec.common.git_data_parser import GitDataParser

class CreateDeployException(Exception):
    pass


class PerformDeployException(Exception):
    pass


def get_default_params_values(cmd_params):
    """ Further information in https://click.palletsprojects.com/en/8.1.x/api/?highlight=params#click.Command.params

    Args:
        cmd_params (List[click.core.Parameter]):

    Returns:
        dict: default params values dictionarie
    """
    default_params = {}
    for param in cmd_params:
        unwanted = param.name in ['help', 'verbosity']
        if not unwanted:
            default_params.update({param.name: param.default})
    return default_params


def parse_params(ctx_params: dict, expected_params: list):
    """ Parse the params from the context extracting the expected params values to the context.

    Args:
        ctx_params (dict): context params: Further information at https://click.palletsprojects.com/en/8.1.x/api/?highlight=context%20param#click.Context.params
        expected_params (list): Further information at https://click.palletsprojects.com/en/8.1.x/api/?highlight=params#click.Command.params

    Returns:
        dict: parsed_params: parsed params as key and value
    """
    parsed_params = get_default_params_values(expected_params)
    for param in ctx_params:
        if param in parsed_params:
            parsed_params.update({param: ctx_params.get(param)})
    return parsed_params


def perform_sast(context) -> None:
    """Setup and runs the "sast run" command.

    Args:
        context (<class 'click.core.Context'>): clonned context
    """
    sast_run = sast.commands.get('run')

    specific_params = {
        "deploy_id": context.obj.deploy['id'],
        "start_commit": context.obj.deploy['previous_commit'],
        "end_commit": context.obj.deploy['current_commit'],
    }
    context.params.update(specific_params)
    context.params = parse_params(context.params, sast_run.params)
    try:
        LOGGER.info(
            'Running SAST on deploy ID "{deploy_id}"'
            .format(deploy_id=context.params["deploy_id"])
        )
        sast_run.invoke(context)

    except Exception as err:
        raise click.ClickException(str(err)) from err


def perform_sca(context) -> None:
    """Setup and runs the "sca run" command.

    Args:
        context (<class 'click.core.Context'>): clonned context
    """
    sca_run = sca.commands.get('run')
    context.params.update({"deploy_id": context.obj.deploy['id']})
    context.params = parse_params(context.params, sca_run.params)
    try:
        LOGGER.info(
            'Running SCA on deploy ID "{deploy_id}"'
            .format(deploy_id=context.params["deploy_id"])
        )
        sca_run.invoke(context)

    except Exception as err:
        raise click.ClickException(str(err)) from err


def perform_deploy(context):
    """Setup and runs the "deploy create with values" command.

    Args:
        context (<class 'click.core.Context'>): clonned context

    Returns:
        dict: deploy
         int: deploy.id
         int: deploy.project_id
         str: deploy.current_tag
         str: deploy.previous_tag
         str: deploy.current_commit
         str: deploy.previous_commit
         str: deploy.created_at
    """
    context.obj.output_formatter = DeployFormatter(
        format=DeployFormatter.DEFAULT
    )
    context.params = parse_params(context.params, values.params)
    try:
        LOGGER.info("Creating new deploy ...")
        created_deploy = values.invoke(context)

        if created_deploy:
            return created_deploy

        raise CreateDeployException("Deploy not created.")

    except CreateDeployException as err:
        raise PerformDeployException(err)

    except Exception as err:
        raise click.ClickException(str(err)) from err

def list_assets(company_id, asset_name, scan_type):
    url = safe_join_url(os.environ['FLOW_API_URL'], "/graphql")
    conviso_api = ConvisoGraphQLClient(api_url=url,api_key=os.environ['FLOW_API_KEY'])

    asset_model = CreateAssetInput(
        int(company_id),
        asset_name,
        scan_type
    )

    return conviso_api.assets.list_assets(asset_model)

def create_asset(company_id, asset_name, scan_type):
    url = safe_join_url(os.environ['FLOW_API_URL'], "/graphql")
    conviso_api = ConvisoGraphQLClient(api_url=url,api_key=os.environ['FLOW_API_KEY'])

    asset_model = CreateAssetInput(
        int(company_id),
        asset_name,
        scan_type
    )

    return conviso_api.assets.create_asset(asset_model)


def create_project(company_id, asset_id, label):
    url = safe_join_url(os.environ['FLOW_API_URL'], "/graphql")
    conviso_api = ConvisoGraphQLClient(api_url=url,api_key=os.environ['FLOW_API_KEY'])

    project_model = CreateProjectInput(
        company_id,
        asset_id,
        label
        )
    
    return conviso_api.projects.create_project(project_model)

def update_project(project_id, asset_id):
    url = safe_join_url(os.environ['FLOW_API_URL'], "/graphql")
    conviso_api = ConvisoGraphQLClient(api_url=url, api_key=os.environ['FLOW_API_KEY'])

    project_model = UpdateProjectInput(
        project_id,
        asset_id,
    )

    conviso_api.projects.update_project(project_model)

def preparing_context(context):
    """due to the new vulnerability management we need to do some checks before continuing the flow
    """
    project_code = context.params['project_code']

    if project_code:
        projects = Projects()
        projects_filtered = projects.ls(project_code=project_code)
        graphql_response = projects_filtered[0]
        custom_features = graphql_response['company']['customFeatures']
        assets = graphql_response['assets']

        if len(assets) == 0:
            raise CreateDeployException("Project doens't have an Asset associated")

        asset_id = assets[0]['id']

        if 'CONVISO_NEW_ISSUE_MANAGEMENT_ALLOWED_COMPANY' in custom_features:
            context.params['asset_id'] = asset_id
            context.params['experimental'] = True

            return context
        else:
            context.params['asset_id'] = asset_id
            context.params['experimental'] = False

            return context
    else:
        companies = Companies()
        companies_filtered = companies.ls()
        company_id = context.params['company_id']

        if company_id:
            for company in companies_filtered:
                if company['id'] == company_id:
                    companies_filtered = [company]
                    break

        if len(companies_filtered) > 1:
            raise CreateDeployException("Deploy not created. You have access to multiple companies, specify one using FLOW_COMPANY_ID")

        company = companies_filtered[0]
        if 'CONVISO_NEW_ISSUE_MANAGEMENT_ALLOWED_COMPANY' not in company['customFeatures']:
            raise CreateDeployException("Deploy not created. You are not on new vuln manegement")

        project_label_git = GitDataParser(context.params['repository_dir']).parse_name()
        project_label = project_label_git + '_ast'
        projects = Projects()
        projects_filtered = projects.ls(
            project_label=project_label,
        )

        asset_name = project_label_git

        if len(projects_filtered) == 1:
            project = projects_filtered[0]

            # necessary? this flow use api_key, so user will not have access to another projects
            if project['company']['id'] != company_id:
                raise CreateDeployException("Deploy not created. You do not have access to this project, specify one by informing env var FLOW_PROJECT_CODE")

            assets = project['assets']

            if len(assets) > 0:
                asset = assets[0]
            else:
                asset = create_asset(company['id'], asset_name, 'SAST')
                update_project(project['id'], asset['id'])

            context.params['project_code'] = project['apiCode']
            context.params['asset_id'] = asset['id']
            context.params['experimental'] = True

            return context
        elif not len(projects_filtered):
            asset = list_assets(company['id'], asset_name, 'SAST')

            if len(asset) == 0:
                asset = create_asset(company['id'], asset_name, 'SAST')
            else:
                asset = asset[0]

            project = create_project(company['id'], asset['id'], project_label)

            context.params['project_code'] = project['apiCode']
            context.params['asset_id'] = asset['id']
            context.params['experimental'] = True

            return context
        else:
            raise CreateDeployException("Deploy not created. More than one project found, you have specify a project code")

@click.command(
    context_settings=dict(
        allow_extra_args=True,
        ignore_unknown_options=True
    )
)
@asset_id_option(
    required=False
)
@project_code_option(
    help="Not required when --no-send-to-flow option is set",
    required=False
)
@click.option(
    "--send-to-flow/--no-send-to-flow",
    default=True,
    show_default=True,
    required=False,
    help="""Enable or disable the ability of send analysis result
    reports to flow. When --send-to-flow option is set the --project-code
    option is required""",
    hidden=True
)
@click.option(
    '-r',
    '--repository-dir',
    default=".",
    show_default=True,
    type=click.Path(exists=True, resolve_path=True),
    required=False,
    help="""The source code repository directory.""",
)
@click.option(
    "-c",
    "--current-commit",
    required=False,
    help="If no value is given the HEAD commit of branch is used. [DEPLOY]",
)
@click.option(
    "-p",
    "--previous-commit",
    required=False,
    help="""If no value is given, the value is retrieved from the lastest
    deploy at flow application. [DEPLOY]""",
)
@click.option(
    "--company-id",
    required=False,
    envvar="FLOW_COMPANY_ID",
    help="Company ID on Conviso Platform",
)
@help_option
@pass_create_context
@click.pass_context
def run(context, create_context, **kwargs):
    """ AST - Application Security Testing. Unifies deploy issue, SAST and SCA analyses.  """
    try:
        prepared_context = preparing_context(clone(context))
        prepared_context.obj.deploy = perform_deploy(clone(prepared_context))
        perform_sast(clone(prepared_context))
        perform_sca(clone(prepared_context))

    except PerformDeployException as err:
        LOGGER.warning(err)

    except Exception as err:
        raise click.ClickException(str(err)) from err


@click.group()
def ast():
    pass


ast.add_command(run)
