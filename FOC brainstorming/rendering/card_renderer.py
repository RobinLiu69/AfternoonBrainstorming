import pygame

from core.setting import RED
from cards.base import CardRenderData
from rendering.sprite_registry import SpriteRegistry
from core.game_screen import GameScreen, draw_text


class CardRenderer:
    def __init__(self, game_screen: GameScreen):
        self.game_screen = game_screen
        self._surfaces: dict[str, pygame.Surface] = {}

    def _get_card_surface(self, instance_id: str) -> pygame.Surface:
        if instance_id not in self._surfaces:
            bs = int(self.game_screen.block_size)
            self._surfaces[instance_id] = pygame.Surface((bs, bs), pygame.SRCALPHA)
        return self._surfaces[instance_id]
    
    def release(self, instance_id: str) -> None:
        self._surfaces.pop(instance_id, None)

    def render(self, data: CardRenderData) -> None:
        surface = self._get_card_surface(data.instance_id)
        surface.fill((0, 0, 0, 0))

        sprite = (SpriteRegistry.get_instance().get(data.sprite_key) if data.use_sprite else None)

        if sprite:
            self._render_with_sprite(surface, data, sprite)
        else:
            self._render_with_shape(surface, data)

        if data.show_stats:
            self._draw_stats(surface, data)

        self._blit(surface, data)
    
    def _render_with_sprite(self, surface: pygame.Surface, data: CardRenderData, sprite: pygame.Surface) -> None:
        surface.blit(sprite, (0, 0))
    
    def _render_with_shape(self, surface: pygame.Surface, data: CardRenderData) -> None:
        bs = self.game_screen.block_size
        if data.shape_type == "circle":
            pygame.draw.circle(surface, data.color, (int(bs*0.5), int(bs*0.5)), int(bs*0.2), int(self.game_screen.thickness/1.1))
        else:
            points = [(int(x * bs), int(y * bs)) for x, y in data.shape_points]
            pygame.draw.lines(surface, data.color, True, points, int(self.game_screen.thickness/1.1))
    
    def _draw_stats(self, surface: pygame.Surface, data: CardRenderData) -> None:
        bs = self.game_screen.block_size
        
        text_color = (255, 255, 255) if data.use_sprite else data.color
        
        match data.job_and_color:
            case "CUBES":
                draw_text("CUBES", self.game_screen.big_text_font,
                         text_color, bs * 0.23, bs * 0.37, surface)
            case "MOVE":
                draw_text("MOVE", self.game_screen.big_text_font,
                         text_color, bs * 0.27, bs * 0.37, surface)
            case "HEAL":
                draw_text("HEAL", self.game_screen.big_text_font,
                         text_color, bs * 0.27, bs * 0.37, surface)
            case _:
                draw_text(f"HP:{data.health}", self.game_screen.info_text_font, text_color, bs * 0.1, bs * 0.03, surface)
                atk_text = (f"ATK:{data.damage}+{data.extra_damage}" if data.extra_damage else f"ATK:{data.damage}")
                draw_text(atk_text, self.game_screen.info_text_font, text_color, bs * 0.5 if data.extra_damage else bs * 0.6, bs * 0.03, surface)
                if data.armor > 0:
                    draw_text(f"arm:{data.armor}", self.game_screen.small_text_font, text_color, bs * 0.1, bs * 0.12, surface)
                if data.anger:
                    draw_text("anger", self.game_screen.small_text_font, text_color, bs * 0.6, bs * 0.775, surface)
                if data.numbness:
                    draw_text("numbness", self.game_screen.small_text_font, text_color, bs * 0.6, bs * 0.85, surface)
                if data.moving:
                    draw_text("moving" if not data.mouse_selected else "Selected", self.game_screen.small_text_font, text_color,
                              bs*0.6, bs*0.12, surface)
                if data.been_targeted:
                    draw_text("Target", self.game_screen.small_text_font, (200, 0, 0),
                            bs * 0.1, bs * 0.75, surface)

                if data.owner == "display":
                    draw_text(data.job_and_color, self.game_screen.text_font, text_color, bs * 0.1, bs * 0.8, surface)
                else:
                    draw_text(data.owner, self.game_screen.text_font, text_color, bs * 0.1, bs * 0.8, surface)
    
    def _blit(self, surface: pygame.Surface, data: CardRenderData) -> None:
        game_screen = self.game_screen
        x = (game_screen.display_width / 2 - game_screen.block_size * 2) + data.board_x * game_screen.block_size
        y = (game_screen.display_height / 2 - game_screen.block_size * 1.65) + data.board_y * game_screen.block_size

        game_screen.surface.blit(surface, (x, y))
