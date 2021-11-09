
import random as random_lib
import string


def random(length=8, chars=string.ascii_letters + string.digits):
    return ''.join(random_lib.choice(chars) for _ in range(length))
