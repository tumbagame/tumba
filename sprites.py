import pygame as pg

SKY = pg.image.load("assets/sprites/sky.png")
MOUNTAINS0 = pg.image.load("assets/sprites/mountains0.png")
MOUNTAINS1 = pg.image.load("assets/sprites/mountains1.png")
PLAYER = pg.image.load("assets/sprites/player/idle.png")
ATLAS = pg.image.load("assets/sprites/atlas.png")

BUTTON = pg.image.load("assets/sprites/ui/button.png")
BUTTON_PRESSED = pg.image.load("assets/sprites/ui/button_pressed.png")
ITEM_SLOT = pg.image.load("assets/sprites/ui/slot.png")
ITEM_SLOT_SELECT = pg.image.load("assets/sprites/ui/slot_select.png")


BLOCKS = []
BLOCKS16 = []
for y in range(ATLAS.get_height() // 32):
    for x in range(ATLAS.get_width() // 32):
        block = pg.Surface((32, 32), pg.SRCALPHA)
        block.fill((0,) * 4)
        block.blit(ATLAS, (-x * 32, -y * 32))
        BLOCKS.append(block)
        BLOCKS16.append(pg.transform.smoothscale(block, (16, 16)))
