import pygame as pg


class Text:
    def __init__(self):
        self.font = pg.font.Font("assets/font.ttf", 8)
        self.font_memo = {}

    def render(self, text):
        if text in self.font_memo:
            return self.font_memo[text]

        shadow = self.font.render(text, False, (0,) * 3)
        top = self.font.render(text, False, (255,) * 3)
        surf = pg.Surface((top.get_width() + 1, top.get_height() + 1), pg.SRCALPHA)
        surf.fill((0,) * 4)
        surf.blit(shadow, (1, 1))
        surf.blit(top, (0, 0))
        self.font_memo[text] = surf
        return surf
