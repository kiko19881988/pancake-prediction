import math
from pancake import Prediction


def apply(psp: Prediction, df_running, current_epoch,
          base_bet, value, factor, safe_bet, current_round_stats, bet_status):
    """
    This strategy bets exactly the same as the last known epoch.
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

    data = psp.get_round(current_epoch - 2)
    lock_price = data["lockPrice"].iloc[0]
    close_price = data["closePrice"].iloc[0]

    if factor == 0:
        if safe_bet:
            custom_factor = min(current_round_stats["bear_pay_ratio"], current_round_stats["bull_pay_ratio"])
        else:
            if lock_price < close_price:
                # bull
                custom_factor = current_round_stats["bull_pay_ratio"]
            else:
                # bear
                custom_factor = current_round_stats["bear_pay_ratio"]

        value = (bet_status["recent_loss"] + base_bet) / custom_factor
        if value < base_bet:
            value = base_bet

    if lock_price > close_price:
        # bearish
        trx_hash = psp.bet_bear(value)
        position = "bear"
    elif lock_price < close_price:
        # bullish
        trx_hash = psp.bet_bull(value)
        position = "bull"
    elif lock_price == close_price:
        # draw
        trx_hash = psp.bet_bear(value)
        position = "bear"

    return position, value, trx_hash
