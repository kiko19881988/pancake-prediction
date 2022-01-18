from pancake import Prediction


def bearish(psp: Prediction, value, plh_running):
    res = psp.betBear(value)

    plh_running.write(psp.get_running_df())
