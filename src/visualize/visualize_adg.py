import itertools
import os
from pathlib import Path

from graphviz import Digraph

from src.adg.adg import ADG

adg_counter = itertools.count()


def visualize_adg(adg: ADG, show_id=False, view=True, file_path: Path = None):
    if not adg.graph.nodes:
        print("Empty graph, cannot generate visualization.")
        return

    dot = Digraph(comment="Action Dependency Graph", format='svg')
    dot.attr(rankdir="LR")

    shuttle_clusters = {}

    vertex_color_map = {}
    edge_colors = [
        "darkred", "darkgreen", "darkblue", "darkorange", "indigo", "deeppink", "gold", "darkcyan", "darkmagenta"
    ]
    color_index = 0
    
    all_actions = [adg.get_action(node_id) for node_id in adg.graph.nodes]
    
    for action in all_actions:
        shuttle_id = action.shuttle_R
        if shuttle_id not in shuttle_clusters:
            cluster = Digraph(name=f'cluster_{shuttle_id}')
            cluster.attr(label=f"Shuttle: {shuttle_id}")
            shuttle_clusters[shuttle_id] = cluster

        # Assign an edge color for each vertex
        if action.related_vertex_id not in vertex_color_map:
            vertex_color_map[action.related_vertex_id] = edge_colors[color_index]
            color_index = (color_index + 1) % len(edge_colors)

        label = f"[{action.start_s} -> {action.goal_g}]\nt:{action.time_step_t}"
        if show_id:
            label += f"\n(id: {str(action.related_vertex_id)})"

        node_color = {"PENDING": "grey", "ENQUEUED": "yellow", "COMPLETED": "green"}.get(action.status.name, "red")
        shuttle_clusters[shuttle_id].node(str(action.related_vertex_id), label, style="filled", color=node_color)

    for cluster in shuttle_clusters.values():
        dot.subgraph(cluster)

    for action in all_actions:
        edge_color = vertex_color_map[action.related_vertex_id] 
        for dep_node_ids in adg.get_successors(action.related_vertex_id):
            dep_action = adg.get_action(dep_node_ids)
            style = "solid"
            color = edge_color
            dot.edge(str(action.related_vertex_id), str(dep_action.related_vertex_id), color=color, style=style, constraint='true')
            
    dot.render(file_path, view=view, cleanup=True)
