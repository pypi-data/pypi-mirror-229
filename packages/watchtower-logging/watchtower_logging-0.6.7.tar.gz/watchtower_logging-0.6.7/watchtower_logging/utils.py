from itertools import accumulate as _accumulate, repeat as _repeat
from bisect import bisect as _bisect
import random
import traceback
from functools import wraps

def random_choices(population, weights=None, *, cum_weights=None, k=1):
    """Return a k sized list of population elements chosen with replacement.
    If the relative weights or cumulative weights are not specified,
    the selections are made with equal probability.
    """
    n = len(population)
    if cum_weights is None:
        if weights is None:
            _int = int
            n += 0.0    # convert to float for a small speed improvement
            return [population[_int(random.random() * n)] for i in _repeat(None, k)]
        cum_weights = list(_accumulate(weights))
    elif weights is not None:
        raise TypeError('Cannot specify both weights and cumulative weights')
    if len(cum_weights) != n:
        raise ValueError('The number of weights does not match the population')
    bisect = _bisect
    total = cum_weights[-1] + 0.0   # convert to float
    hi = n - 1
    return [population[bisect(cum_weights, random.random() * total, 0, hi)]
            for i in _repeat(None, k)]


def monitor_func(logger,
                 func_name=None,
                 set_execution_id=True,
                 execution_id=None,
                 start_done=True,
                 except_level='error'):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            fname = func_name or func.__name__

            try:
                if set_execution_id:
                    logger.setExecutionId(execution_id)

                if start_done:
                    logger.start(f'Starting {fname}')

                result = func(*args, **kwargs)

                if start_done:
                    logger.done(f'Done with {fname}')

                return result

            except Exception as e:

                getattr(logger, except_level.lower())(
                    str(e), data={'traceback': traceback.format_exc()}
                )
                if hasattr(logger, 'return_when_exception'):
                    return logger.return_when_exception

        return wrapper

    return decorator
