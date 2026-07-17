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

import core.setting_config as setting_config


def test_last_join_ip_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(setting_config, "SETTING_PATH", str(tmp_path / "user_setting.json"))

    assert setting_config.load_setting("last_join_ip") == ""

    setting_config.save_setting("last_join_ip", "192.168.1.23")
    assert setting_config.load_setting("last_join_ip") == "192.168.1.23"

    setting_config.save_setting("display_mode", "80")
    assert setting_config.load_setting("display_mode") == "80"
    assert setting_config.load_setting("last_join_ip") == "192.168.1.23"


def test_invalid_values_fall_back_to_defaults(tmp_path, monkeypatch):
    path = tmp_path / "user_setting.json"
    monkeypatch.setattr(setting_config, "SETTING_PATH", str(path))

    path.write_text('{"display_mode": "999", "last_join_ip": 42}', encoding="utf-8")
    assert setting_config.load_setting("display_mode") == "100"
    assert setting_config.load_setting("last_join_ip") == ""
