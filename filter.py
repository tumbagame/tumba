from vector import Vector


class Filter:
    def __init__(self, cutoff, initial=0):
        self.value = initial
        self.cutoff = cutoff

    def process(self, sample):
        self.value += self.cutoff * (sample - self.value)
        return self.value


class VectorFilter:
    def __init__(self, cutoff, initial=Vector()):
        self.x = Filter(cutoff, initial.x)
        self.y = Filter(cutoff, initial.y)

    def process(self, vector):
        return Vector(self.x.process(vector.x), self.y.process(vector.y))
