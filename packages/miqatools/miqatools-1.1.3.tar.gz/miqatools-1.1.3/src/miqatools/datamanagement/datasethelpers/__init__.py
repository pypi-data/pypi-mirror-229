import requests


def get_ds_ids_by_name(miqa_server, pipeline_id):
    info = get_ds_ids_by_name_internal(miqa_server, pipeline_id)
    return info


def get_ds_ids_by_name_internal(miqa_server, pipeline_id):
    remote_url = f'https://{miqa_server}/api/get_ds_ids_by_name?pipeline_id={pipeline_id}'
    info = requests.get(remote_url).json()
    return info


def tag_ds_ids_by_name(miqa_server, pipeline_id, name, tag):
    info = get_ds_ids_by_name_internal(miqa_server, pipeline_id)
    source_ids_lookup = info.get('data',{})
    if source_ids_lookup and source_ids_lookup.get(name):
        tag_url = f"https://{miqa_server}/api/batch_tag_datasources/{tag}?inline=1&source_ids={source_ids_lookup.get(name)}"
        resp = requests.get(tag_url)
        return resp
    else:
        raise Exception("No matching datasource IDs found")


def tag_ds_ids_by_names(miqa_server, pipeline_id, names, tag, raise_if_names_not_found=False):
    info = get_ds_ids_by_name_internal(miqa_server, pipeline_id)
    source_ids_lookup = info.get('data',{})
    source_ids_for_names = [source_ids_lookup.get(name) for name in names]
    source_ids_for_names = [str(i) for i in source_ids_for_names if i]
    if source_ids_for_names and (not raise_if_names_not_found or len(source_ids_for_names) == len(names)):
        tag_url = f"https://{miqa_server}/api/batch_tag_datasources/{tag}?inline=1&source_ids={','.join(source_ids_for_names)}"
        resp = requests.get(tag_url)
        return resp
    else:
        raise Exception("Matching datasource IDs not found")


def batch_create_datasets_and_tag_or_group(miqa_server, org_id, pipeline_id, new_ds_names, tags, dsg_name=None):
    tag_url = f"https://{miqa_server}/api/batch_create_dataset_and_tag?org_id={org_id}&pipeline_id={pipeline_id}&names={','.join(new_ds_names)}"

    if tags:
        tag_url += f"&tags={','.join(tags)}"
    if dsg_name:
        tag_url += f"&create_dsg={dsg_name}"

    resp = requests.get(tag_url)
    return resp
