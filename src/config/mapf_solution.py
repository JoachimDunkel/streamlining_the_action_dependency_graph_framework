from typing import Dict, List

from src.common.action import Action
from src.common.pydantic_util import BaseConfig
from src.common.grid_map import GridMap


class MapfSolution(BaseConfig):
    grid_map: GridMap
    robot_actions: Dict[int, List[Action]]

    class Config:
        arbitrary_types_allowed = True
        
    def get_all_actions(self) -> List[Action]:
        return [act for actions in self.robot_actions.values() for act in actions]
