"""Spectator mode -- watch the autobattler fight itself.

Builds two random rosters on equal gold budgets, runs the battle engine to
completion, and prints the opening lineup, the combat log, and the outcome.
No interactivity: great for a quick demo or for sanity-checking balance.

    python3 sim.py                 # one battle, static render
    python3 sim.py --battles 20    # run 20 battles, print a win tally
    python3 sim.py --watch         # animated blow-by-blow (uses game renderer)
    python3 sim.py --seed 7        # reproducible matchup
"""

import argparse
import random

import renderer
from data import UNIT_TYPES
from units import make_unit, run_battle

COLS, ROWS = 4, 4
MAX_UNITS = 6


def random_roster(side, budget):
    """Place random units on distinct cells until the gold budget is spent."""
    cells = [(c, r) for r in range(ROWS) for c in range(COLS)]
    random.shuffle(cells)
    units, spent = [], 0
    for (c, r) in cells:
        affordable = [u for u in UNIT_TYPES if u["cost"] <= budget - spent]
        if not affordable or len(units) >= MAX_UNITS:
            break
        pick = random.choice(affordable)
        units.append(make_unit(pick["id"], side, c, r))
        spent += pick["cost"]
    return units


def roster_line(units):
    counts = {}
    for u in units:
        counts[u.type_id] = counts.get(u.type_id, 0) + 1
    return ", ".join(f"{n}x {t}" if n > 1 else t for t, n in counts.items())


def one_battle(budget, watch=False):
    player = random_roster("player", budget)
    enemy = random_roster("enemy", budget)
    log = []
    winner, _survivors = run_battle(player, enemy, log)

    if watch:
        renderer.animate_battle(player, enemy, log, delay=0.05)
    return winner, player, enemy, log


def show_battle(budget, watch):
    winner, player, enemy, log = one_battle(budget, watch=watch)

    if not watch:
        print(renderer.hline())
        print(f"  SPECTATOR BATTLE  (budget {budget}g each)")
        print(renderer.hline())
        print(f"  LEFT : {roster_line(player)}")
        print(f"  RIGHT: {roster_line(enemy)}")
        print()
        for line in renderer.render_battle_boards(player, enemy):
            print(line)
        print()
        for line in renderer.render_combat_log(log, max_lines=16):
            print(line)
        print()

    banner = {"player": "*** LEFT WINS ***",
              "enemy": "*** RIGHT WINS ***"}.get(winner, "*** DRAW ***")
    p_alive = sum(u.alive for u in player)
    e_alive = sum(u.alive for u in enemy)
    print(f"  {banner}   (survivors -- left {p_alive}, right {e_alive})")
    return winner


def run_tally(budget, battles):
    tally = {"player": 0, "enemy": 0, "draw": 0}
    for _ in range(battles):
        winner, *_ = one_battle(budget)
        tally[winner] += 1
    print(renderer.hline())
    print(f"  {battles} battles at {budget}g each:")
    print(f"    left wins : {tally['player']}")
    print(f"    right wins: {tally['enemy']}")
    print(f"    draws     : {tally['draw']}")
    print(renderer.hline())


def main():
    ap = argparse.ArgumentParser(description="Watch the autobattler fight itself.")
    ap.add_argument("--budget", type=int, default=12, help="gold budget per side (default 12)")
    ap.add_argument("--battles", type=int, default=1, help="number of battles to run")
    ap.add_argument("--watch", action="store_true", help="animated blow-by-blow")
    ap.add_argument("--seed", type=int, default=None, help="RNG seed for reproducibility")
    args = ap.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    if args.battles > 1:
        run_tally(args.budget, args.battles)
    else:
        show_battle(args.budget, args.watch)


if __name__ == "__main__":
    main()
