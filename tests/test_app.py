"""
Integration test for Streamlit app execution.
Ensures streamlit_app.py compiles, runs, and renders all tabs without raising exceptions.
"""

import os
import unittest
from streamlit.testing.v1 import AppTest


class TestStreamlitApp(unittest.TestCase):
    def test_app_run_without_exceptions(self):
        app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "streamlit_app.py"))
        at = AppTest.from_file(app_path, default_timeout=30)
        at.run()
        self.assertFalse(at.exception, f"App raised exceptions: {at.exception}")
        # Verify that tabs rendered
        self.assertGreater(len(at.tabs), 0)


if __name__ == "__main__":
    unittest.main()
