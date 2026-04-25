"""Shop and economy."""

import random
from data import UNIT_TYPES


STARTING_GOLD = 6
GOLD_PER_ROUND = 4
REROLL_COST = 2
SELL_RETURN = 1  # gold back when selling a unit
SHOP_SIZE = 4


def make_pool():
    """Weighted pool: cheaper units appear more often."""
    pool = []
    for u in UNIT_TYPES:
        weight = max(1, 6 - u["cost"])
        pool.extend([u["id"]] * (weight * 3))
    return pool


class Shop:
    def __init__(self):
        self.gold = STARTING_GOLD
        self.pool = make_pool()
        self.offers = []
        self.reroll()

    def reroll(self, cost=0):
        if self.gold < cost:
            return False, "Not enough gold."
        self.gold -= cost
        random.shuffle(self.pool)
        self.offers = [self.pool[i] for i in range(min(SHOP_SIZE, len(self.pool)))]
        return True, ""

    def buy(self, idx):
        if idx < 0 or idx >= len(self.offers):
            return None, "Invalid selection."
        unit_id = self.offers[idx]
        from data import UNIT_BY_ID
        cost = UNIT_BY_ID[unit_id]["cost"]
        if self.gold < cost:
            return None, f"Need {cost}g (have {self.gold}g)."
        self.gold -= cost
        self.offers.pop(idx)
        return unit_id, ""

    def sell(self, unit):
        self.gold += SELL_RETURN
        return SELL_RETURN

    def add_round_gold(self):
        self.gold += GOLD_PER_ROUND

    def refresh_after_round(self):
        self.add_round_gold()
        self.reroll()
