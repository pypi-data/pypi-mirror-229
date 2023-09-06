from godata import open_project
from pathlib import Path
project = open_project("test_project")
path = project.get("test_data")
print(path)