import os
import shutil
from glob import glob


def get_image_paths_from_directory(dir_path: str) -> list[str]:
    jpg_files = f"{dir_path}/*.jpg"
    jpeg_files = f"{dir_path}/*.jpeg"
    png_files = f"{dir_path}/*.png"
    files = glob(jpg_files)
    files.extend(glob(jpeg_files))
    files.extend(glob(png_files))
    return files


def rename_file(file_path: str, new_name: str) -> str:
    try:
        file_dir_path, _ = os.path.split(file_path)
        new_path = os.path.join(file_dir_path, new_name)
        if os.path.isfile(new_path):
            raise FileExistsError(f"File {new_path} already exists")

        os.rename(file_path, new_path)
        return new_path
    except FileNotFoundError:
        print(f"File {file_path} not found")
        return ""


def zip_directory(dir_path: str) -> str:
    arch_path, archive_name = os.path.split(dir_path)
    try:
        return _make_archive(dir_path, os.path.join(dir_path, archive_name) + ".zip")
    except FileNotFoundError:
        print(f"Error while archiving {dir_path}: File {dir_path} not found")
    except FileExistsError:
        print(f"Error creating archive {dir_path}: File {dir_path}/{archive_name} already exists")
        print(f"Error creating archive {dir_path}: File {os.path.join(dir_path, archive_name)} already exists")


def _make_archive(source, destination):
    base = os.path.basename(destination)
    name = base.split('.')[0]
    format = base.split('.')[1]
    shutil.make_archive(name, format, source)
    shutil.move('%s.%s' % (name, format), destination)
    return destination


def get_file_name(file_path: str) -> str:
    _, file_name = os.path.split(file_path)
    return file_name
