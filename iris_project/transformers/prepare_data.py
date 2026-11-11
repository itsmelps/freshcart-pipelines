
from sklearn.model_selection import train_test_split

if 'transformer' not in globals():
    try:
        from mage_ai.data_preparation.decorators import transformer
    except ModuleNotFoundError:
        from iris_project.mage_compat import transformer
if 'test' not in globals():
    try:
        from mage_ai.data_preparation.decorators import test
    except ModuleNotFoundError:
        from iris_project.mage_compat import test


def transform(df, *args, **kwargs):
    if df is None:
        raise ValueError('Input dataframe is required.')

    data = df.copy()
    target_column = kwargs.get('target_column', 'target')
    test_size = kwargs.get('test_size', 0.2)
    random_state = kwargs.get('random_state', 42)

    if target_column in data.columns:
        y = data[target_column]
        train_idx, test_idx = train_test_split(
            data.index,
            test_size=test_size,
            random_state=random_state,
            stratify=y,
        )
    else:
        train_idx, test_idx = train_test_split(
            data.index,
            test_size=test_size,
            random_state=random_state,
        )

    result = data.copy()
    result['split'] = 'train'
    result.loc[test_idx, 'split'] = 'test'
    return result


@transformer
def prepare_data(df, *args, **kwargs):
    if df is None:
        raise ValueError('Input dataframe is required.')

    target_column = kwargs.get('target_column', 'target')
    if target_column not in df.columns:
        raise ValueError(f"Input dataframe must contain a '{target_column}' column.")

    X = df.drop(columns=[target_column])
    y = df[target_column].apply(
        lambda value: value.get(target_column) if isinstance(value, dict) else value
    ).astype('int64')
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=kwargs.get('test_size', 0.2),
        random_state=kwargs.get('random_state', 42),
        stratify=y,
    )

    return {
        'X_train': X_train,
        'X_test': X_test,
        'y_train': y_train,
        'y_test': y_test,
    }

@test
def test_split(output, *args):
    assert len(output['X_train']) == 120
    assert len(output['X_test']) == 30
    assert len(output['y_train']) == 120
    assert len(output['y_test']) == 30