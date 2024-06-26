GRAVITY = 500
JUMP_HEIGHT = 300
MOVE_ACCELERATION = 500
MAX_SPEED = 200
ENTITY_SPEED = 100
MAX_JUMPS = 1
FRICTION = 0.1

def hitbox_collide(self, position1, size1, position2, size2):
        return (position1.x > (position2 - size1).x) and (position1.x < (position2 + size2).x) and (position1.y > (position2 - size1).y) and (position1.y < (position2 + size2).y)
