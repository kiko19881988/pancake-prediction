import math
import pandas as pd
import streamlit as st
import datetime as dt
from ui.history import get_history
from utils.config import config
from utils.round import important_round_columns, current_round_columns


def update_current(psp, plh_update):
    with plh_update:
        # current round
        current_epoch = psp.get_current_epoch()

        df_current_round = psp.get_round(current_epoch)
        current_expander = st.expander(f"Current #{current_epoch}", expanded=True)
        with current_expander:
            round_stats = psp.get_round_stats(current_epoch)
            bull_amount = df_current_round["bullAmount"].iloc[0]
            bear_amount = df_current_round["bearAmount"].iloc[0]
            total_amount = round_stats["total_amount"]
            bull_ratio = round_stats["bull_ratio"]
            bear_ratio = round_stats["bear_ratio"]
            bear_pay_ratio = round_stats["bear_pay_ratio"]
            bull_pay_ratio = round_stats["bull_pay_ratio"]

            round_start_time = round_stats["round_start_time"]
            round_bet_time = round_stats["round_bet_time"]
            round_lock_time = round_stats["round_lock_time"]
            round_close_time = round_stats["round_close_time"]

            # st.write(df_current_round[current_round_columns])

            if total_amount > 0:
                col1, col2, col3 = st.columns(3)

                df_history_round = get_history(psp, current_epoch, back_in_time=config["ui"]["back_in_time"])
                df_history_round["pool"] = df_history_round["bearAmount"] + df_history_round["bullAmount"]
                average_pool = df_history_round.mean()["pool"]
                col1.metric(label="BULLISH",
                            value=f"{bull_pay_ratio:.2f}x",
                            delta=f"{bull_amount:.5f} BNB | {bull_ratio:.2f}%",
                            delta_color="normal")
                col2.metric(label="BEARISH",
                            value=f"{bear_pay_ratio:.2f}x",
                            delta=f"{bear_amount:.5f} BNB | {bear_ratio:.2f}%",
                            delta_color="inverse")
                col3.metric(label="POOL SIZE",
                            value=f"{total_amount:.2f} BNB",
                            delta=f"Average {average_pool:.2f} BNB",
                            delta_color="off")

                # col1.write(f"Bullish **x{bull_pay_ratio:.2f}** - {bull_ratio:.2f}%")
                # col2.write(f"Bearish **x{bear_pay_ratio:.2f}** - {bear_ratio:.2f}%")
            else:
                st.warning("No deposit yet. Wait few seconds...")

            st.info(f"Now: {dt.datetime.now()}")

            st.subheader("Time Source")
            datetime_format = "%Y-%m-%d  %H:%M:%S"
            time_df_columns = ["Source", "Start", "Bet", "Lock", "Close"]
            time_data = [[f"Contract",
                          f"{round_start_time.strftime(datetime_format)}",
                          f"{round_bet_time.strftime(datetime_format)}",
                          f"{round_lock_time.strftime(datetime_format)}",
                          f"{round_close_time.strftime(datetime_format)}"],
                         ["Estimated",
                          f"{psp.start_time.strftime(datetime_format)}",
                          f"{psp.bet_time.strftime(datetime_format)}",
                          f"{psp.lock_time.strftime(datetime_format)}",
                          f"{psp.close_time.strftime(datetime_format)}"]
                         ]
            time_df = pd.DataFrame(data=time_data, columns=time_df_columns)
            st.dataframe(time_df)
            st.caption("Please wait for a new round to be started for accurate timing.")


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
            estimated_gain = df_running.sum()["reward"]
            max_spent = df_running.max()["amount"]

            last_win_epoch = df_running[df_running["reward"] > 0].max()["epoch"]
            if last_win_epoch is None or math.isnan(last_win_epoch):
                recent_loss = abs(df_running.sum()["reward"])
                recent_loss_times = df_running[df_running["reward"] < 0].count()["reward"]
            else:
                recent_loss = abs(df_running[df_running["epoch"] > last_win_epoch].sum()["reward"])
                recent_loss_times = df_running[(df_running["epoch"] > last_win_epoch)
                                               & (df_running["reward"] < 0)].count()["reward"]

            st.subheader("Overview")
            summary_df_columns = ["Total Spent", "Max Spent", "Recent Loss", "Total Loss", "Estimated Win",
                                  "Estimated Gain"]
            summary_data = [[f"{total_spent:.5f} BNB / {df_running.shape[0]}",
                             f"{max_spent:.5f} BNB",
                             f"{recent_loss:.5f} BNB / {recent_loss_times}",
                             f"{total_loss:.5f} BNB / {loss_times}",
                             f"{estimated_win:.5f} BNB / {win_times}",
                             f"{estimated_gain:.5f} BNB"]]
            summary_df = pd.DataFrame(data=summary_data, columns=summary_df_columns)
            st.dataframe(summary_df)

            return {"total_spent": total_spent,
                    "max_spent": max_spent,
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
            df_history_round = get_history(psp, current_epoch, back_in_time=config["ui"]["back_in_time"])
            st.write(df_history_round[important_round_columns])
