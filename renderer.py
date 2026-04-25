"""ASCII renderer -- print-based, no curses."""

import os
import time
from data import UNIT_BY_ID, UNIT_TYPES, TRAIT_BONUSES
from board import COLS, ROWS

CELL_W = 4   # chars per cell
DIVIDER = "|"

TRAIT_SYMBOLS = {
    "armored": "A", "mystic": "M", "swift": "S",
    "commander": "C", "ranged": "R",
}


def clear():
    os.system("clear")


def hline(width=72):
    return "-" * width


def render_dual_board(player_board, enemy_units_by_rc):
    """
    Render player board (left) and enemy board (right) side by side.
    player_board: Board instance
    enemy_units_by_rc: dict (col, row) -> Unit for enemy side
    """
    lines = []
    col_header = "  " + "".join(f" {c+1}  " for c in range(COLS))
    lines.append(col_header + "   " + col_header)

    for r in range(ROWS):
        player_cells = []
        enemy_cells = []
        for c in range(COLS):
            pu = player_board.grid[r][c]
            player_cells.append(_cell_str(pu))
            eu = enemy_units_by_rc.get((c, r))
            enemy_cells.append(_cell_str(eu))
        row_str = f"{r+1} " + DIVIDER + DIVIDER.join(player_cells) + DIVIDER
        row_str += "  VS  "
        row_str += DIVIDER + DIVIDER.join(enemy_cells) + DIVIDER
        lines.append(row_str)

    return lines


def render_battle_boards(player_units, enemy_units):
    """Render live battle state -- both sides on one board."""
    by_rc_p = {(u.col, u.row): u for u in player_units}
    by_rc_e = {(u.col, u.row): u for u in enemy_units}
    lines = []
    col_header = "  " + "".join(f" {c+1}  " for c in range(COLS))
    lines.append(col_header + "   " + col_header)

    for r in range(ROWS):
        pc, ec = [], []
        for c in range(COLS):
            pc.append(_cell_str(by_rc_p.get((c, r))))
            ec.append(_cell_str(by_rc_e.get((c, r))))
        row_str = f"{r+1} " + DIVIDER + DIVIDER.join(pc) + DIVIDER
        row_str += "  -- "
        row_str += DIVIDER + DIVIDER.join(ec) + DIVIDER
        lines.append(row_str)
    return lines


def _cell_str(unit):
    if unit is None:
        return " .. "
    g = unit.display_glyph()
    hp_pct = unit.hp / unit.max_hp
    if hp_pct > 0.6:
        bar = "+"
    elif hp_pct > 0.3:
        bar = "~"
    else:
        bar = "-"
    return f" {g}{bar} "


def render_shop(shop, board):
    lines = []
    lines.append(hline())
    lines.append(f"  GOLD: {shop.gold}g   |   Board: {board.count()}/6 units   |   [r] reroll ({shop.REROLL_COST if hasattr(shop, 'REROLL_COST') else 2}g)")
    lines.append("")
    lines.append("  SHOP:")
    for i, uid in enumerate(shop.offers):
        u = UNIT_BY_ID[uid]
        traits = _trait_active_str(uid)
        lines.append(f"    [{i+1}] {u['glyph']} {uid:<10} {u['cost']}g  hp:{u['hp']:>3} atk:{u['atk']:>2} spd:{u['spd']}  [{u['trait']}]  {u['desc']}")
    lines.append(hline())
    return lines


def render_bench(board):
    lines = []
    if board.bench:
        lines.append("  BENCH:")
        for i, u in enumerate(board.bench):
            lines.append(f"    bench[{i}] {u.glyph} {u.type_id:<10} hp:{u.hp}/{u.max_hp}  {u.hp_bar()}")
    return lines


def render_trait_summary(board):
    units = board.all_units()
    trait_counts = {}
    for u in units:
        trait_counts[u.trait] = trait_counts.get(u.trait, 0) + 1

    active = []
    for trait, count in trait_counts.items():
        bonuses = TRAIT_BONUSES.get(trait, {})
        achieved = [v for k, v in bonuses.items() if count >= k]
        sym = TRAIT_SYMBOLS.get(trait, "?")
        status = achieved[-1] if achieved else "inactive"
        active.append(f"  {sym} {trait}({count}): {status}")
    return active


def render_unit_list(board):
    lines = ["  YOUR UNITS (on board):"]
    for r in range(ROWS):
        for c in range(COLS):
            u = board.grid[r][c]
            if u:
                lines.append(f"    ({c+1},{r+1}) {u.glyph} {u.type_id:<10} hp:{u.hp}/{u.max_hp}  atk:{u.atk}  spd:{u.spd}  {u.hp_bar()}")
    return lines


def render_combat_log(log, max_lines=12):
    lines = []
    lines.append("  --- Combat Log ---")
    shown = log[-max_lines:] if len(log) > max_lines else log
    for l in shown:
        lines.append("  " + l)
    return lines


def render_header(round_num, player_hp, max_rounds=8):
    bar_w = 20
    filled = round(player_hp / 30 * bar_w)
    hp_bar = "[" + "#" * filled + "." * (bar_w - filled) + "]"
    return [
        hline(),
        f"  AUTOBATTLER  |  Round {round_num}/{max_rounds}  |  HP: {hp_bar} {player_hp}/30",
        hline(),
    ]


def _trait_active_str(uid):
    return ""


def animate_battle(player_units, enemy_units, log, delay=0.07):
    """Step through log lines with periodic board redraws."""
    clear()
    chunk = 4
    for i in range(0, len(log), chunk):
        clear()
        board_lines = render_battle_boards(player_units, enemy_units)
        for l in board_lines:
            print(l)
        print()
        shown = log[max(0, i - 8):i + chunk]
        for l in shown:
            print("  " + l)
        time.sleep(delay)

    # Final state
    clear()
    board_lines = render_battle_boards(player_units, enemy_units)
    for l in board_lines:
        print(l)
    print()
    for l in log[-16:]:
        print("  " + l)
