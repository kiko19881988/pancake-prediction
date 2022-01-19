def check_results(psp):
    df_running = psp.get_running_df()
    current_epoch = psp.get_current_epoch()

    unchecked_epochs = df_running[
        (df_running["epoch"] <= current_epoch - 2)
        &
        (df_running["reward"] == 0)
        ]["epoch"].tolist()

    for epoch in unchecked_epochs:
        psp.claimable(epoch)
