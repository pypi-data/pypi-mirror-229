import polars as pl
import pandas as pd
from typing import Union, List
import importlib
from ..utils import get_gpu_info


def aggregate_data_cpu(
    df: Union[pl.DataFrame, pd.DataFrame],
    columns_to_aggregate: List[str],
    groupby_columns: List[str],
    aggregation_function: str = "mean",
):
    """
    Aggregates morphology data using the specified columns and aggregation function.

    Args:
        df (Union[pl.DataFrame, pd.DataFrame]): The input DataFrame to be aggregated.
        columns_to_aggregate (List[str]): The list of columns to be aggregated.
        groupby_columns (List[str]): The list of columns to group by.
        aggregation_function (str, optional): The aggregation function to be applied. Defaults to "mean" where 
        possible values could set to: "mean", median, "sum", "min", "max", "first", "last".

    Returns:
        pl.DataFrame: The aggregated DataFrame.

    Examples:
        ```python
        df = pd.DataFrame({
            'A': [1, 2, 3, 4],
            'B': [5, 6, 7, 8],
            'C': [9, 10, 11, 12]
        })
        aggregated_df = aggregate_morphology_data_cpu(df, ['A', 'B'], ['C'])
        print(aggregated_df)
        ```
    """
    
    # Check if data is in pandas DataFrame, if so convert to polars DataFrame
    if isinstance(df, pd.DataFrame):
        df = pl.from_pandas(df)
        
    grouped = df.lazy().groupby(groupby_columns)
    retain_cols = [c for c in df.columns if c not in columns_to_aggregate]
    retained_metadata_df = df.lazy().select(retain_cols)

    # Aggregate only the desired columns.
    agg_exprs = [
        getattr(pl.col(col), aggregation_function)().alias(col)
        for col in columns_to_aggregate
    ]

    # Execute the aggregation.
    agg_df = grouped.agg(agg_exprs)
    agg_df = agg_df.join(retained_metadata_df, on=groupby_columns, how="left")

    return agg_df.sort(groupby_columns).collect()


def aggregate_data_gpu(
    df: Union[pl.DataFrame, pd.DataFrame],
    columns_to_aggregate: List[str],
    groupby_columns: List[str],
    aggregation_function: str = "mean",
):
    """
    Aggregates data using the specified columns and aggregation function with GPU acceleration.

    Args:
        df (Union[pl.DataFrame, pd.DataFrame]): The input DataFrame to be aggregated.
        columns_to_aggregate (List[str]): The list of columns to be aggregated.
        groupby_columns (List[str]): The list of columns to group by.
        aggregation_function (str, optional): The aggregation function to be applied. Defaults to "mean" where 
        possible values could set to: "mean", median, "sum", "min", "max", "first", "last".

    Returns:
        pl.DataFrame: The aggregated DataFrame.

    Raises:
        ImportError: Raised when Dask-CUDA is not available.
        RuntimeError: Raised when an unexpected error occurs during the aggregation process.

    Example:
        ```python
        df = pd.DataFrame({
            'A': [1, 2, 3, 4],
            'B': [5, 6, 7, 8],
            'C': [9, 10, 11, 12]
        })
        aggregated_df = aggregate_data_gpu(df, ['A', 'B'], ['C'])
        print(aggregated_df)
        ```
    """

    # Check if data is in pandas DataFrame, if so convert to polars DataFrame
    if isinstance(df, pd.DataFrame):
        df = pl.from_pandas(df)
    
    total_memory, n_gpus = get_gpu_info()

    if total_memory is not None and n_gpus is not None:
        device_memory_limit = f"{total_memory * 0.8}MB"
        npartitions = n_gpus * 4
    else:
        print("Failed to get GPU information.")

    try:
        # Check if 'client' exists in the global namespace
        if "client" not in globals() or client is None:
            LocalCUDACluster = importlib.import_module("dask_cuda").LocalCUDACluster
            Client = importlib.import_module("dask.distributed").Client
            dask = importlib.import_module("dask")
            with dask.config.set(jit_unspill=True):
                cluster = LocalCUDACluster(
                    n_workers=n_gpus, device_memory_limit=device_memory_limit
                )
                client = Client(cluster)

        dd = importlib.import_module("dask.dataframe")

        agg_dict = {col: aggregation_function for col in columns_to_aggregate}

        # Convert the Polars DataFrame to a Dask DataFrame
        # The number of partitions can be adjusted depending on your needs
        ddf = dd.from_pandas(df.to_pandas(), npartitions=npartitions)
        agg_ddf = (
            ddf.groupby(groupby_columns).agg(agg_dict, shuffle="tasks").reset_index()
        )

        sorted_ddf = agg_ddf.compute().sort_values(by=groupby_columns)

        result = pl.from_pandas(sorted_ddf.to_pandas())

        # Cleanup
        client.close()
        cluster.close()

        return result

    except ImportError as e:
        raise ImportError(
            "Dask-CUDA is not available. Please install it to use GPU acceleration."
        ) from e
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {str(e)}") from e
