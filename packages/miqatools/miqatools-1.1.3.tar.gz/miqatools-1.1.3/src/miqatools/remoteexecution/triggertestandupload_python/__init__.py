from argparse import ArgumentParser

from ..executionhelpers import complete_exec
from ..offlineexecution import upload_files_or_folder_for_exec
from ..triggertest_helpers import trigger_miqa_test, get_tcr_info_json


def trigger_test_and_upload_single_results(miqa_server, trigger_id, version_name, directory_containing_outputs, filepattern_end=None, filepattern_start=None, exclude_filepattern_end=None, max_filesize=None, api_key=None, max_connections=None, filepatterns=None):
    run_id = trigger_miqa_test(miqa_server, trigger_id, version_name)
    get_info_response_json = get_tcr_info_json(miqa_server, run_id, directory_containing_outputs)
    exec_id = get_info_response_json.get("exec_id")
    upload_files_or_folder_for_exec(exec_id, miqa_server, directory_containing_outputs, None, filepattern_end=filepattern_end,
                                    filepattern_start=filepattern_start, exclude_filepattern_end=exclude_filepattern_end, max_filesize=max_filesize, api_key=api_key,
                                    max_connections=max_connections, filepatterns=filepatterns)
    complete_exec(exec_id, miqa_server)


def trigger_test_and_upload_by_dsid(miqa_server, trigger_id, version_name, ds_lookup, filepattern_end=None, filepattern_start=None, exclude_filepattern_end=None, max_filesize=None, api_key=None, max_connections=None, skip_completed=True, filepatterns=None):
    run_id = trigger_miqa_test(miqa_server, trigger_id, version_name)
    upload_to_test_by_dsid(run_id, miqa_server, ds_lookup, filepattern_end, filepattern_start, exclude_filepattern_end, api_key,
                           max_connections, max_filesize, skip_completed=skip_completed, filepatterns=filepatterns)


def upload_to_test_by_dsid(run_id, miqa_server, ds_lookup, filepattern_end=None, filepattern_start=None, exclude_filepattern_end=None, api_key=None,
                           max_connections=None, max_filesize=None, skip_completed=True, filepatterns=None):
    for ds_id, directory_containing_outputs in ds_lookup.items():
        get_info_response_json = get_tcr_info_json(miqa_server, run_id, directory_containing_outputs, ds_id=ds_id)
        exec_id = get_info_response_json.get("exec_id")
        if skip_completed:
            if "exec_status" in get_info_response_json:
                if get_info_response_json.get("exec_status").lower() == "done":
                    print(f"Skipping upload for {exec_id}: status is already Done")
                    continue
        upload_files_or_folder_for_exec(exec_id, miqa_server, directory_containing_outputs, None,
                                        filepattern_end=filepattern_end,
                                        filepattern_start=filepattern_start,
                                        exclude_filepattern_end=exclude_filepattern_end, max_filesize=max_filesize,
                                        api_key=api_key,
                                        max_connections=max_connections, filepatterns=filepatterns)
        complete_exec(exec_id, miqa_server)


if __name__ == '__main__':
    parser = ArgumentParser(description='A command line tool for interacting with the Miqa API')
    parser.add_argument('--trigger_id', type=str, default=None, help='Trigger ID in Miqa')
    parser.add_argument('--server', type=str, default=None, help='Miqa Server URL')
    parser.add_argument('--version_name', type=str, default=None, help='Version Name to create (e.g. MyPipeline v1.0, or commit ID e.g. abc123de')
    parser.add_argument('--directory', type=str, default=None, help='Path to local directory containing files to upload')
    args = parser.parse_args()

    trigger_test_and_upload_single_results(args.server, args.trigger_id, args.version_name, args.directory)

