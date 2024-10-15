from typing import Tuple, Dict, List
from shapely.geometry import box


def check_rectangle_collision(rect_positions: Dict[int, Tuple[float, float]],
                              rect_size_x: float, rect_size_y: float, eps: float = 1e-8) -> List[Tuple[int, int]]:
    collisions = []
    robot_rectangles = {}

    # Create rectangles using shapely's box and shrink them using a negative epsilon
    for robot_id, (robot_x, robot_y) in rect_positions.items():
        rect = box(robot_x, robot_y, robot_x + rect_size_x, robot_y + rect_size_y).buffer(-eps)  # Shrink with -eps
        robot_rectangles[robot_id] = rect

    robot_ids = list(robot_rectangles.keys())
    for i in range(len(robot_ids)):
        for j in range(i + 1, len(robot_ids)):
            rect1 = robot_rectangles[robot_ids[i]]
            rect2 = robot_rectangles[robot_ids[j]]

            if rect1.intersects(rect2):  # Check if rectangles overlap
                collisions.append((robot_ids[i], robot_ids[j]))

    return collisions
