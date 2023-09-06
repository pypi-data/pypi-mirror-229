import os
import click
import click_log

from convisoappsec.flowcli.common import on_http_error
from convisoappsec.common import safe_join_url
from convisoappsec.logger import LOGGER
from convisoappsec.flow.graphql_api.v1.client import ConvisoGraphQLClient

class Companies():
    def __init__(self):
        pass

    def ls(self):
        api_key = os.environ['FLOW_API_KEY']
        try:
            url = safe_join_url(os.environ['FLOW_API_URL'], "/graphql")
            conviso_api = ConvisoGraphQLClient(api_url=url,api_key=api_key)

            return perform_command(conviso_api)
        except Exception as exception:
            on_http_error(exception)
            raise click.ClickException(str(exception)) from exception

def perform_command(conviso_api):
    companies = conviso_api.companies.get_companies()

    return companies
