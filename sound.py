import pygame as pg
import json
import random
pg.mixer.pre_init(buffer=1024)
pg.mixer.init(buffer=1024)

class MusicQueue:
    def __init__(self):
        with open("assets/music.json", "r") as fp:
            musicdata = json.loads(fp.read())

        self.sky = []
        self.ground = []
        self.cave = []

        for song in musicdata["sky"]:
            songsound = pg.mixer.Sound(song["file"])
            songsound.set_volume(song["gain"])
            self.sky.append(songsound)
        
        for song in musicdata["cave"]:
            songsound = pg.mixer.Sound(song["file"])
            songsound.set_volume(song["gain"])
            self.cave.append(songsound)

        for song in musicdata["overworld"]:
            songsound = pg.mixer.Sound(song["file"])
            songsound.set_volume(song["gain"])
            self.ground.append(songsound)

        random.shuffle(self.sky)
        random.shuffle(self.ground)
        random.shuffle(self.cave)

        self.timer = 4 * 60

    def update(self, deltatime, player_y):
        if self.timer > 4 * 60:
            self.timer = 0
            if player_y < -32 * 32:
                region = self.sky
            elif player_y > 8 * 32:
                region = self.cave
            else:
                region = self.ground 
            region[0].play()
            region.append(region.pop(0))
        
        self.timer += deltatime



JUMP = pg.mixer.Sound("assets/sounds/effects/jump.ogg")
EAT = pg.mixer.Sound("assets/sounds/effects/eat.ogg")
BREAK = pg.mixer.Sound("assets/sounds/effects/break.ogg")
HIT = pg.mixer.Sound("assets/sounds/effects/hit.ogg")
SWING = pg.mixer.Sound("assets/sounds/effects/swing.ogg")
DAMAGE = pg.mixer.Sound("assets/sounds/effects/damage.ogg")

JUMP.set_volume(0.05)
BREAK.set_volume(0.1)
SWING.set_volume(0.1)
HIT.set_volume(0.1)
DAMAGE.set_volume(0.1)
