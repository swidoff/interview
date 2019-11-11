from abc import ABC
from dataclasses import dataclass
from datetime import date
from typing import Dict, List
from typing import Optional, Iterable, Tuple

import pandas as pd
import sqlite3
from sqlalchemy import *

engine = create_engine('sqlite+pysqlite:///data/interview.db', module=sqlite3)


class Equation(ABC):
    """Supertype of all equation objects."""
    pass


@dataclass(frozen=True)
class Market(Equation):
    """Describes how to query a market item for stocks at time `t`."""
    item: str  # one of 'close' or 'shares'
    periods: int = 1  # matches all periods in the range [t-periods+1, t] (inclusive) according to the frequency
    freq: str = "months"  # determines the frequency of selection when periods > 1 (one of 'months' or 'weeks')
    agg: Optional[str] = None  # the aggregation (by stock) to apply if periods > 1 (None, 'min' or 'max')


@dataclass(frozen=True)
class Fundamental(Equation):
    """Describes how to query a fundamental item for stocks at time `t`."""
    item: str
    quarters: int = 1  # matches all quarters in the range [t-quarters+1, t] (inclusive)
    agg: Optional[str] = None  # the aggregation (by stock) to apply if quarters > 1 (None or 'sum')


@dataclass(frozen=True)
class Ref(Equation):
    """References another equation."""
    name: str  # Equation name


@dataclass
class Op(Equation):
    """Applies a binary function to the results of the operands."""
    operator: str  # One of '+' , '-', '*' or '/'
    lhs: Equation
    rhs: Equation


equations = {
    'marketcap': Op('*', Market('close'), Market('shares')),
    'earnings': Fundamental('net_income', quarters=4, agg='sum'),
    'e2p': Op('/', Ref('earnings'), Ref('marketcap')),
    'range_52w': Op('/',
                    Op('-',
                       Market('close'),
                       Market('close', freq='weeks', periods=52, agg='min')),
                    Op('-',
                       Market('close', freq='weeks', periods=52, agg='max'),
                       Market('close', freq='weeks', periods=52, agg='min'))
                    )
}


###
# Helper Functions
###
def to_sqlite_str(d: date) -> str:
    """Converts date to a sqlite str parameter (sqlite does not have a native DATE type)."""
    return d.strftime('%Y-%m-%d 00:00:00.000000')


def weeks(end: date, num: int) -> List[date]:
    """Returns list of `num` Fridays up to the supplied date (inclusive, if a Friday)"""
    freq = pd.offsets.CustomBusinessDay(n=1, weekmask='Fri')
    return list(d.date() for d in pd.date_range(end=end, periods=num, freq=freq))


def months(end: date, num: int) -> List[date]:
    """Returns list of `num` month end dates up to the supplied date (inclusive, if a month end)"""
    freq = pd.offsets.MonthEnd(n=1)
    return list(d.date() for d in pd.date_range(end=end, periods=num, freq=freq))


def calculate_t(equation_name: str, universe_name: str, t: date, equations: Dict[str, Equation]) \
        -> Iterable[Tuple[str, float]]:
    """
    Calculates the equation named `equation_name` that appears in the supplied `equations` dictionary for the
    universe named `universe_name` at date `t`.

    :name maps to an equation in `equations`
    :universe the name of a universe in the universe table
    :t an end-of-quarter date (for example, date(2019, 3, 31))
    :equations complete dictionary of equations, where any Ref refers to a name in the dictionary
    :returns an Iterable of values, one for each primary_id in the universe at date `t`
    """
    pass


if __name__ == '__main__':
    calculate_t('marketcap', 'BacktestUniverse', date(2019, 3, 31), equations)
    calculate_t('earnings', 'BacktestUniverse', date(2019, 3, 31), equations)
    calculate_t('e2p', 'BacktestUniverse', date(2019, 3, 31), equations)
    calculate_t('range_52w', 'BacktestUniverse', date(2019, 3, 31), equations)
