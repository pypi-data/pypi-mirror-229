import requests


class HolisticsClient:

    def __init__(self, token):
        self.host = 'https://us.holistics.io/api/v2/'
        self.dashboards = self.host + 'dashboards/'
        self.dashboard_widgets = self.host + 'dashboard_widgets/'
        self.users = self.host + 'users/'
        self.headers = {
            'Content-type': 'application/json',
            # 'Authorization': f'X-Holistics-Key {token}'
            'X-Holistics-Key': token
        }

    def get_dashboards(self, limit):

        params = {
            'limit': limit,
            'after': None
        }

        all_dashboards = []
        cursor_next = True
        while cursor_next:
            response = requests.request('GET', self.dashboards, headers=self.headers, params=params)
            response_date = response.json()
            all_dashboards.extend(response_date['dashboards'])
            params['after'] = response_date['cursors']["next"]
            cursor_next = response_date['cursors']["next"] is not None

        try:
            return all_dashboards
        except:
            print(" Status Code", response.status_code)
            response.raise_for_status()

    def get_dashboard_widgets(self, widget_id):

        params = {
            'include_dashboard': 1,
            'include_report': 1,
            'include_url': 1
        }
        url_api = f'{self.dashboard_widgets}{widget_id}'
        response = requests.request('GET', url_api, headers=self.headers, params=params)
        try:
            return response.json()
        except:
            print(" Status Code", response.status_code)
            response.raise_for_status()

    def get_users(self, limit):

        params = {
            'limit': limit
        }

        response = requests.request('GET', self.users, headers=self.headers, params = params)
        try:
            return response.json()
        except:
            print(" Status Code", response.status_code)
            response.raise_for_status()
