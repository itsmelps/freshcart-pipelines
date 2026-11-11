import os

if 'data_exporter' not in globals():
    try:
        from mage_ai.data_preparation.decorators import data_exporter
    except ModuleNotFoundError:
        from iris_project.mage_compat import data_exporter
if 'test' not in globals():
    try:
        from mage_ai.data_preparation.decorators import test
    except ModuleNotFoundError:
        from iris_project.mage_compat import test


@data_exporter
def export_data(metrics, *args, **kwargs):
    metrics.to_csv('iris_metrics.csv', index=False)


@test
def test_output(*args):
    assert os.path.exists('iris_metrics.csv')
    assert os.path.getsize('iris_metrics.csv') > 0


save_metrics = export_data