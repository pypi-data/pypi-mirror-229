from ..executionhelpers import get_exec_info
from ..uploadhelpers import upload_files_or_folder


def upload_files_or_folder_for_exec(exec_id, server, args_folder=None, args_files=None, filepattern_end=None, filepattern_start=None, exclude_filepattern_end=None, max_filesize=None, api_key=None, max_connections=None, filepatterns=None):
    exec_info = get_exec_info(exec_id, server)
    bucket = exec_info.get('bucket')
    key = exec_info.get('key')
    cloud_provider = exec_info.get('cloud_provider', 'aws')
    org_config_id = exec_info.get('org_config_id')
    upload_files_or_folder(args_folder, server, bucket, key, cloud_provider, org_config_id, args_files,
                           filepattern=filepattern_end, filepattern_start=filepattern_start,
                           exclude_filepattern_end=exclude_filepattern_end,
                           max_filesize=max_filesize, api_key=api_key,
                           max_connections=max_connections, filepatterns=filepatterns)
