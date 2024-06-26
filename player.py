from vector import Vector
from animation import Animation
import inventory


class Player:
    def __init__(self, id, name, position):
        self.id = id
        self.name = name
        self.position = position
        self.velocity = Vector()
        self.hitbox_size = Vector(9, 60)
        self.hitbox_offset = Vector(11, 3)
        self.standing = False
        self.animation = Animation("assets/sprites/player.png", 3, 16, 15)
        self.inventory = inventory.Inventory()
        self.animation.set_animation(1)
        self.health = 100
