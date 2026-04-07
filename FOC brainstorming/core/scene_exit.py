from dataclasses import dataclass
from typing import Literal, Optional

from core.draft_state import DraftState


ExitKind = Literal["quit", "finished", "scene_handoff"]


@dataclass
class DraftExitReason:
    kind: ExitKind
    draft_state: Optional[DraftState] = None
    next_scene_state: Optional[dict] = None