import pandas as pd

def basic_clean(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out = out.drop_duplicates()
    out.columns = [c.strip().lower() for c in out.columns]
    return out
