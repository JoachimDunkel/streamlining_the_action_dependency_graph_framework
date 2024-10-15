import pickle
import numpy as np
from typing import Dict, Tuple, List
from src.common.rect_collision import check_rectangle_collision 
from tqdm import tqdm
from src.common.grid_map import GridMap


class SimulationResultConfig:
    def __init__(self, paths: Dict[int, np.ndarray], fps: int, grid_map: GridMap):
        self.paths = paths
        self.fps = fps
        self.grid_map = grid_map

    def save(self, filepath: str):
        with open(filepath, 'wb') as f:
            pickle.dump({'paths': self.paths,
                         'fps': self.fps,
                         'grid_map': self.grid_map}, f)

    @classmethod
    def load(cls, filepath: str):
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            paths = data['paths']
            fps = data['fps']
            grid_map = data['grid_map']
        return cls(paths, fps, grid_map)

    def check_collisions_in_paths(self, rect_size_x: float = 1.0, rect_size_y: float = 1.0, eps: float = 1e-8) -> List[Tuple[int, int, int]]:
        total_frames = max(len(path) for path in self.paths.values())
        collisions_found = []

        for frame in tqdm(range(total_frames), desc="Checking frames for collisions"):
            robot_positions = {robot_id: path[min(frame, len(path) - 1)] for robot_id, path in self.paths.items()}
            collisions = check_rectangle_collision(robot_positions, rect_size_x, rect_size_y, eps)

            if collisions:
                for (shuttle_id_1, shuttle_id_2) in collisions:
                    collisions_found.append((frame, shuttle_id_1, shuttle_id_2))

        return collisions_found

