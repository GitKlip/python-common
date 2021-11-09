from common.strings import random


def test_random():
    rand_string = random(13)
    assert len(rand_string) == 13
