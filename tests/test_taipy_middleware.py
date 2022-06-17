# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from functools import wraps
from unittest.mock import MagicMock, patch

from src.taipy.rest.api.middlewares._taipy_middleware import _taipy_middleware


def mock_enterprise_middleware(request):
    def wrapper(f):
        @wraps(f)
        def inner(*args, **kwargs):
            return f(*args, **kwargs)

        return inner

    return wrapper


@patch("src.taipy.rest.api.middlewares._taipy_middleware._using_enterprise")
@patch("src.taipy.rest.api.middlewares._taipy_middleware._enterprise_middleware")
def test_enterprise_middleware_applied_when_enterprise_is_installed(
    enterprise_middleware: MagicMock, using_enterprise: MagicMock
):
    enterprise_middleware.return_value = mock_enterprise_middleware
    using_enterprise.return_value = True

    @_taipy_middleware
    def f():
        return "f"

    rv = f()
    assert rv == "f"
    using_enterprise.assert_called_once()
    enterprise_middleware.assert_called_once()


@patch("src.taipy.rest.api.middlewares._taipy_middleware._using_enterprise")
@patch("src.taipy.rest.api.middlewares._taipy_middleware._enterprise_middleware")
def test_enterprise_middleware_not_applied_when_enterprise_is_not_installed(
    enterprise_middleware: MagicMock, using_enterprise: MagicMock
):
    enterprise_middleware.return_value = mock_enterprise_middleware
    using_enterprise.return_value = False

    @_taipy_middleware
    def f():
        return "f"

    rv = f()
    assert rv == "f"
    using_enterprise.assert_called_once()
    enterprise_middleware.assert_not_called()
