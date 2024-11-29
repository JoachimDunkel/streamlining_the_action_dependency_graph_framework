import collections
from pathlib import Path
from typing import List, Dict

from pydantic import BaseModel

from src.adg.create_adg import ADGBuilder, NaiveDepCreator, CandidatePartitioningDepCreator, \
    SparseCandidatePartitioningDepCreator, ADGCreationResult
from src.common.action import Action
from src.common.path_util import append_timestamp_to_filename
from src.common.pydantic_util import BaseConfig
from src.visualize.visualize_adg import visualize_adg


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


def run_comparison(actions: List[Action], skip_wait_actions: bool = True,
                   skip_exhaustive: bool = False) -> ADGPerformanceComparisonResult:
    comparison_result = ADGPerformanceComparisonResult()

    adg_scp = ADGBuilder().create_adg(actions, skip_wait_actions=skip_wait_actions).get_adg()
    if not adg_scp.is_acyclic():
        return comparison_result
    comparison_result.scp = SparseCandidatePartitioningDepCreator().create_type2_dependencies(adg_scp)

    adg_cp = ADGBuilder().create_adg(actions, skip_wait_actions=skip_wait_actions).get_adg()
    comparison_result.cp = CandidatePartitioningDepCreator().create_type2_dependencies(adg_cp)
    if not adg_cp.is_acyclic():
        return comparison_result

    if not skip_exhaustive:
        adg_naive = ADGBuilder().create_adg(actions, skip_wait_actions=skip_wait_actions).get_adg()
        comparison_result.naive = NaiveDepCreator().create_type2_dependencies(adg_naive)
        if not adg_naive.is_acyclic():
            return comparison_result

        reduced_graph = adg_naive.transitive_reduction()

        # if not reduced_graph.has_same_edges(adg_scp):
            # f_p = append_timestamp_to_filename(Path("/home/dunkel3/Downloads/compare_scp_redundant/"))
            # visualize_adg(reduced_graph, f_p / "adg_reduced")
            # visualize_adg(adg_scp,  f_p / "adg_scp")
            # print("Reduced graph and SCP graph are not equal.")
        print(f"Comparing ADG results - Naive: {len(adg_naive.graph.edges())}, reduced: {len(reduced_graph.graph.edges)}, SCP edges: {len(adg_scp.graph.edges())}, cp edges: {len(adg_cp.graph.edges())}")

    return comparison_result
