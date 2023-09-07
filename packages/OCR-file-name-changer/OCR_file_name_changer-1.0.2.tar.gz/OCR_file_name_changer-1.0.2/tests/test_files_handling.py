import unittest

from helpers import TemporaryTestFile, zip_archive_contains_files
from ocr_file_name_changer.files_handling import *


class TestFilesHandling(unittest.TestCase):
    test_files_dir = os.path.join(os.getcwd(), "test_files")

    jpg_test_files_dir = os.path.join(test_files_dir, "image_path_retrieving_tests", "jpg_files")
    png_test_files_dir = os.path.join(test_files_dir, "image_path_retrieving_tests", "png_files")
    jpeg_test_files_dir = os.path.join(test_files_dir, "image_path_retrieving_tests", "jpeg_files")
    mixed_formats_files_dir = os.path.join(test_files_dir, "image_path_retrieving_tests", "mixed_format_files")
    rename_file_tests_dir = os.path.join("test_files", "rename_file_tests")

    archive_tests_dir = os.path.join("test_files", "archive_tests")

    def test_get_image_paths_from_directory_when_no_images(self):
        files = get_image_paths_from_directory(self.test_files_dir)
        self.assertEqual(0, len(files))

    def test_get_image_paths_from_directory_when_jpg_files(self):
        files = get_image_paths_from_directory(self.jpg_test_files_dir)
        self.assertEqual(2, len(files))

    def test_get_image_paths_from_directory_when_png_files(self):
        files = get_image_paths_from_directory(self.png_test_files_dir)
        self.assertEqual(2, len(files))

    def test_get_image_paths_from_directory_when_jpeg_files(self):
        files = get_image_paths_from_directory(self.jpeg_test_files_dir)
        self.assertEqual(2, len(files))

    def test_get_image_paths_from_directory_when_mixed_files(self):
        files = get_image_paths_from_directory(self.mixed_formats_files_dir)
        self.assertEqual(3, len(files))

    def test_rename_file_not_not_existing_file(self):
        path = os.path.join(self.rename_file_tests_dir, "some_not_existing_file_123123.txt")

        name = rename_file(path, "new_name")
        # fn should silently ignore error and return empty string
        self.assertEqual(name, "")

    def test_rename_file_new_name_exists(self):
        file_path = os.path.join(self.rename_file_tests_dir, "existing_file1.txt")

        def test_fn(): (
            rename_file(file_path, "existing_file2.txt"))

        self.assertRaises(FileExistsError, test_fn)

    def test_rename_file(self):
        file_path = os.path.join(self.rename_file_tests_dir, "tmp_file.txt")

        with TemporaryTestFile(file_path) as tmp_file:
            new_path = rename_file(file_path, "new_name.txt")
            tmp_file.update_path(new_path)
            self.assertTrue(os.path.isfile(new_path))

    def test_zip_directory_not_existing_path(self):
        zip_directory("/some/invalid/path")

    def test_zip_directory_archive_name_exists(self):
        zip_directory(self.archive_tests_dir)

    def test_zip_directory(self):
        path = os.path.join(self.archive_tests_dir, "example_archive")
        archive_name = zip_directory(path)
        self.assertTrue(os.path.isfile(archive_name))
        self.assertTrue(zip_archive_contains_files(archive_name, ["file.txt"]))
        os.remove(archive_name)
