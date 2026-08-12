from verify import verify


def test_certificate():
    result=verify()
    assert result['alpha']==2
    assert result['rhs'] < 0.397
    assert result['margin'] > 1.60
