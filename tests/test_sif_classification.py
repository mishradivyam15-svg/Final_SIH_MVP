"""Tests for deterministic SIF-potential / IOGP Life-Saving Rule classification."""

import unittest

from ai.sif_classification import classify_sif


class TestNoHazard(unittest.TestCase):
    def test_no_hazard_is_unclassified(self):
        result = classify_sif(None, None, None)
        self.assertIsNone(result["sif_potential"])
        self.assertIsNone(result["severity_potential"])
        self.assertIsNone(result["iogp_life_saving_rule"])

    def test_empty_string_hazard_is_unclassified(self):
        result = classify_sif("", "fall_from_height", None)
        self.assertIsNone(result["sif_potential"])


class TestHighEnergyWithExposure(unittest.TestCase):
    def test_working_at_height_with_exposure_is_high_severity_sif(self):
        result = classify_sif("working_at_height", "fall_from_height", None)
        self.assertEqual(result["severity_potential"], "high")
        self.assertTrue(result["sif_potential"])
        self.assertEqual(result["iogp_life_saving_rule"], "Working at Height")

    def test_high_energy_with_only_barrier_failure_is_high_severity(self):
        result = classify_sif("confined_space", None, "gas_test_not_performed")
        self.assertEqual(result["severity_potential"], "high")
        self.assertTrue(result["sif_potential"])
        self.assertEqual(result["iogp_life_saving_rule"], "Confined Space")

    def test_title_cased_display_input_is_accepted(self):
        # backend/pipeline.py title-cases fields before some callers might
        # pass them through — the classifier must not depend on casing.
        result = classify_sif("Working At Height", "Fall From Height", None)
        self.assertEqual(result["severity_potential"], "high")
        self.assertEqual(result["iogp_life_saving_rule"], "Working at Height")


class TestHighEnergyWithoutExposure(unittest.TestCase):
    def test_high_energy_hazard_alone_is_medium_severity(self):
        result = classify_sif("moving_machinery", None, None)
        self.assertEqual(result["severity_potential"], "medium")
        self.assertTrue(result["sif_potential"])


class TestLowEnergyHazard(unittest.TestCase):
    def test_slip_trip_fall_is_low_severity_non_sif(self):
        result = classify_sif("slip_trip_fall", "struck_by", "handrail_missing")
        self.assertEqual(result["severity_potential"], "low")
        self.assertFalse(result["sif_potential"])
        self.assertIsNone(result["iogp_life_saving_rule"])


class TestIogpMappingCoverage(unittest.TestCase):
    def test_unmapped_high_energy_hazards_have_no_forced_rule(self):
        for hazard in ("mobile_equipment", "moving_machinery", "excavation",
                       "falling_object", "hydrocarbon_or_process_hazard",
                       "chemical_exposure"):
            result = classify_sif(hazard, "some_exposure", None)
            self.assertIsNone(
                result["iogp_life_saving_rule"],
                msg=f"{hazard} should not be force-mapped to an IOGP rule",
            )


if __name__ == "__main__":
    unittest.main()
