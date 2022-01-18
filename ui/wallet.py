def update_balance(plh, my_balance):
    if my_balance is None:
        plh.error(f'Invalid address')
    else:
        plh.info(f'Balance: **{my_balance:.5f} BNB**')
