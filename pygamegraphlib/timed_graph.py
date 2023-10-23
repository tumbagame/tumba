import pygame as pg
from pygamegraphlib.filter import Filter


class TimedGraph:
    def __init__(self, width_pixels=200, height_pixels=200, filter=1.0):
        self.surface = pg.Surface((width_pixels, height_pixels))
        self.values = [0] * width_pixels
        pg.init()
        self.font = pg.font.Font(None, 16)
        self.filter = Filter(filter)

    def get_surface(self, value):
        new_value = self.filter.process(value)
        self.values.pop(0)
        self.values.append(new_value)
        min_value = min(self.values)
        max_value = max(self.values)
        self.surface.fill((60, 60, 60))

        def scale(n):
            if abs(max_value - min_value) < 0.00001:
                return self.surface.get_height() // 2

            return self.surface.get_height() - int(((n - min_value) / (max_value - min_value))
                                                   * self.surface.get_height())
        for i in range(len(self.values)-1):
            val_1 = scale(self.values[i])
            val_2 = scale(self.values[i+1])
            pg.draw.line(self.surface, (60, 200, 60), (i, val_1), (i+1, val_2))
            # pg.draw.rect(self.surface, (60, 200, 60),
            #  (i, min(val_1, val_2), 1, abs(val_1 - val_2)))

        max_text = self.font.render(
            f'{round(max_value,3)}', True, (200,)*3, None)
        min_text = self.font.render(
            f'{round(min_value,3)}', True, (200,)*3, None)

        self.surface.blit(max_text, (0, 0))
        self.surface.blit(
            min_text, (0, self.surface.get_height() - min_text.get_height()))

        return self.surface
