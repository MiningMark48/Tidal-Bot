import random


def mockify(text: str):
    return ''.join(random.choice((str.upper, str.lower))(x) for x in text)
