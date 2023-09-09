import requests


def trigger_miqa_test(miqa_server, trigger_id, version_name):
    trigger_url = f"https://{miqa_server}/api/trigger_test_auto/{trigger_id}?app=mn&offline_version=True&name={version_name}"
    trigger_response_json = requests.get(trigger_url).json()
    run_id = trigger_response_json.get('run_id')
    return run_id


def get_tcr_info_json(miqa_server, run_id, directory_containing_outputs=None, ds_id=None, wfv_id=None):
    get_info_url = f"https://{miqa_server}/api/get_tcr_exec_info/{run_id}"
    query_pars = []
    if directory_containing_outputs:
        query_pars.append(f"source_location={directory_containing_outputs}")
    if ds_id:
        query_pars.append(f"ds_id={ds_id}")
    if wfv_id:
        query_pars.append(f"&wfv_id={wfv_id}")

    if len(query_pars)>0:
        get_info_url = f"{get_info_url}?{'&'.join(query_pars)}"

    get_info_response_json = requests.get(get_info_url).json()
    return get_info_response_json


def get_trigger_info(miqa_server, trigger_id):
    trigger_url = f"https://{miqa_server}/api/test_trigger/{trigger_id}/get_ds_id_mapping"
    trigger_response_json = requests.get(trigger_url).json()
    # return {"ds_id_mapping":{"results":trigger_response_json, "url":trigger_url}}
    return {"ds_id_mapping":{"results":trigger_response_json}}