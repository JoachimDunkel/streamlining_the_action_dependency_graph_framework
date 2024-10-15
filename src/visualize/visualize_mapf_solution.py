from src.config.mapf_solution import MapfSolution
from src.visualize.pygame_sim_base import PygameSimulationBase

STEPS_PER_SECOND = 2


class PygameMapfSolutionVisualizer(PygameSimulationBase):
    def __init__(self, mapf_solution: MapfSolution, cell_size=30):
        grid_map = mapf_solution.grid_map
        super().__init__(grid_map, cell_size)
        self.fps = STEPS_PER_SECOND
        self.robot_actions = mapf_solution.robot_actions
        self.robot_positions = {robot_id: actions[0].start_s for robot_id, actions in self.robot_actions.items()}
        self.robot_color_map = self.generate_robot_color_map(len(self.robot_positions))
        self.num_steps = max(len(actions) for actions in self.robot_actions.values())

    def get_next_robot_positions(self, step: int):
        for robot_id, robot_action_list in self.robot_actions.items():
            if step < len(robot_action_list):
                action = robot_action_list[step]
                self.robot_positions[robot_id] = action.goal_g

    def get_num_steps(self):
        return self.num_steps


def run_simulation_from_fp(filepath: str):
    mapf_solution = MapfSolution.from_file(filepath)
    run_simulation(mapf_solution)


def run_simulation(mapf_solution: MapfSolution):
    simulation = PygameMapfSolutionVisualizer(mapf_solution)
    simulation.run_simulation()
