import os
from convisoappsec.flowcli.common import CreateDeployException, DeployFormatter, project_code_option, asset_id_option
from convisoappsec.flowcli.deploy.create.context import pass_create_context
from convisoappsec.flowcli.deploy.create.with_.values import values
from convisoappsec.logger import LOGGER
from convisoappsec.flowcli.projects.ls import Projects
from convisoappsec.flowcli.companies.ls import Companies
from convisoappsec.flow.graphql_api.v1.models.asset import CreateAssetInput
from convisoappsec.flow.graphql_api.v1.models.project import CreateProjectInput, UpdateProjectInput
from convisoappsec.flow.graphql_api.v1.client import ConvisoGraphQLClient
from convisoappsec.common import safe_join_url
from convisoappsec.common.git_data_parser import GitDataParser



class RequirementsVerifier:

    @staticmethod
    def list_assets(company_id, asset_name, scan_type):
        url = safe_join_url(os.environ['FLOW_API_URL'], "/graphql")
        conviso_api = ConvisoGraphQLClient(api_url=url,api_key=os.environ['FLOW_API_KEY'])

        asset_model = CreateAssetInput(
            int(company_id),
            asset_name,
            scan_type
        )

        return conviso_api.assets.list_assets(asset_model)

    @staticmethod
    def create_asset(company_id, asset_name, scan_type):
        url = safe_join_url(os.environ['FLOW_API_URL'], "/graphql")
        conviso_api = ConvisoGraphQLClient(api_url=url,api_key=os.environ['FLOW_API_KEY'])

        asset_model = CreateAssetInput(
            int(company_id),
            asset_name,
            scan_type
        )

        return conviso_api.assets.create_asset(asset_model)

    @staticmethod
    def create_project(company_id, asset_id, label):
        url = safe_join_url(os.environ['FLOW_API_URL'], "/graphql")
        conviso_api = ConvisoGraphQLClient(api_url=url,api_key=os.environ['FLOW_API_KEY'])

        project_model = CreateProjectInput(
            company_id,
            asset_id,
            label
            )
        
        return conviso_api.projects.create_project(project_model)

    @staticmethod
    def update_project(project_id, asset_id):
        url = safe_join_url(os.environ['FLOW_API_URL'], "/graphql")
        conviso_api = ConvisoGraphQLClient(api_url=url, api_key=os.environ['FLOW_API_KEY'])

        project_model = UpdateProjectInput(
            project_id,
            asset_id,
        )

        conviso_api.projects.update_project(project_model)

    @staticmethod
    def prepare_context(context):
        """due to the new vulnerability management we need to do some checks before continuing the flow
        """
        project_code = context.params['project_code']

        if project_code:
            projects = Projects()
            projects_filtered = projects.ls(project_code=project_code)

            if len(projects_filtered) == 0:
                raise CreateDeployException("Project doesn't exists!")

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
            company_id = context.params['company_id']

            if company_id is not None:
                companies_filtered = [ companies.ls(company_id=company_id) ]
            else:
                companies_filtered = companies.ls()

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
                company_id=company_id
            )

            asset_name = project_label_git

            if len(projects_filtered) == 1:
                project = projects_filtered[0]
                assets = project['assets']

                if len(assets) == 1:
                    asset = assets[0]

                    if asset['name'] != asset_name:
                        asset = RequirementsVerifier.create_asset(company['id'], asset_name, 'SAST')
                        RequirementsVerifier.update_project(project['id'], asset['id'])
                elif len(assets) > 1:
                    for item in assets:
                        if item['name'] != asset_name:
                            continue
                        else:
                            asset = item
                else:
                    asset = RequirementsVerifier.create_asset(company['id'], asset_name, 'SAST')
                    RequirementsVerifier.update_project(project['id'], asset['id'])

                context.params['project_code'] = project['apiCode']
                context.params['asset_id'] = asset['id']
                context.params['experimental'] = True

                return context
            elif not len(projects_filtered):
                asset = RequirementsVerifier.list_assets(company['id'], asset_name, 'SAST')

                if len(asset) == 0:
                    asset = RequirementsVerifier.create_asset(company['id'], asset_name, 'SAST')
                else:
                    asset = asset[0]

                project = RequirementsVerifier.create_project(company['id'], asset['id'], project_label)

                context.params['project_code'] = project['apiCode']
                context.params['asset_id'] = asset['id']
                context.params['experimental'] = True

                return context
            else:
                raise CreateDeployException("Deploy not created. More than one project found, you have specify a project code")
