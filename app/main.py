from sys import argv

import requests


def main():
    server_url = argv[1]
    player_key = argv[2]
    print('ServerUrl: %s; PlayerKey: %s' % (server_url, player_key))

    res = requests.get('%s?playerKey=%s' % (server_url, player_key))
    res.raise_for_status()


if __name__ == '__main__':
    main()
