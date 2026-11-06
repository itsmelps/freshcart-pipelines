try:
    from mage_ai.data_preparation.decorators import transformer
except ImportError:
    def transformer(func):
        return func


def transform(df):
    from sklearn.model_selection import train_test_split

    train_idx, test_idx = train_test_split(
        df.index,
        test_size=0.3,
        random_state=42,
        stratify=df["target"]
    )

    result = df.copy()
    result["split"] = "train"
    result.loc[test_idx, "split"] = "test"

    return result


@transformer
def prepare_data(df, **kwargs):
    return transform(df)