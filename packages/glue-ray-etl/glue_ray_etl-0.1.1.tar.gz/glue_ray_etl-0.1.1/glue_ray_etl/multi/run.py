import pandas
import pyarrow
import ray
import ray.data


def empty_pandas_dataframe(schema):
    return pandas.DataFrame({n: pandas.Series(dtype=t) for n, t in schema.items()})


def to_pandas_schema(dataset):
    raw_schema = dataset.schema()
    types = [t.to_pandas_dtype() if isinstance(t, pyarrow.lib.DataType) else t
             for t in raw_schema.types]
    pandas_schema = {n: t for n, t in zip(raw_schema.names, types)}
    return pandas_schema


def apply_remote_multiple(wrapped_function, datasets, kwargs=None):
    if kwargs is None:
        kwargs = {}
    schemas = [to_pandas_schema(dataset) for dataset in datasets]

    @ray.remote
    def remote_func(*dataframes):
        fixed_dataframes = list(dataframes)
        for i in range(len(schemas)):
            df = dataframes[i]
            if len(df) == 0:
                fixed_dataframes[i] = empty_pandas_dataframe(schemas[i])
        return wrapped_function(*fixed_dataframes, **kwargs)

    refs = ray.data.from_pandas_refs(
        [remote_func.remote(*refs) for refs in zip(*[ds.get_internal_block_refs() for ds in datasets])])
    return refs
