import os
import sys
import unittest
from io import BytesIO
from unittest.mock import patch

from openpyxl import load_workbook

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "VRM"))

import app as vrm_app


class ExportRouteTest(unittest.TestCase):
    def setUp(self):
        self.client = vrm_app.app.test_client()

    def test_export_returns_excel_workbook(self):
        sample_kwh = {
            "Gc": [[1_700_000_000_000, 2.0]],
            "Pc": [[1_700_000_000_000, 4.0]],
            "Bc": [[1_700_000_000_000, 1.0]],
            "Pb": [[1_700_000_000_000, 0.0]],
            "Gb": [[1_700_000_000_000, 0.0]],
            "kwh": [[1_700_000_000_000, 5.0]],
        }
        sample_evcs = {"evE": [[1_700_000_000_000, 3.0]]}
        sample_battery = {"bs": [[1_700_000_000_000, 80.0]]}

        with patch.object(vrm_app, "get_live_records", return_value=(sample_kwh, sample_evcs, sample_battery)):
            response = self.client.get("/export?startdate=2025-01-01&enddate=2025-01-02&interval=days&cost_per_kwh=0.5")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.mimetype,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        self.assertIn("attachment; filename=", response.headers["Content-Disposition"])

        workbook = load_workbook(BytesIO(response.data))
        self.assertEqual(workbook.sheetnames, ["Summary", "Raw KWH", "Raw EVCS", "Raw Battery Stats"])


if __name__ == "__main__":
    unittest.main()
