import streamlit as st
import pandas as pd

from utils.round import round_columns


@st.cache_data(ttl=60 * 5)
def get_history(_psp, current_epoch, back_in_time=100):
    start_epoch_history = current_epoch - 2 - back_in_time

    df_history_round = pd.DataFrame(columns=round_columns)
    for i in range(start_epoch_history, current_epoch - 1):
        df_round = _psp.get_round(i)

        if df_round.empty:
            df_history_round = df_history_round.copy()
        if df_history_round.empty:
            df_history_round = df_history_round.copy()
        if not df_round.empty and not df_history_round.empty:
            df_history_round = pd.concat([df_history_round, df_round])

    df_history_round = df_history_round.sort_values('epoch', ascending=False)
    df_history_round = df_history_round.reset_index(drop=True)

    return df_history_round
