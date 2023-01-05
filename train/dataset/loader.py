import pandas as pd
from sklearn.preprocessing import LabelEncoder


def load_df(in_base_dir: str, filename: str, is_train: bool) -> pd.DataFrame:
    df = pd.read_csv(f"{in_base_dir}/{filename}")
    encoder = LabelEncoder()
    df["id"] = encoder.fit_transform(df["id"])
    return df
