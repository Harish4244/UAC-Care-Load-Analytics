"""
Unit and integration test suite for the UAC Analytics data pipeline and forecasting engine.
Run with:
    python -m unittest tests/test_pipeline.py
    or
    python tests/test_pipeline.py
"""

import unittest
import numpy as np
import pandas as pd

from src.pipeline import clean_raw_dataframe, derive_metrics, aggregate_data, resolve_and_load_data
from src.forecasting import ols_fit, generate_linear_forecast, generate_weekly_summary
from src.components import safe_int


class TestUACPipelines(unittest.TestCase):
    def setUp(self):
        # Create a synthetic dataset mimicking raw HHS export
        self.raw_data = pd.DataFrame({
            "Date": ["January 12, 2023", "January 13, 2023", "January 14, 2023", "January 15, 2023", "January 16, 2023", "January 17, 2023", "January 18, 2023"],
            "Children apprehended and placed in CBP custody*": ["120", "130", "110", "140", "150", "160", "170"],
            "Children in CBP custody": ["500", "520", "490", "510", "530", "550", "560"],
            "Children transferred out of CBP custody": ["100", "110", "105", "115", "120", "130", "140"],
            "Children in HHS Care": ["8,000", "8,050", "8,020", "8,100", "8,150", "8,200", "8,250"],
            "Children discharged from HHS Care": ["90", "95", "110", "100", "105", "110", "115"]
        })

    def test_clean_raw_dataframe(self):
        cleaned = clean_raw_dataframe(self.raw_data)
        self.assertEqual(len(cleaned), 7)
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(cleaned["date"]))
        self.assertEqual(cleaned["hhs_care"].iloc[0], 8000.0)
        self.assertEqual(cleaned["cbp_intake"].iloc[0], 120.0)

    def test_derive_metrics(self):
        cleaned = clean_raw_dataframe(self.raw_data)
        derived = derive_metrics(cleaned)
        
        # Check total system load = cbp_custody + hhs_care
        expected_load = derived["cbp_custody"] + derived["hhs_care"]
        pd.testing.assert_series_equal(derived["total_system_load"], expected_load, check_names=False)

        # Check net intake = transferred_out - discharged
        expected_net = derived["cbp_transferred_out"] - derived["hhs_discharged"]
        pd.testing.assert_series_equal(derived["net_daily_intake"], expected_net, check_names=False)

        # Check backlog streak is positive integer
        self.assertTrue((derived["backlog_streak"] >= 0).all())

        # Check discharge offset ratio
        self.assertTrue(derived["discharge_offset_ratio"].notna().all())

    def test_aggregation(self):
        cleaned = clean_raw_dataframe(self.raw_data)
        derived = derive_metrics(cleaned)

        daily = aggregate_data(derived, "Daily")
        self.assertEqual(len(daily), len(derived))

        weekly = aggregate_data(derived, "Weekly")
        self.assertGreater(len(weekly), 0)
        self.assertIn("total_system_load", weekly.columns)
        self.assertIn("backlog_streak", weekly.columns)

        monthly = aggregate_data(derived, "Monthly")
        self.assertGreater(len(monthly), 0)

    def test_forecasting(self):
        cleaned = clean_raw_dataframe(self.raw_data)
        derived = derive_metrics(cleaned)

        res = generate_linear_forecast(derived["date"], derived["hhs_care"], horizon_days=14, lookback_obs=7)
        self.assertIsNotNone(res)
        self.assertEqual(len(res["future_dates"]), 14)
        self.assertEqual(len(res["future_values"]), 14)
        self.assertGreaterEqual(res["r_squared"], 0.0)

        summary = generate_weekly_summary(res)
        self.assertGreater(len(summary), 0)
        self.assertIn("Avg_Forecast", summary.columns)

    def test_safe_int(self):
        self.assertEqual(safe_int(42), 42)
        self.assertEqual(safe_int("42"), 42)
        self.assertEqual(safe_int(42.8), 42)
        self.assertEqual(safe_int(np.nan, default=0), 0)
        self.assertEqual(safe_int(None, default=99), 99)
        self.assertEqual(safe_int("invalid", default=5), 5)

    def test_resolve_and_load_data(self):
        df, source = resolve_and_load_data()
        self.assertIsNotNone(df)
        self.assertGreater(len(df), 100)
        self.assertIn("total_system_load", df.columns)


if __name__ == "__main__":
    unittest.main()
