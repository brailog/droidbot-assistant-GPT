from functools import wraps
import time
import pickle


def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f'Function {func.__name__} Took {total_time:.4f} seconds')
        return result
    return timeit_wrapper


def save_to_pickle(obj: object, file_path: str) -> None:
    """Serialize and save the object to a pickle file."""
    with open(file_path, 'wb') as file:
        pickle.dump(obj, file)


def load_from_pickle(file_path: str) -> object:
    """Load and deserialize the object from a pickle file."""
    with open(file_path, 'rb') as file:
        obj = pickle.load(file)
    return obj
