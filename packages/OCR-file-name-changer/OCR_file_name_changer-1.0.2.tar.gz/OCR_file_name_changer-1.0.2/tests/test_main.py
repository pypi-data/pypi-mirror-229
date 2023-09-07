import os
import unittest
import zipfile

from helpers import TempDirOfValidSamples, zip_archive_contains_files
from ocr_file_name_changer.main import *
from samples import *


class TestMain(unittest.TestCase):
    test_dir = os.path.join(os.getcwd(), "test_files")

    def test_read_img_paths_read_all_valid_samples(self):
        with TempDirOfValidSamples(os.path.join(self.test_dir, "tmp")) as current_dir:
            paths = read_img_paths(current_dir.dir_path)
            self.assertTrue(len(VALID_SAMPLES), len(paths))

    def test_read_img_paths_generate_file_names(self):
        with TempDirOfValidSamples(os.path.join(self.test_dir, "tmp")) as current_dir:
            paths = read_img_paths(current_dir.dir_path)
            names_dict = generate_new_file_names(paths)
            self.assertTrue(len(VALID_SAMPLES), len(names_dict))

    def test_rename_files(self):
        with TempDirOfValidSamples(os.path.join(self.test_dir, "tmp")) as current_dir:
            paths = read_img_paths(current_dir.dir_path)
            names_dict = generate_new_file_names(paths)
            rename_img_files(names_dict)

            for old_path, new_name in names_dict.items():
                self.assertFalse(os.path.isfile(old_path))
                file_dir_path, _ = os.path.split(old_path)
                new_path = os.path.join(file_dir_path, new_name)
                self.assertTrue(os.path.isfile(new_path))

    def test_read_sn_and_rename_files(self):
        with TempDirOfValidSamples(os.path.join(self.test_dir, "tmp")) as current_dir:
            archive_path = read_sn_and_rename_files(dir_path=current_dir.dir_path)
            self.assertTrue(os.path.isfile(archive_path))
            zip_file = zipfile.ZipFile(archive_path)
            files = zip_file.namelist()
            self.assertEqual(len(VALID_SAMPLES), len(files))
            zip_file.close()

