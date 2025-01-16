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