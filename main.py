import random
import time
import datetime as dt
from web3 import Web3
from web3.middleware import geth_poa_middleware
import streamlit as st

from utils.budget import simulate_budget
from utils.config import config
from utils.contract import PREDICTION_ABI, PREDICTION_CONTRACT

STRATEGIES = ["Random", "Bullish", "Bearish", "Auto"]


def main():
    st.title("PS Prediction")
    web3_provider = st.sidebar.text_input("Web3 Provider", value="https://bsc-dataseed1.binance.org/")
    ADDRESS = st.sidebar.text_input("Wallet Address", value="")
    PRIVATE_KEY = st.sidebar.text_area("Private Key", value="")
    STRATEGY = st.sidebar.selectbox("Strategy", options=STRATEGIES)
    BASE_BET = st.sidebar.number_input("Base Bet (BNB)",
                                       value=0.01, min_value=0.001, step=0.001)
    FACTOR = st.sidebar.number_input("Multiplication Factor",
                                     value=2.0, min_value=2.0,
                                     step=0.1, max_value=10.0)
    st.sidebar.write(f"You may need {simulate_budget(base_bet=BASE_BET, factor=FACTOR)} BNB")

    # BSC NODE
    w3 = Web3(Web3.HTTPProvider(web3_provider))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    # V2 CONTRACT
    predictionContract = w3.eth.contract(address=PREDICTION_CONTRACT, abi=PREDICTION_ABI)

    def betBull(value, round):
        bull_bet = predictionContract.functions.betBull(round).buildTransaction({
            'from': ADDRESS,
            'nonce': w3.eth.getTransactionCount(ADDRESS),
            'value': value,
            'gas': config["tx"]["gas"],
            'gasPrice': config["tx"]["gas_price"],
        })
        signed_tx = w3.eth.account.signTransaction(bull_bet, private_key=PRIVATE_KEY)
        w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        st.write(f'{w3.eth.waitForTransactionReceipt(signed_tx.hash)}')

    def betBear(value, round):
        bear_bet = predictionContract.functions.betBear(round).buildTransaction({
            'from': ADDRESS,
            'nonce': w3.eth.getTransactionCount(ADDRESS),
            'value': value,
            'gas': config["tx"]["gas"],
            'gasPrice': config["tx"]["gas_price"],
        })
        signed_tx = w3.eth.account.signTransaction(bear_bet, private_key=PRIVATE_KEY)
        w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        st.write(f'{w3.eth.waitForTransactionReceipt(signed_tx.hash)}')

    def claim(epochs):
        claim = predictionContract.functions.claim(epochs).buildTransaction({
            'from': ADDRESS,
            'nonce': w3.eth.getTransactionCount(ADDRESS),
            'value': 0,
            'gas': 800000,
            'gasPrice': 5000000000,
        })
        signed_tx = w3.eth.account.signTransaction(claim, private_key=PRIVATE_KEY)
        w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        st.write(f'{w3.eth.waitForTransactionReceipt(signed_tx.hash)}')

    def fetchClaimable():
        epochs = []
        current = predictionContract.functions.currentEpoch().call()
        epoch = current - 2
        stop = epoch - config["bnb"]["range"]

        while epoch >= stop:
            claimable = predictionContract.functions.claimable(epoch, ADDRESS).call()
            if claimable:
                epochs.append(epoch)
            epoch -= 1
        return epochs

    def handleClaim():
        myBalance = w3.eth.getBalance(ADDRESS)
        myBalance = w3.fromWei(myBalance, 'ether')
        st.write(f'My Balance:  {myBalance:.5f} | Limit {config["bnb"]["limit"]}')
        if myBalance <= config["bnb"]["limit"]:
            st.write(f'Balance Bellow {config["bnb"]["limit"]}, fetching claimable rounds...%')
            epochs = fetchClaimable()
            if len(epochs) > 0:
                st.write(f'Attempting to claim {len(epochs)} rounds...%\n {epochs}')
                claim(epochs)
            else:
                st.write(f'Sorry, no rounds to claim')

    def makeBet(epoch):
        """
        Add your bet logic here
        This example bet random either up or down:
        """
        value = w3.toWei(0.01, 'ether')

        if STRATEGY == "Random":
            rand = random.getrandbits(1)
        elif STRATEGY == "Bullish":
            rand = 1
        elif STRATEGY == "Bearish":
            rand = 0

        if rand:
            st.write(f'Going Bull #{epoch} | {value} BNB')
            betBull(value, epoch)
        else:
            st.write(f'Going Bear #{epoch} | {value} BNB')
            betBear(value, epoch)

    def newRound():
        try:
            current = predictionContract.functions.currentEpoch().call()
            data = predictionContract.functions.rounds(current).call()
            bet_time = dt.datetime.fromtimestamp(data[2]) - dt.timedelta(seconds=config["bet"]["seconds_left"])
            if config["bnb"]["claim"]:
                handleClaim()
            st.write(f'New round: #{current}')
            return [bet_time, current]
        except Exception as e:
            st.write(f'New round fail - {e}')

    if st.button("Run"):
        new_round = newRound()
        n = True
        while n:
            try:
                now = dt.datetime.now()
                if now >= new_round[0]:
                    makeBet(new_round[1])
                    time.sleep(130)
                    new_round = newRound()
            except Exception as e:
                st.write(f'(error) Restarting...% {e}')
                new_round = newRound()


if __name__ == '__main__':
    main()
