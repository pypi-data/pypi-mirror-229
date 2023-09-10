import numpy as np

from distribution import Distribution

distribution = Distribution(np.array([[1, 2, 3], [4, 5, 6]]))

for i in distribution:
    for j in i:
        print(j)
