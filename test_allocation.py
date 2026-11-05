"""Visible behavioral acceptance tests. Tests do not enforce implementation text."""
import copy
import unittest
from allocation import allocate_discount


class AllocationContract(unittest.TestCase):
    def check(self, total, lines, expected):
        before = copy.deepcopy(lines)
        actual = allocate_discount(total, lines)
        self.assertIsInstance(actual, dict)
        self.assertEqual(actual, expected)
        self.assertEqual(lines, before, "caller input must not change")
        self.assertTrue(all(type(v) is int for v in actual.values()))
        self.assertEqual(sum(actual.values()), total)
        for line_id, cents in lines:
            self.assertGreaterEqual(actual[line_id], 0)
            self.assertLessEqual(actual[line_id], cents)
        return actual

    def test_incident_reconciles_101_to_100(self):
        self.check(100, [("a_book", 335), ("b_pen", 335), ("c_bag", 330)],
                   {"a_book": 34, "b_pen": 33, "c_bag": 33})

    def test_half_cent_is_not_lost(self):
        self.check(1, [("b", 1), ("a", 1)], {"a": 1, "b": 0})

    def test_rounding_does_not_create_a_cent(self):
        self.check(2, [("c", 1), ("a", 1), ("b", 1)], {"a": 1, "b": 1, "c": 0})

    def test_exact_quotas_need_no_extra_cent(self):
        self.check(6, [("a", 2), ("b", 4), ("c", 6)], {"a": 1, "b": 2, "c": 3})

    def test_remainder_outranks_alphabet(self):
        self.check(1, [("a", 1), ("z", 2)], {"a": 0, "z": 1})

    def test_two_largest_remainders_receive_one_each(self):
        self.check(2, [("a", 1), ("b", 2), ("c", 3)], {"a": 0, "b": 1, "c": 1})

    def test_remainder_outranks_line_value(self):
        self.check(4, [("a", 4), ("b", 3), ("c", 3)], {"a": 2, "b": 1, "c": 1})

    def test_tie_uses_id_not_input_position(self):
        self.check(5, [("z", 3), ("m", 3), ("a", 3)], {"a": 2, "m": 2, "z": 1})

    def test_ties_use_lexical_not_numeric_id_order(self):
        self.check(1, [("line2", 1), ("line10", 1)], {"line10": 1, "line2": 0})

    def test_zero_weight_is_retained_with_zero(self):
        self.check(1, [("zero", 0), ("b", 1), ("a", 1)], {"zero": 0, "a": 1, "b": 0})

    def test_zero_coupon_preserves_all_keys(self):
        self.check(0, [("a", 99), ("b", 0)], {"a": 0, "b": 0})

    def test_all_zero_weights_zero_coupon(self):
        self.check(0, [("a", 0), ("b", 0)], {"a": 0, "b": 0})

    def test_empty_zero_coupon(self):
        self.check(0, [], {})

    def test_full_subtotal_discount(self):
        self.check(14, [("a", 9), ("b", 5), ("c", 0)], {"a": 9, "b": 5, "c": 0})

    def test_single_line(self):
        self.check(17, [("a", 35)], {"a": 17})

    def test_tuple_and_mutable_pair_inputs(self):
        self.check(1, (["b", 1], ["a", 1]), {"a": 1, "b": 0})

    def test_input_list_and_records_unchanged(self):
        self.check(1, [["z", 1], ["a", 1]], {"a": 1, "z": 0})

    def test_permutation_invariance(self):
        import itertools
        lines = [("z", 3), ("m", 3), ("a", 3)]
        for permutation in itertools.permutations(lines):
            self.check(5, list(permutation), {"a": 2, "m": 2, "z": 1})

    def test_large_total_has_no_float_rounding(self):
        total = 10**40 + 1
        self.check(total, [("b", total), ("a", total)],
                   {"a": (total + 1)//2, "b": total//2})

    def test_hundred_digit_weights_keep_remainder_order(self):
        big = 10**100
        self.check(1, [("a", big), ("z", big+1)], {"a": 0, "z": 1})

    def test_almost_full_coupon_still_conserves(self):
        self.check(5, [("c", 2), ("b", 2), ("a", 2)], {"a": 2, "b": 2, "c": 1})

    def test_small_lines_receive_larger_remainders(self):
        self.check(3, [("a", 1), ("b", 1), ("c", 5)], {"a": 1, "b": 0, "c": 2})

    def test_one_cent_among_many_lines(self):
        lines = [(f"line{i:02d}", 1) for i in range(11)]
        self.check(1, lines, {key: int(key == "line00") for key, _ in lines})

    def test_many_remaining_cents_go_to_distinct_lines(self):
        lines = [(f"line{i:02d}", 1) for i in range(11)]
        self.check(10, lines, {key: int(key != "line10") for key, _ in lines})

    def test_near_equal_remainders_need_exact_order(self):
        big = 10**60
        self.check(1, [("a", big), ("b", big+1), ("c", big+2)],
                   {"a": 0, "b": 0, "c": 1})

    def test_zero_weight_does_not_break_equal_positive_tie(self):
        self.check(1, [("z", 1), ("a", 1), ("b", 0)], {"a": 1, "z": 0, "b": 0})

    def test_large_odd_subtotal_with_even_discount(self):
        self.check(8, [("a", 3), ("b", 3), ("c", 3)], {"a": 3, "b": 3, "c": 2})

    def test_zero_coupon_still_checks_later_bad_line(self):
        with self.assertRaises(ValueError):
            allocate_discount(0, [("a", 1), ("b", -1)])

    def test_rejects_bad_totals(self):
        for value in (-1, True, False, 1.0, "1", None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                allocate_discount(value, [("a", 10)])

    def test_rejects_bad_outer_containers(self):
        for value in (None, "a", {"a": 1}, iter([("a", 1)]), {("a", 1)}):
            with self.subTest(value=repr(value)), self.assertRaises(ValueError):
                allocate_discount(0, value)

    def test_rejects_malformed_pairs(self):
        for value in (None, "ab", [], ["a"], ["a", 1, 2], {"a": 1}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                allocate_discount(0, [value])

    def test_rejects_bad_line_identifiers(self):
        for value in ("", "UPPER", " a", "a b", "a/b", "é", "1a", "a"*65, 2, None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                allocate_discount(0, [(value, 1)])

    def test_accepts_id_boundary_and_allowed_punctuation(self):
        key = "a" * 64
        self.check(1, [(key, 1), ("a_-0", 1)], {key: 0, "a_-0": 1})

    def test_rejects_bad_eligible_amounts(self):
        for value in (-1, True, False, 1.0, "1", None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                allocate_discount(0, [("a", value)])

    def test_rejects_duplicate_identifiers_even_at_zero(self):
        with self.assertRaises(ValueError):
            allocate_discount(0, [("a", 0), ("a", 1)])

    def test_rejects_discount_above_subtotal(self):
        for total, lines in ((2, [("a", 1)]), (1, []), (1, [("a", 0)])):
            with self.subTest(total=total, lines=lines), self.assertRaises(ValueError):
                allocate_discount(total, lines)

    def test_output_is_fresh_and_calls_do_not_share_state(self):
        lines = [("a", 1), ("b", 1)]
        first = self.check(1, lines, {"a": 1, "b": 0})
        first["a"] = 99
        self.check(1, lines, {"a": 1, "b": 0})
        self.check(2, lines, {"a": 1, "b": 1})


if __name__ == "__main__":
    unittest.main()
