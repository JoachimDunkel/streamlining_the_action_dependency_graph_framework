import itertools
from collections import deque
from typing import List
import networkx as nx
from src.common.action import Action, ActionStatus

_global_node_counter = itertools.count()


class ADG:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_action(self, action: Action) -> int:
        node_id = next(_global_node_counter)
        action.related_vertex_id = node_id
        self.graph.add_node(node_id, action=action)
        return node_id

    def add_dependency(self, action_vertex_id_from: int, action_vertex_id_to: int) -> None:
        if action_vertex_id_from in self.graph and action_vertex_id_to in self.graph:
            self.graph.add_edge(action_vertex_id_from, action_vertex_id_to)
        else:
            raise ValueError("One or both action IDs not found in the graph.")

    def get_action(self, node_id: int) -> Action:
        action = self.graph.nodes[node_id].get('action')
        if not action:
            raise ValueError("Action not found for node ID.")
        return action

    def is_action_equable(self, action: Action) -> bool:
        if action.status != ActionStatus.PENDING:
            return False
        predecessors = self.get_predecessors(action.related_vertex_id)
        predecessors_allow_enqueued_status = True
                        
        for predecessor in predecessors:
            predecessor_action = self.get_action(predecessor)
            if predecessor_action.shuttle_R != action.shuttle_R:
                if predecessor_action.status != ActionStatus.COMPLETED:
                    predecessors_allow_enqueued_status = False
                    break
            else:
                if predecessor_action.status == ActionStatus.PENDING:
                    predecessors_allow_enqueued_status = False
                    break

        return predecessors_allow_enqueued_status

    def enqueue_actions_bfs(self, start_action: Action) -> List[Action]:
        queue = deque([start_action])
        enqueued_actions = []

        while queue:
            current_action = queue.popleft()
            if self.is_action_equable(current_action):
                current_action.move_status_forward()
                enqueued_actions.append(current_action)
                
            if current_action.status != ActionStatus.PENDING:
                successors = self.get_successors(current_action.related_vertex_id)
                for successor_id in successors:
                    successor_action = self.get_action(successor_id)
                    if successor_action.status == ActionStatus.PENDING:
                        queue.append(successor_action)
                    
        return enqueued_actions

    def get_all_actions(self) -> List[Action]:
        return [self.get_action(node_id) for node_id in self.graph.nodes]

    def is_reachable(self, source_id: int, target_id: int) -> bool:
        return nx.has_path(self.graph, source_id, target_id)

    def reverse_graph(self) -> 'ADG':
        reversed_graph = ADG()
        reversed_graph.graph = self.graph.reverse(copy=True)
        return reversed_graph

    def display_graph(self) -> None:
        for node_id in self.graph.nodes:
            action = self.get_action(node_id)
            print(f"Node {node_id}: {action}")
            successors = list(self.graph.successors(node_id))
            for successor in successors:
                print(f"  -> depends on {successor}")

    def traverse_graph(self, start_id: int) -> List[int]:
        if start_id not in self.graph:
            raise ValueError(f"Node with ID {start_id} not found.")
        return list(nx.dfs_preorder_nodes(self.graph, start_id))

    def get_successors(self, node_id: int) -> List[int]:
        if node_id not in self.graph:
            raise ValueError(f"Node with ID {node_id} not found.")
        return list(self.graph.successors(node_id))

    def get_predecessors(self, node_id: int) -> List[int]:
        if node_id not in self.graph:
            raise ValueError(f"Node with ID {node_id} not found.")
        return list(self.graph.predecessors(node_id))

    def get_neighbors(self, node_id: int) -> List[int]:
        if node_id not in self.graph:
            raise ValueError(f"Node with ID {node_id} not found.")
        successors = set(self.graph.successors(node_id))
        predecessors = set(self.graph.predecessors(node_id))
        return list(successors.union(predecessors))

    def is_acyclic(self):
        return nx.is_directed_acyclic_graph(self.graph)

    def transitive_reduction(self) -> 'ADG':
        if not self.is_acyclic():
            raise ValueError("Transitive reduction is only defined for directed acyclic graphs (DAGs).")

        reduced_adg = ADG()

        for node_id, data in self.graph.nodes(data=True):
            reduced_adg.graph.add_node(node_id, **data)

        edges = list(self.graph.edges())
        for u, v in edges:
            self.graph.remove_edge(u, v)  # Temporarily remove the edge
            if not nx.has_path(self.graph, u, v):  # Check if reachability is lost
                reduced_adg.graph.add_edge(u, v)  # Edge is essential, add to reduced graph
            self.graph.add_edge(u, v)  # Re-add the edge

        return reduced_adg

    def has_same_edges(self, other: 'ADG') -> bool:
        # Compare edges without considering node attributes
        this_edges = set(self.graph.edges())
        other_edges = set(other.graph.edges())
        return this_edges == other_edges
