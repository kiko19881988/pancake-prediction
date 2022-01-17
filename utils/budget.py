def simulate_budget(base_bet, factor, max_iter=9):
    budget = base_bet * (factor ** max_iter)
    return budget
