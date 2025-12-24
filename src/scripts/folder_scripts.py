# add '__init__.py' file to every sub-folder paths
import os
from pathlib import Path

src_path = Path.cwd().parent
print(src_path)

for root, dirs, files in os.walk(src_path):
    print(root)
    with open(fr"{root}\__init__.py", 'w') as f:
        pass


