def _identity_decorator(*args, **kwargs):
    if len(args) == 1 and callable(args[0]) and not kwargs:
        return args[0]

    def decorator(func):
        return func

    return decorator


try:
    from mage_ai.data_preparation.decorators import data_exporter, data_loader, test, transformer
except ModuleNotFoundError:
    data_exporter = _identity_decorator
    data_loader = _identity_decorator
    test = _identity_decorator
    transformer = _identity_decorator
