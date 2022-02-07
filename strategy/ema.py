import math
import numpy as np
from pancake import Prediction
from ui.history import get_history


def calculate_ema(prices, days, smoothing=2):
    ema = [sum(prices[:days]) / days]
    for price in prices[days:]:
        ema.append((price * (smoothing / (1 + days))) + ema[-1] * (1 - (smoothing / (1 + days))))
    return ema


def apply(psp: Prediction, df_running, current_epoch,
          base_bet, value, factor, safe_bet, bet_status):
    """
    This strategy calculates the Exponential Moving Average (EMA) of the last 9 and 21 epochs
    to estimate which position should be placed.
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

    df_history_round = get_history(psp, current_epoch, back_in_time=21)

    currentPrice = np.round(df_history_round["closePrice"].iloc[0], 1)
    ema9 = np.round(calculate_ema(df_history_round["closePrice"].iloc[:9], 9), 1)
    ema21 = np.round(calculate_ema(df_history_round["closePrice"].iloc[:21], 21), 1)

    print('ema9 :', ema9, ' ema21:', ema21)

    custom_factor = 0
    if ema9 == ema21:
        print('do nothing')
        position = "skip"

    elif ema9 < ema21:
        custom_factor = current_round_stats["bear_pay_ratio"] - safe_bet
        position = "bear"
        if currentPrice > ema9:
            print('bet bearish , confidence 100')
        else:
            print('bet bearish , confidence enough')

    elif ema9 > ema21:
        custom_factor = current_round_stats["bull_pay_ratio"] - safe_bet
        position = "bull"
        if currentPrice < ema9:
            print('bet bullish , confidence 100')
        else:
            print('bet bullish , confidence enough')

    if factor == 0:
        if custom_factor < 1:
            custom_factor += safe_bet

        if bet_status["estimated_gain"] >= 0:
            loss = bet_status["recent_loss"]
        else:
            loss = max(bet_status["recent_loss"], abs(bet_status["estimated_gain"]))

        value = (loss + base_bet) / (custom_factor - 1)
        if value < base_bet:
            value = base_bet

    if position == "bull":
        # bullish
        trx_hash = psp.bet_bull(value)
    elif position == "bear":
        # bearish
        trx_hash = psp.bet_bear(value)
    else:
        trx_hash = None
        position = "skip"

    print(
        f"[{current_epoch}] Trend: {position} - V: {value} - F: x{factor} - CF: x{custom_factor} - Loss: {bet_status['recent_loss']}")
    return position, value, trx_hash
