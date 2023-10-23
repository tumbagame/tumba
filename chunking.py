import pygame as pg
import sprites
import blockprop

# Class to store chunk data along with textures and collision masks


class Chunk:
    def __init__(self):
        self.blocks = [9] * (32 * 32)
        self.surface = pg.Surface((1, 1), pg.SRCALPHA)
        self.collision = pg.mask.Mask((32 * 32, 32 * 32))
        self.collision.fill()
        # self.surface = self.collision.to_surface()

        self.surface_loaded = False

    def set_block(self, x, y, block):
        self.blocks[y * 32 + x] = block

    def get_block(self, x, y):
        return self.blocks[y * 32 + x]

    def serialize(self):
        out_bytes = b""
        for block in self.blocks:
            out_bytes += b"\xff" if (block == -1) else block.to_bytes(1, "little")
        return out_bytes

    def load_bytes(self, from_bytes):
        for ind, byte in enumerate(from_bytes):
            self.blocks[ind] = -1 if (byte == 255) else byte

    def load_surface(self):
        new_surf = self.surface.copy()
        new_surf = pg.Surface((32 * 32, 32 * 32), pg.SRCALPHA)
        new_surf.fill((0,) * 4)
        col_surf = new_surf.copy()
        for y in range(32):
            for x in range(32):
                block = self.get_block(x, y)
                if block != -1:
                    new_surf.blit(sprites.BLOCKS[block], (x * 32, y * 32))
                    if blockprop.BLOCKS[block].collision:
                        col_surf.blit(sprites.BLOCKS[block], (x * 32, y * 32))
        self.collision = pg.mask.from_surface(col_surf)
        # self.surface = self.collision.to_surface()
        self.surface = new_surf
        self.surface_loaded = True

    def unload_surface(self):
        self.surface = pg.Surface((1, 1), pg.SRCALPHA)
        self.collision = pg.mask.Mask((32 * 32, 32 * 32))
        self.collision.fill()
        # self.surface = self.collision.to_surface()
        self.surface_loaded = False

    def collide(self, x, y, width, height):
        hitbox = pg.Mask((int(width), int(height)))
        hitbox.fill()
        return self.collision.overlap_area(hitbox, (int(x), int(y))) != 0
