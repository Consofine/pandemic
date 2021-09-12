import random
import string
from constants import CITY_LIST


def generate_id(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def validate_keys(keys, types):
    try:
        for x in range(len(keys)):
            keys[x] = types[x](keys[x])
    except ValueError:
        return False
    return True
