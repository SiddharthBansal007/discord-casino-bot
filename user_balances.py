import json
import os

STARTING_COINS = 5000

def save_balances(balances):
    with open('user_balances.json', 'w') as f:
        json.dump(balances, f, indent=4)

def load_balances():
    if os.path.exists('user_balances.json'):
        with open('user_balances.json', 'r') as f:
            return json.load(f)
    return {}

def add_new_user(user_id):
    balances = load_balances()
    balances[user_id] = {
        "balance": STARTING_COINS,
        "total_spent": 0,
        "total_profit": 0,
        "total_loss": 0
    }
    save_balances(balances)
