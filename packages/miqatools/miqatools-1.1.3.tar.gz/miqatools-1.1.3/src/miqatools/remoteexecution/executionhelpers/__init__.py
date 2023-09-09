import requests


def complete_exec(exec_id, facet_server=None):
    print(f"Completing execution {exec_id}")
    remote_url = f'https://{facet_server}/api/execution/{exec_id}/mark_complete'
    info = requests.get(remote_url).json()
    print(info.get('message'))
    return info


def get_exec_info(exec_id, facet_server=None):
    remote_url = f'https://{facet_server}/api/execution/{exec_id}'
    info = requests.get(remote_url).json()
    return info


def get_exec_url(exec_id, facet_server=None):
    return f'https://{facet_server}/execution/{exec_id}'
