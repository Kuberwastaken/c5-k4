# V1 operational-status addendum

This addendum does not modify or upgrade the frozen v1 result. In v1 no pending
candidate existed, so the independent final verifier did not run. The v1 field
`final_verifier_exit_code=0` in each cell is therefore operationally corrected
for v2 interpretation to `final_verifier_status="NOT_RUN"` and
`final_verifier_exit_code=null`. It was not a successful verification. All v1
mathematical conclusions remain unchanged: zero target assignments were
evaluated and no mathematical result was obtained.
