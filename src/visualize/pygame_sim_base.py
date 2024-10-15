import abc
import time
import pygame
import distinctipy
from typing import Dict, Tuple

WALKABLE_COLOR = (102, 102, 102)  # Light Green
NON_WALKABLE_COLOR = (0, 0, 0)  # Dark Gray
GRID_LINE_COLOR = (51, 51, 51)  # White
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

pygame.font.init()
font = pygame.font.SysFont(None, 24)


# TODO implement proper functioning resize.
class PygameSimulationBase(abc.ABC):
    def __init__(self, grid_map, cell_size=30):
        self.fps = 60
        self.grid_map = grid_map
        self.cell_size = cell_size
        self.window_size_x = grid_map.grid_size_y * cell_size
        self.window_size_y = grid_map.grid_size_x * cell_size
        self.screen = pygame.display.set_mode((self.window_size_x, self.window_size_y), pygame.RESIZABLE)
        pygame.display.set_caption(f"Robot Movement Replay: {grid_map.grid_size_x}x{grid_map.grid_size_y}")
        self.update_cell_size()

        self.resizing = False
        self.last_resize_time = 0
        self.resize_timeout = 0.5

    @abc.abstractmethod
    def get_next_robot_positions(self, step: int):
        pass

    def on_video_resize_started(self):
        self.resizing = True

    def on_video_resize_finished(self):
        self.resizing = False
        self.update_cell_size()
        self.redraw_screen()

    def redraw_screen(self):
        self.get_next_robot_positions(step=0)
        self.draw_robots(self.robot_positions, self.robot_color_map)
        pygame.display.flip()

    def run_simulation(self):
        running = True
        step = 0
        num_steps = self.get_num_steps()

        while running and step < num_steps:
            current_time = time.time()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    if not self.resizing:
                        self.on_video_resize_started()
                    self.window_size_x, self.window_size_y = event.w, event.h
                    self.screen = pygame.display.set_mode(
                        (self.window_size_x, self.window_size_y), pygame.RESIZABLE
                    )
                    self.last_resize_time = current_time

            if self.resizing and (current_time - self.last_resize_time > self.resize_timeout):
                self.on_video_resize_finished()

            if not self.resizing:
                self.get_next_robot_positions(step)
                self.draw_robots(self.robot_positions, self.robot_color_map)
                pygame.display.flip()

            step += 1
            time.sleep(1 / self.fps)

        self.quit_simulation()

    def update_cell_size(self):
        self.cell_size_x = self.window_size_x // self.grid_map.grid_size_y
        self.cell_size_y = self.window_size_y // self.grid_map.grid_size_x

    def draw_grid(self):
        for x in range(self.grid_map.grid_size_x):
            for y in range(self.grid_map.grid_size_y):
                rect = pygame.Rect(y * self.cell_size_x, x * self.cell_size_y, self.cell_size_x, self.cell_size_y)
                if self.grid_map.MAP[x][y] == 0:
                    pygame.draw.rect(self.screen, WALKABLE_COLOR, rect)
                elif self.grid_map.MAP[x][y] == -1:
                    pygame.draw.rect(self.screen, NON_WALKABLE_COLOR, rect)
                pygame.draw.rect(self.screen, GRID_LINE_COLOR, rect, 1)

    def draw_robots(self, robot_positions, robot_color_map: Dict[int, Tuple[int, int, int]]):
        self.screen.fill(BLACK)
        self.draw_grid()

        for robot_id, pos in robot_positions.items():
            robot_x, robot_y = pos
            robot_rect = pygame.Rect(robot_y * self.cell_size_x, robot_x * self.cell_size_y, self.cell_size_x, self.cell_size_y)

            pygame.draw.rect(self.screen, robot_color_map[robot_id], robot_rect)

            text = font.render(str(robot_id), True, WHITE)
            text_rect = text.get_rect(
                center=(robot_y * self.cell_size_x + self.cell_size_x // 2, robot_x * self.cell_size_y + self.cell_size_y // 2))
            self.screen.blit(text, text_rect)

    def generate_robot_color_map(self, num_robots: int):
        distinct_colors = distinctipy.get_colors(num_robots)
        robot_colors = [(int(r * 255), int(g * 255), int(b * 255)) for r, g, b in distinct_colors]
        return {robot_id: color for robot_id, color in zip(range(num_robots), robot_colors)}

    def quit_simulation(self):
        pygame.quit()

    @abc.abstractmethod
    def get_num_steps(self):
        pass
