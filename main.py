import pandas as pd


def generate_data():
    return pd.DataFrame(
        [
            (0, 0, 200),
            (0, 0, 120),
            (0, 1, 300),
            (1, 0, 500),
            (1, 0, 600),
            (1, 1, 800),
        ],
        
        columns=["t", "x", "y"],
    )
