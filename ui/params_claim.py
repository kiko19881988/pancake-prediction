import streamlit as st
from ui.wallet import update_balance

STRATEGIES = ["Random", "Same-Before", "Trend", "Bullish", "Bearish"]
EPOCHS = ["All", "Odd", "Even"]


def create_params_ui(psp):
    wallet_address = st.sidebar.text_input("Wallet Address", value="0x4a6779DaA59d5C0467E48CAE716557099AF842e3")

    if len(wallet_address) > 0:
        psp.set_address(address=wallet_address)
        my_balance = psp.get_balance()

        lbl_account_balance = st.sidebar.empty()
        update_balance(lbl_account_balance, my_balance)

    private_key = st.sidebar.text_area("Private Key", value="")
    if len(private_key) > 0:
        psp.set_private_key(private_key=private_key)

    return {"wallet_address": wallet_address,
            "private_key": private_key}