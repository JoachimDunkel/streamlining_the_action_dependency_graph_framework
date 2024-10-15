import numpy as np
from pydantic import BaseModel, Field

CELL_FREE_VALUE = 0
CELL_UNPASSABLE_VALUE = -1


class GridMap(BaseModel):
    grid_size_x: int
    grid_size_y: int
    MAP: list = Field(default_factory=list)

    def __init__(self, **data):
        super().__init__(**data)
        if 'MAP' not in data:
            self.MAP = np.zeros((self.grid_size_x, self.grid_size_y), dtype=int).tolist()
        else:
            self.MAP = np.array(data['MAP']).tolist()

    def update_pos(self, x: int, y: int, value: int):
        assert not self.cell_contains_obstacle((x, y))
        self.MAP[x][y] = value

    def get_num_unpassable_cells(self):
        num_unpassable = 0
        for x in range(self.grid_size_x):
            for y in range(self.grid_size_y):
                if self.cell_contains_obstacle((x, y)):
                    num_unpassable += 1
        return num_unpassable

    def pretty_print(self):
        # Print column headers
        column_headers = "    " + " ".join(f"{i:02}" for i in range(self.grid_size_y))
        print(column_headers)
        print("   " + "-" * (self.grid_size_y * 3))  # Separator line

        for idx, row in enumerate(self.MAP):
            row_index = f"{idx:02} | "  # Format row index with leading zeros and separator
            row_content = "  ".join(str(cell) for cell in row)
            print(row_index + row_content)

    def is_cell_occupied(self, position):
        x, y = position
        return self.MAP[x][y] != CELL_FREE_VALUE

    def cell_contains_obstacle(self, position):
        x, y = position
        return self.MAP[x][y] == CELL_UNPASSABLE_VALUE

    def any_cell_occupied(self, positions):
        for pos in positions:
            if self.is_cell_occupied(pos):
                return True
        return False

    def get_n_free_random_cells(self, n):
        free_cells = np.argwhere(np.array(self.MAP) == CELL_FREE_VALUE)
        random_free_cells = free_cells[np.random.choice(len(free_cells), n, replace=False)]
        assert not self.any_cell_occupied(random_free_cells)
        return random_free_cells

    class Config:
        arbitrary_types_allowed = True
