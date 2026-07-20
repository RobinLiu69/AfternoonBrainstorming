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

from __future__ import annotations
import json
from dataclasses import dataclass
from typing import Any, Literal, Optional, TYPE_CHECKING

import pygame

from utils.controls import key_pressed

if TYPE_CHECKING:
    from screens.draft.exhibit_registry import ExhibitRegistry


DraftActionType = Literal[
    "add_card",
    "remove_card",
    "remove_last_card",
    "advance_phase",
    "page_next",
    "page_prev",
    "toggle_hint",
    "confirm_start",
    "quit",
    "change_index",
    "index_next",
    "index_prev",
]


@dataclass
class DraftAction:
    player: str
    action_type: DraftActionType
    card_name: Optional[str] = None
    data: Any = None

    def to_json(self) -> str:
        return json.dumps(self.__dict__)

    @classmethod
    def from_json(cls, s: str) -> "DraftAction":
        return cls(**json.loads(s))


@dataclass
class DraftResult:
    success:  bool
    message:  str  = ""
    quit: bool = False


SPECTATOR_ALLOWED: tuple[str, ...] = ("page_next", "page_prev", "toggle_hint", "quit",
                                      "change_index", "index_next", "index_prev")


def collect_draft_actions(current_editor: str, page: int, index: int, registry: ExhibitRegistry,
                          mouse_board_x: Optional[int], mouse_board_y: Optional[int]) -> list[DraftAction]:
    actions: list[DraftAction] = []
    is_spectator = current_editor in ("spectator", "god")

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            actions.append(DraftAction(current_editor, "quit"))
            continue

        if event.type == pygame.MOUSEWHEEL:
            t = "page_next" if event.y > 0 else "page_prev"
            actions.append(DraftAction(current_editor, t))
            continue

        if event.type == pygame.MOUSEBUTTONDOWN:
            card = registry.card_name_at(page, index, mouse_board_x, mouse_board_y)
            match event.button:
                case 1:
                    if card != "None":
                        actions.append(DraftAction(current_editor, "add_card", card))
                    for i in range(len(registry.get_page_colors(page))):
                        if registry.switch_rects[i].collidepoint(event.pos):
                            actions.append(DraftAction(current_editor, "change_index", data=i))
                case 3:
                    if card != "None":
                        actions.append(DraftAction(current_editor, "remove_card", card))
                    else:
                        actions.append(DraftAction(current_editor, "remove_last_card"))

        if event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()
            match key_pressed(keys):
                case pygame.K_ESCAPE:
                    actions.append(DraftAction(current_editor, "quit"))
                case pygame.K_SPACE | pygame.K_d | pygame.K_RIGHT:
                    if keys[pygame.K_LSHIFT]:
                        actions.append(DraftAction(current_editor, "index_next"))
                    else:
                        actions.append(DraftAction(current_editor, "page_next"))
                case pygame.K_a | pygame.K_LEFT:
                    if keys[pygame.K_LSHIFT]:
                        actions.append(DraftAction(current_editor, "index_prev"))
                    else:
                        actions.append(DraftAction(current_editor, "page_prev"))
                case pygame.K_s:
                    card = registry.card_name_at(page, index, mouse_board_x, mouse_board_y)
                    if card != "None":
                        actions.append(DraftAction(current_editor, "add_card", card))
                case pygame.K_c:
                    actions.append(DraftAction(current_editor, "remove_last_card"))
                case pygame.K_e:
                    actions.append(DraftAction(current_editor, "advance_phase"))
                case pygame.K_r:
                    actions.append(DraftAction(current_editor, "confirm_start"))
                case pygame.K_f:
                    actions.append(DraftAction(current_editor, "toggle_hint"))
    if is_spectator:
        actions = [a for a in actions if a.action_type in SPECTATOR_ALLOWED]
    return actions