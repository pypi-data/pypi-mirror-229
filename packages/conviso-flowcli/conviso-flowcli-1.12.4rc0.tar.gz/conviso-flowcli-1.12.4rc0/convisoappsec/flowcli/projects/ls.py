import os
import click
import click_log

from convisoappsec.flowcli.common import on_http_error
from convisoappsec.common import safe_join_url
from convisoappsec.logger import LOGGER
from convisoappsec.flow.graphql_api.v1.client import ConvisoGraphQLClient

click_log.basic_config(LOGGER)

class Projects():
    def __init__(self):
        pass

    def ls(self, project_code="", project_label="", page=1, limit=10):
        try:
            url = safe_join_url(os.environ['FLOW_API_URL'], "/graphql")
            conviso_api = ConvisoGraphQLClient(api_url=url,api_key=os.environ['FLOW_API_KEY'])

            return perform_command(conviso_api, project_code, project_label, page, limit)

        except Exception as exception:
            on_http_error(exception)
            raise click.ClickException(str(exception)) from exception

def perform_command(conviso_api, project_code, project_label, page, limit):
    projects_found = conviso_api.projects.get_by_code_or_label(
        project_code,
        project_label,
        page,
        limit
    )

    return projects_found
