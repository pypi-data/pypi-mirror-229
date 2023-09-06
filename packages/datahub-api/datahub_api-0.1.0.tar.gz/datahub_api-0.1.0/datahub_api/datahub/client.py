import json
import logging
import os
from datetime import datetime, timedelta

import requests
import toml
from retrying import retry
import sqlglot


def get_token(credentials_file):
    with open(credentials_file) as f:
        sa = json.load(f)
    token_request = dict(
        grant_type="password",
        username=sa['account_id'],
        password=sa['secret_key'],
        scope='openid',
        client_id=sa['client_id'],
        response_type='token'
    )
    token_response = requests.post(sa["token_uri"], data=token_request)
    return token_response.json()['access_token']


class Client:

    def __init__(self, org_id, credentials_file):
        self.org_id = org_id
        self.token = get_token(credentials_file)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_file_path = os.path.join(project_root, "config/api_config.toml")
        self.config = toml.load(config_file_path)
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def required_headers(self):
        return {
            'Authorization': f"Bearer {self.token}",
            'LR-Org-ID': self.org_id,
            "Content-Type": "application/json"
        }

    def refresh_token(self):
        self.logger.info("Refreshing token...")
        self.token = get_token(self.credentials_file)

    def check_response(self, response):
        """

        :param response:
        """
        if response.status_code == 401 and "errorCode" in response.json() \
                and response.json()["errorCode"] == "TOKEN_EXPIRED":
            self.logger.error(f"TOKEN_EXPIRED: {response.status_code}, {response.text}")
            self.refresh_token()
            raise Exception(f"TOKEN_EXPIRED: {response.status_code}, {response.text}")

        elif response.status_code != 200:
            self.logger.error(f"Unexpected response: {response.status_code}, {response.text}")
            raise Exception(f"Unexpected response: {response.status_code}, {response.text}")

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=10000)
    def send_request(self, method, endpoint, data=None, params=None):
        # Set header
        headers = self.required_headers()
        full_endpoint = f"{self.config['api']['server_address']}{self.config['api']['version']}{endpoint}"
        self.logger.info(f"Request: {method} {full_endpoint}")
        response = requests.request(method, full_endpoint, json=data, headers=headers, params=params)
        self.check_response(response)
        return response.json()

    def run_sql(self, statement, is_sync, request_timeout_seconds=300):
        """
        Run query in sync or async,with request timeout.
        :param statement: your sql
        :param is_sync: if true will wait for the result, false will return query id, and you can fetch the result later
        :param request_timeout_seconds:if it's sync this param is useful, if it's async this value is useless
        :return:
        """

        endpoint = self.config['endpoints']['sql_resource']
        # if it's async need to set request_timeout_seconds to 0
        if not is_sync:
            request_timeout_seconds = 0

        sql_request = dict(statement=statement, timeoutSeconds=request_timeout_seconds)
        response_data = self.send_request("POST", endpoint, sql_request)
        return response_data

    def get_sql_result_metadata(self, query_id):
        """
        get result meta data by your query id
        :param query_id: query id
        """
        endpoint = self.config['endpoints']['sql_result'].format(query_id=query_id)
        response_data = self.send_request("GET", endpoint)
        return response_data

    def fetch_sql_detail(self, query_id):
        """
        Get your query detail info by query_id
        :param query_id: query id
        :return:
        """
        endpoint = self.config['endpoints']['sql_operation'].format(query_id=query_id)
        response_data = self.send_request("GET", endpoint)
        return response_data

    def get_query_list(self, limit=None, after=None, start_time=None, end_time=None, query_org_id=None,
                       status=None,
                       sort_by=None,
                       sort_order=None):
        """
        To list all queries to which you have access. This will list past requests run by yourself, and those run
        by your partners, if they referenced assets owned by your organisation.
        :param limit:the limit of the result you want.
        :param after:If you would like to fetch the next page of the list, you can pass the value of _pagination.after
        property as an after parameter to the get_query_list function.
        :param start_time:queries after this time.
        :param end_time:queries before this time.
        :param query_org_id: filter the queries to only those run by your org
        :param status:accepted values are RUNNING, SUCCESS and ERROR
        :param sort_by:createdOn, queryOrgId, status and queryOrgId
        :param sort_order: desc or asc
        :return:
        """
        params = {}
        if limit:
            params["limit"] = limit
        if start_time:
            params["startTime"] = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        if end_time:
            params["endTime"] = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        if query_org_id:
            params["queryOrgId"] = query_org_id
        if status:
            params["status"] = status
        if sort_by:
            params["sortBy"] = sort_by
        if sort_order:
            params["sortOrder"] = sort_order
        endpoint = self.config['endpoints']['sql_resource']

        response_data = self.send_request("GET", endpoint, params=params)
        return response_data

    def create_view(self, name, sql):
        """
        You can create a view by this function
        :param name: view name
        :param sql: sql to create view
        :return:
        """
        view_request = {"name": name, "sql": sql}
        endpoint = self.config['endpoints']['view_resource']

        response_data = self.send_request("POST", endpoint, json=view_request)
        return response_data

    def delete_view(self, view_id):
        endpoint = self.config['endpoints']['view_operation'].format(id=view_id)

        response_data = self.send_request("DELETE", endpoint)
        return response_data

    def get_assets(self, after=None):
        (assets, next_page) = self.__get_assets_page()
        while next_page:
            (assets_on_page, next_page) = self.__get_assets_page(next_page)
            assets += assets_on_page

        return assets

    def __get_assets_page(self, after=None):
        params = {"limit": 500}
        if after is not None:
            params["after"] = after
        endpoint = self.config['endpoints']['asset_resource']
        response_data = self.send_request("GET", endpoint, params=params)

        assets_on_page = response_data["assets"]
        next_page = response_data["_pagination"].get('after')
        return assets_on_page, next_page

    def add_asset_tags(self, asset_tags):
        endpoint = self.config['endpoints']['asset_add_tag']
        response_data = self.send_request("POST", endpoint, json=asset_tags)
        return response_data

    def remove_asset_tags(self, asset_tags):
        endpoint = self.config['endpoints']['asset_remove_tag']
        response_data = self.send_request("POST", endpoint, json=asset_tags)
        return response_data

    def share_udf(self, name, asset_id, partner_id, query_visibility, udf_visibility, number_of_days=None):
        permission_request = {
            "name": name,
            "assetIDs": [asset_id],
            "partnerOrgID": partner_id,
            "startDate": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            "collaborationRules": {
                "dataActivityVisibility": {"query": query_visibility},
                "propertiesVisibility": {"createStatement": udf_visibility}
            }
        }

        if number_of_days:
            permission_request["endDate"] = (datetime.utcnow() + timedelta(days=number_of_days)).strftime('%Y-%m-%dT'
                                                                                                          '%H:%M:%SZ')

        endpoint = self.config['endpoints']['permission_resource']
        response_data = self.send_request("POST", endpoint, json=permission_request)
        return response_data['id']

    def share_table_or_view(self,
                            name,
                            asset_id,
                            partner_id,
                            allow_joining_with_partners_data,
                            allow_joining_with_data_providers_data,
                            allow_joining_with_other_orgs_data,
                            allow_joining_with_specific_orgs_data,
                            minimum_aggregation_column=None,
                            minimum_aggregation_records=None,
                            number_of_days=None
                            ):
        collaboration_rules = {
            "dataCombinations": {
                "myPartner": allow_joining_with_partners_data,
                "dataProvider": allow_joining_with_data_providers_data,
                "otherOrgs": allow_joining_with_other_orgs_data,
                "orgs": allow_joining_with_specific_orgs_data
            }
        }

        if minimum_aggregation_column and minimum_aggregation_records:
            collaboration_rules["queryThreshold"] = {
                "aggregationColumn": minimum_aggregation_column,
                "minRecords": minimum_aggregation_records
            }

        permission_request = {
            "name": name,
            "assetIDs": [asset_id],
            "partnerOrgID": partner_id,
            "startDate": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            "collaborationRules": collaboration_rules
        }

        if number_of_days:
            permission_request["endDate"] = (datetime.utcnow() + timedelta(days=number_of_days)).strftime(
                '%Y-%m-%dT%H:%M:%SZ')

        endpoint = self.config['endpoints']['permission_resource']
        response_data = self.send_request("POST", endpoint, json=permission_request)

        return response_data['id']

    def list_permissions(self, asset_ids=None, statuses=None, after=None):
        asset_ids_param = {"assetIDs": ",".join(asset_ids)} if asset_ids else {}
        statuses_param = {"statuses": ",".join(statuses)} if statuses else {}
        after_param = {"after": after} if after else {}

        endpoint = self.config['endpoints']['permission_resource']
        response_data = self.send_request("GET", endpoint,
                                          params={**{"limit": 500}, **asset_ids_param, **statuses_param, **after_param})

        pagination = response_data["_pagination"]
        new_after = pagination["after"] if "after" in pagination else None
        remaining_permissions = self.list_permissions(asset_ids, statuses, new_after) if new_after else []
        return response_data["permissions"] + remaining_permissions

    def update_permission(self, permission_id, end_date=None):

        permission_request = {}
        if end_date:
            permission_request["endDate"] = end_date
        endpoint = self.config['endpoints']['permission_operation'].format(id=permission_id)
        response_data = self.send_request("POST", endpoint,
                                          data=permission_request)
        return response_data

    def revoke_permission(self, permission_id):
        endpoint = self.config['endpoints']['permission_operation'].format(id=permission_id)
        response_data = self.send_request("DELETE", endpoint)

    def list_partners(self):
        endpoint = self.config['endpoints']['partner_resource']
        response_data = self.send_request("GET", endpoint)
        return response_data

    def list_pre_approved_data_combination_partners(self):
        endpoint = self.config['endpoints']['partner_data_combination_approved_resource']
        response_data = self.send_request("GET", endpoint)
        return response_data

    @staticmethod
    def transpile(sql, from_dialect, to_dialect):
        return sqlglot.transpile(sql, read=from_dialect, write=to_dialect)[0]
