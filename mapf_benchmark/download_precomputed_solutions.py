import requests
import zipfile
import io

from src.common.resources import PATH_MAPF_BENCHMARK_PRECOMPUTED_SOLUTIONS

url = "https://www.dropbox.com/scl/fi/n2ymplfot8sam3ilw03bo/lns2_init_states.zip?rlkey=jkxqaai78yy5ny9hefz0fe4ly&e=2&st=3oghuigi&dl=1"

response = requests.get(url)
response.raise_for_status()

with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
    zip_ref.extractall(PATH_MAPF_BENCHMARK_PRECOMPUTED_SOLUTIONS)
    