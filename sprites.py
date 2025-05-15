import pygame as pg

SKY = pg.image.load("assets/sprites/sky.png")
MOUNTAINS0 = pg.image.load("assets/sprites/mountains0.png")
MOUNTAINS1 = pg.image.load("assets/sprites/mountains1.png")
ATLAS = pg.image.load("assets/sprites/atlas.png")
CAVE = pg.image.load("assets/sprites/cave.png")
LIGHT = pg.image.load("assets/sprites/light.png")

BUTTON = pg.image.load("assets/sprites/ui/button.png")
BUTTON_PRESSED = pg.image.load("assets/sprites/ui/button_pressed.png")
ITEM_SLOT = pg.image.load("assets/sprites/ui/slot.png")
ITEM_SLOT_SELECT = pg.image.load("assets/sprites/ui/slot_select.png")
HEALTH_BAR_EMPTY = pg.image.load("assets/sprites/ui/health_empty.png")
HEALTH_BAR_FULL = pg.image.load("assets/sprites/ui/health_full.png")


BLOCKS = []
BLOCKS16 = []
for y in range(ATLAS.get_height() // 32):
    for x in range(ATLAS.get_width() // 32):
        block = pg.Surface((32, 32), pg.SRCALPHA)
        block.fill((0,) * 4)
        block.blit(ATLAS, (-x * 32, -y * 32))
        BLOCKS.append(block)
        BLOCKS16.append(pg.transform.smoothscale(block, (16, 16)))
