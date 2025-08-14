# import os
# import certifi
# os.environ['CRYPTOGRAPHY_OPENSSL_NO_LEGACY'] = '1'

import requests


def fetch_html(url, timeout=10):
    try:
        # Try with proxy first
        proxies = {
            "http": "http://www-proxy.us.oracle.com:80",
            "https": "http://www-proxy.us.oracle.com:80"
        }
        response = requests.get(url, proxies=proxies, timeout=timeout)
        response.raise_for_status()
    except (requests.exceptions.ProxyError, requests.exceptions.ConnectTimeout):
        # Retry without proxy if failed
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
    
    return response.text
