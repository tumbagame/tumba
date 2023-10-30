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


class Game:
    def __init__(self, username):
        self.player = Player(randint(0, 65535), username, Vector())
        self.player.position.y = -640
        self.camera = Vector()
        self.camera_filter = VectorFilter(0.1)
        self.to_set = []
        self.tps = 1
        self.world = World()
        self.hitbox_offset = Vector(11, 3)
        self.hitbox_size = Vector(9, 60)
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

        self.fps = 1
        self.fps_filter = Filter(0.1, 1)
        self.can_air_jump = False
        self.cloud_pos = 0

    def inventory_index_setter(self, index):
        def setter():
            self.inventory_index = index

        return setter

    def start(self):
        self.running = True

    def update(self, keys, mouse, deltatime):
        if not self.running:
            return
        if deltatime > 0.5:
            return
        if deltatime > 0.001:
            self.fps = self.fps_filter.process(1 / deltatime)
        self.cloud_pos -= deltatime * 15
        camera_target = self.player.position + Vector(16, 32)
        self.camera.x += (camera_target.x - self.camera.x) * deltatime * 8
        self.camera.y += (camera_target.y - self.camera.y) * deltatime * 8

        self.move_player(keys, deltatime)
        self.selection_x = int(
            (self.player.position.x + self.selection_position.x * 32 - 1) / 32
        )
        self.selection_y = int(
            (self.player.position.y + self.selection_position.y * 32 + 16) / 32
        )

        self.selection_position += mouse.velocity * 0.01

        if self.selection_position.length() > self.selection_reach:
            self.selection_position = (
                self.selection_position.norm() * self.selection_reach
            )

        if self.mouse_left_trigger.is_triggered(mouse.left):
            pg.event.set_grab(True)
            pg.mouse.set_visible(False)
        #     block = self.world.get_block(self.selection_x, self.selection_y)
        #     if block != -1:
        #         self.to_set.append(BlockSet(self.selection_x, self.selection_y, -1))
        if mouse.left:
            block = self.world.get_block(self.selection_x, self.selection_y)
            if block != -1:
                self.destroy_timer += deltatime * 2
                if self.destroy_timer >= 1:
                    self.world.set_block(self.selection_x, self.selection_y, -1)
                    self.to_set.append(BlockSet(self.selection_x, self.selection_y, -1))
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

        if self.mouse_right_trigger.is_triggered(mouse.right):
            self.to_set.append(
                BlockSet(self.selection_x, self.selection_y, self.inventory_index)
            )
        if pg.K_ESCAPE in keys:
            pg.event.set_grab(False)
            pg.mouse.set_visible(True)
            self.in_menu = True

        if pg.K_e in keys:
            pg.event.set_grab(False)
            pg.mouse.set_visible(True)
            self.in_inventory = True

    def move_player(self, keys, deltatime):
        acc = Vector()
        if pg.K_a in keys:
            acc.x = -physics.MOVE_ACCELERATION
            self.player.animation.set_animation(1)
            self.player.animation.mirror = True
        elif pg.K_d in keys:
            acc.x = physics.MOVE_ACCELERATION
            self.player.animation.set_animation(1)
            self.player.animation.mirror = False

        if abs(self.player.velocity.x) < 0.001 and self.player.standing:
            self.player.animation.set_animation(0)

        if pg.K_f in keys:
            sleep(0.05)

        acc.y = physics.GRAVITY

        vel = self.player.velocity * deltatime + (acc * 0.5 * deltatime * deltatime)

        self.player.position.x += vel.x
        if self.world.collide(
            self.player.position + self.hitbox_offset, self.hitbox_size
        ):
            self.player.position.x -= vel.x
            self.player.velocity.x = 0

        self.player.position.y += vel.y

        self.player.standing = False

        jump_triggered = self.jump_trigger.is_triggered(
            pg.K_w in keys or pg.K_SPACE in keys
        )
        if self.can_air_jump and jump_triggered:
            self.player.velocity.y = -physics.JUMP_HEIGHT
            self.can_air_jump = False

        if self.world.collide(
            self.player.position + self.hitbox_offset, self.hitbox_size
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

        self.player.velocity += acc * deltatime
        # if abs(self.player.velocity.x) > physics.MAX_SPEED:
        #     self.player.velocity.x /= abs(self.player.velocity.x)
        #     self.player.velocity.x *= physics.MAX_SPEED
        self.player.velocity.x *= physics.FRICTION**deltatime
        self.stand_timer = max(0, self.stand_timer - deltatime)


class BlockSet:
    def __init__(self, x, y, block):
        self.x = x
        self.y = y
        self.block = block
