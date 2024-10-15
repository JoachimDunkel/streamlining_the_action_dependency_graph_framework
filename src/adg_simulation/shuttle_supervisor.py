from collections import defaultdict
from typing import List, Dict

import simpy
from pubsub import pub

from src.adg.adg import ADG
from src.adg_simulation.communication import CommunicationSubs, CommMsgBuilder, CommunicationPubs
from src.adg_simulation.shuttle import Shuttle
from src.common.action import Action, ActionStatus
from src.visualize.visualize_adg import visualize_adg

# This (realistic) delays would add to the contrast even further.
ACTION_COMPLETED_DELAY = 0.0
QUEUE_NEW_ACTION_DELAY = 0.0


class ShuttleSupervisor(CommunicationSubs.IActionCompletedSubscriber):
    def __init__(self, env: simpy.Environment, shuttles: List[Shuttle], adg: ADG, log_output: bool = False):
        self.log_output = log_output
        shuttle_ids = [shuttle.shuttle_id for shuttle in shuttles]
        CommunicationSubs.IActionCompletedSubscriber.__init__(self, shuttle_ids)
        self.env = env
        self.adg = adg
        self.shuttles = {}

        for shuttle in shuttles:
            self.shuttles[shuttle.shuttle_id] = shuttle
            pub.subscribe(self.handle_action_completed, CommMsgBuilder.action_completed_msg(shuttle.shuttle_id))

    def handle_action_completed(self, shuttle_id: int, action: Action):
        self.env.process(self.process_action_completed(shuttle_id, action))
            
    def process_action_completed(self, shuttle_id: int, action: Action):
        if action.status == ActionStatus.COMPLETED:
            raise ValueError(f"Action {action} already completed. DOUBLE - COMPLETE")
        
        if action.status != ActionStatus.ENQUEUED:
            raise ValueError(f"Action {action} is not in ENQUEUED status.")
        action.move_status_forward()
        assert action.status == ActionStatus.COMPLETED
        yield self.env.timeout(ACTION_COMPLETED_DELAY)
        if self.log_output:
            print(f"Shuttle {shuttle_id} completed action [{action.start_s}, {action.goal_g}] at t= {self.env.now}")
        
        enqueued_actions = self.adg.enqueue_actions_bfs(action)
        shuttle_action_map: Dict[int, Action] = defaultdict(list)
        for a in enqueued_actions:
            shuttle_action_map[a.shuttle_R].append(a)

        yield from self.notify_shuttles_for_queue_update(shuttle_action_map)

    def notify_shuttles_for_queue_update(self, shuttle_actions_map: Dict[int, Action]):
        for shuttle_id, actions in shuttle_actions_map.items():
            actions.sort()
            shuttle = self.shuttles[shuttle_id]
            shuttle.action_queue.extend(actions)
            yield self.env.timeout(QUEUE_NEW_ACTION_DELAY)
            CommunicationPubs.publish_shuttle_queue_updated(shuttle_id)

    def start_simulation(self):
        first_actions_for_shuttles = {}
        for action in self.adg.get_all_actions():
            if first_actions_for_shuttles.get(action.shuttle_R) is None:
                first_actions_for_shuttles[action.shuttle_R] = action
                continue

            curr_action_for_shuttle = first_actions_for_shuttles[action.shuttle_R]
            assert curr_action_for_shuttle.time_step_t != action.time_step_t
            if curr_action_for_shuttle.time_step_t > action.time_step_t:
                first_actions_for_shuttles[action.shuttle_R] = action
        
        enqueued_actions_per_shuttle: Dict[int, Action] = defaultdict(list)
        for shuttle_id, action in first_actions_for_shuttles.items():
            enqueued_actions = self.adg.enqueue_actions_bfs(action)
            for e in enqueued_actions:
                enqueued_actions_per_shuttle[e.shuttle_R].append(e)

        yield from self.notify_shuttles_for_queue_update(enqueued_actions_per_shuttle)
