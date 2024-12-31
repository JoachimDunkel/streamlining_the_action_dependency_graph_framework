# streamlining_the_action_dependency_graph_framework
Supplementary Material  for the Paper: [Streamlining the Action Dependency Graph Framework: Two Key Enhancements](https://arxiv.org/abs/2412.01277)

## Setup

Assuming you have a Linux environment...

### Build the cpp Part

1. Install necessary dependencies:
```bash
sudo apt update && sudo apt install cmake python3-dev g++ git python3-venv
```

2. Go to `cpp/scripts` and build the cmake project:
```bash
cd cpp/scripts
chmod +x build.sh
./build.sh
```

### Setup the Python Environment

1. Create a virtual environment:
```bash
python3 -m venv venv  
source venv/bin/activate
```

2. Install the necessary Python dependencies:
```bash
pip install -r requirements.txt
```

3. Export the root directory to PATH: (always before running something)
```bash
echo 'export PYTHONPATH=$(pwd)' >> venv/bin/activate
source venv/bin/activate
```

4. Optional - Use Pycharm and skip 1 - 3.


### Download precomputed data from the Benchmark

The publicly available benchmark used in our study is available at [mapf-lns-benchmark](https://github.com/ChristinaTan0704/mapf-lns-benchmark]).
Either manually download the data [Download Initial States ->Ins2 init states JSON](https://github.com/ChristinaTan0704/mapf-lns-benchmark/blob/main/docs/data.md)
and put it into the `mapf_benchmark/precomputed_solutions` directory.

Or run the command 
```bash
python3 mapf_benchmark/download_precomputed_solutions.py
```

In the rear case that the link becomes unavailable, please contact the conference organizers for further assistance.

Note that this will only download the precomputed solutions (which exceed the 100MB submission limit), all benchmark maps should already be included
in `mapf_benchmark/maps`.

### Overview

The repository is structured as follows:

- `cpp/` contains the C++ implementation of the compared action dependency graph construction algorithms
- `mapf_benchmark/` - where the benchmark data is stored
- `src/evaluation/` - contains all the runnable scripts for this evaluation, most importantly :
  - `evaluate_adg_construction_benchmark_performance.py` - evaluate the performance of the ADG construction algorithms and stores it in `mapf_benchmark/adg_results`
  - `eval_wait_action_removal_on_execution.py`- evaluate the performance of the wait action removal on the execution time and stores it in `mapf_benchmark/simulation_results`

Note: For both scripts, make sure to adjust the number of cores used.
To plot results, `plot_construction_runtime_line.py` and `plot_wait_action_removal.py` respectively.
(manually change the file-name used in the script to the created evaluation result you want to plot)


### Wait action impact remarks
Please note that, due to cycles in the ADG on most scenarios, proper solutions for `eval_wait_action_removal_on_execution.py `can only be obtained for two maps - as seen in the paper.
This limitation arose from a strategic decision to use this benchmark, which we were unable to correct before the deadline. 
However, we believe this does not affect the validity of our evaluation on the impact of wait actions nor does it have any influence on the ADG construction process. 
This clarifies why the full benchmark was not used for the wait-action impact evaluation

