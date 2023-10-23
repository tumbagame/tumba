import time
import pygame as pg

# Class to load animation atlases as seperate frames


class Animation:

    def __init__(self, filename, num_animations, frames, fps):
        self.delay = 1/fps

        self.animations = []
        self.index = 0
        self.frame = 0
        self.mirror = False
        self.num_animations = num_animations
        self.num_frames = frames

        atlas = pg.image.load(filename)
        width, height = atlas.get_size()
        frame_width = width // frames
        frame_height = height // num_animations

        for an in range(num_animations):
            anim = []
            for frame in range(frames):
                srf = pg.Surface((frame_width, frame_height), pg.SRCALPHA)
                srf.fill((0,)*4)
                srf.blit(atlas, (-frame*frame_width, -an*frame_height))
                anim.append(srf)
            self.animations.append(anim)

        self.prev_time = time.time()

    def set_animation(self, index):
        self.index = min(max(index, 0), self.num_animations)

    def get_frame(self):
        dt = time.time() - self.prev_time
        if dt > self.delay:
            self.frame = (self.frame + 1) % self.num_frames
            self.prev_time = time.time()

        return pg.transform.flip(self.animations[self.index][self.frame], self.mirror, False)
