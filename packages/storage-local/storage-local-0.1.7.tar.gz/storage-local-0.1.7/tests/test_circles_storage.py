import os
import sys
sys.path.append(os.getcwd())
from circles_local_aws_s3_storage_python import constants # noqa: E402
from circles_local_aws_s3_storage_python.CirclesStorage import circles_storage # noqa: E402
from circles_local_aws_s3_storage_python.StorageDB import StorageDB # noqa: E402

import unittest
from dotenv.main import load_dotenv
import pytest
load_dotenv()

PROFILE_ID = 1

class circles_storage_test(unittest.TestCase):
    def setUp(self) -> None:
        self.circles_storage = circles_storage(True)
        self.db=StorageDB()
        self.test = 0
        #print("REGION:"+str(os.getenv("REGION")))

    def test_get_folder(self):
        actual_folder = self.circles_storage._get_folder(
            constants.PROFILE_IMAGE)
        expected_folder = 'Profile Image'
        self.assertEqual(actual_folder, expected_folder)

    def test_get_region_and_folder(self):
        actual = self.circles_storage._get_region_and_folder(profile_id=PROFILE_ID,
                                                             entity_type_id=constants.PROFILE_IMAGE)
        actual = str(actual).replace(" ", "")
        expected = "['ProfileImage','us-east-1']"
        self.assertEqual(actual, expected)

    def test_put(self):
        cwd = os.getcwd()
        filepath = os.path.join(cwd, 'tests/test.txt')
        id = self.circles_storage.put(profile_id=PROFILE_ID, entity_type_id=constants.PROFILE_IMAGE, file_name='circles_test.txt',
                                      local_file_path=filepath)
        self.assertGreater(id, 0)

    def test_download(self):
        cwd = os.getcwd()
        filepath = os.path.join(cwd, 'download_test.txt')
        self.circles_storage.download(
            entity_type_id=constants.PROFILE_IMAGE, profile_id=PROFILE_ID, file_name='circles_test.txt', local_path=filepath)
        assert os.path.isfile(
            filepath)

    def test_download_storage_id(self):
        cwd=os.getcwd()
        filepath = os.path.join(cwd, 'download_test.txt')
        self.circles_storage.download_by_storage_id(self.db.getLastId())
        assert os.path.isfile(filepath)

if __name__ == '__main__':
    unittest.main()
