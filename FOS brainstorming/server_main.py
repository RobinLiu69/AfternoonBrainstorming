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

import argparse
import time

from shared.setting import VERSION
from cards.factory import CardFactory
from server.room_server import RoomServer


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Afternoon Brainstorming dedicated room server")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=5555)
    parser.add_argument("--max-rooms", type=int, default=50)
    parser.add_argument("--room-client-cap", type=int, default=16)
    args = parser.parse_args()

    CardFactory.register_all()

    server = RoomServer(VERSION, host=args.host, port=args.port,
                        max_rooms=args.max_rooms,
                        room_client_cap=args.room_client_cap)
    server.start()
    print(f"[server_main] room server running (game version {VERSION})")
    print("[server_main] players join with an empty room number to create a room,")
    print("[server_main] or enter an existing room number to join it. Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\n[server_main] shutting down...")
    finally:
        server.stop()


if __name__ == "__main__":
    main()
