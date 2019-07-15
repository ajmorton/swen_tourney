import typing


def print_dict_sorted(dict: typing.Dict, depth: int = 0):
    """
    Sort and print a dictionary, recursively printing any sub-dictionaries
    :param dict: the dictionary to print
    :param depth: how many tabs to place infront of printed output
    :return:
    """
    for key in sorted(dict.keys()):
        if isinstance(dict[key], typing.Dict):
            print("{}{}".format("    " * depth, key))
            print_dict_sorted(dict[key], depth + 1)
        else:
            print("{}{} = {}".format("    " * depth, key, dict[key]))
