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
def export_data(data, *args, **kwargs):
    out = data['X_test'].copy()
    out['actual'] = data['y_test']
    out['predicted'] = data['preds']
    out.to_csv('iris_predictions.csv', index=False)


@test
def test_output(*args):
    assert os.path.exists('iris_predictions.csv')


save_results = export_data