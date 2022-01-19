import streamlit as st
import pandas as pd
from ui.params_claim import create_params_ui
import pancake


def main():
    st.title("Claim Rewards")

    psp = pancake.Prediction()

    params_claim = create_params_ui(psp)

    csv_file_uploaded = st.file_uploader("Upload Running CSV File", type=['csv'])
    if csv_file_uploaded is not None:
        df = pd.read_csv(csv_file_uploaded)
        st.write(df)

        total_reward = df[df.reward > 0].sum()["reward"]
        win_epochs = df[df.reward > 0]["epoch"].tolist()
        st.info(f"Total Estimated Reward: **{total_reward:.6f} BNB** in **{len(win_epochs)} rounds**.")

        if st.button("Claim Rewards"):
            if len(params_claim["wallet_address"]) > 0 and len(params_claim["private_key"]) > 0:
                psp.set_address(params_claim["wallet_address"])
                psp.set_private_key(params_claim["private_key"])
                claim_hash = psp.claim(win_epochs)
                st.success(f"Trx Hash: ***{claim_hash}***")
            else:
                st.error("Enter Wallet Address and Private Key")


if __name__ == '__main__':
    main()
