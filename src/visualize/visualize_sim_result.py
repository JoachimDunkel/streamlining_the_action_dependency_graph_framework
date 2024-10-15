import time
import pygame

from src.common.rect_collision import check_rectangle_collision
from src.common.resources import PATH_DATA_OUT
from src.config.simulation_result_config import SimulationResultConfig
from src.visualize.pygame_sim_base import PygameSimulationBase


# If you may want to visually check if following the ADG actually works.
class PygameAdgSimulationResultVisualizer(PygameSimulationBase):
    def __init__(self, config: SimulationResultConfig, cell_size=30, fail_at_collision=False):
        grid_map = config.grid_map
        super().__init__(grid_map, cell_size)
        self.interpolated_paths = config.paths
        self.fps = config.fps
        self.fail_at_collision = fail_at_collision
        self.robot_positions = {robot_id: path[0] for robot_id, path in self.interpolated_paths.items()}
        self.robot_color_map = self.generate_robot_color_map(len(self.interpolated_paths))
        self.total_frames = max(len(path) for path in self.interpolated_paths.values())
        self.start_time = time.time()

    def get_next_robot_positions(self, step: int):
        elapsed_time = time.time() - self.start_time
        current_frame = int(elapsed_time * self.fps)

        if current_frame >= self.total_frames:
            raise StopIteration("Simulation Complete")

        self.robot_positions = {
            robot_id: path[min(current_frame, len(path) - 1)]
            for robot_id, path in self.interpolated_paths.items()
        }

        collision_eps = 1e-8
        collisions = check_rectangle_collision(self.robot_positions, rect_size_x=1.0, rect_size_y=1.0,
                                               eps=collision_eps)
        if collisions:
            if self.fail_at_collision:
                screenshot_path = PATH_DATA_OUT / f"collision_screenshot_t{elapsed_time:.2f}.png"
                self.take_screenshot(screenshot_path)
                raise StopIteration("Collision Detected, Simulation Aborted")
            else:
                print(f"Collisions detected at t= {elapsed_time:.2f}: {collisions}")

    def get_num_steps(self):
        return self.total_frames

    def take_screenshot(self, filename="collision_screenshot.png"):
        pygame.image.save(self.screen, filename)
        print(f"Screenshot saved as {filename}")


def run_simulation_from_interpolated_paths(filepath: str, fail_at_collision=False):
    config = SimulationResultConfig.load(filepath)
    simulation = PygameAdgSimulationResultVisualizer(config, fail_at_collision=fail_at_collision)
    simulation.run_simulation()
