import collections
import os
from enum import Enum

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

from src.common.plotting_common import NAIVE_LABEL, \
    CP_LABEL, SCP_LABEL, SCP_COLOR, CP_COLOR, NAIVE_COLOR, Y_AXIS_LABEL, X_AXIS_LABEL, BOX_PLOT_WIDTH, SCP_LIGHT_COLOR, \
    CP_LIGHT_COLOR, NAIVE_LIGHT_COLOR, Y_AXIS_TYPE2_DEP_LABEL, get_short_map_name, AXIS_LABELS_FONT_SIZE, \
    LEGEND_FONT_SIZE, FONT_WEIGHT, AXIS_NUMBER_FONT_SIZE, AXIS_LABEL_PAD, USE_GRID_LINES, TITLE_FONT_SIZE
from src.common.resources import PATH_MAPF_BENCHMARK_ADG_RESULTS, PATH_MAPF_BENCHMARK_MAPS_PICS
from src.evaluation.evaluate_adg_construction_benchmark_performance import ADGPerformanceResultAcrossMaps


class PlotType(Enum):
    LINE_PLOT = 0
    SCATTER_PLOT = 1
    BOX_PLOT = 2
    CONFIDENCE_BANDS = 3
    NUM_TYP2_COMPARISON = 4


def extract_data_for_plotting(f_p, plot_type):
    eval_results = ADGPerformanceResultAcrossMaps.from_file(f_p)

    data_per_map = {}

    for map_name, results_across_shuttles in eval_results.results_per_map.items():
        shuttles = set()
        naive_results = collections.defaultdict(list)
        cp_results = collections.defaultdict(list)
        scp_results = collections.defaultdict(list)

        for shuttle_id in results_across_shuttles.results_per_shuttle.keys():
            results = results_across_shuttles.results_per_shuttle[shuttle_id]
            shuttles.add(int(shuttle_id))

            for result in results:
                if type(result.naive) == float:
                    naive_results[shuttle_id].append(result.naive)
                    cp_results[shuttle_id].append(result.cp)
                    scp_results[shuttle_id].append(result.scp)
                else:
                    if plot_type == PlotType.NUM_TYP2_COMPARISON:
                        naive_results[shuttle_id].append(result.naive.created_type2_dependencies)
                        cp_results[shuttle_id].append(result.cp.created_type2_dependencies)
                        scp_results[shuttle_id].append(result.scp.created_type2_dependencies)
                    else:
                        naive_results[shuttle_id].append(result.naive.elapsed_time)
                        cp_results[shuttle_id].append(result.cp.elapsed_time)
                        scp_results[shuttle_id].append(result.scp.elapsed_time)

        sorted_shuttles = sorted(shuttles)

        data_per_map[map_name] = {
            'shuttles': sorted_shuttles,
            'naive': naive_results,
            'cp': cp_results,
            'scp': scp_results
        }

    return data_per_map


def plot_runtime_comparison_grid_with_images(f_p, plot_type=PlotType.LINE_PLOT, include_naive=True,
                                             include_images_in_legend=True, reduce_axis_titles=True):
    if include_naive:
        include_images_in_legend = False

    data_per_map = extract_data_for_plotting(f_p, plot_type)
    num_maps = len(data_per_map)

    grid_size_rows = 1 if num_maps <= 2 else 2 if num_maps <= 4 else 3
    grid_size_cols = 1 if num_maps < 2 else 2

    fig, axes = plt.subplots(grid_size_rows, grid_size_cols, figsize=(10, 8) if num_maps == 1 else (15, 15))

    axes = [axes] if num_maps == 1 else axes.flatten()

    y_axis_label = Y_AXIS_LABEL

    for idx, (map_name, data) in enumerate(data_per_map.items()):
        ax = axes[idx]
        shuttles = data['shuttles']
        naive_results = data['naive']
        cp_results = data['cp']
        scp_results = data['scp']

        if plot_type == PlotType.NUM_TYP2_COMPARISON:
            import matplotlib.ticker as mticker

            def thousands_formatter(x, pos):
                return f'{int(x / 1000)}K'

            ax.yaxis.set_major_formatter(mticker.FuncFormatter(thousands_formatter))

            y_axis_label = Y_AXIS_TYPE2_DEP_LABEL
            cp = [np.mean(cp_results[shuttle_id]) for shuttle_id in shuttles]
            scp = [np.mean(scp_results[shuttle_id]) for shuttle_id in shuttles]

            ax.plot(shuttles, cp, label=CP_LABEL, color=CP_COLOR, marker='o', linestyle='--')
            ax.plot(shuttles, scp, label=SCP_LABEL, color=SCP_COLOR, marker='o', linestyle='-')

        if plot_type == PlotType.LINE_PLOT:
            if include_naive:
                naive = [np.mean(naive_results[shuttle_id]) for shuttle_id in shuttles]
                ax.plot(shuttles, naive, label=NAIVE_LABEL, color=NAIVE_COLOR, marker='o', linestyle='--')

            cp = [np.mean(cp_results[shuttle_id]) for shuttle_id in shuttles]
            scp = [np.mean(scp_results[shuttle_id]) for shuttle_id in shuttles]

            ax.plot(shuttles, cp, label=CP_LABEL, color=CP_COLOR, marker='o', linestyle='-')
            ax.plot(shuttles, scp, label=SCP_LABEL, color=SCP_COLOR, marker='o', linestyle='-')

        elif plot_type == PlotType.CONFIDENCE_BANDS:
            if include_naive:
                naive_mean = [np.mean(naive_results[shuttle_id]) for shuttle_id in shuttles]
                naive_std = [np.std(naive_results[shuttle_id]) for shuttle_id in shuttles]
                ax.plot(shuttles, naive_mean, label=NAIVE_LABEL, color=NAIVE_COLOR, marker='o', linestyle='--')
                ax.fill_between(shuttles,
                                [m - s for m, s in zip(naive_mean, naive_std)],
                                [m + s for m, s in zip(naive_mean, naive_std)],
                                color=NAIVE_COLOR, alpha=0.1)

            cp_mean = [np.mean(cp_results[shuttle_id]) for shuttle_id in shuttles]
            cp_std = [np.std(cp_results[shuttle_id]) for shuttle_id in shuttles]
            scp_mean = [np.mean(scp_results[shuttle_id]) for shuttle_id in shuttles]
            scp_std = [np.std(scp_results[shuttle_id]) for shuttle_id in shuttles]

            ax.plot(shuttles, cp_mean, label=CP_LABEL, color=CP_COLOR, marker='o', linestyle='-')
            ax.plot(shuttles, scp_mean, label=SCP_LABEL, color=SCP_COLOR, marker='o', linestyle='-')

            ax.fill_between(shuttles,
                            [m - s for m, s in zip(cp_mean, cp_std)],
                            [m + s for m, s in zip(cp_mean, cp_std)],
                            color=CP_COLOR, alpha=0.2)

            ax.fill_between(shuttles,
                            [m - s for m, s in zip(scp_mean, scp_std)],
                            [m + s for m, s in zip(scp_mean, scp_std)],
                            color=SCP_COLOR, alpha=0.2)

        elif plot_type == PlotType.SCATTER_PLOT:
            if include_naive:
                naive = [np.mean(naive_results[shuttle_id]) for shuttle_id in shuttles]
                ax.scatter(shuttles, naive, label=NAIVE_LABEL, color=NAIVE_COLOR, marker='o')

            cp = [np.mean(cp_results[shuttle_id]) for shuttle_id in shuttles]
            scp = [np.mean(scp_results[shuttle_id]) for shuttle_id in shuttles]

            ax.scatter(shuttles, cp, label=CP_LABEL, color=CP_COLOR, marker='x')
            ax.scatter(shuttles, scp, label=SCP_LABEL, color=SCP_COLOR, marker='^')

        elif plot_type == PlotType.BOX_PLOT:
            offset = BOX_PLOT_WIDTH
            avg_dist = np.mean(np.diff(shuttles))
            scaled_box_width = BOX_PLOT_WIDTH * avg_dist / 50
            if include_naive:
                positions_naive = [s - offset for s in shuttles]
                positions_cp = shuttles
                positions_scp = [s + offset for s in shuttles]

                naive_data = [naive_results[shuttle_id] for shuttle_id in shuttles]
                ax.boxplot(naive_data, positions=positions_naive, widths=scaled_box_width, patch_artist=True,
                           boxprops=dict(facecolor=NAIVE_LIGHT_COLOR),
                           medianprops=dict(color=NAIVE_COLOR), showfliers=False)
            else:
                positions_cp = [s - offset / 2 for s in shuttles]
                positions_scp = [s + offset / 2 for s in shuttles]

            cp_data = [cp_results[shuttle_id] for shuttle_id in shuttles]
            ax.boxplot(cp_data, positions=positions_cp, widths=scaled_box_width, patch_artist=True,
                       boxprops=dict(facecolor=CP_LIGHT_COLOR),
                       medianprops=dict(color=CP_COLOR), showfliers=False)

            scp_data = [scp_results[shuttle_id] for shuttle_id in shuttles]
            ax.boxplot(scp_data, positions=positions_scp, widths=scaled_box_width, patch_artist=True,
                       boxprops=dict(facecolor=SCP_LIGHT_COLOR),
                       medianprops=dict(color=SCP_COLOR), showfliers=False)

            ax.set_xticks(shuttles)
            ax.set_xticklabels(shuttles)

        if include_naive and plot_type:
            ax.set_yscale('log')

        if not reduce_axis_titles or idx % grid_size_cols == 0:
            ax.set_ylabel(y_axis_label, fontsize=AXIS_LABELS_FONT_SIZE, fontweight=FONT_WEIGHT, labelpad=AXIS_LABEL_PAD)
        if not reduce_axis_titles or idx >= (grid_size_rows - 1) * grid_size_cols:
            ax.set_xlabel(X_AXIS_LABEL, fontsize=AXIS_LABELS_FONT_SIZE, fontweight=FONT_WEIGHT, labelpad=AXIS_LABEL_PAD)

        ax.tick_params(axis='both', which='major', labelsize=AXIS_NUMBER_FONT_SIZE)
        plot_map_name = get_short_map_name(map_name)

        if include_images_in_legend:
            image_path = PATH_MAPF_BENCHMARK_MAPS_PICS / f"{map_name}.png"
            if os.path.exists(image_path):
                img = mpimg.imread(image_path)

                bbox = ax.get_position()
                axis_height = bbox.height
                axis_width = bbox.width
                zoom_factor = min(axis_height, axis_width) * 0.5

                imagebox = OffsetImage(img, zoom=zoom_factor)

                box_coords = (0.15, 0.85)
                ab = AnnotationBbox(imagebox, box_coords, frameon=True,
                                    bboxprops=dict(edgecolor='black', linewidth=1),
                                    xycoords='axes fraction')

                ax.add_artist(ab)
                ax.text(box_coords[0], box_coords[1] + 0.1, plot_map_name, transform=ax.transAxes, fontsize=12,
                        fontweight='bold',
                        verticalalignment='bottom', horizontalalignment='center',
                        bbox=dict(facecolor='white', alpha=1.0, edgecolor='black'))

        else:
            ax.set_title(plot_map_name, fontsize=TITLE_FONT_SIZE, fontweight=FONT_WEIGHT)

        if USE_GRID_LINES:
            ax.grid(True)

    for i in range(num_maps, grid_size_rows * grid_size_cols):
        fig.delaxes(axes[i])

    line_plots = [PlotType.LINE_PLOT, PlotType.SCATTER_PLOT, PlotType.CONFIDENCE_BANDS, PlotType.NUM_TYP2_COMPARISON]
    if plot_type in line_plots:
        legend_elements, labels = ax.get_legend_handles_labels()
    else:
        from matplotlib.patches import Patch
        legend_elements = []

        if include_naive:
            legend_elements.append(Patch(facecolor=NAIVE_LIGHT_COLOR, edgecolor=NAIVE_COLOR, label=NAIVE_LABEL))
        legend_elements.append(Patch(facecolor=CP_LIGHT_COLOR, edgecolor=CP_COLOR, label=CP_LABEL))
        legend_elements.append(Patch(facecolor=SCP_LIGHT_COLOR, edgecolor=SCP_COLOR, label=SCP_LABEL))

    fig.legend(handles=legend_elements, loc='upper center', fontsize=LEGEND_FONT_SIZE, ncol=3)

    plt.tight_layout(rect=(0.0, 0.0, 1.0, 0.93))
    plt.savefig(os.path.expanduser("~/Downloads/construction_plot.png"), bbox_inches="tight")


if __name__ == "__main__":
    file_path = PATH_MAPF_BENCHMARK_ADG_RESULTS / "full_eval_no_exhaustive_with_type2_count.json"
    plot_runtime_comparison_grid_with_images(
        file_path,
        plot_type=PlotType.NUM_TYP2_COMPARISON,
        # Change to PlotType.LINE_PLOT, PlotType.SCATTER_PLOT, or PlotType.BOX_PLOT CONFIDENCE_BANDS NUM_TYP2_COMPARISON
        include_naive=False,
        include_images_in_legend=True,
        reduce_axis_titles=True
    )
