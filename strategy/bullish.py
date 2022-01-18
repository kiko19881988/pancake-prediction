from pancake import Prediction


def bullish(psp: Prediction, value, plh_running):
    res = psp.betBull(value)

    plh_running.write(psp.get_running_df())

