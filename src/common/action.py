import json
from pydantic import BaseModel
from enum import Enum
from typing import List, Tuple, Dict


class ActionStatus(str, Enum):
    PENDING = "PENDING"
    ENQUEUED = "ENQUEUED"
    COMPLETED = "COMPLETED"


class Action(BaseModel):
    start_s: Tuple[int, int]
    goal_g: Tuple[int, int]
    time_step_t: int
    shuttle_R: int
    status: ActionStatus = ActionStatus.PENDING
    related_vertex_id: int = -1
    
    @staticmethod
    def new_action(start_s: Tuple[int, int], goal_g: Tuple[int, int], time_step_t: int, shuttle_R: int, status: ActionStatus = ActionStatus.PENDING):
        return Action(start_s=start_s, goal_g=goal_g, time_step_t=time_step_t, shuttle_R=shuttle_R, status=status)
    
    def move_status_forward(self):
        if self.status == ActionStatus.PENDING:
            self.status = ActionStatus.ENQUEUED
        elif self.status == ActionStatus.ENQUEUED:
            self.status = ActionStatus.COMPLETED
        else:
            raise ValueError(f"Action {self} already completed.")

    def __repr__(self):
        return f"Action({self.start_s}, {self.goal_g}, {self.time_step_t}, {self.shuttle_R}, {self.status})"

    def __lt__(self, other):
        if isinstance(other, Action):
            return self.time_step_t < other.time_step_t
        return NotImplemented

    def is_move_action(self):
        return self.start_s != self.goal_g


def load_actions_from_file_raw(filepath: str) -> dict:
    with open(filepath, 'r') as f:
        robot_actions = json.load(f)

    return robot_actions


def parse_actions_from_manual_dict(stored_actions: dict) -> List[Action]:
    shuttle_actions = []
    for shuttle_id, moves in stored_actions.items():
        for time_step, (start_s, goal_g) in enumerate(moves):
            action = Action(start_s=start_s, goal_g=goal_g, time_step_t=time_step, shuttle_R=int(shuttle_id))
            shuttle_actions.append(action)
    return shuttle_actions


