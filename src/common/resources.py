import os
from pathlib import Path


def _path_to_project_root(project_name):
    path = os.getcwd()
    while not str(path).endswith(project_name):
        path = Path(path).parent

    return Path(path)

PATH_ROOT_NAME = "streamlining_the_action_dependency_graph_framework"
PATH_ROOT_DIR = _path_to_project_root(PATH_ROOT_NAME)


PATH_DATA = PATH_ROOT_DIR / "data"
PATH_RAND_MAPF_SOLUTIONS = PATH_DATA / "random_mapf_solutions"
PATH_MANUAL_MAPF_CASES = PATH_DATA / "manual_cases"
PATH_EVALUATE_CONSTRUCTION = PATH_DATA / "evaluate_construction_performance"
PATH_EVALUATION_RESULTS = PATH_DATA / "evaluation_results"
PATH_MAPF_BENCHMARK = PATH_ROOT_DIR / "mapf_benchmark"
PATH_MAPF_BENCHMARK_MAPS = PATH_MAPF_BENCHMARK / "maps"
PATH_MAPF_BENCHMARK_MAPS_PICS = PATH_MAPF_BENCHMARK_MAPS / "map_pics"

PATH_MAPF_BENCHMARK_SOLUTIONS = PATH_MAPF_BENCHMARK / "precomputed_solutions"

PATH_MAPF_BENCHMARK_ADG_RESULTS = PATH_MAPF_BENCHMARK / "adg_results"
PATH_MAPF_BENCHMARK_SIMULATION_RESULTS = PATH_MAPF_BENCHMARK / "simulation_results"
PATH_MAPF_BENCHMARK_PRECOMPUTED_SOLUTIONS = PATH_MAPF_BENCHMARK / "precomputed_solutions"

PATH_DATA_OUT = PATH_DATA / "out"


PATH_TESTS = PATH_ROOT_DIR / "tests"
PATH_TESTS_MAPS = PATH_TESTS / "maps"
PATH_TESTS_TEMP = PATH_TESTS / "temp"