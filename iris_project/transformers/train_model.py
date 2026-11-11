from sklearn.metrics import accuracy_score
from sklearn.tree import DecisionTreeClassifier
import pandas as pd

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
def train(data, *args, **kwargs):
    max_depth = int(kwargs.get('max_depth', 3))
    model = DecisionTreeClassifier(max_depth=max_depth, random_state=42)

    y_train = data['y_train'].map(
        lambda value: value.get('target') if isinstance(value, dict) else value
    ).astype('int64')
    y_test = data['y_test'].map(
        lambda value: value.get('target') if isinstance(value, dict) else value
    ).astype('int64')

    model.fit(data['X_train'], y_train)

    predictions = model.predict(data['X_test'])
    accuracy = accuracy_score(y_test, predictions)
    predictions = predictions.tolist()

    print(f'max_depth={max_depth} test_accuracy={accuracy:.4f}')

    return {
        'model': model,
        'X_test': data['X_test'],
        'y_test': y_test.tolist(),
        'preds': predictions,
        'predictions': predictions,
        'accuracy': accuracy,
        'max_depth': model.max_depth
    }



@test
def test_accuracy(output, *args):
    assert output['accuracy'] >= 0.9, f"accuracy {output['accuracy']:.4f} below 0.9"


train_model = train