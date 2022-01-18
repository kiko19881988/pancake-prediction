import random

from pancake import Prediction


def random(psp: Prediction, value, plh_running):

    """
    Add your bet logic here
    This example bet random either up or down:
    """
    rand = random.getrandbits(1)

    if rand:
        res = psp.betBull(value)
    else:
        res = psp.betBear(value)

    plh_running.write(psp.get_running_df())
