import unittest

from server.routes.ngo import _build_specialty_counts, _check_facility_has_capability, _format_specialty_name


class NgoHelperTests(unittest.TestCase):
    def test_build_specialty_counts_uses_each_specialty_once_per_facility(self):
        specialty_values = [
            '["cardiology","urology","cardiology"]',
            '["neurology"]',
            None,
        ]

        counts = _build_specialty_counts(specialty_values)

        self.assertEqual(counts["cardiology"], 1)
        self.assertEqual(counts["urology"], 1)
        self.assertEqual(counts["neurology"], 1)

    def test_check_facility_has_capability_matches_keywords_in_specialties_and_description(self):
        row = {
            "specialties": '["emergencyMedicine","pediatrics"]',
            "capability": '["cardiology"]',
            "description": "24/7 emergency services and trauma care available.",
        }

        self.assertTrue(_check_facility_has_capability(row, "emergency"))
        self.assertTrue(_check_facility_has_capability(row, "pediatrics"))
        self.assertFalse(_check_facility_has_capability(row, "maternity"))

    def test_format_specialty_name_creates_readable_labels(self):
        self.assertEqual(_format_specialty_name("emergencyMedicine"), "Emergency Medicine")
        self.assertEqual(_format_specialty_name("gynecologyAndObstetrics"), "Gynecology & Obstetrics")
        self.assertEqual(_format_specialty_name("urology"), "Urology")


if __name__ == "__main__":
    unittest.main()
