from dataclasses import dataclass
from typing import Optional, Callable, Iterable

_FRACTION_SLASH = '\u2044'


@dataclass(frozen=True, repr=False)
class VulgarFraction:
    """
    >>> str(VulgarFraction(-1234567890, -1234567890))
    '⁻¹²³⁴⁵⁶⁷⁸⁹⁰⁄₋₁₂₃₄₅₆₇₈₉₀'
    >>> str(VulgarFraction(3, 4))
    '¾'
    """
    nominator: int
    denominator: int

    def __repr__(self):
        return _single_character_fraction(self) or _format_vulgar_fraction(self.nominator, self.denominator)


def _format_vulgar_fraction(nominator: int, denominator: int) -> str:
    return f'{_format_number(nominator, _superscript)}{_FRACTION_SLASH}{_format_number(denominator, _subscript)}'


def _format_number(n: int, format_digit: Callable[[str], str]) -> str:
    return ''.join((format_digit(digit) for digit in _digits(n)))


def _digits(n: int) -> Iterable[str]:
    return str(n)


def _superscript(character: str) -> str:
    match character:
        case '-':
            return '⁻'
        case '0':
            return '⁰'
        case '1':
            return '¹'
        case '2':
            return '²'
        case '3':
            return '³'
        case '4':
            return '⁴'
        case '5':
            return '⁵'
        case '6':
            return '⁶'
        case '7':
            return '⁷'
        case '8':
            return '⁸'
        case '9':
            return '⁹'


def _subscript(character: str) -> str:
    match character:
        case '-':
            return '₋'
        case '0':
            return '₀'
        case '1':
            return '₁'
        case '2':
            return '₂'
        case '3':
            return '₃'
        case '4':
            return '₄'
        case '5':
            return '₅'
        case '6':
            return '₆'
        case '7':
            return '₇'
        case '8':
            return '₈'
        case '9':
            return '₉'


def _single_character_fraction(fraction: VulgarFraction) -> Optional[str]:
    match (fraction.nominator, fraction.denominator):
        case (1, 4):
            return '\u00bc'
        case (1, 2):
            return '\u00bd'
        case (3, 4):
            return '\u00be'
        case (1, 7):
            return '\u2150'
        case (1, 9):
            return '\u2151'
        case (1, 10):
            return '\u2152'
        case (1, 3):
            return '\u2153'
        case (2, 3):
            return '\u2154'
        case (1, 5):
            return '\u2155'
        case (2, 5):
            return '\u2156'
        case (3, 5):
            return '\u2157'
        case (4, 5):
            return '\u2158'
        case (1, 6):
            return '\u2159'
        case (5, 6):
            return '\u215a'
        case (1, 8):
            return '\u215b'
        case (3, 8):
            return '\u215c'
        case (5, 8):
            return '\u215d'
        case (7, 8):
            return '\u215e'
        case (0, 3):
            return '\u2189'
        case _:
            return None


if __name__ == '__main__':
    import doctest
    doctest.testmod()
