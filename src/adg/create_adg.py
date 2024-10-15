import bisect
import copy
from abc import abstractmethod, ABC
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Optional, Tuple, Set

import networkx
from pydantic import BaseModel
from ttictoc import tic, toc

from src.adg.adg import ADG
from src.adg.dependency_creator_cpp_wrapper import DepCreationType, DependencyCreatorCpp, DepCreationResult
from src.common.action import Action
from src.common.resources import PATH_ROOT_DIR


def create_candidate_action_lookup(adg: ADG) -> defaultdict[Tuple[int, int], List[Action]]:
    all_actions = adg.get_all_actions()
    candidate_action_lookup_S: defaultdict[Tuple[int, int], List[Action]] = defaultdict(list)
    for action in all_actions:
        candidate_action_lookup_S[action.start_s].append(action)
    return candidate_action_lookup_S


class ADGCreationResult(BaseModel):
    elapsed_time: float = -1.0
    created_type2_dependencies: int = 0


class Type2DepCreator(ABC):

    def __init__(self):
        self.dep_creator_cpp = DependencyCreatorCpp(PATH_ROOT_DIR)

    @abstractmethod
    def create_type2_dependencies(self, adg: ADG) -> ADGCreationResult:
        pass


class NaiveDepCreator(Type2DepCreator):

    def create_type2_dependencies(self, adg: ADG):
        all_actions = adg.get_all_actions()
        result = self.dep_creator_cpp.get_type2_dependencies(all_actions, DepCreationType.EXHAUSTIVE)
        for dep in result.dependencies:
            adg.add_dependency(dep[0], dep[1])

        creation_result = ADGCreationResult(elapsed_time=result.elapsed_time, created_type2_dependencies=len(result.dependencies))
        return creation_result

class CandidatePartitioningDepCreator(Type2DepCreator):
    def create_type2_dependencies(self, adg: ADG):
        all_actions = adg.get_all_actions()
        result = self.dep_creator_cpp.get_type2_dependencies(all_actions, DepCreationType.CP)
        for dep in result.dependencies:
            adg.add_dependency(dep[0], dep[1])

        creation_result = ADGCreationResult(elapsed_time=result.elapsed_time, created_type2_dependencies=len(result.dependencies))
        return creation_result


class SparseCandidatePartitioningDepCreator(Type2DepCreator):

    @staticmethod
    def find_rel_candidate(candidate_actions: List[Action], for_this_action: Action) -> Optional[Action]:
        idx = bisect.bisect_right(candidate_actions, for_this_action) - 1
        while idx >= 0:
            candidate = candidate_actions[idx]
            assert candidate.time_step_t <= for_this_action.time_step_t
            if candidate.shuttle_R == for_this_action.shuttle_R:
                idx -= 1
                continue

            return candidate
        return None

    def create_type2_dependencies(self, adg: ADG):
        all_actions = adg.get_all_actions()
        result = self.dep_creator_cpp.get_type2_dependencies(all_actions, DepCreationType.SCP)
        for dep in result.dependencies:
            adg.add_dependency(dep[0], dep[1])

        creation_result = ADGCreationResult(elapsed_time=result.elapsed_time, created_type2_dependencies=len(result.dependencies))
        return creation_result


class ADGBuilder:

    def create_adg(self, all_actions: List[Action], skip_wait_actions=False) -> 'ADGBuilder':
        self.adg = ADG()

        actions_per_robot = defaultdict(list)
        all_actions_copied = copy.deepcopy(all_actions)
        for action in all_actions_copied:
            if action.start_s == action.goal_g and skip_wait_actions:
                continue
            actions_per_robot[action.shuttle_R].append(action)

        for actions_per_robot in actions_per_robot.values():
            for i in range(len(actions_per_robot)):
                self.adg.add_action(actions_per_robot[i])
                if i > 0:
                    self.adg.add_dependency(actions_per_robot[i - 1].related_vertex_id,
                                            actions_per_robot[i].related_vertex_id)

        return self

    def get_adg(self) -> ADG:
        return self.adg

    def build(self, all_actions: List[Action], type2_dep_creator: Type2DepCreator = NaiveDepCreator(),
              skip_wait_actions=False) -> ADG:
        self.create_adg(all_actions, skip_wait_actions=skip_wait_actions)
        type2_dep_creator.create_type2_dependencies(self.adg)
        if not networkx.is_directed_acyclic_graph(self.adg.graph):
            raise ValueError("ADG contains a Cycle!")
        return self.get_adg()
