"""Integer-cent allocation for the authored checkout simulation.

Edit only allocate_discount(). The supplied validation helper is complete.
"""
import re


def allocate_discount(total_cents, lines):
    """Return one exact integer discount per line; see README for the policy."""
    subtotal = _validate_inputs(total_cents, lines)
    if subtotal == 0:
        return {line_id: 0 for line_id, _ in lines}
    # BUG: independently rounded amounts do not necessarily conserve the coupon.
    return {line_id: round(total_cents * cents / subtotal)
            for line_id, cents in lines}


def _validate_inputs(total_cents, lines):
    """Validate the entire request before any allocation, including zero totals."""
    if type(total_cents) is not int or total_cents < 0:
        raise ValueError("total_cents must be a nonnegative integer, not bool")
    if not isinstance(lines, (list, tuple)):
        raise ValueError("lines must be a list or tuple of (line_id, eligible_cents)")
    seen = set()
    subtotal = 0
    for line in lines:
        if not isinstance(line, (list, tuple)) or len(line) != 2:
            raise ValueError("each line must be a pair")
        line_id, eligible_cents = line
        if (not isinstance(line_id, str)
                or re.fullmatch(r"[a-z][a-z0-9_-]{0,63}", line_id) is None):
            raise ValueError("line_id must be a lowercase ASCII token, 1 to 64 characters")
        if line_id in seen:
            raise ValueError("line_id must be unique")
        seen.add(line_id)
        if type(eligible_cents) is not int or eligible_cents < 0:
            raise ValueError("eligible_cents must be a nonnegative integer, not bool")
        subtotal += eligible_cents
    if total_cents > subtotal:
        raise ValueError("discount cannot exceed the eligible subtotal")
    return subtotal
