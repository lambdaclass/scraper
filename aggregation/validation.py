import logging
import pandas as pd
import pandas_market_calendars as mcal
from . import utils

logger = logging.getLogger(__name__)


def validate_dates_in_month(date_range):
    """Compares `date_range` (month) with NYSE trading calendar.
    Returns `True` if there are no missing days.
    """
    # NYSE and CBOE have the same trading calendar
    # https://www.nyse.com/markets/hours-calendars
    # http://cfe.cboe.com/about-cfe/holiday-calendar
    nyse = mcal.get_calendar("NYSE")
    first_date = date_range[0]
    period = pd.Period(year=first_date.year, month=first_date.month, freq="M")
    trading_days = nyse.valid_days(start_date=period.start_time,
                                   end_date=period.end_time)

    # Remove timezone info
    trading_days = trading_days.tz_convert(tz=None)
    missing_days = trading_days.difference(date_range)
    if not missing_days.empty:
        logger.error("Error validating monthly dates. Missing: %s",
                     missing_days)
    return missing_days.empty


def validate_aggregate_file(aggregate_file, daily_files):
    """Compares `aggregate_file` with the data from `daily_files`."""
    aggregate_df = pd.read_csv(aggregate_file)
    recreated_df = utils.concatenate_files(daily_files)
    return aggregate_df.equals(recreated_df)
