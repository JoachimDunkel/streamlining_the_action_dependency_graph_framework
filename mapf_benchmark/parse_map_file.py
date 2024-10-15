from src.common.grid_map import GridMap, CELL_FREE_VALUE, CELL_UNPASSABLE_VALUE


def parse_map_file(filepath: str) -> GridMap:

    terrain_mapping = {
        '.': CELL_FREE_VALUE,                        # Passable terrain
        'G': CELL_FREE_VALUE,                        # Passable terrain
        '@': CELL_UNPASSABLE_VALUE,                  # Out of bounds (impassable)
        'O': CELL_UNPASSABLE_VALUE,                  # Out of bounds (impassable)
        'T': CELL_UNPASSABLE_VALUE,                  # Trees (unpassable)
        'S': CELL_FREE_VALUE,                        # Swamp (passable, but marked differently if needed)
        'W': CELL_UNPASSABLE_VALUE                   # Water (impassable from terrain)
    }

    with open(filepath, 'r') as f:
        lines = f.readlines()

    # Parse header
    assert lines[0].strip() == "type octile", "Invalid map file format"
    height = int(lines[1].split()[1])
    width = int(lines[2].split()[1])

    grid_map = GridMap(grid_size_x=height, grid_size_y=width)

    for y, line in enumerate(lines[4:]): 
        for x, char in enumerate(line.strip()):
            if char not in terrain_mapping:
                raise ValueError(f"Unknown terrain type: {char} in map file")
            mapped_char = terrain_mapping[char]
            grid_map.update_pos(y, x, mapped_char)
    return grid_map
