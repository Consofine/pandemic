import random
import string
from constants import CITY_LIST


def generate_id(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def validate_keys(keys, types):
    for x in range(keys):
        if not isinstance(keys[x], types[x]):
            return False
    return True
