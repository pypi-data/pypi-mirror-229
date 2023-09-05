import polars as pl
from itertools import islice
from typing import Iterable, List, Union

def grouper(n, iterable):
    it = iter(iterable)
    while True:
        chunk = tuple(islice(it, n))
        if not chunk:
            return
        yield chunk

def normalize_uids(uids: Union[str, Iterable[str]]) -> List[str]:
    """Normalize uids to ensure they are given as a sequence of string.

    Parameters
    ----------
    uids : Union[str, Iterable[str]]
        uids as scalar or sequence

    Returns
    -------
    List[str]
        uids as a list of string
    """
    if not isinstance(uids, Iterable) or isinstance(uids, str):
        uids = [uids]
    return list(uids)

class FakeLock:
    def __enter__(self):
        pass

    def __exit__(self, *args):
        pass

def taxonomy2lineage(df):
    """ Convert a dataframe with raw taxonomy information to a dataframe with the same
    data organized in a lineage format.

    Parameters
    ----------
    df : pl.DataFrame
        dataframe with raw taxonomy information (coming from the stores)

    Returns
    -------
    pl.DataFrame
        dataframe with the same data organized in a lineage format
    """
    lineage = (
        df.explode("lineage_ex")
        .select(
            "tax_id",
            pl.col("lineage_ex").struct.field("rank"),
            pl.col("lineage_ex").struct.field("scientific_name"),
        )
        .pivot(
            index="tax_id",
            columns="rank",
            values="scientific_name",
            aggregate_function=None,
        )
        .select(pl.all().exclude("no rank"))
    )

    return df.select(
        "tax_id",
        "scientific_name",
        "rank",
        "division",
        "create_date",
        "update_date",
        "pub_date",
    ).join(lineage, on="tax_id")