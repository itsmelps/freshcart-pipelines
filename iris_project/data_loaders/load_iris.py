import pandas as pd
from sklearn.datasets import load_iris as sk_load_iris

if 'data_loader' not in globals():
    try:
        from mage_ai.data_preparation.decorators import data_loader
    except ModuleNotFoundError:
        from iris_project.mage_compat import data_loader
if 'test' not in globals():
    try:
        from mage_ai.data_preparation.decorators import test
    except ModuleNotFoundError:
        from iris_project.mage_compat import test


@data_loader
def load_data(*args, **kwargs):
    from sklearn.datasets import load_iris

    iris = load_iris(as_frame=True)
    df = iris.frame.copy()

    df['target'] = iris.target.astype(int)
    return df


@test
def test_output(output, *args):
    assert output is not None
    assert len(output) == 150
    assert 'target' in output.columns


load_iris = load_data