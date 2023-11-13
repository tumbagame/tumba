import pygame as pg
import sprites
import text


def scale_button(image, size):
    new_surface = pg.Surface(size)
    new_surface.fill(image.get_at((3, 3)))
    horiz_slice = pg.Surface((1, 2))
    vert_slice = pg.Surface((2, 1))

    vert_slice.blit(image, (0, -2))
    new_surface.blit(pg.transform.scale(vert_slice, (2, size[1])), (0, 0))
    vert_slice.blit(image, (-image.get_width() + 2, -2))
    new_surface.blit(pg.transform.scale(vert_slice, (2, size[1])), (size[0] - 2, 0))
    horiz_slice.blit(image, (-2, 0))
    new_surface.blit(pg.transform.scale(horiz_slice, (size[0], 2)), (0, 0))
    horiz_slice.blit(image, (-2, -image.get_height() + 2))
    new_surface.blit(pg.transform.scale(horiz_slice, (size[0], 2)), (0, size[1] - 2))

    return new_surface


class UIComponent:
    def __init__(self):
        pass

    def update(self, mouse, keyboard):
        return pg.Surface((1, 1))

    def get_pos(self):
        return (0, 0)


class Image(UIComponent):
    def __init__(self, path, x, y):
        self.image = pg.image.load(path)
        self.x = x
        self.y = y

    def update(self, mouse, keyboard):
        return self.image

    def get_pos(self):
        return (self.x, self.y)


class ItemSlot(UIComponent):
    def __init__(self, x, y, block_getter, command=lambda: None):
        self.image = sprites.ITEM_SLOT
        self.block_getter = block_getter
        self.command = command
        self.x = x
        self.y = y
        self.text = text.Text()
        self.is_pressed = False

    def update(self, mouse, keyboard):
        block = self.block_getter()
        clone = self.image.copy()
        if not block.has_item():
            return clone

        count_text = self.text.render(
            f"{block.count}{'+' if block.count >= 255 else ''}"
            if block.count > 1
            else ""
        )

        if self.x < mouse.position.x < self.x + 32:
            if self.y < mouse.position.y < self.y + 32:
                clone.blit(sprites.BLOCKS[block.item], (0, 0))
                clone.blit(sprites.ITEM_SLOT_SELECT, (0, 0))
                clone.blit(count_text, (4, 0))
                if mouse.left:
                    self.command()
                    mouse.left = False
                return clone
        clone.blit(sprites.BLOCKS16[block.item], (8, 8))
        clone.blit(count_text, (4, 0))
        return clone

    def get_pos(self):
        return (self.x, self.y)


class Label(UIComponent):
    def __init__(self, label, x, y):
        self.text_image = text.Text().render(label)
        self.x = x
        self.y = y

    def update(self, mouse, keyboard):
        return self.text_image

    def get_pos(self):
        return (self.x, self.y)


class Button(UIComponent):
    def __init__(self, label, x, y, command=lambda: None):
        self.text_image = text.Text().render(label)
        self.button_size = (
            self.text_image.get_width() + 4,
            self.text_image.get_height(),
        )
        self.x = x
        self.y = y
        self.image = scale_button(sprites.BUTTON, self.button_size)
        self.pressed_image = scale_button(sprites.BUTTON_PRESSED, self.button_size)
        self.image.blit(self.text_image, (2, 0))
        self.pressed_image.blit(self.text_image, (2, 0))
        self.hover = False
        self.is_pressed = False
        self.command = command

    def get_pos(self):
        if self.hover:
            return (self.x, self.y - 2)
        return (self.x, self.y)

    def update(self, mouse, keyboard):
        self.hover = False
        if self.x < mouse.position.x < self.x + self.pressed_image.get_width():
            if self.y < mouse.position.y < self.y + self.pressed_image.get_height():
                self.hover = True
                if mouse.left:
                    self.is_pressed = True
                    return self.pressed_image
                if self.is_pressed:
                    self.command()
        self.is_pressed = False
        return self.image


class GUI:
    def __init__(self, *buttons):
        self.buttons = buttons
        self.escapeable = False

    def can_escape(self):
        self.escapeable = True
        return self

    def update(self, mouse, keyboard):
        screen = pg.Surface((512, 256), pg.SRCALPHA)
        screen.fill((0, 0, 0, 0))
        for button in self.buttons:
            screen.blit(button.update(mouse, keyboard), button.get_pos())
        return screen
