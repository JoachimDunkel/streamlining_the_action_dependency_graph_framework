from collections import deque
from enum import Enum
from typing import Tuple

import simpy

from src.adg_simulation.communication import CommunicationPubs
from src.adg_simulation.communication import CommunicationSubs
from src.common.action import Action
from src.common.math_util import lerp_a_to_b

FPS = 60
EPS = 1e-8
EXECUTION_TIME = 1.0
CONSECUTIVE_MOVE_EXECUTION_TIME = 0.8


class ShuttleState(Enum):
    IDLE = 0
    MOVING = 1


class Shuttle(CommunicationSubs.IShuttleQueueUpdatedSubscriber):

    def __init__(self, env: simpy.Environment, shuttle_id: int,
                 log_output: bool = False, store_path_positions=True):
        self.store_path_positions = store_path_positions
        self.log_output = log_output
        CommunicationSubs.IShuttleQueueUpdatedSubscriber.__init__(self, shuttle_id)
        self.shuttle_id = shuttle_id
        self.path_positions = []
        self.action_queue = deque()
        self.env = env
        self.busy_executing_action = False
        self.prev_state = ShuttleState.IDLE
        self._change_state(ShuttleState.IDLE)
        self.went_idle_at = 0.0
        self.path_positions = []

    def _change_state(self, new_state: ShuttleState):
        self.state = new_state
        if self.state == ShuttleState.IDLE and self.prev_state != ShuttleState.IDLE:
            self.went_idle_at = self.env.now

        if self.log_output:
            print(f"SHUTTLE {self.shuttle_id} changed state: {self.prev_state} to {self.state}")
        self.prev_state = self.state

    def finish_action(self, action: Action):
        assert action.related_vertex_id != -1
        CommunicationPubs.publish_action_completed(self.shuttle_id, action)

    def handle_shuttle_queue_updated(self) -> None:
        if not self.busy_executing_action and self.action_queue:
            self.env.process(self.execute_actions())

    def sync_time_and_path_interpolation(self, duration: float) -> Tuple[int, float]:
        frames_to_wait = duration * FPS
        frames_to_interpolate = int(frames_to_wait)

        if frames_to_interpolate < frames_to_wait:
            frames_to_interpolate += 1

        time_to_yield = (frames_to_interpolate - frames_to_wait) / FPS
        return frames_to_interpolate, time_to_yield

    def assert_time_synced(self, process_time: float):
        interpolated_time_progression = len(self.path_positions) / FPS
        assert abs(process_time - interpolated_time_progression) < EPS

    def execute_actions(self):
        self.busy_executing_action = True
        while self.action_queue:
            action: Action = self.action_queue.popleft()
            action_duration = EXECUTION_TIME

            if len(self.action_queue) > 0:
                next_action: Action = self.action_queue[0]
                if action.is_move_action() and next_action.is_move_action():
                    action_duration = CONSECUTIVE_MOVE_EXECUTION_TIME

            if self.state == ShuttleState.IDLE:
                idle_duration = self.env.now - self.went_idle_at
                if idle_duration >= EPS:
                    frames_to_interpolate, time_diff_to_yield = self.sync_time_and_path_interpolation(idle_duration)
                    wait_positions = lerp_a_to_b(action.start_s, action.start_s, frames_to_interpolate)
                    if time_diff_to_yield > 0:
                        yield self.env.timeout(time_diff_to_yield)

                    if self.store_path_positions:
                        self.path_positions.extend(wait_positions)
                        self.assert_time_synced(self.env.now)

            self._change_state(ShuttleState.MOVING)
            frames_to_interpolate, time_diff_to_yield = self.sync_time_and_path_interpolation(action_duration)
            movement_positions = lerp_a_to_b(action.start_s, action.goal_g, frames_to_interpolate)

            yield self.env.timeout(action_duration + time_diff_to_yield)
            if self.store_path_positions:
                self.path_positions.extend(movement_positions)
                self.assert_time_synced(self.env.now)
            self.finish_action(action)

        self.busy_executing_action = False
        self._change_state(ShuttleState.IDLE)
        if self.log_output:
            print(f"[Shuttle {self.shuttle_id}] - Finished all actions in its queue.")
