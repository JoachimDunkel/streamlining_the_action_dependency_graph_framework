import copy
import multiprocessing
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

import ttictoc
from pydantic import BaseModel, Field

from mapf_benchmark.parse_map_file import parse_map_file
from mapf_benchmark.parse_precomputed_solutions import (
    parse_precomputed_solution_from_file,
)
from mapf_benchmark.prepare_benchmark_scenarios import prepare_benchmark_scenarios
from src.adg.create_adg import SparseCandidatePartitioningDepCreator
from src.adg_simulation.adg_simulation import adg_simulation
from src.common.path_util import append_timestamp_to_filename
from src.common.pydantic_util import BaseConfig
from src.common.resources import PATH_MAPF_BENCHMARK_SIMULATION_RESULTS
from src.config.mapf_solution import MapfSolution


class WaitActionRemovalComparisonResult(BaseModel):
    with_wait: float = -1.0
    without_wait: float = -1.0


class WaitActionRemovalAcrossShuttles(BaseConfig):
    results_per_shuttle: Dict[int, List[WaitActionRemovalComparisonResult]] = Field(
        default_factory=lambda: defaultdict(list)
    )


class WaitActionRemovalAcrossMaps(BaseConfig):
    results_per_map: Dict[
        str, WaitActionRemovalAcrossShuttles
    ] = Field(default_factory=lambda: defaultdict(WaitActionRemovalAcrossShuttles))


def run_comparison(mapf_solution: MapfSolution, log_output=False, check_collision=False, store_shuttle_path_results=False) -> WaitActionRemovalComparisonResult:
    result = WaitActionRemovalComparisonResult()

    result.with_wait = adg_simulation(
        mapf_solution,
        SparseCandidatePartitioningDepCreator(),
        log_output=log_output,
        check_collision=False, # uninteresting with wait actions.
        skip_wait_actions=False,
        store_shuttle_path_results=store_shuttle_path_results
    )
    result.without_wait = adg_simulation(
        copy.deepcopy(mapf_solution),
        SparseCandidatePartitioningDepCreator(),
        log_output=log_output,
        check_collision=check_collision,
        skip_wait_actions=True,
        store_shuttle_path_results=store_shuttle_path_results
    )
    return result

ITERATIONS = 1


def process_solution_file(args):
    solution_file, grid_map, num_robots, scenario_stem = args
    file_name = Path(solution_file).name
    try:
        comp_results = []
        print(f"Processing solution file: {file_name}")
        for _ in range(ITERATIONS):
            shuttle_actions = parse_precomputed_solution_from_file(solution_file)
            mapf_solution = MapfSolution(
                grid_map=copy.deepcopy(grid_map), robot_actions=shuttle_actions
            )
            comp_results.append(run_comparison(mapf_solution))
        return num_robots, scenario_stem, comp_results, solution_file
    except Exception as e:
        print(f"Error in {file_name}: {e}")
        return None, None, None, solution_file


def process_scenario_multiprocess(
        scenario, results_across_maps, out_fp, failed_scenarios
):
    print(f"Running for Map: {scenario.map_file}")
    grid_map = parse_map_file(scenario.map_file)
    scenario_stem = scenario.map_file.stem

    for num_robots, solution_files in scenario.solution_files.items():
        print(
            f"Processing {len(solution_files)} solution files for {num_robots} robots."
        )
        tasks = [
            (solution_file, grid_map, num_robots, scenario_stem)
            for solution_file in solution_files
        ]

        ttictoc.tic()
        pool = multiprocessing.Pool(processes=6)
        all_results = pool.map(process_solution_file, tasks)

        for num_robots_result, scenario_stem_result, comp_results, solution_file in all_results:
            if num_robots_result is not None:
                results_across_maps.results_per_map[
                    scenario_stem_result
                ].results_per_shuttle[num_robots_result].extend(comp_results)
            else:
                failed_scenarios.append(solution_file)

        pool.close()
        pool.join()

        print(" === Results saved. === ")
        results_across_maps.to_file(out_fp)
        print(
            f"Processing of {len(solution_files)} solution files took: {ttictoc.toc()} seconds."
        )

if __name__ == "__main__":
    out_fp = PATH_MAPF_BENCHMARK_SIMULATION_RESULTS / "wait_action_compare.json"
    out_fp = append_timestamp_to_filename(out_fp)

    benchmark_scenarios = prepare_benchmark_scenarios()
    results_across_maps = WaitActionRemovalAcrossMaps()
    failed_scenarios = []

    for scenario in benchmark_scenarios:
        process_scenario_multiprocess(
            scenario, results_across_maps, out_fp, failed_scenarios
        )

    print("Failed scenarios:")
    print(failed_scenarios)
