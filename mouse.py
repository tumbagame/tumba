from vector import Vector


class Mouse:
    def __init__(
        self, position=Vector(), velocity=Vector(), left=False, right=False, scroll=0
    ):
        self.position = position
        self.velocity = velocity
        self.left = left
        self.right = right
        self.scroll = scroll
