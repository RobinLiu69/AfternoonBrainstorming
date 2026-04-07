from __future__ import annotations
import json
from dataclasses import dataclass
from typing import Literal, Optional, TYPE_CHECKING

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
    "toggle_timer",
    "toggle_file_save",
    "toggle_hint",
    "confirm_start",
    "quit",
]


@dataclass
class DraftAction:
    player: str
    action_type: DraftActionType
    card_name: Optional[str] = None

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


def collect_draft_actions(current_editor: str, page: int, registry: ExhibitRegistry,
                          mouse_board_x: Optional[int], mouse_board_y: Optional[int]) -> list[DraftAction]:
    actions: list[DraftAction] = []

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            actions.append(DraftAction(current_editor, "quit"))
            continue

        if event.type == pygame.MOUSEWHEEL:
            t = "page_next" if event.y > 0 else "page_prev"
            actions.append(DraftAction(current_editor, t))
            continue

        if event.type == pygame.MOUSEBUTTONDOWN:
            card = registry.card_name_at(page, mouse_board_x, mouse_board_y)
            match event.button:
                case 1:
                    if card != "None":
                        actions.append(DraftAction(current_editor, "add_card", card))
                case 3:
                    if card != "None":
                        actions.append(DraftAction(current_editor, "remove_card", card))
                    else:
                        actions.append(DraftAction(current_editor, "remove_last_card"))
            continue

        if event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()
            match key_pressed(keys):
                case pygame.K_ESCAPE:
                    actions.append(DraftAction(current_editor, "quit"))
                case pygame.K_SPACE | pygame.K_d:
                    actions.append(DraftAction(current_editor, "page_next"))
                case pygame.K_a:
                    actions.append(DraftAction(current_editor, "page_prev"))
                case pygame.K_s:
                    card = registry.card_name_at(page, mouse_board_x, mouse_board_y)
                    if card != "None":
                        actions.append(DraftAction(current_editor, "add_card", card))
                case pygame.K_c:
                    actions.append(DraftAction(current_editor, "remove_last_card"))
                case pygame.K_e:
                    actions.append(DraftAction(current_editor, "advance_phase"))
                case pygame.K_r:
                    actions.append(DraftAction(current_editor, "confirm_start"))
                case pygame.K_t:
                    actions.append(DraftAction(current_editor, "toggle_timer"))
                case pygame.K_y:
                    actions.append(DraftAction(current_editor, "toggle_file_save"))
                case pygame.K_f:
                    actions.append(DraftAction(current_editor, "toggle_hint"))
    return actions