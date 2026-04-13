# -----------------------------------------------------------------
# Afternoon Brainstorming
# Copyright (C) 2024 Robin Liu, Angus Yu / FOS Studio
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

import pygame


def key_pressed(keys: pygame.key.ScancodeWrapper) -> int:
    keys_func = [
    pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
    pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9,
    pygame.K_a, pygame.K_b, pygame.K_c, pygame.K_d, pygame.K_e,
    pygame.K_f, pygame.K_g, pygame.K_h, pygame.K_i, pygame.K_j,
    pygame.K_k, pygame.K_l, pygame.K_m, pygame.K_n, pygame.K_o,
    pygame.K_p, pygame.K_q, pygame.K_r, pygame.K_s, pygame.K_t,
    pygame.K_u, pygame.K_v, pygame.K_w, pygame.K_x, pygame.K_y,
    pygame.K_z, pygame.K_SPACE, pygame.K_ESCAPE, pygame.K_TAB,
    pygame.K_LEFT, pygame.K_UP, pygame.K_DOWN, pygame.K_RIGHT
    ]
    
    for pygame_key in keys_func:
        if keys[pygame_key]:
            return pygame_key
    return -1