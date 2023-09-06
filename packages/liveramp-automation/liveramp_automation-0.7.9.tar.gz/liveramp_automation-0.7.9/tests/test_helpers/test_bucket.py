from liveramp_automation.helpers.gcs import GoogleCloudStorageHelper
from liveramp_automation.utils.time import MACROS

project_id = "liveramp-eng-qa-reliability"
bucket_name = "liveramp_automation_test"
file = "test.ini"
file_download = "test_download.ini"
number_lines = 3
string = "test"
source_file_path = "tests/test_helpers/"
destination_blob_name = "liveramp_automation_test/bucket/{}/".format('now'.format(**MACROS))
bucket_manager = GoogleCloudStorageHelper(project_id, bucket_name)
file_manager = GoogleCloudStorageHelper(project_id, bucket_name)


def test_upload_files():
    result = bucket_manager.upload_files_to_bucket(source_file_path, destination_blob_name)
    assert result


def test_upload_file():
    result = bucket_manager.upload_file(source_file_path, destination_blob_name)
    assert result == 0


def test_check_file_exists():
    result = bucket_manager.check_file_exists(destination_blob_name)
    assert result


def test_download_file():
    result = bucket_manager.download_file(source_file_path, file_download)
    assert result == 1


def test_list_files_with_substring():
    result = bucket_manager.list_files_with_substring(string)
    assert result


def test_get_total_rows():
    result = file_manager.get_total_rows(destination_blob_name)
    assert result


def test_read_file_content():
    result = file_manager.read_file_content(destination_blob_name)
    assert result


def test_read_file_lines():
    result = file_manager.read_file_lines(destination_blob_name, number_lines)
    assert result
