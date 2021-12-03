import time

import numpy as np
import pandas as pd


def increment_head(rows: int, columns: int):

    col = np.random.rand(rows)
    df = pd.DataFrame({f"col{i}": col for i in range(1, columns + 1)})

    start = time.perf_counter()
    for i in range(len(df)):
        df_head = df.head(i + 1)
    end = time.perf_counter()

    print(f"Execution time ({rows} rows, {columns} columns): {end - start} seconds")


increment_head(rows=100_000, columns=40)
