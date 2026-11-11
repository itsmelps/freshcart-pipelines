import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix

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


@transformer
def evaluate(data, *args, **kwargs):
    y_test = np.asarray(data['y_test'], dtype='int64')
    predictions = np.asarray(data['preds'], dtype='int64')

    cm = confusion_matrix(y_test, predictions)
    print('Confusion matrix')
    print(pd.DataFrame(cm))
    report = classification_report(y_test, predictions, output_dict=True)
    metrics = pd.DataFrame(report).transpose().reset_index()
    metrics = metrics.rename(columns={'index': 'label'})
    print('Metrics')
    print(metrics.to_string(index=False))
    return metrics


@test
def test_output(output, *args):
    assert 'precision' in output.columns
    assert len(output) >= 5


evaluate_model = evaluate