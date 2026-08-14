# V2.2 operational correction

- Supersedes operational execution of v2.1; it does not rewrite v2 or v2.1.
- Failed v2.1 run: `31811239530`, freeze commit
  `8c1046821df46d141c1c83f32cb6209262df4eb2`.
- V2.1 standing: six `SMALL_BASIS_CEGAR` round-zero assignments emitted; all
  six exact adversaries reached outer exit 124 with no terminal; downstream
  stages failed closed; zero candidates; no mathematical result.
- Cause: at the deadline during `q=19`, `queue_hash(following)` revisited the
  large insertion-order partial queue after a 368,640-state `q=17` frontier,
  leaving no bounded time to close the ledger and terminal before the outer
  kill.
- Correction: 48-second search plus six-second finalization reserve;
  incremental deterministic insertion-order queue digest; no unbounded
  post-deadline sort/hash/minimum pass.
- No deduplication, resume, exhaustion, infeasibility, or verification upgrade.
- Unchanged external cap: 60 seconds plus the existing six-second TERM-to-KILL
  grace.
- Unchanged trust boundary: exact source gate, hash-chained evidence,
  fail-closed predecessor validation, exact adversary, independent final.
