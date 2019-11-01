import os
import glob
import pandas as pd


def get_save_data_path():
    """Reads data path from environment variable `$SAVE_DATA_PATH`.
    If it is not set, defaults to `./data/scraped`.
    """

    data_dir = os.environ.get('SAVE_DATA_PATH', 'data/scraped')
    data_dir = os.path.expanduser(data_dir)

    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    return data_dir


def remove_files(data_dir, pattern, logger=None):
    """Removes files in `data_dir` that match `pattern`"""
    for file in glob.glob(os.path.join(data_dir, pattern)):
        remove_file(file, logger)


def remove_file(file, logger=None):
    os.remove(file)
    if logger:
        logger.debug("Removed file %s", file)


def concatenate_files(files):
    """Returns a dataframe of the concatenated data from `files`."""
    df_generator = (pd.read_csv(file) for file in sorted(files))
    return pd.concat(df_generator, ignore_index=True)
