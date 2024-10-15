from collections import defaultdict

from src.common.path_util import get_all_files_in_directory, Path
from typing import List
from src.common.resources import PATH_MAPF_BENCHMARK_SOLUTIONS, PATH_MAPF_BENCHMARK_MAPS


class BenchmarkScenario:
    def __init__(self, map_file: str, solution_files: List[str]):
        self.map_file = map_file
        self.group_solutions_per_agent_count(solution_files)

    def group_solutions_per_agent_count(self, solution_files: List[str]):
        group = defaultdict(list)
        for sol in solution_files:
            agent_count = int(Path(sol).stem.split("-")[-1])
            group[agent_count].append(sol)
        self.solution_files = group


def prepare_benchmark_scenarios():
    map_files = get_all_files_in_directory(PATH_MAPF_BENCHMARK_MAPS, file_extension="map")
    solution_files = get_all_files_in_directory(PATH_MAPF_BENCHMARK_SOLUTIONS, file_extension="json")

    grouped_solutions = defaultdict(list)

    for file in solution_files:
        file_name = file.stem
        prefix = file_name.split("-")[1]

        grouped_solutions[prefix].append(file)

    benchmark_scenarios = []
    for map_file in map_files:
        map_file_name = map_file.stem
        benchmark_scenarios.append(
            BenchmarkScenario(map_file=map_file, solution_files=grouped_solutions[map_file_name.split("-")[0]]))

    return benchmark_scenarios

