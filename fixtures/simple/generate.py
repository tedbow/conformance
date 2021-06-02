"""
Generates a simple fixture with a single, valid target file.
"""

from builder import FixtureBuilder

FixtureBuilder().create_target('testtarget.txt').publish()
