import requests


class TapedToggl:

    class TapedTogglException(Exception):
        """ no data was fetched """

        def get_code(self):
            return self.args[1]

        def get_message(self):
            return self.args[0]

    WORKSPACES_ENDPOINT = 'https://www.toggl.com/api/v8/workspaces'
    DETAILS_ENDPOINT = 'https://toggl.com/reports/api/v2/details'
    USER_AGENT = 'python/requests'

    def __init__(self, token):
        self.token = token
        self.user_agent = TapedToggl.USER_AGENT
        self.error = None

    def get_workspaces(self):
        try:
            r = self.__request_get(TapedToggl.WORKSPACES_ENDPOINT, auth=(self.token, 'api_token'), headers=self.__get_headers())
            return r.json()
        except TapedToggl.TapedTogglException:
            return None

    def get_detailed_report(self, workspace_id, since=None, until=None, client_ids=None, project_ids=None):
        """
        :param workspace_id: int
        :param since: date, by default until - 6 days.
        :param until: date, by default today
        :param client_ids: str client ids separated by a comma, 0 if you want to filter out time entries without a client
        :param project_ids: str project ids separated by a comma, 0 if you want to filter out time entries without a project
        :return:
        """
        # this code can fetch paged data, but it is not actual for now so we hardcode default parameters
        page = 1         # page to fetch, 1 based
        per_page = None  # records per page, None means all available records
        # first time always get first page because we don't know what toggl per_page value is
        try:
            params = self.__get_params_for_details(
                workspace_id=workspace_id,
                since=since,
                until=until,
                client_ids=client_ids,
                project_ids=project_ids
            )
            r = self.__request_get(TapedToggl.DETAILS_ENDPOINT, auth=(self.token, 'api_token'),
                                   headers=self.__get_headers(), params=params)
            toggl_per_page = r.json()['per_page']
            total_count = r.json()['total_count']
            range_fetched = (0, toggl_per_page)
            if per_page is None:
                per_page = total_count
            range_required = (per_page * (page - 1), per_page * page)
            result_list = []
            while True:
                acceptable_range = self.__range_intersection(range_fetched, range_required)
                if (acceptable_range[1] - acceptable_range[0]) > 0:
                    base = range_fetched[0]
                    result_list += r.json()['data'][acceptable_range[0] - base:acceptable_range[1] - base]
                    if len(result_list) == per_page or range_fetched[1] == total_count:
                        break  # all data fetched
                # calc new applicable page to fetch
                target_index = per_page * (page - 1) + len(result_list)
                if target_index >= total_count:
                    raise IndexError("Requested page out of max count of entries {}".format(total_count))
                toggle_page = target_index // toggl_per_page + 1
                params = self.__get_params_for_details(
                    workspace_id=workspace_id,
                    since=since,
                    until=until,
                    client_ids=client_ids,
                    project_ids=project_ids,
                    page=toggle_page
                )
                r = self.__request_get(TapedToggl.DETAILS_ENDPOINT, auth=(self.token, 'api_token'),
                                       headers=self.__get_headers(), params=params)
                range_fetched = (
                    (toggle_page - 1) * toggl_per_page,
                    (toggle_page - 1) * toggl_per_page + len(r.json()['data'])
                )

            return result_list
        except TapedToggl.TapedTogglException:
            return None

    def __request_get(self, endpoint, **kwargs):
        self.error = None
        r = requests.get(endpoint, **kwargs)
        if r.status_code // 100 != 2:
            self.error = (r.status_code, r.reason)
            raise TapedToggl.TapedTogglException(r.reason, r.status_code)
        return r

    def __range_intersection(self, tuple1, tuple2):
        """
        tuple left inclusive right exclusive
        :param tuple1: tuple
        :param tuple2: tuple
        :return: tuple
        """
        x1 = max(tuple1[0], tuple2[0])
        x2 = x1 + min(tuple1[1] - tuple1[0], tuple2[1] - tuple2[0], tuple1[1] - tuple2[0], tuple2[1] - tuple1[0])
        return x1, x2

    def __get_params_for_details(self, workspace_id, since=None, until=None, client_ids=None, project_ids=None, page=1):
        params = {
            'user_agent': self.user_agent,
            'workspace_id': workspace_id,
            'order_field': 'date',
            'order_desc': 'on',
            'page': page
        }
        if since:
            params.update({'since': since.strftime('%Y-%m-%d')})
        if until:
            params.update({'until': until.strftime('%Y-%m-%d')})
        if client_ids:
            params.update({'client_ids': client_ids})
        if project_ids:
            params.update({'project_ids': project_ids})
        return params

    def __get_headers(self):
        return {'Content-Type': 'application/json', 'User-Agent': self.user_agent}
