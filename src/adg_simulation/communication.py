from typing import List

from pubsub import pub
from abc import ABC, abstractmethod

from src.common.action import Action


class CommunicationRes:
    SHUTTLE_QUEUE_UPDATED_FORMAT = 'shuttle_queue_updated.shuttle.{}'
    ACTION_COMPLETED_FORMAT = 'action_completed.shuttle.{}'


class CommMsgBuilder:

    @staticmethod
    def shuttle_queue_updated_msg(shuttle_id: int) -> str:
        return CommunicationRes.SHUTTLE_QUEUE_UPDATED_FORMAT.format(shuttle_id)

    @staticmethod
    def action_completed_msg(shuttle_id: int) -> str:
        return CommunicationRes.ACTION_COMPLETED_FORMAT.format(shuttle_id)


class CommunicationPubs:
    @staticmethod
    def publish_shuttle_queue_updated(shuttle_id: int):
        pub.sendMessage(CommMsgBuilder.shuttle_queue_updated_msg(shuttle_id))

    @staticmethod
    def publish_action_completed(shuttle_id: int, action: Action):
        pub.sendMessage(CommMsgBuilder.action_completed_msg(shuttle_id), shuttle_id=shuttle_id, action=action)


class CommunicationSubs:
    class IShuttleQueueUpdatedSubscriber(ABC):
        def __init__(self, shuttle_id: int):
            pub.subscribe(self.handle_shuttle_queue_updated, CommMsgBuilder.shuttle_queue_updated_msg(shuttle_id))

        @abstractmethod
        def handle_shuttle_queue_updated(self) -> None:
            pass

    class IActionCompletedSubscriber(ABC):
        def __init__(self, shuttle_ids: List[int]):
            for shuttle_id in shuttle_ids:
                pub.subscribe(self.handle_action_completed, CommMsgBuilder.action_completed_msg(shuttle_id))

        @abstractmethod
        def handle_action_completed(self, shuttle_id: int, action_node_id: int) -> None:
            pass
