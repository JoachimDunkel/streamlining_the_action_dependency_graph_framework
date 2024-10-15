import json
from collections import defaultdict
from typing import List, Dict

from src.common.action import Action


def parse_precomputed_solution_from_file(solution_file: str) -> Dict[int, List[Action]]:
    with open(solution_file) as json_file:
        data = json.load(json_file)
    return parse_precomputed_solution(data)


def parse_precomputed_solution(stored_actions: dict) -> Dict[int, List[Action]]:
    shuttle_actions = defaultdict(list)
    for shuttle_id, moves in stored_actions.items():
        prev_pos = None
        for time_step, goal_g in enumerate(moves):
            if prev_pos is None:
                start_s = goal_g
            else:
                start_s = prev_pos
            action = Action(start_s=start_s, goal_g=goal_g, time_step_t=time_step, shuttle_R=int(shuttle_id))
            shuttle_actions[shuttle_id].append(action)

            prev_pos = goal_g
    return shuttle_actions
