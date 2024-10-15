import math
import os

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from src.common.resources import PATH_MAPF_BENCHMARK_SIMULATION_RESULTS

from src.evaluation.eval_wait_action_removal_on_execution import WaitActionRemovalAcrossMaps
from src.common.plotting_common import get_short_map_name, AXIS_LABELS_FONT_SIZE, TITLE_FONT_SIZE, LEGEND_FONT_SIZE, \
    FONT_WEIGHT, X_AXIS_LABEL, USE_GRID_LINES, AXIS_NUMBER_FONT_SIZE, AXIS_LABEL_PAD

BOX_PLOT_WIDTH = 0.6
WITH_COLOR = 'lightblue'
WITHOUT_COLOR = 'lightgreen'


def plot_wait_action_removal_comparison(results_across_maps: WaitActionRemovalAcrossMaps):
    map_names = list(results_across_maps.results_per_map.keys())
    num_maps = len(map_names)

    grid_size = math.ceil(math.sqrt(num_maps))
    fig, axes = plt.subplots(grid_size, grid_size, figsize=(15, 15))
    axes = axes.flatten()

    for idx, map_name in enumerate(map_names):
        ax = axes[idx]
        data_per_shuttle = results_across_maps.results_per_map[map_name].results_per_shuttle
        shuttle_counts = sorted(data_per_shuttle.keys())

        with_wait_data = []
        without_wait_data = []

        for num_shuttles in shuttle_counts:
            results_list = data_per_shuttle[num_shuttles]
            with_wait_times = [res.with_wait for res in results_list]
            without_wait_times = [res.without_wait for res in results_list]
            with_wait_data.append(with_wait_times)
            without_wait_data.append(without_wait_times)

        offset = BOX_PLOT_WIDTH
        positions = np.array(range(len(shuttle_counts))) * 2.0
        positions_with = positions - offset / 2
        positions_without = positions + offset / 2

        ax.boxplot(
            with_wait_data,
            positions=positions_with,
            widths=BOX_PLOT_WIDTH,
            patch_artist=True,
            boxprops=dict(facecolor=WITH_COLOR),
            medianprops=dict(color='blue'),
            showfliers=False
        )
        ax.boxplot(
            without_wait_data,
            positions=positions_without,
            widths=BOX_PLOT_WIDTH,
            patch_artist=True,
            boxprops=dict(facecolor=WITHOUT_COLOR),
            medianprops=dict(color='green'),
            showfliers=False
        )

        ax.tick_params(axis='both', which='major', labelsize=AXIS_NUMBER_FONT_SIZE)
        ax.set_xticks(positions)
        ax.set_xticklabels(shuttle_counts)
        ax.set_xlabel(X_AXIS_LABEL, fontsize=AXIS_LABELS_FONT_SIZE, fontweight=FONT_WEIGHT
                      , labelpad=AXIS_LABEL_PAD)
        if idx == 0:
            ax.set_ylabel('Simulation Makespan [s]', fontsize=AXIS_LABELS_FONT_SIZE,
                          fontweight=FONT_WEIGHT, labelpad=AXIS_LABEL_PAD)
        plot_map_name = get_short_map_name(map_name)
        ax.set_title(plot_map_name, fontsize=TITLE_FONT_SIZE, fontweight=FONT_WEIGHT)
        if USE_GRID_LINES:
            ax.grid(True)

        medians_with = [np.median(data) for data in with_wait_data]
        medians_without = [np.median(data) for data in without_wait_data]
        ax.plot(positions_with, medians_with, color='blue', linestyle='--', marker='o', label='With Wait Median')
        ax.plot(positions_without, medians_without, color='green', linestyle='--', marker='o',
                label='Without Wait Median')

    for i in range(num_maps, grid_size * grid_size):
        fig.delaxes(axes[i])

    blue_patch = mpatches.Patch(color=WITH_COLOR, label='With Wait Actions')
    green_patch = mpatches.Patch(color=WITHOUT_COLOR, label='Without Wait Actions')
    fig.legend(handles=[blue_patch, green_patch], loc='upper center', ncol=2, fontsize=LEGEND_FONT_SIZE)
    plt.tight_layout(rect=(0, 0, 1, 0.95))
    plt.savefig(os.path.expanduser("~/Downloads/wait_plot.png"), bbox_inches="tight")


if __name__ == "__main__":
    f_p = PATH_MAPF_BENCHMARK_SIMULATION_RESULTS / "consecutive_move_2.json" # "very_fast_agents.json" # "new_wait_compare_without_supervisor_yields.json"  # "wait_compare_to_use.json" #
    results_across_maps = WaitActionRemovalAcrossMaps.from_file(f_p)
    plot_wait_action_removal_comparison(results_across_maps)
