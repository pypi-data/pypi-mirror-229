from godata import create_project
import numpy as np

data = np.zeros((50, 50))
f = np.save


store_f = lambda data, path: np.save(path, data)

test = create_project("test_project")
test.store(data, "test_data")
test.store(data, "test_folder/test_data")
test.ls()