import os

import requests
import zipfile
import io

from src.common.resources import PATH_MAPF_BENCHMARK_PRECOMPUTED_SOLUTIONS

url = "https://www.dropbox.com/scl/fi/n2ymplfot8sam3ilw03bo/lns2_init_states.zip?rlkey=jkxqaai78yy5ny9hefz0fe4ly&e=2&st=3oghuigi&dl=1"

print("starting download")
response = requests.get(url)
response.raise_for_status()

with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
    for member in zip_ref.namelist():
        if not member.endswith('/'):
            filename = os.path.basename(member)
            target_path = os.path.join(PATH_MAPF_BENCHMARK_PRECOMPUTED_SOLUTIONS, filename)
            with open(target_path, 'wb') as output_file:
                output_file.write(zip_ref.read(member))

print("finished download")
