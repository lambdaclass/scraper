import logging
import unittest
import os
import shutil
import pandas as pd

from .. import aggregation
from unittest.mock import patch

logging.disable(level=logging.CRITICAL)


class TestAggregation(unittest.TestCase):
    """Tests aggregation"""

    test_dir = os.path.join(os.getcwd(), os.path.dirname(__file__))
    test_data_path = os.path.realpath(os.path.join(test_dir, "data"))
    cboe_data_path = os.path.join(test_data_path, "cboe")
    bfr_data_path = os.path.join(cboe_data_path, "BFR_June_2019.csv")

    @classmethod
    def setUpClass(cls):
        cls.save_data_path = os.environ.get("SAVE_DATA_PATH", None)
        os.environ["SAVE_DATA_PATH"] = cls.test_data_path

    @classmethod
    def tearDownClass(cls):
        if cls.save_data_path:
            os.environ["SAVE_DATA_PATH"] = cls.save_data_path

    @patch("aggregation.utils.remove_file", return_value=None)
    def test_data_aggregation(self, mocked_remove):
        """Test data aggregation happy path"""
        aggregation.aggregate_cboe_monthly_data(["BFR"])
        aggregate_file = os.path.join(TestAggregation.cboe_data_path, "BFR",
                                      "BFR_20190701_to_20190731.csv")
        self.addCleanup(self.remove_files, os.path.dirname(aggregate_file))
        self.assertTrue(mocked_remove.called)
        if self.assertTrue(os.path.exists(aggregate_file)):
            spx_df = pd.read_csv(TestAggregation.bfr_data_path)
            aggregate_df = pd.read_csv(aggregate_file)
            self.assertTrue(spx_df.equals(aggregate_df))

    @patch("aggregation.utils.remove_file", return_value=None)
    def test_data_aggregation_missing_days(self, mocked_remove):
        """Data aggregation should fail when there are missing days"""
        done, failed = aggregation.aggregate_cboe_monthly_data(["SPX"])
        self.assertTrue(done == 0 and failed == ["SPX"])

    def remove_files(self, file_path):
        if os.path.exists(file_path):
            shutil.rmtree(file_path)


if __name__ == "__main__":
    unittest.main()
