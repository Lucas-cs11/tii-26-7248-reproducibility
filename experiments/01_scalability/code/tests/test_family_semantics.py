import unittest

from scripts.validate_family_semantics import validate_family
from src.benchmarks.families import FAMILY_SPECS


class V6FamilySemanticTests(unittest.TestCase):
    def test_all_families_have_exact_timed_witnesses_and_invariants(self):
        failures = {}
        for family in FAMILY_SPECS:
            result = validate_family(family, seed=0)
            if not result["PASS"]:
                failures[family] = result
        self.assertFalse(failures)


if __name__ == "__main__":
    unittest.main()
