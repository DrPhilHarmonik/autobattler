"""Board state: placement grid and active unit management."""

COLS = 4
ROWS = 4
MAX_UNITS = 6


class Board:
    def __init__(self):
        # grid[row][col] = Unit or None
        self.grid = [[None] * COLS for _ in range(ROWS)]
        self.bench = []  # units bought but not placed

    def units(self):
        return [self.grid[r][c] for r in range(ROWS) for c in range(COLS) if self.grid[r][c]]

    def count(self):
        return len(self.units())

    def place(self, unit, col, row):
        if self.grid[row][col] is not None:
            return False, "That cell is occupied."
        if col < 0 or col >= COLS or row < 0 or row >= ROWS:
            return False, "Out of bounds."
        if unit in self.bench:
            self.bench.remove(unit)
        unit.col = col
        unit.row = row
        self.grid[row][col] = unit
        return True, ""

    def remove(self, col, row):
        unit = self.grid[row][col]
        if unit:
            self.grid[row][col] = None
            self.bench.append(unit)
        return unit

    def move(self, from_col, from_row, to_col, to_row):
        unit = self.grid[from_row][from_col]
        if not unit:
            return False, "No unit there."
        if self.grid[to_row][to_col]:
            # Swap
            other = self.grid[to_row][to_col]
            self.grid[from_row][from_col] = other
            self.grid[to_row][to_col] = unit
            other.col, other.row = from_col, from_row
            unit.col, unit.row = to_col, to_row
        else:
            self.grid[to_row][to_col] = unit
            self.grid[from_row][from_col] = None
            unit.col, unit.row = to_col, to_row
        return True, ""

    def sell(self, col, row):
        unit = self.grid[row][col]
        if unit:
            self.grid[row][col] = None
            return unit
        # check bench
        return None

    def sell_bench(self, idx):
        if 0 <= idx < len(self.bench):
            return self.bench.pop(idx)
        return None

    def is_full(self):
        return self.count() >= MAX_UNITS

    def all_units(self):
        return self.units() + self.bench
