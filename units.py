"""Unit instances and combat logic."""

import copy
import random
from data import UNIT_BY_ID


class Unit:
    def __init__(self, type_id, side, col, row):
        base = UNIT_BY_ID[type_id]
        self.type_id = type_id
        self.glyph = base["glyph"]
        self.trait = base["trait"]
        self.range = base["range"]
        self.cost = base["cost"]
        self.max_hp = base["hp"]
        self.hp = base["hp"]
        self.atk = base["atk"]
        self.spd = base["spd"]
        self.side = side  # "player" or "enemy"
        self.col = col    # 0-3 within their half
        self.row = row    # 0-3
        self.alive = True
        self.cursed = False      # hexblade debuff
        self.heal_per_turn = 8 if type_id == "cleric" else 0
        self.tick = 0            # accumulates until >= 10/spd threshold

    def name(self):
        return self.type_id.capitalize()

    def effective_atk(self):
        a = self.atk
        if self.cursed:
            a = max(1, a - 10)
        return a

    def hp_bar(self, width=8):
        pct = self.hp / self.max_hp
        filled = round(pct * width)
        bar = "#" * filled + "." * (width - filled)
        return f"[{bar}]"

    def display_glyph(self):
        if not self.alive:
            return "."
        return self.glyph.lower() if self.hp < self.max_hp * 0.35 else self.glyph


def apply_trait_buffs(units):
    """Mutate unit stats based on active traits for their side."""
    for side in ("player", "enemy"):
        side_units = [u for u in units if u.side == side and u.alive]
        trait_counts = {}
        for u in side_units:
            trait_counts[u.trait] = trait_counts.get(u.trait, 0) + 1

        armored_bonus = 0
        if trait_counts.get("armored", 0) >= 4:
            armored_bonus = 12
        elif trait_counts.get("armored", 0) >= 2:
            armored_bonus = 5

        mystic_mult = 1.0
        if trait_counts.get("mystic", 0) >= 3:
            mystic_mult = 1.35
        elif trait_counts.get("mystic", 0) >= 2:
            mystic_mult = 1.15

        swift_double = trait_counts.get("swift", 0) >= 2

        for u in side_units:
            u._armored_reduction = armored_bonus if u.trait == "armored" else 0
            if u.trait == "mystic":
                u.atk = round(UNIT_BY_ID[u.type_id]["atk"] * mystic_mult)
            u._double_attack = swift_double and u.trait == "swift"
            u._commander_bonus = 0

        # commander: buff adjacent units
        commanders = [u for u in side_units if u.trait == "commander"]
        for cmd in commanders:
            for u in side_units:
                if u is not cmd:
                    dist = abs(u.col - cmd.col) + abs(u.row - cmd.row)
                    if dist <= 1:
                        u._commander_bonus = u.__dict__.get("_commander_bonus", 0) + 8


def pick_target(attacker, enemies):
    """Pick closest enemy. Ranged units can target anyone if ranged trait synergy active."""
    alive = [e for e in enemies if e.alive]
    if not alive:
        return None
    # Prefer lowest col (closest frontline) unless out of range
    by_col = sorted(alive, key=lambda e: (e.col, e.row))
    # Check range: col distance counts as primary
    for e in by_col:
        col_dist = abs(attacker.col - e.col) + 4  # +4 because they're on opposite halves
        if col_dist <= attacker.range + 3:  # range 1 = melee, range 3 = full board
            return e
    return by_col[0]  # fallback


def run_battle(player_units, enemy_units, log):
    """
    Simulate one battle to completion.
    Returns ("player"|"enemy"|"draw", surviving_units, log).
    log is a list of strings appended to during simulation.
    """
    all_units = player_units + enemy_units
    apply_trait_buffs(all_units)

    # Initialize commander bonuses into atk
    for u in all_units:
        u.atk += getattr(u, "_commander_bonus", 0)

    ticks = 0
    max_ticks = 500

    while ticks < max_ticks:
        alive_p = [u for u in player_units if u.alive]
        alive_e = [u for u in enemy_units if u.alive]
        if not alive_p or not alive_e:
            break

        # Advance ticks and collect all units ready to act
        ticks += 1
        for u in all_units:
            if u.alive:
                u.tick += u.spd

        actors = sorted([u for u in all_units if u.alive and u.tick >= 10], key=lambda u: -u.tick)

        for actor in actors:
            if not actor.alive:
                continue
            actor.tick -= 10

            enemies = alive_e if actor.side == "player" else alive_p
            allies = alive_p if actor.side == "player" else alive_e

            # Healer: restore HP to lowest ally
            if actor.heal_per_turn > 0:
                wounded = [a for a in allies if a.alive and a.hp < a.max_hp]
                if wounded:
                    target = min(wounded, key=lambda a: a.hp)
                    healed = min(actor.heal_per_turn, target.max_hp - target.hp)
                    target.hp += healed
                    log.append(f"  {actor.name()} heals {target.name()} for {healed}")

            target = pick_target(actor, [u for u in enemies if u.alive])
            if not target:
                continue

            dmg = max(1, actor.effective_atk() - getattr(target, "_armored_reduction", 0))
            dmg += random.randint(-3, 3)
            dmg = max(1, dmg)

            # Hexblade: curse target
            if actor.type_id == "hexblade" and not target.cursed:
                target.cursed = True
                log.append(f"  {actor.name()} curses {target.name()}!")

            target.hp -= dmg
            log.append(f"  {actor.name()} -> {target.name()} for {dmg} dmg (hp:{max(0,target.hp)}/{target.max_hp})")

            if target.hp <= 0:
                target.alive = False
                target.hp = 0
                log.append(f"  *** {target.name()} dies! ***")

            # Double attack for swift synergy
            if getattr(actor, "_double_attack", False):
                target2 = pick_target(actor, [u for u in enemies if u.alive])
                if target2:
                    dmg2 = max(1, actor.effective_atk() - getattr(target2, "_armored_reduction", 0))
                    dmg2 += random.randint(-3, 3)
                    dmg2 = max(1, dmg2)
                    target2.hp -= dmg2
                    log.append(f"  {actor.name()} (swift) -> {target2.name()} for {dmg2} dmg")
                    if target2.hp <= 0:
                        target2.alive = False
                        target2.hp = 0
                        log.append(f"  *** {target2.name()} dies! ***")

        alive_p = [u for u in player_units if u.alive]
        alive_e = [u for u in enemy_units if u.alive]

    alive_p = [u for u in player_units if u.alive]
    alive_e = [u for u in enemy_units if u.alive]

    if alive_p and not alive_e:
        return "player", alive_p
    if alive_e and not alive_p:
        return "enemy", alive_e
    return "draw", []


def make_unit(type_id, side, col, row):
    return Unit(type_id, side, col, row)


def clone_unit(u):
    """Deep copy a unit for battle simulation (preserves placement state)."""
    return copy.deepcopy(u)
