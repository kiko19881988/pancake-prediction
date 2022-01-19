import math
import random

from pancake import Prediction


def apply(psp: Prediction, df_running, current_epoch, base_bet, value, factor):

    """
    Add your bet logic here
    This example bet random either up or down:
    """
    last_claimable_epoch = df_running[
        (df_running["epoch"] <= current_epoch - 2)
        &
        (df_running["result"] == -1)
        ].max()["epoch"]

    if (last_claimable_epoch is None) or math.isnan(last_claimable_epoch):
        value = base_bet
    elif psp.claimable(last_claimable_epoch):
        value = base_bet
    else:
        value = value * factor

    rand = random.getrandbits(1)
    if rand:
        trx_hash = psp.betBull(value)
        position = "bull"
    else:
        trx_hash = psp.betBear(value)
        position = "bear"

    return position, value, trx_hash
