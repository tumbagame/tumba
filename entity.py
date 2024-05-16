from vector import Vector
from animation import Animation
import netencode
import random
import json

class Entity:
    def __init__(self):
        self.id = random.randint(0,0xff)
        self.type = 0
        self.position = Vector()
        self.velocity = Vector()
        self.animation = Animation("assets/chest.png", 1, 1, 1)
        self.health = 100
        self.damage = 10
        self.drop = -1
        self.is_hostile = False
        self.is_scared = False
        self.gravity = False
        self.lifetime = 86400

    def serialize(self):
        return netencode.encode_byte(self.id) + self.encode_byte(self.type) + 
                self.encode_int(self.position.x) + self.encode_int(self.position.y)

    def with_position(self, position):
        self.position = position
        return self

    def with_velocity(self, velocity):
        self.velocity = velocity
        return self

    def with_animation(self, animation):
        self.animation = animation
        return self
    
    def with_health(self, health):
        self.health = health
        return self
    
    def with_damage(self, damage):
        self.damage = damage
        return self
    
    def with_drop(self, drop):
        self.drop = drop
        return self
    
    def with_hostility(self, hostile):
        self.is_hostile = hostile
        return self

    def with_fear(self, scared):
        self.is_scared = scared
        return self

    def with_gravity(self, gravity):
        self.gravity = gravity
        return self

    def with_lifetime(self, lifetime):
        self.lifetime = lifetime
        return self

def load_dict(entity_dict):
    return Entity().with_animation(Animation(entity_dict["animation"]), 1, entity_dict["frames"], entity_dict["fps"])
            .with_health(entity_dict["health"])
            .with_damage(entity_dict["damage"])
            .with_drop(entity_dict["drop"])
            .with_hostility(entity_dict["hostile"])
            .with_fear(entity_dict["scared"])
            .with_lifetime(entity_dict["lifetime"])


ENTITIES = []
with open('assets/entities.json', 'r') as fp:
    entity_list = json.loads(fp.read())["entities"]
for entity in entity_list:
    ENTITIES.append(load_dict(entity))
