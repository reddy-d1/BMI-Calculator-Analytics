"""
Unit and Integration Tests for BMI Calculator Suite
Tests calculation, WHO classification, database persistence, and GUI widget initialization.
"""

import os
import tempfile
import unittest

from bmi_cli import calculate_bmi, classify_bmi
import bmi_db

class TestBMICalculator(unittest.TestCase):

    def test_calculate_bmi(self):
        """Verifies BMI calculation formula accuracy."""
        # 70 kg, 1.75 m => 70 / (1.75^2) = 22.85714...
        bmi = calculate_bmi(70, 1.75)
        self.assertAlmostEqual(bmi, 22.857142857, places=5)
        
        # 50 kg, 1.60 m => 50 / (1.60^2) = 19.53125
        bmi2 = calculate_bmi(50, 1.60)
        self.assertAlmostEqual(bmi2, 19.53125, places=5)

    def test_classify_bmi_boundaries(self):
        """Verifies WHO classification boundary thresholds."""
        self.assertEqual(classify_bmi(17.5), "Underweight")
        self.assertEqual(classify_bmi(18.49), "Underweight")
        self.assertEqual(classify_bmi(18.5), "Normal")
        self.assertEqual(classify_bmi(24.9), "Normal")
        self.assertEqual(classify_bmi(25.0), "Overweight")
        self.assertEqual(classify_bmi(29.9), "Overweight")
        self.assertEqual(classify_bmi(30.0), "Obese")
        self.assertEqual(classify_bmi(35.2), "Obese")

class TestBMIDatabase(unittest.TestCase):

    def setUp(self):
        """Creates a temporary database file for testing."""
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.db_fd)
        bmi_db.init_db(self.db_path)

    def tearDown(self):
        """Removes temporary database file."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_db_operations(self):
        """Tests table initialization, record insertion, user retrieval, and query ordering."""
        # Insert records for User Alice and User Bob
        row_id1 = bmi_db.add_record("Alice", 60, 1.65, 22.04, "Normal", self.db_path)
        row_id2 = bmi_db.add_record("Bob", 85, 1.75, 27.76, "Overweight", self.db_path)
        row_id3 = bmi_db.add_record("Alice", 62, 1.65, 22.77, "Normal", self.db_path)

        self.assertIsNotNone(row_id1)
        self.assertIsNotNone(row_id2)
        self.assertIsNotNone(row_id3)

        # Test distinct user list
        users = bmi_db.get_users(self.db_path)
        self.assertEqual(sorted(users), ["Alice", "Bob"])

        # Test user record history
        alice_records = bmi_db.get_records("Alice", self.db_path)
        self.assertEqual(len(alice_records), 2)
        self.assertEqual(alice_records[0]["weight"], 60)
        self.assertEqual(alice_records[1]["weight"], 62)
        self.assertEqual(alice_records[0]["bmi"], 22.04)

    def test_database_error_handling(self):
        """Verifies that invalid DB paths raise custom DatabaseError."""
        invalid_path = "/invalid_directory_path_12345/test.db"
        with self.assertRaises(bmi_db.DatabaseError):
            bmi_db.init_db(invalid_path)

if __name__ == "__main__":
    unittest.main()
