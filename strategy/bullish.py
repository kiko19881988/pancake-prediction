import math

from pancake import Prediction


def apply(psp: Prediction, df_running, current_epoch, base_bet, value, factor):
    """
    This strategy bets always bullish.
    Martingle technique is also being applied.
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

    trx_hash = psp.bet_bull(value)
    position = "bull"

    return position, value, trx_hash
