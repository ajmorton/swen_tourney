import typing


def print_dict_sorted(d: typing.Dict, depth: int = 0):
    """
    Sort and print a dictionary, recursively printing any sub-dictionaries
    :param d: the dictionary to print
    :param depth: how many tabs to place in front of printed output
    :return:
    """
    for key in sorted(d.keys()):
        if isinstance(d[key], typing.Dict):
            print("{}{}".format("    " * depth, key))
            print_dict_sorted(d[key], depth + 1)
        else:
            print("{}{} = {}".format("    " * depth, key, d[key]))
