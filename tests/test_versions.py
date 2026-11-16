"""Regression tests for Cargo requirements and SemVer precedence."""

import unittest

from cargograph.config import AppError
from cargograph.versions import Version, matches


class VersionTests(unittest.TestCase):
    """Check stable, prerelease, wildcard and partial version semantics."""

    def test_requirements(self):
        """Match representative requirements used by the Cargo index."""
        cases = [
            ('1.9.0', '1.2', True), ('2.0.0', '^1.2', False),
            ('0.2.9', '^0.2.3', True), ('0.3.0', '^0.2.3', False),
            ('0.0.4', '^0.0.3', False), ('0.9.0', '^0', True),
            ('1.3.0', '~1.2.3', False), ('1.2.9', '~1.2', True),
            ('1.4.0', '>=1.2, <2', True), ('2.0.0', '<2', False),
            ('2.1.0', '*', True), ('2.1.0', '1.*', False),
            ('1.2.9', '1.2.x', True), ('1.3.0', '=1.2', False),
            ('1.2.9', '<=1.2', True), ('1.9.0', '>1', False),
            ('2.0.0', '>1', True), ('1.2.3', '=1.2.3', True),
            ('1.2.4', '=1.2.3', False), ('1.2.3-rc.1', '*', False),
            ('1.2.3-rc.2', '>=1.2.3-rc.1, <2', True),
            ('1.2.4-rc.1', '>=1.2.3-rc.1', False),
        ]
        for version, requirement, expected in cases:
            with self.subTest(version=version, requirement=requirement):
                self.assertEqual(matches(version, requirement), expected)

    def test_order(self):
        """Numeric prerelease components sort numerically before text."""
        order = ['1.0.0-alpha', '1.0.0-alpha.2', '1.0.0-alpha.10',
                 '1.0.0-beta', '1.0.0', '1.0.1']
        self.assertEqual(sorted(order, key=Version.parse), order)
        self.assertEqual(Version.parse('1.0.0+a'), Version.parse('1.0.0+b'))

    def test_invalid(self):
        """Reject malformed exact versions and unsupported constraints."""
        for value in ['01.0.0', '1.0', '1.0.0-01', 'a.b.c']:
            with self.subTest(value=value), self.assertRaises(AppError):
                Version.parse(value)
        for value in ['1 || 2', '>=1.*', '', '1.2.3.4', '1.01']:
            with self.subTest(value=value), self.assertRaises(AppError):
                matches('1.0.0', value)
