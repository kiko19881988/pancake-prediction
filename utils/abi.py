import requests
import json
from web3 import Web3
from web3.middleware import geth_poa_middleware
import streamlit as st

from utils.config import config


@st.experimental_memo()
def get_abi():
    url_eth = config["general"]["abi_api"]
    # BSC NODE
    w3 = Web3(Web3.HTTPProvider(config["general"]["web3_provider"]))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    contract_address = w3.toChecksumAddress(config["general"]["smart_contract"])
    API_ENDPOINT = url_eth + "?module=contract&action=getabi&address=" + str(contract_address)
    r = requests.get(url=API_ENDPOINT)
    response = r.json()
    contract_abi = json.loads(response["result"])

    return contract_abi
