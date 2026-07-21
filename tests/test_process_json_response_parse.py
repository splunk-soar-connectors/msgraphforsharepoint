# Copyright (c) 2026 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Tests for the parse boundary in _process_json_response.

Regression for PAPP-37752: MS Graph returns bare Infinity/-Infinity/NaN tokens in
number-column metadata for unbounded columns. The connector previously called
requests' Response.json(), whose backend (simplejson) RAISES on those tokens, so the
_sanitize_non_finite_floats() pass was never reached and 'get list' failed at parse.

The fix parses raw response text with the stdlib json module using
parse_constant=lambda _: None (neutralizes the bare tokens at decode time), then still
runs _sanitize_non_finite_floats() to catch overflow numeric literals (e.g. 1e400) that
decode to inf but are not covered by parse_constant.

These tests reimplement the parse+sanitize logic standalone (matching the style of the
other test modules) so they run without the full phantom SDK installed.
"""

import json
import math

import pytest  # pylint: disable=import-error


def _sanitize_non_finite_floats(data):
    if isinstance(data, dict):
        return {k: _sanitize_non_finite_floats(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_sanitize_non_finite_floats(item) for item in data]
    if isinstance(data, float) and not math.isfinite(data):
        return None
    return data


def _parse_response_text(text):
    """Mirror of _process_json_response's parse boundary after the fix."""
    resp_json = json.loads(text, parse_constant=lambda _constant: None)
    return _sanitize_non_finite_floats(resp_json)


# The actual MS Graph 'get list' + expand=columns payload shape that triggers the bug.
MS_GRAPH_LIST_TEXT = (
    '{"displayName": "Test List",'
    ' "columns": [{"name": "Amount",'
    ' "number": {"decimalPlaces": "automatic", "displayAs": "number",'
    ' "maximum": Infinity, "minimum": -Infinity}}],'
    ' "items": [{"fields": {"Amount": 42.0}}]}'
)


class TestParseBoundary:
    def test_bare_infinity_token_neutralized_not_raised(self):
        """The core regression: bare Infinity tokens must parse to None, not raise."""
        result = _parse_response_text('{"maximum": Infinity, "minimum": -Infinity, "n": NaN}')
        assert result == {"maximum": None, "minimum": None, "n": None}

    def test_full_get_list_column_metadata(self):
        result = _parse_response_text(MS_GRAPH_LIST_TEXT)
        number = result["columns"][0]["number"]
        assert number["maximum"] is None
        assert number["minimum"] is None
        assert number["decimalPlaces"] == "automatic"
        assert result["items"][0]["fields"]["Amount"] == 42.0

    def test_result_is_valid_json_after_parse(self):
        """Re-serializing the parsed result must not reintroduce a non-JSON token."""
        result = _parse_response_text(MS_GRAPH_LIST_TEXT)
        json_str = json.dumps(result)
        assert "Infinity" not in json_str
        assert "NaN" not in json_str

    def test_overflow_numeric_literal_caught_by_sanitize_pass(self):
        """parse_constant does NOT fire for 1e400 (a numeric literal, not a constant);
        the _sanitize_non_finite_floats pass must catch the resulting inf."""
        # parse_constant alone leaves inf in place ...
        raw = json.loads('{"maximum": 1e400}', parse_constant=lambda _c: None)
        assert math.isinf(raw["maximum"])
        # ... the full parse+sanitize path neutralizes it.
        result = _parse_response_text('{"maximum": 1e400}')
        assert result == {"maximum": None}

    def test_normal_values_preserved(self):
        text = '{"maximum": 100.5, "minimum": 0, "name": "col", "flag": true, "empty": null}'
        result = _parse_response_text(text)
        assert result == {"maximum": 100.5, "minimum": 0, "name": "col", "flag": True, "empty": None}

    def test_invalid_json_still_raises(self):
        """Genuinely malformed JSON must still raise (caught by the connector's except)."""
        with pytest.raises(ValueError):
            _parse_response_text('{"maximum": }')


class TestSimplejsonWouldHaveRaised:
    """Documents WHY the fix is needed: requests' simplejson backend raises on the token,
    which is why the previous r.json()-based code never reached the sanitizer."""

    def test_simplejson_raises_on_bare_infinity(self):
        try:
            import simplejson
        except ImportError:
            pytest.skip("simplejson not installed")
        with pytest.raises(simplejson.JSONDecodeError):
            simplejson.loads('{"maximum": Infinity}')

    def test_stdlib_json_parses_bare_infinity_to_inf(self):
        """stdlib json (used by the fix) parses the token; parse_constant lets us intercept it."""
        assert math.isinf(json.loads('{"maximum": Infinity}')["maximum"])
