import pygame as pg
import version
import sprites
from text import Text
from filter import Filter
import time
from vector import Vector
from mouse import Mouse
import blockprop
import ui
import animation


class Renderer:
    def __init__(self):
        self.size = (512, 256)
        pg.display.set_caption(
            f"{version.NAME} - {version.VERSION}"
            + (" (DEBUG)" if version.DEBUG else "")
        )
        self.window = pg.display.set_mode(self.size, pg.RESIZABLE)
        self.disp = pg.Surface(self.size)
        self.running = True

        self.text = Text()

        self.width_filt = Filter(0.5, self.size[0])
        self.height_filt = Filter(0.5, self.size[1])
        self.gui = ui.GUI()
        self.select_box = pg.Surface((32, 32), pg.SRCALPHA)
        self.select_box.fill((255, 255, 255, 127))

        self.destroy = animation.Animation("assets/sprites/destroy.png", 1, 16, 1)

        self.keys_down = []

        self.mouse = Mouse()
        self.in_gui = False

    def _game_to_screen(self, position, camera):
        return (
            int(position.x - camera.x) + self.size[0] // 2,
            int(position.y - camera.y) + self.size[1] // 2,
        )

    def show_gui(self, gui):
        self.gui = gui
        self.in_gui = True

    def clear_gui(self):
        self.gui = ui.GUI()
        self.in_gui = False

    def quit_game(self):
        pg.quit()
        self.running = False

    def update(self, game):
        if not self.running:
            return
        self.mouse.scroll = 0
        for e in pg.event.get():
            if e.type == pg.QUIT:
                self.quit_game()
                return
            elif e.type == pg.KEYDOWN:
                self.keys_down.append(e.key)
            elif e.type == pg.KEYUP:
                while e.key in self.keys_down:
                    self.keys_down.remove(e.key)
            elif e.type == pg.MOUSEBUTTONDOWN:
                if e.button == 1:
                    self.mouse.left = True
                elif e.button == 3:
                    self.mouse.right = True
                elif e.button == 4:
                    self.scroll = 1
                elif e.button == 5:
                    self.scroll = -1
            elif e.type == pg.MOUSEBUTTONUP:
                if e.button == 1:
                    self.mouse.left = False
                elif e.button == 3:
                    self.mouse.right = False

        if self.in_gui and self.gui.escapeable and pg.K_ESCAPE in self.keys_down:
            self.clear_gui()
            while pg.K_ESCAPE in self.keys_down:
                self.keys_down.remove(pg.K_ESCAPE)
        self.mouse.position = Vector(*pg.mouse.get_pos())
        self.mouse.position.x = self.mouse.position.x / self.window.get_width() * 512
        self.mouse.position.y = self.mouse.position.y / self.window.get_height() * 256
        self.mouse.velocity = Vector(*pg.mouse.get_rel())

        for i in range(2):
            self.disp.blit(
                sprites.SKY,
                (int(-game.camera.x / 4 + game.cloud_pos) % 512 - 512 + (i * 512), 0),
            )
        for i in range(2):
            self.disp.blit(
                sprites.MOUNTAINS1,
                (int(-game.camera.x / 3) % 512 - 512 + (i * 512), 0),
            )
        for i in range(2):
            self.disp.blit(
                sprites.MOUNTAINS0,
                (int(-game.camera.x / 2) % 512 - 512 + (i * 512), 0),
            )

        for chunk in game.world.chunks:
            self.disp.blit(
                game.world.chunks[chunk].surface,
                self._game_to_screen(Vector(chunk[0], chunk[1]) * 1024.0, game.camera),
            )

        self.disp.blit(
            self.destroy.get_man_frame(0, game.destroy_timer),
            self._game_to_screen(
                Vector(game.selection_x, game.selection_y) * 32.0,
                game.camera,
            ),
        )
        self.disp.blit(
            game.player.animation.get_frame(),
            self._game_to_screen(game.player.position, game.camera),
        )

        if game.destroy_timer < 0.01:
            self.disp.blit(
                self.select_box,
                self._game_to_screen(
                    Vector(game.selection_x, game.selection_y) * 32.0,
                    game.camera,
                ),
            )

        # pg.draw.rect(
        #     self.disp,
        #     (200, 60, 60, 100),
        #     self._game_to_screen(game.player.position + game.hitbox_offset, game.camera)
        #     + (int(game.hitbox_size.x), int(game.hitbox_size.y)),
        # )

        self.disp.blit(sprites.ITEM_SLOT, (10, 40))
        slot = game.player.inventory.slots[game.inventory_index]
        if slot.has_item():
            self.disp.blit(blockprop.BLOCKS[slot.item].sprite, (10, 40))
            self.disp.blit(sprites.ITEM_SLOT_SELECT, (10, 40))
            self.disp.blit(self.text.render(f"{slot.count}"), (14, 40))
            self.disp.blit(self.text.render(blockprop.BLOCKS[slot.item].name), (14, 72))

        self.disp.blit(self.gui.update(self.mouse, self.keys_down), (0, 0))

        if version.DEBUG:
            self.disp.blit(
                self.text.render(f"{round(game.fps,2)}fps, {game.tps}tps"), (8, 8)
            )

        self.window.blit(
            pg.transform.scale(
                self.disp,
                (
                    int(self.width_filt.process(self.window.get_width())),
                    int(self.height_filt.process(self.window.get_height())),
                ),
            ),
            (0, 0),
        )

        pg.display.update()
        # while(time.time() - frame_start <= (1/60)):
        #     pass
