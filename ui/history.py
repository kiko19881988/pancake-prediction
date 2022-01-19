import streamlit as st
import pandas as pd

from utils.round import round_columns


@st.experimental_memo(ttl=60 * 5)
def get_history(_psp, current_epoch, back_in_time=100):
    start_epoch_history = current_epoch - 2 - back_in_time

    df_history_round = pd.DataFrame(columns=round_columns)
    for i in range(start_epoch_history, current_epoch - 1):
        df_round = _psp.get_round(i)
        df_history_round = df_history_round.append(df_round)

    df_history_round = df_history_round.sort_values('epoch', ascending=False)
    df_history_round = df_history_round.reset_index(drop=True)

    return df_history_round
