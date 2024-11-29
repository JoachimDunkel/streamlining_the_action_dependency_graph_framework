import collections
import logging
import multiprocessing
from pathlib import Path
from typing import Dict

from ttictoc import tic, toc

from mapf_benchmark.parse_map_file import parse_map_file
from mapf_benchmark.parse_precomputed_solutions import parse_precomputed_solution_from_file
from mapf_benchmark.prepare_benchmark_scenarios import prepare_benchmark_scenarios
from src.common.path_util import append_timestamp_to_filename
from src.common.pydantic_util import BaseConfig
from src.common.resources import PATH_MAPF_BENCHMARK_ADG_RESULTS
from src.config.mapf_solution import MapfSolution
from src.evaluation.evaluate_adg_construction_performance import ADGPerformanceResultAcrossShuttles, run_comparison


class ADGPerformanceResultAcrossMaps(BaseConfig):
    results_per_map: Dict[str, ADGPerformanceResultAcrossShuttles] = collections.defaultdict(ADGPerformanceResultAcrossShuttles)


def process_solution_file(solution_file, grid_map, iterations, skip_wait_actions, skip_exhaustive=False):
    print(f"Processing solution file: {Path(solution_file).stem}")
    shuttle_actions = parse_precomputed_solution_from_file(solution_file)
    mapf_solution = MapfSolution(grid_map=grid_map, robot_actions=shuttle_actions)

    results = []
    for _ in range(iterations):
        result = run_comparison(mapf_solution.get_all_actions(), skip_wait_actions, skip_exhaustive=skip_exhaustive)
        results.append(result)
    return results


def process_scenario_multiprocess(scenario, iterations, skip_wait_actions, performance_result, out_file_path, skip_exhaustive=False):
    print(f"Running for Map: {scenario.map_file}")
    grid_map = parse_map_file(scenario.map_file)

    for num_robots, solution_files in scenario.solution_files.items():
        tic()
        pool = multiprocessing.Pool(processes=12)

        tasks = [(solution_file, grid_map, iterations, skip_wait_actions, skip_exhaustive)
                 for solution_file in solution_files]

        all_results = pool.starmap(process_solution_file, tasks)
        logging.info(f"Finished processing {len(solution_files)} solutions for {num_robots} robots.")

        for result_list in all_results:
            performance_result.results_per_map[scenario.map_file.stem].results_per_shuttle[num_robots].extend(result_list)
        performance_result.to_file(out_file_path)

        pool.close()
        pool.join()

        print(f"The pool took {toc()} seconds.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    ITERATIONS = 1
    SKIP_WAIT_ACTIONS = True
    SKIP_EXHAUSTIVE = False # It just takes too long, aint nobody got time for that

    out_file_path_ = PATH_MAPF_BENCHMARK_ADG_RESULTS / f"iter_{ITERATIONS}_skip_wait_{SKIP_WAIT_ACTIONS}.json"
    out_file_path_ = append_timestamp_to_filename(out_file_path_)

    benchmark_scenarios = prepare_benchmark_scenarios()
    performance_result_ = ADGPerformanceResultAcrossMaps()

    for scenario in benchmark_scenarios:
        process_scenario_multiprocess(scenario, ITERATIONS, SKIP_WAIT_ACTIONS, performance_result_, out_file_path_, skip_exhaustive=SKIP_EXHAUSTIVE)

