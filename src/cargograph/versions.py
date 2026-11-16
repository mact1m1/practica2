"""SemVer ordering and Cargo version requirements without dependencies."""

from dataclasses import dataclass
from functools import total_ordering
import re

from .config import AppError


@total_ordering
@dataclass(frozen=True)
class Version:
    """Semantic version; build metadata does not change precedence."""

    core: tuple
    pre: tuple = ()

    @classmethod
    def parse(cls, text):
        """Parse an exact SemVer and reject leading zeroes."""
        match = re.fullmatch(
            r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
            r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
            r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?", text
        )
        if not match:
            raise AppError(f"Invalid SemVer: {text}")
        pre = tuple((match[4] or "").split('.')) if match[4] else ()
        if any(p.isdigit() and len(p) > 1 and p[0] == '0' for p in pre):
            raise AppError(f"Invalid prerelease: {text}")
        return cls(tuple(int(match[i]) for i in range(1, 4)), pre)

    def __lt__(self, other):
        """Compare core numbers, then numeric/text prerelease components."""
        if self.core != other.core:
            return self.core < other.core
        if not self.pre or not other.pre:
            return bool(self.pre) and not other.pre
        left = tuple(pre_key(part) for part in self.pre)
        right = tuple(pre_key(part) for part in other.pre)
        return left < right


def pre_key(part):
    """Place numeric prerelease identifiers before textual identifiers."""
    return (0, int(part)) if part.isdigit() else (1, part)


def requirement_part(text):
    """Return an operator, padded version and specified core length."""
    match = re.fullmatch(r"(>=|<=|>|<|=|\^|~)?\s*(\S+)", text.strip())
    if not match:
        raise AppError(f"Unsupported Cargo requirement: {text}")
    operator, number = match.groups()
    pieces = number.split('-')[0].split('+')[0].split('.')
    wild = next((i for i, p in enumerate(pieces) if p in '*xX'), None)
    if wild is not None:
        if operator or any(p not in '*xX' for p in pieces[wild:]):
            raise AppError(f"Invalid wildcard requirement: {text}")
        pieces = pieces[:wild]
        operator = '*'
    length = len(pieces)
    if length > 3:
        raise AppError(f"Invalid version requirement: {text}")
    padded = '.'.join(pieces + ['0'] * (3 - length))
    if length == 3:
        padded = number
    return operator or '^', Version.parse(padded), length


def upper_bound(base, index):
    """Increment one component and zero subsequent components."""
    numbers = list(base.core)
    numbers[index] += 1
    numbers[index + 1:] = [0] * (2 - index)
    return Version(tuple(numbers))


def accepts(version, operator, base, length):
    """Evaluate one Cargo comparator, including partial comparisons."""
    if operator == '*':
        return not length or base <= version < upper_bound(base, length - 1)
    if operator == '^':
        nonzero = next((i for i, n in enumerate(base.core) if n), None)
        index = min(nonzero if nonzero is not None else 2, length - 1)
        return base <= version < upper_bound(base, index)
    if operator == '~':
        return base <= version < upper_bound(base, min(length - 1, 1))
    return comparison(version, operator, base, length)


def comparison(version, operator, base, length):
    """Evaluate equality and ordered bounds, including partial versions."""
    if operator == '=':
        if length < 3:
            return base <= version < upper_bound(base, length - 1)
        return version == base
    if operator == '>':
        if length < 3:
            return version >= upper_bound(base, length - 1)
        return version > base
    if operator == '<=':
        if length < 3:
            return version < upper_bound(base, length - 1)
        return version <= base
    if operator == '>=':
        return version >= base
    if operator == '<':
        return version < base
    raise AppError(f"Unsupported comparator: {operator}")


def matches(text, requirement):
    """Match comma intersections; prereleases require an explicit core."""
    version = Version.parse(text)
    clauses = [requirement_part(item) for item in requirement.split(',')]
    if version.pre and not any(
        base.pre and base.core == version.core for _, base, _ in clauses
    ):
        return False
    return all(accepts(version, *clause) for clause in clauses)
