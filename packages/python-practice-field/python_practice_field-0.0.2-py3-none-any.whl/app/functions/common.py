"""General purpose functions. Most probably for methods_functions simplifying."""
import json

from app.configs.functions_config import PATH_DATA_FOLDER


def read_json_to_dict(file_name: str) -> dict:
    """
    Read default store positions.

    :param file_name: name of file with extension
    :returns: Validated via StorePositions class default store positions
    """
    file_path = PATH_DATA_FOLDER / file_name
    with open(file_path) as file_object:
        dict_object = json.load(file_object)

    return dict_object


def read_txt_to_list(file_name: str) -> list:
    """
    Read default products substrs.

    :param file_name: name of file with extension
    :returns: List of substrs
    """
    file_path = PATH_DATA_FOLDER / file_name
    with open(file_path) as file_object:
        list_object = file_object.read().split('\n')

    return list(filter(None, list_object))
