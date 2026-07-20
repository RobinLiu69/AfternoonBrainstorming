# -----------------------------------------------------------------
# Afternoon Brainstorming
# Copyright (C) 2024 Robin Liu, Angus Yu / Five O'clock Shadow Studio
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
# -----------------------------------------------------------------

import pytest

import core.network.client as network_client
import core.network.token_store as token_store


@pytest.fixture(autouse=True)
def _isolate_token_store(tmp_path, monkeypatch):
    monkeypatch.setattr(token_store, "TOKEN_FILE", tmp_path / "net_tokens.json")
    monkeypatch.setattr(network_client, "load_token", lambda host, port, room: "")
