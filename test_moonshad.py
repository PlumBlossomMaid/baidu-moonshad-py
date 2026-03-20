# MIT License
# 
# Copyright (c) 2026 PlumBlossomMaid
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

import json
import os
import unittest

from parameterized import parameterized_class

from moonshad import MoonshadSigner


# Reference: This test code follows the style of PaddlePaddle legacy tests
# https://github.com/PaddlePaddle/Paddle/tree/develop/test/legacy_test


def load_test_data():
    """Load test cases from JSON file."""
    test_file = os.path.join(os.path.dirname(__file__), "test_data.json")
    with open(test_file, "r", encoding="utf-8") as f:
        return json.load(f)


# Load test data once at module level
TEST_DATA = load_test_data()


@parameterized_class(
    ("case_id", "params", "expected_sig", "expected_shaone"),
    [(case["id"], case["params"], case["sig"], case["shaOne"]) for case in TEST_DATA],
)
class TestMoonshadSignature(unittest.TestCase):
    """
    Test cases for Baidu moonshad signature algorithm.
    Compares Python implementation with JavaScript reference results.
    """

    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all test cases."""
        cls.screen_width = 1536
        cls.screen_height = 864
        cls.signer = MoonshadSigner(
            screen_width=cls.screen_width, screen_height=cls.screen_height
        )

    def test_signature_generation(self):
        """
        Test signature generation against JS reference results.
        """
        # Fixed timestamp from test data
        fixed_tt = self.params.get("tt", 1700000000000)

        # Generate signature
        sha_one = self.signer.generate_shaone(fixed_tt)
        sig = self.signer.generate_sig(self.params)

        # Assert results match JS reference
        self.assertEqual(
            sig,
            self.expected_sig,
            f"Case {self.case_id}: sig mismatch\n"
            f"  Python: {sig}\n"
            f"  JS:     {self.expected_sig}",
        )

        self.assertEqual(
            sha_one,
            self.expected_shaone,
            f"Case {self.case_id}: shaOne mismatch\n"
            f"  Python: {sha_one}\n"
            f"  JS:     {self.expected_shaone}",
        )


class TestMoonshadSignatureBasic(unittest.TestCase):
    """
    Basic functional tests for Baidu moonshad signature algorithm.
    """

    def setUp(self):
        """Initialize test environment."""
        self.screen_width = 1536
        self.screen_height = 864
        self.signer = MoonshadSigner(
            screen_width=self.screen_width, screen_height=self.screen_height
        )

    def test_screen_resolution_consistency(self):
        """Verify screen resolution is correctly set."""
        self.assertEqual(self.signer.screen_width, self.screen_width)
        self.assertEqual(self.signer.screen_height, self.screen_height)

    def test_version_key_selection(self):
        """Test version key selection based on timestamp."""
        # Test known timestamps
        test_cases = [
            (1700000000, "moonshad5moonsh2"),   # day 19675, index 0
            (1700000000 + 86400, "moonshad3moonsh0"),  # day 19676, index 1
            (1700000000 + 86400 * 2, "moonshad8moonsh6"),  # day 19677, index 2
            (1700000000 + 86400 * 3, "moonshad0moonsh1"),  # day 19678, index 3
            (1700000000 + 86400 * 4, "moonshad1moonsh9"),  # day 19679, index 4
        ]

        for timestamp, expected_key in test_cases:
            key = self.signer._get_version_key(timestamp)
            self.assertEqual(
                key,
                expected_key,
                f"Timestamp {timestamp}: expected {expected_key}, got {key}",
            )

    def test_excluded_params(self):
        """Verify that excluded parameters are not included in signature."""
        params = {
            "sig": "test_sig",
            "traceid": "test_trace",
            "callback": "test_callback",
            "elapsed": "100",
            "shaOne": "test_sha",
            "normal_param": "value",
        }

        sign_str = self.signer._prepare_sign_string(params)

        # Excluded params should not appear in sign string
        self.assertNotIn("sig=", sign_str)
        self.assertNotIn("traceid=", sign_str)
        self.assertNotIn("callback=", sign_str)
        self.assertNotIn("elapsed=", sign_str)
        self.assertNotIn("shaOne=", sign_str)
        self.assertIn("normal_param=value", sign_str)

    def test_empty_param_handling(self):
        """Test that empty string parameters are preserved in signature."""
        params = {
            "empty_param": "",
            "normal_param": "value",
        }

        sign_str = self.signer._prepare_sign_string(params)

        # Empty param should be included as "empty_param="
        self.assertIn("empty_param=", sign_str)
        self.assertIn("normal_param=value", sign_str)

    def test_interleave_strings(self):
        """Test the string interleaving algorithm."""
        str1 = "abcde"
        str2 = "123"

        result = self.signer._interleave_strings(str1, str2)
        expected = "a1b2c3de"

        self.assertEqual(result, expected)

        # Test when second string is longer
        str1 = "ab"
        str2 = "12345"
        result = self.signer._interleave_strings(str1, str2)
        expected = "a1b2345"
        self.assertEqual(result, expected)

    def test_screen_mapping(self):
        """Test screen resolution to string mapping."""
        original_width = self.signer.screen_width
        original_height = self.signer.screen_height

        self.signer.screen_width = 1920
        self.signer.screen_height = 1080
        mapped = self.signer._generate_screen_string()

        # Correct mapping: 19201080 -> 1,9,2,0,1,0,8,0 -> t,n,r,s,t,s,m,s
        expected = "tnrstsms"
        self.assertEqual(mapped, expected)

        # Restore
        self.signer.screen_width = original_width
        self.signer.screen_height = original_height

    def test_signature_deterministic(self):
        """
        Test signature generation with static input parameters.
        This test ensures deterministic output for fixed inputs.
        """
        # Fixed input parameters
        params = {
            "test_param_1": "value1",
            "test_param_2": "value2",
            "test_number": 12345,
            "test_empty": "",
        }

        # Fixed timestamp
        fixed_tt = 1700000000000

        # Generate signature twice to ensure consistency
        sha_one_1 = self.signer.generate_shaone(fixed_tt)
        sha_one_2 = self.signer.generate_shaone(fixed_tt)
        sig_1 = self.signer.generate_sig(params)
        sig_2 = self.signer.generate_sig(params)

        self.assertEqual(sha_one_1, sha_one_2)
        self.assertEqual(sig_1, sig_2)


if __name__ == "__main__":
    unittest.main()