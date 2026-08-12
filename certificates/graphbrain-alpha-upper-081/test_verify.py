from fractions import Fraction
from verify import verify


def test_carrier():
    result=verify(4)
    assert result['order']==20
    assert result['rhs']==str(Fraction(4,3))
    assert result['margin']==str(Fraction(2,3))


def test_family_threshold():
    for m in range(4,20): verify(m)
