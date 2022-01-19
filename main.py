import streamlit as st
import time
import datetime as dt
import asyncio

import strategy
from ui.expanders import update_current, update_history, update_running
from ui.params import create_params_ui
import pancake
from utils.config import config

st.set_page_config(page_title="PancakeSwap Prediction V2",
                   page_icon=None,
                   layout="wide", initial_sidebar_state="auto",
                   menu_items=None)


async def update_ui(psp, current_epoch, plh_update):
    while True:
        update_current(psp, current_epoch, plh_update)
        _ = await asyncio.sleep(1)


def main():
    st.title("PancakeSwap Prediction V2")
    if config["experimental"]["debug"]:
        st.warning(":warning: **Debug/Simulation Mode** is turned on. No actual bet will be placed."
                   " Change it in the **config.toml** file.")

    psp = pancake.Prediction()

    sidebar_params = create_params_ui(psp)
    psp = sidebar_params["psp"]

    current_epoch = psp.get_current_epoch()

    plh_current = st.empty()
    update_current(psp, current_epoch, plh_current)

    plh_history = st.empty()
    update_history(psp, current_epoch, plh_history)

    plh_running = st.empty()
    update_running(psp, plh_running)

    st.download_button(label="Download Running History (CSV)",
                       data=st.session_state.df_running.to_csv().encode('utf-8'),
                       file_name="running.csv",
                       mime="text/csv")

    plh_timer = st.empty()
    plh_status = st.empty()

    if st.button("Run Strategy"):
        i_bet = 0
        btn_stop = st.button("Stop")
        value = base_bet = sidebar_params["base_bet"]

        while True:
            update_current(psp, current_epoch, plh_current)
            update_history(psp, current_epoch, plh_history)
            update_running(psp, plh_running)

            if btn_stop:
                break

            factor = sidebar_params["factor"]
            df_running = psp.get_running_df()
            current_round = psp.new_round()

            bet_time = current_round[0]
            current_epoch = current_round[1]
            now = dt.datetime.now()

            plh_timer.info(f"""
                          Now: {now}
                          
                          Bet: {bet_time}""")

            if now >= bet_time:
                if df_running[df_running["epoch"] == current_epoch].shape[0] == 0:

                    i_bet += 1

                    # --- START STRATEGY HERE ---
                    if sidebar_params["strategy"] == "Random":
                        position, value, trx_hash = strategy.random.apply(psp, df_running, current_epoch,
                                                                          base_bet, value, factor)

                    # --- END STRATEGY HERE ---

                    plh_status.success(f"Bet #{i_bet} - Value: {value} - Position: {position} - Trx: {trx_hash}")
            time.sleep(1)

    if st.button("Claim All"):
        total_claims, claim_hash = psp.handleClaim()
        if total_claims > 0:
            st.info(f"{total_claims} epochs were claimed: {claim_hash}")

    asyncio.run(update_ui(psp, current_epoch, plh_current))


if __name__ == '__main__':
    main()
