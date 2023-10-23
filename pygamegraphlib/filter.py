class Filter:
    def __init__(self, cutoff):
        self.cutoff = min(1.0, max(0.0, cutoff))
        self.buf = 0.0

    def process(self, sample):
        self.buf += self.cutoff * (sample - self.buf)
        return self.buf
