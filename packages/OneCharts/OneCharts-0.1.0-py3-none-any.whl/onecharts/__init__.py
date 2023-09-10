import requests as rq


class OneCharts:

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url_prefix = 'https://onecharts.io/api/'
        self._session = rq.Session()
        self._session.headers['Authorization'] = 'Bearer %s' % self.api_key
        self.ServerResponse = rq.Response

    def _make_request(self, method, api_method: str, params: dict = None, data: dict = None, **kwargs) -> dict:
        url = self.url_prefix + api_method
        self.ServerResponse = self._session.request(method, url, params=params, data=data, **kwargs)
        return self.ServerResponse.json()

    def get_user_charts(self, username: str, q: str = "") -> dict:
        return self._make_request('get', 'user_charts', {'username': username, 'q': q})

    def create_new_chart(self, chart_id: str, chart_title: str = "", notes: str = "", visibility: str = "private",
                         data: dict = None) -> dict:
        return self._make_request('post', 'chart', json={
            'chart_id': chart_id,
            'chart_title': chart_title,
            'visibility': visibility,
            'notes': notes,
            'data': data,
        })

    def get_chart_config(self, chart_id: str) -> dict:
        return self._make_request('get', 'chart', {'chart_id': chart_id})

    def get_chart_data(self, chart_id: str) -> dict:
        return self._make_request('get', 'chart_data', {'chart_id': chart_id})

    def update_chart_data(self, chart_id: str, overwrite: bool = False, data: dict = None):
        return self._make_request('patch', 'chart_data', json={
            'chart_id': chart_id,
            'overwrite': overwrite,
            'data': data
        })

    # TODO: Add methods for remaining API methods: https://onecharts.io/api