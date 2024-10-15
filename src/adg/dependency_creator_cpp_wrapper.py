import os
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Tuple, List

from ttictoc import tic, toc

from src.common.action import Action


class DepCreationType(Enum):
    EXHAUSTIVE = 1
    CP = 2
    SCP = 3


@dataclass
class DepCreationResult:
    dependencies: List[Tuple[int, int]]
    elapsed_time: float


class DependencyCreatorCpp:
    def __init__(self, project_root: Path):
        build_path = project_root / 'cpp' / 'build'
        if build_path not in sys.path:
            sys.path.append(os.path.abspath(build_path))

        import dependency_creator as dep_creator_cpp
        self.dep_creator_cpp = dep_creator_cpp

    def hello_from_cpp(self) -> str:
        return self.dep_creator_cpp.hello_from_cpp()

    def _create_action(self, start_s: Tuple[int, int], goal_g: Tuple[int, int],
                       time_step_t: int, shuttle_R: int, related_vertex_id: int):
        return self.dep_creator_cpp.Action(start_s, goal_g, time_step_t, shuttle_R, related_vertex_id)

    def _enum_correspondence(self, dep_creation_type: DepCreationType) -> Enum:
        match dep_creation_type:
            case DepCreationType.EXHAUSTIVE:
                return self.dep_creator_cpp.DepCreationMethod.EXHAUSTIVE
            case DepCreationType.CP:
                return self.dep_creator_cpp.DepCreationMethod.CP
            case DepCreationType.SCP:
                return self.dep_creator_cpp.DepCreationMethod.SCP

    def get_type2_dependencies(self, actions: List[Action], dep_creation_type: DepCreationType) -> DepCreationResult:
        cpp_actions = [self._create_action(action.start_s, action.goal_g, action.time_step_t, action.shuttle_R,
                                           action.related_vertex_id) for action in actions]
        creation_method = self._enum_correspondence(dep_creation_type)
        tic()
        deps = self.dep_creator_cpp.create_type2_dependencies(cpp_actions, creation_method)
        elapsed = toc()
        return DepCreationResult(deps, elapsed)
