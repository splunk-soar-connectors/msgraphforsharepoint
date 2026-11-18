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
"""Helpers for returning SDK action failures with their input parameters."""

from collections.abc import Callable
from functools import wraps
from typing import Any

from soar_sdk.exceptions import ActionFailure
from soar_sdk.params import Params


def failure_result(params: Params, message: str) -> tuple[bool, str, dict[str, Any]]:
    """Build a failed SDK result that retains the submitted parameters."""
    return False, message, params.model_dump(by_alias=True)


def preserve_action_failure_params(
    action: Callable[..., Any],
) -> Callable[..., Any]:
    """Convert helper-raised ActionFailure into an SDK failure with input params."""

    @wraps(action)
    def wrapped(params: Params, *args: Any, **kwargs: Any) -> Any:
        try:
            return action(params, *args, **kwargs)
        except ActionFailure as exc:
            exc.set_action_name(action.__name__)
            return failure_result(params, str(exc))

    return wrapped
