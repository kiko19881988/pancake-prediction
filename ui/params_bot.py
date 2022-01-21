import streamlit as st
from ui.wallet import update_balance
from utils.wallet import simulate_budget

STRATEGIES = ["Random", "Same-Before", "Trend", "Bullish", "Bearish"]
EPOCHS = ["All", "Odd", "Even"]


def create_params_ui(psp):
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

    bet_estimated_timing = st.sidebar.checkbox("Bet based on estimated time", value=True)
    selected_strategy = st.sidebar.selectbox("Strategy", options=STRATEGIES)
    bet_epochs = st.sidebar.selectbox("Bet on Epochs", options=EPOCHS, index=1)
    base_bet = st.sidebar.number_input("Base Bet (BNB)",
                                       value=float(min_bet), min_value=float(min_bet), step=0.001,
                                       format="%.5f")
    st.sidebar.caption(f'Min Bet: {min_bet:.5f} BNB')

    factor = st.sidebar.number_input("Multiplication Factor",
                                     value=2.0, min_value=0.0,
                                     step=0.1, max_value=10.0)
    st.sidebar.caption("Set to zero for auto factoring")

    budget_factor = factor
    safe_bet = 0.0
    if factor == 0:
        safe_bet = st.sidebar.number_input("Safe Bet for Auto Factoring",
                                           value=0.2, min_value=0.0, max_value=1.0,
                                           step=0.1)
        st.sidebar.caption("Safe Bet deducts a margin from payout factor for each round, "
                           "and it increases the maximum required fund.")
        budget_factor = 2.5

    st.sidebar.warning(f"You may need "
                       f"**{simulate_budget(base_bet=base_bet, factor=budget_factor)} BNB** "
                       f"in your wallet.")

    with st.sidebar.expander("Stop Criteria", expanded=True):
        max_loss_threshold = st.number_input("Max Loss Threshold",
                                             value=0.0, min_value=0.0, step=0.001,
                                             format="%.5f")
        gain_threshold = st.number_input("Gain Threshold",
                                         value=0.0, min_value=0.0, step=0.001,
                                         format="%.5f")
        spend_threshold = st.number_input("Spend Threshold",
                                          value=0.0, min_value=0.0, step=0.001,
                                          format="%.5f")
        st.caption("Set to zero to ignore the stop criteria.")

    return {"wallet_address": wallet_address,
            "private_key": private_key,
            "bet_estimated_timing": bet_estimated_timing,
            "strategy": selected_strategy,
            "bet_epochs": bet_epochs,
            "base_bet": base_bet,
            "factor": factor,
            "safe_bet": safe_bet,
            "max_loss_threshold": max_loss_threshold,
            "gain_threshold": gain_threshold,
            "spend_threshold": spend_threshold,
            "psp": psp}
