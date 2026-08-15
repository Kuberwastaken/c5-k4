# Invalid pre-activation gate timeout

- Attempted commit: `ee46d10fefcdfa6e4f6d58d614e86f96e16b97bb`
- Classification: `INVALID_PRE_EVALUATION_GATE_TIMEOUT`
- Boundary: the authenticated target-free source/status gate exceeded its
  frozen 60-second external cap while scanning open-PR changed files
  sequentially.
- Target rows evaluated: `0`
- Attestation emitted: no
- Consequence: this local attempt is invalid pre-activation evidence and says
  nothing about the mathematical target. No activation token existed or was
  used.
