#!/usr/bin/env python3
"""ASCII Autobattler -- main game loop."""

import sys
import random
from data import ENEMY_BOARDS, UNIT_BY_ID
from units import make_unit, clone_unit, run_battle
from board import Board
from shop import Shop, REROLL_COST, SELL_RETURN
from renderer import (
    clear, hline, render_header, render_dual_board, render_shop,
    render_bench, render_trait_summary, render_unit_list,
    render_combat_log, animate_battle,
)

MAX_ROUNDS = 8
MAX_HP = 30


def get_input(prompt):
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye.")
        sys.exit(0)


def build_enemy_board(round_idx):
    entries = ENEMY_BOARDS[min(round_idx, len(ENEMY_BOARDS) - 1)]
    units = []
    for (uid, col, row) in entries:
        u = make_unit(uid, "enemy", col, row)
        units.append(u)
    return units


def show_placement_screen(board, shop, round_num, player_hp):
    clear()
    for l in render_header(round_num, player_hp):
        print(l)

    enemy_units = build_enemy_board(round_num - 1)
    enemy_by_rc = {(u.col, u.row): u for u in enemy_units}
    board_lines = render_dual_board(board, enemy_by_rc)
    print()
    print("  YOUR BOARD           VS           ENEMY BOARD")
    for l in board_lines:
        print(l)

    print()
    traits = render_trait_summary(board)
    if traits:
        print("  SYNERGIES:")
        for t in traits:
            print(t)

    print()
    for l in render_bench(board):
        print(l)

    print()
    for l in render_shop(shop, board):
        print(l)

    print()
    print("  COMMANDS:")
    print("    [1-4]       Buy unit from shop")
    print("    p <c> <r>   Place bench unit at col,row  (e.g. p 0 1 2)")
    print("    m <c1><r1> <c2><r2>  Move unit  (e.g. m 1 1 2 3)")
    print("    s <c> <r>   Sell board unit  (e.g. s 1 2)")
    print("    sb <i>      Sell bench unit by index")
    print("    r           Reroll shop (2g)")
    print("    go          Start battle")
    print("    q           Quit")
    print()


def shop_phase(board, shop, round_num, player_hp):
    while True:
        show_placement_screen(board, shop, round_num, player_hp)
        cmd = get_input("  > ").lower()

        if cmd == "q":
            print("Goodbye.")
            sys.exit(0)

        elif cmd == "go":
            if board.count() == 0:
                print("  You need at least 1 unit on the board!")
                input("  [enter]")
                continue
            break

        elif cmd == "r":
            ok, msg = shop.reroll(cost=REROLL_COST)
            if not ok:
                input(f"  {msg} [enter]")

        elif cmd.isdigit() and 1 <= int(cmd) <= 4:
            idx = int(cmd) - 1
            if board.is_full() and not board.bench:
                pass  # bench can hold overflow
            uid, msg = shop.buy(idx)
            if uid is None:
                input(f"  {msg} [enter]")
            else:
                u = make_unit(uid, "player", 0, 0)
                board.bench.append(u)
                print(f"  Bought {uid}. Place it with: p <bench_idx> <col> <row>")
                input("  [enter]")

        elif cmd.startswith("p "):
            parts = cmd.split()
            if len(parts) != 4:
                input("  Usage: p <bench_idx> <col> <row>  [enter]")
                continue
            try:
                bi, c, r = int(parts[1]), int(parts[2]) - 1, int(parts[3]) - 1
            except ValueError:
                input("  Bad numbers. [enter]")
                continue
            if bi < 0 or bi >= len(board.bench):
                input(f"  No bench unit at index {bi}. [enter]")
                continue
            u = board.bench[bi]
            ok, msg = board.place(u, c, r)
            if not ok:
                input(f"  {msg} [enter]")

        elif cmd.startswith("m "):
            parts = cmd.split()
            if len(parts) != 5:
                input("  Usage: m <c1> <r1> <c2> <r2>  [enter]")
                continue
            try:
                c1, r1, c2, r2 = int(parts[1])-1, int(parts[2])-1, int(parts[3])-1, int(parts[4])-1
            except ValueError:
                input("  Bad numbers. [enter]")
                continue
            ok, msg = board.move(c1, r1, c2, r2)
            if not ok:
                input(f"  {msg} [enter]")

        elif cmd.startswith("s ") and not cmd.startswith("sb"):
            parts = cmd.split()
            if len(parts) != 3:
                input("  Usage: s <col> <row>  [enter]")
                continue
            try:
                c, r = int(parts[1])-1, int(parts[2])-1
            except ValueError:
                input("  Bad numbers. [enter]")
                continue
            u = board.sell(c, r)
            if u:
                refund = shop.sell(u)
                print(f"  Sold {u.type_id} for {refund}g.")
            else:
                print("  No unit there.")
            input("  [enter]")

        elif cmd.startswith("sb "):
            parts = cmd.split()
            if len(parts) != 2:
                input("  Usage: sb <index>  [enter]")
                continue
            try:
                bi = int(parts[1])
            except ValueError:
                input("  Bad index. [enter]")
                continue
            u = board.sell_bench(bi)
            if u:
                refund = shop.sell(u)
                print(f"  Sold bench {u.type_id} for {refund}g.")
            else:
                print("  No bench unit at that index.")
            input("  [enter]")

        else:
            input("  Unknown command. [enter]")


def battle_phase(board, round_num):
    enemy_units = build_enemy_board(round_num - 1)
    player_units = [clone_unit(u) for u in board.units()]

    log = []
    log.append(f"=== Round {round_num} Battle ===")

    winner, survivors = run_battle(player_units, enemy_units, log)

    animate_battle(player_units, enemy_units, log, delay=0.06)

    print()
    if winner == "player":
        print("  *** YOU WIN THIS ROUND! ***")
        hp_loss = 0
    elif winner == "enemy":
        enemy_alive = len([u for u in enemy_units if u.alive])
        hp_loss = enemy_alive * 3 + 2
        print(f"  *** YOU LOST! -{hp_loss} HP ***")
    else:
        hp_loss = 1
        print("  *** DRAW! -1 HP ***")

    # Carry over hp from surviving player units to board
    for pu in player_units:
        if pu.alive:
            bu = board.grid[pu.row][pu.col]
            if bu:
                bu.hp = pu.hp

    # Remove dead player units from board
    for r in range(4):
        for c in range(4):
            u = board.grid[r][c]
            if u:
                match = next((pu for pu in player_units if pu.col == c and pu.row == r), None)
                if match and not match.alive:
                    board.grid[r][c] = None

    print()
    input("  [enter to continue]")
    return hp_loss, winner


def game_over_screen(round_num, player_hp):
    clear()
    print(hline())
    if player_hp <= 0:
        print("  DEFEAT -- You ran out of HP.")
    else:
        print("  VICTORY -- You survived all 8 rounds!")
    print(f"  You reached round {round_num} with {max(0, player_hp)} HP remaining.")
    print(hline())


def title_screen():
    clear()
    print(hline())
    print()
    print("          A S C I I   A U T O B A T T L E R")
    print()
    print("  Build a team. Place your units. Watch them fight.")
    print("  Survive 8 rounds to win. Lose all HP and it's over.")
    print()
    print("  Tips:")
    print("  - Put tanks (K, G, B) in cols 1-2, damage dealers behind them")
    print("  - Match traits to unlock synergy bonuses")
    print("  - Units carry over HP between rounds -- don't throw them away")
    print()
    print(hline())
    get_input("  Press enter to start...")


def main():
    title_screen()

    board = Board()
    shop = Shop()
    player_hp = MAX_HP

    for round_num in range(1, MAX_ROUNDS + 1):
        # Shop phase
        shop_phase(board, shop, round_num, player_hp)

        # Battle
        hp_loss, winner = battle_phase(board, round_num)
        player_hp -= hp_loss

        if player_hp <= 0:
            game_over_screen(round_num, player_hp)
            return

        # Post-round: restock shop and add gold
        shop.refresh_after_round()

        # Bonus gold for winning streaks could go here

    game_over_screen(MAX_ROUNDS + 1, player_hp)


if __name__ == "__main__":
    main()
