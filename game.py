from player import Player
from random import randint
from vector import Vector
from filter import VectorFilter, Filter
import pygame as pg
from world import World
import physics
from time import sleep
from control import BoolTrigger
import blockprop
import version
import sound
import timing

class Game:
    def __init__(self, username, playerid):
        self.player = Player(playerid, username, Vector())
        self.player.position.y = -640
        self.camera = Vector()
        self.camera_filter = VectorFilter(0.1)
        self.to_set = []
        self.tps = 1
        self.world = World()
        self.selection_position = Vector(0, 0)
        self.selection_x = 0
        self.selection_y = 0
        self.prev_selection_x = 0
        self.prev_selection_y = 0
        self.selection_reach = 3
        self.stand_timer = 0
        self.running = False
        self.jump_trigger = BoolTrigger()
        self.mouse_left_trigger = BoolTrigger()
        self.mouse_right_trigger = BoolTrigger()
        self.in_menu = False
        self.in_inventory = False
        self.inventory_index = 0
        self.destroy_timer = 0
        self.to_craft = []
        self.entities = []
        self.attack = 255
        self.damage_cooldown = 0
        self.last_chosen_slot = 0
        self.onscreen_players = []
        self.entity_count = 0

        self.sstrigger = BoolTrigger()

        self.fps = 1
        self.fps_filter = Filter(0.1, 1)
        self.can_air_jump = False
        self.cloud_pos = 0
        self.music = sound.MusicQueue()

        self.client_queue = timing.EventQueue()

    def inventory_index_setter(self, index):
        def setter():
            self.inventory_index = index
            self.last_chosen_slot = index

        return setter

    def crafting_setter(self, index):
        def setter():
            self.craft(index)

        return setter

    def start(self):
        self.running = True

    def craft(self, index):
        sound.HIT.play()
        self.to_craft.append(index)

    def update(self, keys, mouse, deltatime):
        self.client_queue.run_event()
        self.music.update(deltatime, self.player.position.y)
        
        if not self.running:
            return
        if deltatime > 0.5:
            return
        if deltatime > 0.001:
            self.fps = self.fps_filter.process(1 / deltatime)
        self.cloud_pos -= deltatime * 15
        camera_target = self.player.position + Vector(16, 32)
        self.camera += (camera_target - self.camera) * deltatime * 8

        self.move_player(keys, deltatime)
        self.selection_x = int(
            (self.player.position.x + self.selection_position.x * 32 - 1) / 32
        )
        self.selection_y = int(
            (self.player.position.y + self.selection_position.y * 32 + 16) / 32
        )

        if self.sstrigger.is_triggered(pg.K_p in keys):
            min_x = 0
            max_x = 0
            min_y = 0
            max_y = 0
            for chunk in self.world.chunks:
                max_x = max(max_x, chunk[0])
                max_y = max(max_y, chunk[1])
                min_x = min(min_x, chunk[0])
                min_y = min(min_y, chunk[1])

            out_surf = pg.Surface(((max_x - min_x) * 32 * 4, (max_y - min_y) * 32 * 4), pg.SRCALPHA)
            out_surf.fill((0,0,0,0))
            for chunk in self.world.chunks:
                chnk = self.world.chunks[chunk]
                chunk_surf = pg.transform.smoothscale(chnk.get_surface_no_load(), (32 * 4,32 * 4))
                out_surf.blit(chunk_surf, ( (chunk[0] - min_x)*32 * 4, (chunk[1] - min_y)*32 * 4 ))

            pg.image.save(out_surf, "world.png")

        self.selection_position += mouse.velocity * 0.001

        if self.selection_position.length() > self.selection_reach:
            self.selection_position = (
                self.selection_position.norm() * self.selection_reach
            )

        if self.mouse_left_trigger.is_triggered(mouse.left):
            pg.event.set_grab(True)
            pg.mouse.set_visible(False)
            self.attack = self.inventory_index
            if blockprop.BLOCKS[self.player.inventory.slots[self.inventory_index].item].damage > 1:
                self.player.animation.set_animation(2)
                sound.SWING.play()
            self.player.animation.frame = 0
        #     block = self.world.get_block(self.selection_x, self.selection_y)
        #     if block != -1:
        #         self.to_set.append(BlockSet(self.selection_x, self.selection_y, -1))
        if mouse.left:
            block = self.world.get_block(self.selection_x, self.selection_y)
            holding = self.player.inventory.slots[self.inventory_index].item
            breakable = blockprop.BLOCKS[block].breaks_with <= blockprop.BLOCKS[holding].mine_strength
            if block != -1 and breakable:
                self.destroy_timer += deltatime * 2
                if self.destroy_timer >= 1:
                    self.world.set_block(self.selection_x, self.selection_y, -1)
                    self.to_set.append(BlockSet(self.selection_x, self.selection_y, -1))
                    self.world.set_block(self.selection_x, self.selection_y, -1, True)
                    sound.BREAK.play()
            else:
                self.destroy_timer = 0
        else:
            self.destroy_timer = 0

        if (self.selection_x, self.selection_y) != (
            self.prev_selection_x,
            self.prev_selection_y,
        ):
            self.destroy_timer = 0

        self.prev_selection_x, self.prev_selection_y = (
            self.selection_x,
            self.selection_y,
        )

        for ent in self.entities:
            if ent.is_hostile and physics.hitbox_collide(self.player.position + self.player.hitbox_offset, self.player.hitbox_size, ent.position + ent.hitbox_offset, ent.hitbox_size):
                if self.damage_cooldown < 0.01:
                    self.player.health -= ent.damage
                    self.damage_cooldown = 0.5
                    self.player.velocity = ((self.player.position - ent.position).norm() * physics.JUMP_HEIGHT)
                    sound.DAMAGE.play()

        if self.damage_cooldown > 0:
            self.damage_cooldown -= deltatime

        if self.player.health <= 0:
            self.player.health = 0
        if self.player.health >= 100:
            self.player.health = 100
        

        if self.mouse_right_trigger.is_triggered(mouse.right):
            if self.player.inventory.slots[self.inventory_index].item == 10:
                self.to_set.append(
                    BlockSet(0, 0, self.inventory_index)
                )
                self.player.health += 10
                sound.EAT.play()
            elif self.world.get_block(self.selection_x, self.selection_y) in [-1, 46]:
                self.to_set.append(
                    BlockSet(self.selection_x, self.selection_y, self.inventory_index)
                )
                self.world.set_block(self.selection_x, self.selection_y, self.player.inventory.slots[self.inventory_index].item, True)
                sound.BREAK.play()

        if pg.K_ESCAPE in keys:
            pg.event.set_grab(False)
            pg.mouse.set_visible(True)
            self.in_menu = True

        if pg.K_e in keys:
            pg.event.set_grab(False)
            pg.mouse.set_visible(True)
            self.in_inventory = True

        for p in self.onscreen_players:
            p.position += (p.target - p.position) * 0.1
        
        for e in self.entities:
            e.position += (e.target - e.position) * 0.1

    def move_player(self, keys, deltatime):
        acc = Vector()
        if pg.K_a in keys or pg.K_LEFT in keys:
            acc.x = -physics.MOVE_ACCELERATION
            if self.player.animation.index != 2:
                self.player.animation.set_animation(1)
            self.player.animation.mirror = True
        elif pg.K_d in keys or pg.K_RIGHT in keys:
            acc.x = physics.MOVE_ACCELERATION
            if self.player.animation.index != 2:
                self.player.animation.set_animation(1)
            self.player.animation.mirror = False

        if self.player.animation.index == 2:
            if self.player.animation.frame >= self.player.animation.num_frames-2:
                self.player.animation.set_animation(0)

        if abs(self.player.velocity.x) < 0.001 and self.player.standing and self.player.animation.index != 2:
            self.player.animation.set_animation(0)

        if pg.K_f in keys:
            sleep(0.05)

        if pg.K_2 in keys:
            greatest_damage = 0
            for index, item in enumerate(self.player.inventory.slots):
                if blockprop.BLOCKS[item.item].damage > greatest_damage:
                    greatest_damage = blockprop.BLOCKS[item.item].damage
                    self.inventory_index = index
            
        if pg.K_3 in keys:
            greatest_damage = 0
            for index, item in enumerate(self.player.inventory.slots):
                if blockprop.BLOCKS[item.item].mine_strength > greatest_damage:
                    greatest_damage = blockprop.BLOCKS[item.item].mine_strength
                    self.inventory_index = index

        

        if pg.K_1 in keys:
            self.inventory_index = self.last_chosen_slot
        acc.y = physics.GRAVITY

        vel = self.player.velocity * deltatime + (acc * 0.5 * deltatime * deltatime)

        self.player.position.x += vel.x
        if self.world.collide(
            self.player.position + self.player.hitbox_offset, self.player.hitbox_size
        ):
            self.player.position.x -= vel.x
            self.player.velocity.x = 0

        self.player.position.y += vel.y

        self.player.standing = False

        jump_triggered = self.jump_trigger.is_triggered(
            pg.K_w in keys or pg.K_SPACE in keys or pg.K_UP in keys
        )
        if self.can_air_jump and jump_triggered:
            self.player.velocity.y = -physics.JUMP_HEIGHT
            sound.JUMP.play()
            self.can_air_jump = version.DEBUG

        if self.world.collide(
            self.player.position + self.player.hitbox_offset, self.player.hitbox_size
        ):
            self.player.velocity.y = 0
            self.player.position.y -= vel.y
            if vel.y > 0:
                self.stand_timer = 0.3

        self.player.standing = self.stand_timer > 0
        if self.player.standing:
            self.can_air_jump = True
        if self.player.standing and jump_triggered:
            self.player.velocity.y = -physics.JUMP_HEIGHT
            sound.JUMP.play()

        self.player.velocity += acc * deltatime
        # if abs(self.player.velocity.x) > physics.MAX_SPEED:
        #     self.player.velocity.x /= abs(self.player.velocity.x)
        #     self.player.velocity.x *= physics.MAX_SPEED
        self.player.velocity.x *= physics.FRICTION**deltatime
        self.stand_timer = max(0, self.stand_timer - deltatime)

    def find_player(self, player_id):
        for i in self.onscreen_players:
            if i.id == player_id:
                return i
        return None

    def find_entity(self, entity_id):
        for i in self.entities:
            if i.id == entity_id:
                return i
        return None


class BlockSet:
    def __init__(self, x, y, block):
        self.x = x
        self.y = y
        self.block = block
