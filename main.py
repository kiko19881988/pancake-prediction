import streamlit as st
import time
import datetime as dt
import pandas as pd
import numpy as np

from ui.history import get_history
from ui.wallet import update_balance
from utils.round import important_round_columns, current_round_columns, round_columns
from utils.wallet import simulate_budget
import pancake
import strategy

STRATEGIES = ["Random", "Bullish", "Bearish"]

st.set_page_config(page_title="PancakeSwap Predictions V2",
                   page_icon=None,
                   layout="wide", initial_sidebar_state="auto",
                   menu_items=None)


def main():
    st.title("PancakeSwap Predictions V2")
    psp = pancake.Prediction()

    wallet_address = st.sidebar.text_input("Wallet Address", value="0x4a6779DaA59d5C0467E48CAE716557099AF842e3")

    if len(wallet_address) > 0:
        psp.set_address(address=wallet_address)
        my_balance = psp.get_balance()
        min_bet = psp.get_min_bet()

        lbl_account_balance = st.sidebar.empty()
        update_balance(lbl_account_balance, my_balance)

    private_key = st.sidebar.text_area("Private Key", value="")
    if len(private_key) > 0:
        psp.set_private_key(private_key=private_key)

    selected_strategy = st.sidebar.selectbox("Strategy", options=STRATEGIES)
    base_bet = st.sidebar.number_input("Base Bet (BNB)",
                                       value=float(min_bet), min_value=float(min_bet), step=0.001,
                                       format="%.5f")
    st.sidebar.caption(f'Min Bet: {min_bet:.5f} BNB')

    factor = st.sidebar.number_input("Multiplication Factor",
                                     value=2.0, min_value=2.0,
                                     step=0.1, max_value=10.0)
    st.sidebar.warning(f"You may need "
                       f"**{simulate_budget(base_bet=base_bet, factor=factor)} BNB** "
                       f"in your wallet.")

    st.button("Refresh")

    current_epoch = psp.get_current_epoch()
    df_current_round = psp.get_round(current_epoch)

    current_expander = st.expander(f"Current #{current_epoch}", expanded=True)
    with current_expander:

        total_amount = (df_current_round["bullAmount"] + df_current_round["bearAmount"]).iloc[0]
        st.write(df_current_round[current_round_columns])

        if total_amount > 0:
            bull_ratio = ((df_current_round["bullAmount"] / total_amount) * 100).iloc[0]
            bear_ratio = ((df_current_round["bearAmount"] / total_amount) * 100).iloc[0]
            bear_pay_ratio = ((df_current_round["bullAmount"] / df_current_round["bearAmount"])).iloc[0] + 1
            bull_pay_ratio = ((df_current_round["bearAmount"] / df_current_round["bullAmount"])).iloc[0] + 1

            col1, col2 = st.columns(2)
            col1.write(f"Bullish **x{bull_pay_ratio:.2f}** - {bull_ratio:.2f}%")
            col2.write(f"Bearish **x{bear_pay_ratio:.2f}** - {bear_ratio:.2f}%")
        else:
            st.warning("No deposit yet. Wait few seconds...")

    history_expander = st.expander("Contract History")
    with history_expander:
        df_history_round = get_history(psp, current_epoch, back_in_time=100)
        st.write(df_history_round[important_round_columns])

    running_expander = st.expander("Running History", expanded=True)
    with running_expander:
        df_running = psp.get_running_df()
        plh_running = st.empty()
        plh_running.write(df_running)

        st.download_button(label="Download",
                           data=df_running.to_csv().encode('utf-8'),
                           file_name="running.csv",
                           mime="text/csv")

    if st.button("Run Strategy"):
        if selected_strategy == "Random":
            strategy.random(psp, base_bet, plh_running)
        elif selected_strategy == "Bullish":
            strategy.bullish(psp, base_bet, plh_running)
        elif selected_strategy == "Bearish":
            strategy.bearish(psp, base_bet, plh_running)

    if st.button("Claim All"):
        total_claims, claim_hash = psp.handleClaim()
        if total_claims > 0:
            st.info(f"{total_claims} epochs were claimed: {claim_hash}")


if __name__ == '__main__':
    main()
