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
import player

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
        self.fps_update = 0
        self.fps_text = ""

        self.width_filt = Filter(0.5, self.size[0])
        self.height_filt = Filter(0.5, self.size[1])
        self.gui = ui.GUI()
        self.select_box = pg.Surface((32, 32), pg.SRCALPHA)
        self.select_box.fill((255, 255, 255, 127))
        self.health_bar_state = 0
        self.sensitivity = 1

        self.destroy = animation.Animation("assets/sprites/destroy.png", 1, 16, 1)
        self.keys_down = []

        self.mouse = Mouse()
        self.in_gui = False
        self.player_anim = player.Player(0,"", Vector()).animation
        self.player_anim.set_animation(1)

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
        pg.event.set_grab(True)
        pg.mouse.set_visible(False)

    def quit_game(self):
        pg.quit()
        self.running = False

    def set_sensitivity(self, sensitivity):
        self.sensitivity = sensitivity

    def update(self, game, deltatime):
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
        self.mouse.velocity = Vector(*pg.mouse.get_rel()) * self.sensitivity

        for i in range(2):
            self.disp.blit(
                sprites.SKY,
                (int(-game.camera.x / 4 + game.cloud_pos) % 512 - 512 + (i * 512), 0),
            )
        for i in range(2):
            self.disp.blit(
                sprites.MOUNTAINS1,
                (int(-game.camera.x / 3) % 512 - 512 + (i * 512), int(-game.camera.y / 3)),
            )
        for i in range(2):
            self.disp.blit(
                sprites.MOUNTAINS0,
                (int(-game.camera.x / 2) % 512 - 512 + (i * 512), int(-game.camera.y / 2)),
            )


        cave_opacity = max(0, min(1, (game.player.position.y - (16 * 32)) / ((32 - 16) * 32)))

        cave_clone = sprites.CAVE.copy()

        cave_clone.set_alpha(int(cave_opacity * 255))
        self.disp.blit(
            cave_clone,
            (int(-game.camera.x / 3) % 512 - 512, int(-game.camera.y / 3) % 512 - 512),
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

        for e in game.entities:
            e.animation.mirror = (e.target.x - e.position.x) < 0
            ent_frame = e.animation.get_frame(deltatime)
            if e.damage_cooldown > 0.5:
                dmg_indic = pg.Surface(ent_frame.get_size(), pg.SRCALPHA)
                dmg_indic.fill((255,100,100,255))
                ent_frame.blit(dmg_indic,(0,0), special_flags=pg.BLEND_RGBA_MULT)
            self.disp.blit(ent_frame,
                self._game_to_screen(e.position, game.camera)
            )

        for p in game.onscreen_players:
            self.player_anim.mirror = (p.target.x - p.position.x) < 0
            pframe = self.player_anim.get_frame(deltatime)
            self.disp.blit(pframe,
                self._game_to_screen(p.position, game.camera)
            )
            self.disp.blit(
                self.text.render(p.name),
                self._game_to_screen(p.position + Vector(-16,-16), game.camera)
            )

        player_frame = game.player.animation.get_frame(deltatime)
        damage_indicator = pg.Surface(player_frame.get_size(), pg.SRCALPHA)
        cooldown_map = max(0, min(255, int(game.damage_cooldown / 0.5 * 255) ))
        damage_indicator.fill((255, 255 - cooldown_map, 255-cooldown_map, 255))
        player_frame.blit(damage_indicator,(0,0), special_flags=pg.BLEND_RGBA_MULT)
        self.disp.blit(
            player_frame,
            self._game_to_screen(game.player.position, game.camera),
        )

        light_opacity = max(0, min(1, (game.player.position.y - (32 * 32)) / ((200 - 32) * 32)))

        black_surface = pg.Surface((512,256), pg.SRCALPHA)
        black_surface.fill((0,0,0,255))
        black_surface.blit(
            sprites.LIGHT,
            self._game_to_screen(game.player.position - Vector(128 - 16,128 - 32), game.camera),
            special_flags=pg.BLEND_RGBA_MIN
        )

        black_surface.set_alpha(int(light_opacity * 255))

        self.disp.blit(black_surface, (0,0))

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
            self.disp.blit(
                self.text.render(f"{slot.count}{'+' if (slot.count>=255) else ''}"),
                (14, 40),
            )
            self.disp.blit(self.text.render(blockprop.BLOCKS[slot.item].name), (14, 72))
        self.health_bar_state += 0.2 * (game.player.health - self.health_bar_state)
        self.disp.blit(sprites.HEALTH_BAR_EMPTY, (2, 2))
        full_surface = pg.Surface(( max(1, min(64, int(self.health_bar_state / 100 * 64))) ,16), pg.SRCALPHA)
        full_surface.fill((0,0,0,0))
        full_surface.blit(sprites.HEALTH_BAR_FULL, (0,0))
        self.disp.blit(full_surface, (2, 2))
        self.disp.blit(self.text.render(f"{int(game.player.position.x/32)},{int(-game.player.position.y/32)}"), (8, 86))

        self.disp.blit(self.gui.update(self.mouse, self.keys_down), (0, 0))

        # if version.DEBUG:
        self.fps_update += 1
        if self.fps_update > 60:
            self.fps_update = 0
            self.fps_text = f"{round(game.fps,2)}fps, {game.tps}tps"
            if version.DEBUG:
                self.fps_text += f", {game.entity_count} entities"
        self.disp.blit(
            self.text.render(self.fps_text), (8, 16)
        )
        self.disp.blit(
            self.text.render(f"x: {int(game.player.position.x/32)}, y: {int(-game.player.position.y/32)}"), (10,240)
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
