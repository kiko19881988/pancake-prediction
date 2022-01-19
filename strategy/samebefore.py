import math

from pancake import Prediction


def apply(psp: Prediction, df_running, current_epoch, base_bet, value, factor):

    """
    Add your bet logic here
    This example bet random either up or down:
    """
    last_epoch = df_running[
        (df_running["epoch"] <= current_epoch - 2)
        &
        (df_running["reward"] != 0)
        ].max()["epoch"]

    if (last_epoch is None) or math.isnan(last_epoch):
        value = base_bet
    else:
        last_epoch_result = df_running[
            (df_running["epoch"] == last_epoch)
        ]["reward"].iloc[0]

        if last_epoch_result > 0:
            value = base_bet
        else:
            value = value * factor

    data = psp.get_round_stats(current_epoch - 2)
    lock_price = data["lockPrice"].iloc[0]
    close_price = data["closePrice"].iloc[0]

    if lock_price > close_price:
        # bearish
        trx_hash = psp.betBear(value)
        position = "bear"
    elif lock_price < close_price:
        # bullish
        trx_hash = psp.betBull(value)
        position = "bull"
    elif lock_price == close_price:
        # draw
        trx_hash = psp.betBear(value)
        position = "bear"

    return position, value, trx_hash
