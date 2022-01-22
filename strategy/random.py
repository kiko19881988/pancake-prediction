import math
import random

from pancake import Prediction


def apply(psp: Prediction, df_running, current_epoch,
          base_bet, value, factor, safe_bet, bet_status):
    """
    This strategy bets randomly either up or down.
    Martingle technique is also being applied.
    """
    current_round_stats = psp.get_round_stats(current_epoch)

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

    rand = random.getrandbits(1)

    if factor == 0:
        if rand:
            # bull
            custom_factor = current_round_stats["bull_pay_ratio"] - safe_bet
        else:
            # bear
            custom_factor = current_round_stats["bear_pay_ratio"] - safe_bet

        if custom_factor < 1:
            custom_factor += safe_bet

        if bet_status["estimated_gain"] >= 0:
            loss = bet_status["recent_loss"]
        else:
            loss = max(bet_status["recent_loss"], abs(bet_status["estimated_gain"]))

        value = (loss + base_bet) / (custom_factor - 1)
        if value < base_bet:
            value = base_bet

    if rand:
        trx_hash = psp.bet_bull(value)
        position = "bull"
    else:
        trx_hash = psp.bet_bear(value)
        position = "bear"

    return position, value, trx_hash
