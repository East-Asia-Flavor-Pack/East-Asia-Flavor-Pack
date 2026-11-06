"""Small, comment/string-aware reader for journal migration and source checks.

This preserves source spans and repeated fields; it is not a Jomini interpreter.
Only direct assignments are read. Nested bodies remain untouched source text.
"""
from dataclasses import dataclass
import re


TOKEN = re.compile(r'#[^\n]*|"(?:\\.|[^"\\])*"|\?=|!=|>=|<=|[{}=<>]|[^\s{}=<>!?"#]+')


@dataclass(frozen=True)
class Entry:
    key: str
    op: str
    start: int
    end: int
    value_start: int
    value_end: int

    def value(self, text):
        return text[self.value_start:self.value_end]

    def body(self, text):
        value = self.value(text)
        assert value.startswith('{') and value.endswith('}'), self.key
        return value[1:-1]


def tokens(text):
    return [token for token in TOKEN.finditer(text) if not token[0].startswith('#')]


def normalized(text):
    return tuple(token[0] for token in tokens(text))


def entries(text):
    """Read direct assignments, accepting literal lists inside their value blocks."""
    result = []
    ts = tokens(text)
    i = 0
    while i < len(ts):
        assert i + 2 < len(ts), ('Incomplete assignment', text[ts[i].start():])
        key, op, value = ts[i:i + 3]
        assert op[0] in ('=', '?=', '!=', '>', '<', '>=', '<='), (key[0], op[0])
        j = i + 2
        # Color values can be written as rgb { ... } or hsv { ... }.
        if value[0] in ('rgb', 'hsv', 'hsv360') and j + 1 < len(ts) and ts[j + 1][0] == '{':
            j += 1
        if ts[j][0] == '{':
            depth = 1
            while depth:
                j += 1
                assert j < len(ts), ('Unclosed block', key[0])
                depth += (ts[j][0] == '{') - (ts[j][0] == '}')
        assert ts[j][0] != '}' or j > i + 2, ('Unexpected brace', key[0])
        result.append(Entry(key[0], op[0], key.start(), ts[j].end(), value.start(), ts[j].end()))
        i = j + 1
    return result


def named(text, key):
    matches = [entry for entry in entries(text) if entry.key.split(':')[-1] == key]
    assert len(matches) == 1, (key, len(matches))
    return matches[0]


def outcome(text, kind):
    """Select a migrated outcome by flags/color for existing lifecycle tests."""
    matches = []
    for entry in entries(text):
        if entry.key != 'outcome':
            continue
        body = entry.body(text)
        fields = {field.key: field.value(body) for field in entries(body)}
        flags = normalized(fields.get('flags', '{}'))
        actual = ('invalid' if 'invalid_outcome' in flags else
                  'timeout' if 'timeout' in flags else
                  'complete' if fields.get('color') == '"gold_positive"' else 'fail')
        if actual == kind:
            matches.append(body)
    assert len(matches) == 1, (kind, len(matches))
    return matches[0]
