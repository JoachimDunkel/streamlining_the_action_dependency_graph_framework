import collections
from typing import List, Dict

from pydantic import BaseModel

from src.adg.create_adg import ADGBuilder, NaiveDepCreator, CandidatePartitioningDepCreator, \
    SparseCandidatePartitioningDepCreator, ADGCreationResult
from src.common.action import Action
from src.common.pydantic_util import BaseConfig


class ADGPerformanceComparisonResult(BaseModel):
    naive: ADGCreationResult = ADGCreationResult()
    cp: ADGCreationResult = ADGCreationResult()
    scp: ADGCreationResult = ADGCreationResult()

    def log(self):
        print(f"NaiveDepCreator took {self.naive.elapsed_time} seconds.")
        print(f"CandidatePartitioningDepCreator took {self.cp.elapsed_time} seconds.")
        print(f"SparseCandidatePartitioningDepCreator took {self.scp.elapsed_time} seconds.")


class ADGPerformanceResultAcrossShuttles(BaseConfig):
    results_per_shuttle: Dict[int, List[ADGPerformanceComparisonResult]] = collections.defaultdict(list)


def run_comparison(actions: List[Action], skip_wait_actions: bool = True, skip_exhaustive: bool = False) -> ADGPerformanceComparisonResult:
    comparison_result = ADGPerformanceComparisonResult()

    if not skip_exhaustive:
        adg_1 = ADGBuilder().create_adg(actions, skip_wait_actions=skip_wait_actions).get_adg()
        comparison_result.naive = NaiveDepCreator().create_type2_dependencies(adg_1)

    adg_2 = ADGBuilder().create_adg(actions, skip_wait_actions=skip_wait_actions).get_adg()
    comparison_result.cp = CandidatePartitioningDepCreator().create_type2_dependencies(adg_2)

    adg_3 = ADGBuilder().create_adg(actions, skip_wait_actions=skip_wait_actions).get_adg()
    comparison_result.scp = SparseCandidatePartitioningDepCreator().create_type2_dependencies(adg_3)
    return comparison_result

