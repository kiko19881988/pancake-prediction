import math

import streamlit as st
from ui.history import get_history
from utils.round import important_round_columns, current_round_columns


def update_current(psp, current_epoch, plh_update):
    with plh_update:
        # current round
        df_current_round = psp.get_round(current_epoch)
        current_expander = st.expander(f"Current #{current_epoch}", expanded=True)
        with current_expander:
            round_stats = psp.get_round_stats(current_epoch)
            total_amount = round_stats["total_amount"]
            bull_ratio = round_stats["bull_ratio"]
            bear_ratio = round_stats["bear_ratio"]
            bear_pay_ratio = round_stats["bear_pay_ratio"]
            bull_pay_ratio = round_stats["bull_pay_ratio"]

            st.write(df_current_round[current_round_columns])

            if total_amount > 0:
                col1, col2 = st.columns(2)
                col1.write(f"Bullish **x{bull_pay_ratio:.2f}** - {bull_ratio:.2f}%")
                col2.write(f"Bearish **x{bear_pay_ratio:.2f}** - {bear_ratio:.2f}%")
            else:
                st.warning("No deposit yet. Wait few seconds...")


def update_running(psp, plh_update):
    # running history
    df_running = psp.get_running_df()
    with plh_update:
        running_expander = st.expander(f"Positions History (#{df_running.shape[0]})", expanded=True)
        with running_expander:
            if "df_running" in st.session_state:
                if not st.session_state.df_running.equals(df_running):
                    if df_running.shape[0] == 0:
                        psp.set_df_running(st.session_state.df_running)
                    else:
                        st.session_state.df_running = df_running.copy()
            else:
                st.session_state.df_running = df_running.copy()

            df_running = st.session_state.df_running.copy()
            st.dataframe(df_running.style.bar(subset=['reward'], align='mid', color=['#d65f5f', '#5fba7d']))

            total_spent = df_running.sum()["amount"]
            total_loss = abs(df_running[df_running["reward"] < 0].sum()["reward"])
            loss_times = df_running[df_running["reward"] < 0].count()["reward"]
            estimated_win = df_running[df_running["reward"] > 0].sum()["reward"]
            win_times = df_running[df_running["reward"] > 0].count()["reward"]
            estimated_gain = estimated_win - total_loss

            last_win_epoch = df_running[df_running["reward"] > 0].max()["epoch"]
            if last_win_epoch is None or math.isnan(last_win_epoch):
                recent_loss = abs(df_running.sum()["reward"])
                recent_loss_times = df_running[df_running["reward"] < 0].count()["reward"]
            else:
                recent_loss = abs(df_running[df_running["epoch"] > last_win_epoch].sum()["reward"])
                recent_loss_times = df_running[(df_running["epoch"] > last_win_epoch)
                                               & (df_running["reward"] < 0)].count()["reward"]

            st.write(f"Total Spent: **{total_spent:.5f} BNB** in {df_running.shape[0]} rounds")
            st.write(f"Recent Loss: **{recent_loss:.5f} BNB** in {recent_loss_times} rounds")
            st.write(f"Total Loss: **{total_loss:.5f} BNB** in {loss_times} rounds")
            st.write(f"Estimated Win: **{estimated_win:.5f} BNB** in {win_times} rounds")
            st.write(f"Estimated Gain: **{estimated_gain:.5f} BNB**")

            return {"total_spent": total_spent,
                    "total_loss": total_loss,
                    "loss_times": loss_times,
                    "estimated_win": estimated_win,
                    "win_times": win_times,
                    "estimated_gain": estimated_gain,
                    "recent_loss": recent_loss,
                    "recent_loss_times": recent_loss_times}


def update_history(psp, current_epoch, plh_update):
    with plh_update:
        history_expander = st.expander("Contract History")
        with history_expander:
            df_history_round = get_history(psp, current_epoch, back_in_time=100)
            st.write(df_history_round[important_round_columns])
