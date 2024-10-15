import simpy

from src.adg.create_adg import ADGBuilder, Type2DepCreator
from src.adg_simulation.shuttle import Shuttle, FPS
from src.adg_simulation.shuttle_supervisor import ShuttleSupervisor
from src.common.resources import PATH_DATA_OUT
from src.config.mapf_solution import MapfSolution
from src.config.simulation_result_config import SimulationResultConfig


def adg_simulation(mapf_solution: MapfSolution, dep_creator: Type2DepCreator, log_output=False,
                   check_collision=True, skip_wait_actions=False, store_shuttle_path_results=True) -> float:
    env = simpy.Environment()

    grid_map = mapf_solution.grid_map
    actions = mapf_solution.get_all_actions()
    adg_ = ADGBuilder().build(actions, skip_wait_actions=skip_wait_actions,
                              type2_dep_creator=dep_creator)

    shuttles = []
    for shuttle_id in mapf_solution.robot_actions.keys():
        shuttle = Shuttle(env, shuttle_id=shuttle_id, log_output=log_output,
                          store_path_positions=check_collision or store_shuttle_path_results)
        shuttles.append(shuttle)
    supervisor = ShuttleSupervisor(env, shuttles, adg_, log_output=log_output)

    env.process(supervisor.start_simulation())
    env.run()

    sim_end_time = env.now
    if log_output:
        print("Simulation finished in {:.2f} seconds".format(sim_end_time))

    result = {}
    for shuttle in shuttles:
        result[shuttle.shuttle_id] = shuttle.path_positions

    result_config = SimulationResultConfig(paths=result, fps=FPS, grid_map=grid_map)
    if store_shuttle_path_results:
        result_config.save(PATH_DATA_OUT / "simulation_result.pkl")

    if check_collision:
        collisions = result_config.check_collisions_in_paths()
        if collisions:
            if log_output:
                print(f"!! FAIL: Collisions detected: {collisions}")
            assert not collisions
        else:
            if log_output:
                print("!! SUCCESS: No collisions detected")

    return sim_end_time


def adg_simulation_from_file(f_p: str, dep_creator: Type2DepCreator,
                             use_execution_uncertainty=False, log_output=False,
                             check_collision=True, skip_wait_actions=False) -> float:
    mapf_solution = MapfSolution.from_file(f_p)
    adg_simulation(mapf_solution, dep_creator, use_execution_uncertainty, log_output, check_collision,
                   skip_wait_actions)

