import os
import logging
import pandas as pd

from itertools import groupby
from . import utils, validation

logger = logging.getLogger(__name__)


def aggregate_cboe_monthly_data(symbols=None):
    """Aggregate daily snapshots into monthly files and validate data"""
    symbols = symbols or _get_all_listed_symbols()
    save_data_path = utils.get_save_data_path()
    scraper_dir = os.path.join(save_data_path, "cboe")
    symbols = [symbol.upper() for symbol in symbols]
    done = 0
    failed = []

    for symbol in symbols:
        daily_dir = os.path.join(scraper_dir, symbol + "_daily")

        if not os.path.exists(daily_dir):
            msg = "Error aggregating data. Dir {} not found.".format(daily_dir)
            logger.error(msg)
            continue

        monthly_dir = os.path.join(scraper_dir, symbol)
        symbol_files = [
            file for file in os.listdir(daily_dir) if file.endswith(".csv")
        ]

        for month, files in groupby(sorted(symbol_files), _monthly_grouper):
            file_names = list(files)
            daily_files = [
                os.path.join(daily_dir, name) for name in file_names
            ]

            try:
                symbol_df = utils.concatenate_files(daily_files)
            except Exception:

                msg = "Error concatenating daily files for period " + month
                logger.error(msg, exc_info=True)

                continue

            date_range = pd.to_datetime(symbol_df["quotedate"].unique())

            if not validation.validate_dates_in_month(date_range):
                today = pd.Timestamp.today()
                first_date = date_range[0]
                if first_date.year != today.year or first_date.month != today.month:
                    msg = "Some trading dates were missing for symbol {} in period {}".format(
                        symbol, month)
                    logger.error(msg)

                    failed.append(symbol)
                continue

            if not os.path.exists(monthly_dir):
                os.makedirs(monthly_dir)
                logger.debug("Symbol dir %s created", monthly_dir)

            file_name = _monthly_filename(file_names)
            monthly_file = os.path.join(monthly_dir, file_name)
            symbol_df.to_csv(monthly_file, index=False)
            if not validation.validate_aggregate_file(monthly_file,
                                                      daily_files):
                utils.remove_file(monthly_file)
                msg = "Data in {} differs from the daily files".format(
                    monthly_file)
                logger.error(msg)
                continue

            logger.debug("Saved monthly data %s", monthly_file)
            done += 1

            for file in daily_files:
                utils.remove_file(file, logger)
    return done, failed


def _get_all_listed_symbols():
    """Returns array of all listed symbols.
    http://www.cboe.com/publish/scheduledtask/mktdata/cboesymboldir2.csv
    """
    url = 'http://www.cboe.com/publish/scheduledtask/mktdata/cboesymboldir2.csv'
    symbols_df = pd.read_csv(url, skiprows=1)
    return symbols_df["Stock Symbol"].array


def _monthly_grouper(filename):
    """Returns `{year}{month}` string. Used to group files by month."""
    basename = filename.split(".")[0]
    file_date = basename.split("_")[1]
    return file_date[:-2]


def _monthly_filename(filenames):
    """Returns filename of monthly aggregate file in the form
    `{symbol}_{start_date}_to_{end_date}.csv`
    """
    sorted_files = list(sorted(filenames))
    first_file = sorted_files[0]
    last_file = sorted_files[-1]
    last_day = last_file.split(".")[0][-8:]  # Get only the date
    file_name = first_file.split(".")[0] + "_to_" + last_day + ".csv"
    return file_name
