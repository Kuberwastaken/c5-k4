# V3 observed-design correction

- Input run: `31812806288`, campaign commit
  `74f904b66edcb191f2172eaf04c303b438648b74`.
- V2.2 standing: six small-basis proposals; least cheap-seed misses
  `3,5,29,6,6,22`; six exact deadline receipts; zero mathematical results.
- V3 correction: optimize and durably replay the exact least missed exponent
  before any proposal can leave construction.
- Nonredundant round starts: 192, 256, and 320 active rows.
- Trust-boundary correction: v3 is constructor/diagnostic-only. It contains no
  target-verification jobs and cannot promote a seed proposal.
- The future exact objective is bounded `1 <= x < n`, not finite full-period
  coverage. That backend is intentionally outside this freeze.
