class Vector:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def length(self):
        return (self.x * self.x + self.y * self.y) ** 0.5

    def norm(self):
        return self * (1 / self.length())

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return Vector(self.x * other, self.y * other)

    def __repr__(self):
        return f"[{self.x} {self.y}]"

    def __bool__(self):
        return (abs(self.x) > 0.001) or (abs(self.y) > 0.001)
