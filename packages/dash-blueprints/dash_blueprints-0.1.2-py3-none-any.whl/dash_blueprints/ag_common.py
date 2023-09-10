from __future__ import annotations
from copy import deepcopy
import pandas as pd
import polars as pl
DF = pl.DataFrame
DFPd = pd.DataFrame

GLOBAL_AG_OPTIONS = dict(
    enableEnterpriseModules=True,
    dashGridOptions=dict(
        rowSelection="multiple",
        suppressScrollOnNewData=True,
        suppressAggFuncInHeader=True,
        suppressMenuHide=True,
        quickFilterText='',
    ),
    defaultColDef=dict(
        resizable=True,
        sortable=True,
        filter=True,
        enableValue=True,
    ),
    # columnSize="autoSize",
    # className='ag-theme-balham-dark',
)

def ag_options(dashGridOptions={}, defaultColDef={}, **kwargs) -> dict:
    res = deepcopy(GLOBAL_AG_OPTIONS) | kwargs
    res['dashGridOptions'] |= dashGridOptions
    res['defaultColDef'] |= defaultColDef
    return res

def ag_cols(cols: DF | list, **rest) -> list[dict]:
    if isinstance(cols, (DF, DFPd)):
        cols = cols.columns
    return [{'field': col} | rest for col in cols]
