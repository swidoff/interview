import operator
from dataclasses import dataclass
from datetime import date
from typing import Callable, Optional
from typing import Dict, List

import sqlite3
import pandas as pd
from sqlalchemy import *

engine = create_engine('sqlite+pysqlite:///data/interview.db', module=sqlite3)


class Equation(object):
    """Supertype of all equation objects."""
    pass


@dataclass
class Market(Equation):
    """Describes how to query a market item for stocks at time `t`."""
    item: str  # one of 'close' or 'shares'
    periods: int = 1  # matches all periods in the range [t-periods+1, t] (inclusive) according to the frequency
    freq: str = "months"  # determines the frequency of selection when periods > 1 (one of 'months' or 'weeks')
    agg: Optional[str] = None  # the aggregation (by stock) to apply if periods > 1 (None, 'min' or 'max')


@dataclass
class Fundamental(Equation):
    """Describes how to query a fundamental item for stocks at time `t`."""
    item: str
    quarters: int = 1  # matches all quarters in the range [t-quarters+1, t] (inclusive)
    agg: Optional[str] = None  # the aggregation (by stock) to apply if quarters > 1 (None or 'sum')


@dataclass
class Ref(Equation):
    """References another equation."""
    name: str  # Equation name


@dataclass
class Op(Equation):
    """Applies a binary function to the results of the operands."""
    fn: Callable
    lhs: Equation
    rhs: Equation


equations = {
    'marketcap': Op(operator.mul, Market('close'), Market('shares')),
    'earnings': Fundamental('net_income', quarters=4, agg='sum'),
    'e2p': Op(operator.truediv, Ref('earnings'), Ref('marketcap')),
    'range_52w': Op(operator.truediv,
                    Op(operator.sub,
                       Market('close'),
                       Market('close', freq='weeks', periods=52, agg='min')),
                    Op(operator.sub,
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


def calculate_t(name: str, universe: str, t: date, equations: Dict[str, Equation]):
    """
    Calculates the equation `name` that appears in the supplied `equations` dictionary for the `universe` at time `t`.

    :name maps to an equation in `equations`
    :universe the name of a universe in the universe table
    :t an end-of-quarter date (for example, date(2019, 3, 31))
    :equations complete dictionary of equations, where any Ref refers to a name in the dictionary
    :returns a vector of values, one for each of the names in the `universe` at time `t`
    """
    pass


if __name__ == '__main__':
    calculate_t('marketcap', 'BacktestUniverse', date(2019, 3, 31), equations)
    calculate_t('earnings', 'BacktestUniverse', date(2019, 3, 31), equations)
    calculate_t('e2p', 'BacktestUniverse', date(2019, 3, 31), equations)
    calculate_t('range_52w', 'BacktestUniverse', date(2019, 3, 31), equations)