from vector import Vector
from animation import Animation

class Entity:
    def __init__(self):
        self.position = Vector()
        self.velocity = Vector()
        self.animation = Animation()
        self.health = 100
        self.damage = 10
        self.drops = 0
        self.is_hostile = False
        self.is_scared = False
        self.gravity = False
        self.lifetime = 0

    def with_position(self, position):
        self.position = position
        return self

    def with_velocity(self, velocity):
        self.velocity = velocity
        return self

    def with_animation(self, animation):
        self.animation = animation
        return self
