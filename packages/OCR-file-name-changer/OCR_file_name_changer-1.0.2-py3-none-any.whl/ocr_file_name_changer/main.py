import os
import string
from typing import Callable

from .exceptions import IncorrectImageException
from .files_handling import get_image_paths_from_directory, get_file_name, rename_file, zip_directory
from .ocr_handling import extract_sn_from_img


def read_sn_and_rename_files(dir_path=os.getcwd()):
    print("[1/4] Wyszukiwanie plikow...")
    img_paths = read_img_paths(dir_path)
    if len(img_paths) > 0:
        print("[2/4] Rozpoznawanie tekstu ze zdjec...")
        new_file_names_dict = generate_new_file_names(img_paths)
        print("[3/4] Zmienianie nazw plikow...")
        rename_img_files(new_file_names_dict)
        print("[4/4] Tworzenie archiwum...")
        old_cwd = os.getcwd()
        os.chdir("..")
        archive_path = zip_directory(dir_path)
        os.chdir(old_cwd)
        print("Zadanie wykonane")
        return archive_path
    return ""


def read_img_paths(dir_path: str) -> list[str]:
    img_paths = get_image_paths_from_directory(dir_path)
    print(f"W katalogu {dir_path} znaleziono {len(img_paths)} zdjec")
    return img_paths


def generate_new_file_names(img_paths: list[str]) -> dict[str, str]:
    """
    :return: dict containing: [old_path, new_file_name]
    """

    new_file_names_dict: dict[str, str] = {}
    for img_path in img_paths:
        try:
            extracted_sn = extract_sn_from_img(img_path)
            new_file_names_dict[img_path] = extracted_sn + os.path.splitext(img_path)[1]
        except IncorrectImageException:
            print(f"Plik \n{get_file_name(img_path)}\n zawiera wiecej niz 1 napis - zdjecie zostalo pominiete")
    return new_file_names_dict


def skip_existing_file_name_callback(old_file_path: str, new_file_name: str) -> str:
    return ""


def default_existing_file_name_callback(old_file_path: str, new_file_name: str) -> str:
    for letter in string.ascii_letters:
        alt_name = letter + new_file_name
        file_dir_path, _ = os.path.split(old_file_path)
        path = os.path.join(file_dir_path, alt_name)
        if not os.path.isfile(path):
            return alt_name
    print(f"Failed to generate alternative file name for file {old_file_path}.")
    return ""


def rename_img_files(new_file_names: dict[str, str],
                     alt_file_name_callback: Callable[[str, str], str] = default_existing_file_name_callback):
    """
    :param alt_file_name_callback: callback to generate new file name if given file name is taken
        callback is given old_file_path and new_file_name and returns new alt new file name. If it returns empty string
        the file is not renamed
    :param new_file_names: dict containing: [old_path, new_file_name]
    """

    for img_path, new_name in new_file_names.items():
        try:
            rename_file(img_path, new_name)
        except FileExistsError as exc:
            alt_file_name = alt_file_name_callback(img_path, new_name)
            if alt_file_name != "":
                rename_file(img_path, alt_file_name)
            else:
                print(f"Pominieto zmiane nazwy pliku {img_path}, poniewaz: ")
                print(exc)


def main():
    read_sn_and_rename_files()
