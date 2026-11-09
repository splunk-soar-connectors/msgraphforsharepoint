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
"""Pure input validation shared by actions with a result limit."""


def validate_limit(value: float | None) -> int | None:
    if value is None:
        return None
    if not float(value).is_integer():
        raise ValueError(
            "Please provide a valid integer value in the 'limit' action parameter"
        )
    limit = int(value)
    if limit < 0:
        raise ValueError(
            "Please provide a valid non-zero positive integer in the 'limit' action parameter"
        )
    if limit == 0:
        raise ValueError(
            "Please provide non-zero positive integer in 'limit' action parameter"
        )
    return limit
