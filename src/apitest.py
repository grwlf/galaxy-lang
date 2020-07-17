from openapi_client import *

conf=Configuration(
    host='https://icfpc2020-api.testkontur.ru',
    api_key={'apiKey':'0efd47509729415d884f297166f5e823'})
conf.debug=True


client=ApiClient(conf)


# a=ScoreboardApiApi(client)

a=TeamsApiApi(client)
