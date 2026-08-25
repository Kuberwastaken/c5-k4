# A113250 / A113252 / A113255 — audits (odd-index squares family, m = 4, 6, 9)

**Class: HOLD_BOUNDED x3 BUT SKIP_CLAIMS (contamination). Gates: a ✓, b ✓,
c ✓, d ✗ excluded.**

KitaKen1 repo `oeis-a113249-family-square-terms-lean` (pushed 2026-08-15,
one day before inventory freeze) covers the A113249 family that these three
specialize => no fresh claims from this lane.

Verification record (exact integer_nthroot): odd-index terms of all three
recurrences are perfect squares through index 200:
- A113250: a(n+4) = -4a(n+1... [-4,-,-,64,256] signature; init -1,4,32,64
- A113252: -4/-,144,1296; init -1,4,92,784
- A113255: -4/-,324,6561; init -1,4,227,5329
Head terms match each file's tests. `scripts/a113250_family.py`,
`a113250_run1.log`.
