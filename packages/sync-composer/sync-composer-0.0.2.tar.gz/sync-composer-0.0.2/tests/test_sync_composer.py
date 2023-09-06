import os
import sys
import shutil
sys.path.append('.')
import tempfile

import unittest
from unittest import mock

from  data_mock.google.cloud import storage as mock_storage

from sync_composer import sync_composer as sync_composer

CONTENT1= 'mock-contents'

class Mock1(mock_storage.Client):

    def register_initial_mock_data(self):
        self.register_mock_data(blob_name = 'dags/dag1', 
                bucket_name = 'mock-bucket', contents = CONTENT1 )
        self.register_mock_data(blob_name = 'any', 
                bucket_name = 'mock-bucket', contents = CONTENT1 )

class Mock2(mock_storage.Client):

    def register_initial_mock_data(self):
        self.register_mock_data(blob_name = 'dags/dag1', 
                bucket_name = 'mock-bucket', contents = CONTENT1 )
        self.register_mock_data(blob_name = 'dags/airflow_monitoring.py', 
                bucket_name = 'mock-bucket', contents = CONTENT1 )
        self.register_mock_data(blob_name = 'any', 
                bucket_name = 'mock-bucket', contents = CONTENT1 )

class Mock3(mock_storage.Client):

    def register_initial_mock_data(self):
        self.register_mock_data(blob_name = 'dags/dag1.py', 
                bucket_name = 'mock-bucket', contents = 'xx' )
        self.register_mock_data(blob_name = 'dags/airflow_monitoring.py', 
                bucket_name = 'mock-bucket', contents = CONTENT1 )
        self.register_mock_data(blob_name = 'any', 
                bucket_name = 'mock-bucket', contents = CONTENT1 )

class Mock4(mock_storage.Client):

    def register_initial_mock_data(self):
        self.register_mock_data(blob_name = 'dags/dag1.py', 
                bucket_name = 'mock-bucket', contents = 'no match' )
        self.register_mock_data(blob_name = 'dags/airflow_monitoring.py', 
                bucket_name = 'mock-bucket', contents = CONTENT1 )
        self.register_mock_data(blob_name = 'any', 
                bucket_name = 'mock-bucket', contents = CONTENT1 )


def create_dags(temp_dir, file_names, make_dags = True):
    if make_dags:
        dags_dir = os.path.join(temp_dir, 'dags')
        os.mkdir(dags_dir)
    else:
        dags_dir = temp_dir
    all_files = []
    for i in file_names:
        path = os.path.join(dags_dir, i)
        all_files.append(path)
        with open(path, 'w') as write_obj:
                  write_obj.write('xx')
    return dags_dir, all_files

@mock.patch('google.cloud.storage.Client', side_effect= Mock1 )
def test_1_upload_1_delete_no_patters(m1):
    temp_dir = tempfile.mkdtemp()
    dags_dir, all_files = create_dags(temp_dir = temp_dir, 
                           file_names = ['file1.py'])
    deleted_from_storage, uploaded = sync_composer.sync_bucket(
        directory = os.path.join(dags_dir),
        bucket_name = 'mock-bucket', 
        project = 'mock', 
        ignore_path= None, 
        verbosity = 0)
    shutil.rmtree(temp_dir)
    assert deleted_from_storage == ['dags/dag1']
    assert uploaded == all_files

@mock.patch('google.cloud.storage.Client', side_effect= Mock2 )
def test_patterns_work_for_bucket_and_local(m1):
    temp_dir = tempfile.mkdtemp()
    dags_dir, all_files = create_dags(temp_dir = temp_dir, 
                           file_names = ['file1.py', 'do_not_upload.py'])
    fh, path = tempfile.mkstemp()
    with open(path, 'w') as write_obj:
        write_obj.write(f'dags/airflow_monitoring.py\n')
        write_obj.write(f'*dags/do_not_upload.py\n')
    deleted_from_storage, uploaded = sync_composer.sync_bucket(
        directory = os.path.join(dags_dir),
        bucket_name = 'mock-bucket', 
        project = 'mock', 
        ignore_path= path, 
        verbosity = 0)
    shutil.rmtree(temp_dir)
    os.close(fh)
    os.remove(path)
    for i in uploaded:
        assert 'do_not_upload' not in i
    for i in deleted_from_storage:
        assert 'airflow_monitoring' not in i

@mock.patch('google.cloud.storage.Client', side_effect= Mock3 )
def test_no_changed_file_no_upload_no_delete(m1):
    temp_dir = 'dags'
    shutil.rmtree(temp_dir, ignore_errors = True)
    os.mkdir(temp_dir)
    dags_dir, all_files = create_dags(temp_dir = temp_dir, 
                           file_names = ['dag1.py'], make_dags = False)
    fh, path = tempfile.mkstemp()
    with open(path, 'w') as write_obj:
        write_obj.write(f'dags/airflow_monitoring.py\n')
        write_obj.write(f'*dags/do_not_upload.py\n')
    deleted_from_storage, uploaded = sync_composer.sync_bucket(
        directory = os.path.join(dags_dir),
        bucket_name = 'mock-bucket', 
        project = 'mock', 
        ignore_path= path, 
        verbosity = 0)
    shutil.rmtree(temp_dir)
    os.close(fh)
    os.remove(path)
    assert len(deleted_from_storage) == 0
    assert len(uploaded) == 0

@mock.patch('google.cloud.storage.Client', side_effect= Mock4 )
def test_changed_file_one_upload_no_delete(m1):
    temp_dir = 'dags'
    shutil.rmtree(temp_dir, ignore_errors = True)
    os.mkdir(temp_dir)
    dags_dir, all_files = create_dags(temp_dir = temp_dir, 
                           file_names = ['dag1.py'], make_dags = False)
    fh, path = tempfile.mkstemp()
    with open(path, 'w') as write_obj:
        write_obj.write(f'dags/airflow_monitoring.py\n')
        write_obj.write(f'*dags/do_not_upload.py\n')
    deleted_from_storage, uploaded = sync_composer.sync_bucket(
        directory = os.path.join(dags_dir),
        bucket_name = 'mock-bucket', 
        project = 'mock', 
        ignore_path= path, 
        verbosity = 0)
    shutil.rmtree(temp_dir)
    os.close(fh)
    os.remove(path)
    assert len(deleted_from_storage) == 0
    assert len(uploaded) == 1


