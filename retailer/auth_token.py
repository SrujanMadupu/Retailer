from .credentials import client_id, client_secret, auth_url
import requests


def get_bearer_token():
    res = requests.post(url=auth_url+'/token',
                        headers={'Content-Type': 'application/x-www-form-urlencoded'},
                        data={'client_id': client_id,
                              'client_secret': client_secret,
                              'grant_type': 'client_credentials'})
    if res.status_code == 200:
        res_json = res.json()
        with open('retailer/access_token.txt', 'w') as tk:
            tk.write(res_json['access_token'])
        return True
    else:
        return False


