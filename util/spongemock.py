import random


def mockify(text: str):
    """
    Randomizes character case in a string.

    :param text: Text to randomize case on
    :return: str
    """

    return ''.join(random.choice((str.upper, str.lower))(x) for x in text)
