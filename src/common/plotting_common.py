AXIS_LABELS_FONT_SIZE = 20
AXIS_NUMBER_FONT_SIZE = 19
LEGEND_FONT_SIZE = 20

SHOW_TITLE_ON_PLOTS = False
TITLE_FONT_SIZE = 25

RESULT_PLT_FIG_SIZE = (10, 6)

USE_GRID_LINES = False

NAIVE_COLOR = 'tab:blue'
CP_COLOR = 'tab:green'
SCP_COLOR = 'tab:red'

NAIVE_LIGHT_COLOR = 'lightblue'
CP_LIGHT_COLOR = 'lightgreen'
SCP_LIGHT_COLOR = 'lightcoral'

X_AXIS_LABEL = "Number of Agents [N]"
Y_AXIS_LABEL = "Runtime [s]"

Y_AXIS_TYPE2_DEP_LABEL = "Created Type2 Edges"

CP_LABEL = "Candidate Partitioning (CP)"
SCP_LABEL = "Sparse Candidate Partitioning (SCP)"
NAIVE_LABEL = "Exhaustive"

EFFICIENT_ALG_COMPARE_PLOT_TITLE = "ADG-Construction: CP vs. SCP"
ALL_ALGO_COMPARE_PLOT_TITLE = "ADG-Construction: Exhaustive vs. Efficient Algorithms"
BOX_PLOT_WIDTH = 10.0

FONT_WEIGHT = 'normal' # 'bold'#
AXIS_LABEL_PAD = 10


def get_short_map_name(map_name: str):
    return map_name.split("-")[0].split("_")[0]