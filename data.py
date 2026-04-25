"""Unit type definitions and enemy board presets."""

# name, glyph, hp, atk, spd, range, trait
UNIT_TYPES = [
    {"id": "knight",   "glyph": "K", "hp": 80, "atk": 18, "spd": 3, "range": 1, "trait": "armored",  "cost": 2, "desc": "Tanky frontliner"},
    {"id": "archer",   "glyph": "A", "hp": 45, "atk": 22, "spd": 5, "range": 3, "trait": "ranged",   "cost": 2, "desc": "Fast, long range"},
    {"id": "mage",     "glyph": "M", "hp": 35, "atk": 30, "spd": 4, "range": 2, "trait": "mystic",   "cost": 3, "desc": "High damage, fragile"},
    {"id": "brute",    "glyph": "B", "hp": 110,"atk": 25, "spd": 2, "range": 1, "trait": "armored",  "cost": 3, "desc": "Massive HP, slow"},
    {"id": "rogue",    "glyph": "R", "hp": 40, "atk": 28, "spd": 7, "range": 1, "trait": "swift",    "cost": 3, "desc": "Very fast, melee"},
    {"id": "cleric",   "glyph": "C", "hp": 50, "atk": 12, "spd": 3, "range": 2, "trait": "mystic",   "cost": 3, "desc": "Heals allies each turn"},
    {"id": "golem",    "glyph": "G", "hp": 150,"atk": 20, "spd": 1, "range": 1, "trait": "armored",  "cost": 4, "desc": "Immense tank"},
    {"id": "hexblade", "glyph": "H", "hp": 55, "atk": 35, "spd": 4, "range": 2, "trait": "mystic",   "cost": 4, "desc": "Curses target, -atk"},
    {"id": "scout",    "glyph": "S", "hp": 38, "atk": 20, "spd": 8, "range": 2, "trait": "swift",    "cost": 2, "desc": "Fastest unit"},
    {"id": "warlord",  "glyph": "W", "hp": 70, "atk": 32, "spd": 4, "range": 1, "trait": "commander","cost": 5, "desc": "Buffs adjacent allies"},
]

UNIT_BY_ID = {u["id"]: u for u in UNIT_TYPES}

# Traits: when 2+ of same trait on your board, bonus applies
TRAIT_BONUSES = {
    "armored":   {2: "All armored units take -5 damage per hit",   4: "All armored units take -12 damage per hit"},
    "mystic":    {2: "+15% atk for all mystic units",              3: "+35% atk for all mystic units"},
    "swift":     {2: "Swift units attack twice on their turn",     },
    "commander": {1: "Adjacent allies gain +8 atk",               },
    "ranged":    {2: "Ranged units ignore frontline targeting",    },
}

# Pre-generated enemy boards per round [list of (unit_id, col, row)]
# Board is 4 cols x 4 rows. Enemies occupy right side (cols 4-7 in full grid).
# Here we store relative positions (col 0-3, row 0-3).
ENEMY_BOARDS = [
    # Round 1 - 2 units
    [("knight", 0, 1), ("archer", 3, 2)],
    # Round 2 - 3 units
    [("knight", 0, 0), ("knight", 0, 3), ("archer", 3, 1)],
    # Round 3 - 3 units
    [("brute", 0, 1), ("archer", 3, 0), ("mage", 2, 2)],
    # Round 4 - 4 units
    [("brute", 0, 1), ("knight", 0, 3), ("archer", 3, 2), ("mage", 2, 0)],
    # Round 5 - 4 units
    [("golem", 0, 2), ("rogue", 1, 0), ("rogue", 1, 3), ("archer", 3, 1)],
    # Round 6 - 5 units
    [("golem", 0, 1), ("brute", 0, 3), ("hexblade", 2, 0), ("archer", 3, 2), ("rogue", 1, 2)],
    # Round 7 - 5 units
    [("warlord", 1, 1), ("knight", 0, 0), ("knight", 0, 3), ("mage", 2, 2), ("archer", 3, 1)],
    # Round 8 - 6 units (boss)
    [("warlord", 1, 2), ("golem", 0, 0), ("golem", 0, 3), ("hexblade", 2, 1), ("mage", 2, 3), ("archer", 3, 2)],
]
