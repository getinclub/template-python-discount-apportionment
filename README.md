# The Discount Split That Created a Cent

**Python backend · Medium · about 12 minutes**

Checkout applies a **100-cent coupon** to three eligible lines worth 335, 335
and 330 cents. Each line rounds its own discount. The invoice now says the
coupon was worth **101 cents**. A one-cent coupon can disappear the same way.

Repair **only `allocate_discount()` in `allocation.py`**. Validation is already
implemented. Keep the function signature, validation helper, tests and monitor.

## Start here

```sh
python -m pip install -r requirements.txt
python monitor.py
python -m pytest -v
```

Use Python 3.12. Runtime code uses the standard library; test tools are pinned.
The unmodified starter is intentionally wrong, so tests and the monitor start
red. The monitor is an authored fixture, not a live checkout or payment request.

## Required allocation policy

`allocate_discount(total_cents, lines)` returns a **new dict** with every line ID
mapped to its integer discount, including zero-value lines. Dict iteration order
is not part of the contract. All arithmetic must be exact, without floating-point
quotas or conversions to floats.

1. Let `subtotal` be the sum of eligible line amounts.
2. The exact quota for a line is `total_cents * eligible_cents / subtotal`.
   Allocate the whole-number part of each quota first.
3. Give the unallocated cents to the lines with the **largest fractional
   remainders**, at most one extra cent per line.
4. If remainders tie, use the line ID in **ascending Python string order**.
   IDs are restricted to ASCII; `line10` precedes `line2`. Input order does not
   resolve ties.

Example: the quotas for `a_book`, `b_pen`, `c_bag` are 33.5, 33.5 and 33 cents.
Their whole parts total 99. The one remaining cent goes to `a_book`, so the
result is `{'a_book': 34, 'b_pen': 33, 'c_bag': 33}` and totals exactly 100.

For a zero subtotal, the only valid coupon is zero: return all given IDs with
zero. Empty lines with a zero coupon return `{}`. A positive discount may not
exceed the eligible subtotal. Zero-weight lines must never receive a cent.

The largest-remainder rule is this fictional checkout's specified policy, not a
universal definition of fairness or a tax, refund or accounting rule. Changing
coupon totals can change which lines receive extra cents; monotonic per-line
allocation across different totals is not promised.

## Input and error contract

- `total_cents`: nonnegative Python `int`, excluding `bool`.
- `lines`: a `list` or `tuple` of 2-element lists/tuples
  `(line_id, eligible_cents)`. Iterators, dicts and sets are not accepted.
- `line_id`: unique string matching `[a-z][a-z0-9_-]{0,63}`.
- `eligible_cents`: nonnegative Python `int`, excluding `bool`.
- Invalid input raises `ValueError`, including a discount larger than subtotal.
  The whole input must be validated even when the coupon is zero.
- Do not mutate, sort in place, normalize, drop or merge caller records.
- Return actual `int` values, not floats or booleans. Repeated calls are independent.

Amounts can exceed floating-point precision. Aim for **O(n log n)** comparisons
and **O(n)** additional records for n lines; do not loop over the coupon's cents
or allocate an array sized by the amount. Integer arithmetic also costs work
according to the numbers' bit lengths. A very large amount should not introduce
an equally large number of loop iterations.

## What a passing PR demonstrates

- The authored discrepancy reconciles from 101 allocated cents to exactly 100.
- Conservation alone is insufficient: remainder ranking and tie order match policy.
- Empty/zero inputs, large integers, permutations and invalid requests behave as
  documented, with no input mutation.
- Tests and `python monitor.py` pass. Open a PR against `main` and explain why
  independently rounding every line cannot guarantee the total.

### Hints, if needed

1. The remainder represents what was lost when a quota was rounded down.
2. Every quota has the same denominator. You can compare remainder numerators.
3. `divmod()` gives a whole part and remainder using integers. Sort a copy.

### Scope

This is a single-process pure-function exercise. It does not implement checkout,
refunds, currency conversion, tax treatment, payment idempotency or ledger posting.
Visible tests are learning feedback, not a tamper-proof assessment boundary.
