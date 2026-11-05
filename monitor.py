"""Replay an authored coupon discrepancy. No external services or real payments."""
from allocation import allocate_discount

LINES = [("a_book", 335), ("b_pen", 335), ("c_bag", 330)]
COUPON_CENTS = 100
EXPECTED = {"a_book": 34, "b_pen": 33, "c_bag": 33}


def main():
    actual = allocate_discount(COUPON_CENTS, LINES)
    print(f"Coupon: {COUPON_CENTS} cents; eligible subtotal: 1000 cents")
    print(f"Line discounts: {actual}")
    print(f"Allocated: {sum(actual.values())} cents")
    print("Required policy: largest fractional remainder, then ascending line ID")
    if actual == EXPECTED and all(type(v) is int for v in actual.values()):
        print("COUPON RECONCILED: 100 cents allocated exactly")
        return 0
    print("MISMATCH: expected a_book=34, b_pen=33, c_bag=33")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
