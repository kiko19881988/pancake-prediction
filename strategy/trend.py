import math
import statsmodels.api as sm
from pancake import Prediction
from ui.history import get_history


def apply(psp: Prediction, df_running, current_epoch,
          base_bet, value, factor, safe_bet, current_round_stats, bet_status):
    """
    This strategy takes the last hour, and calculates the trend line to decide if
    it should bet bear or bull.
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

    # retrieving the history in the last 30 min (6 rounds)
    df_history_round = get_history(psp, current_epoch, back_in_time=6)

    X = df_history_round.index
    X = X.astype(float)

    y = df_history_round['closePrice']
    y = y.astype(float)

    X = sm.add_constant(X)
    model = sm.OLS(y, X).fit()

    alpha = model.params['x1']
    # beta = model.params['const']

    if factor == 0:
        if safe_bet:
            custom_factor = min(current_round_stats["bear_pay_ratio"], current_round_stats["bull_pay_ratio"])
        else:
            if alpha < 0:
                # bull
                custom_factor = current_round_stats["bull_pay_ratio"]
            else:
                # bear
                custom_factor = current_round_stats["bear_pay_ratio"]

        value = (bet_status["recent_loss"] + base_bet) / custom_factor
        if value < base_bet:
            value = base_bet

    # because the dataframe is sorted descending, negative alpha is bullish
    if alpha < 0:
        # bullish
        trx_hash = psp.bet_bull(value)
        position = "bull"
    else:
        # bearish
        trx_hash = psp.bet_bear(value)
        position = "bear"

    return position, value, trx_hash
