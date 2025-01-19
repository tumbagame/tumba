import pygame as pg
import json
import random
pg.mixer.init()

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



mq = MusicQueue()
mq.ground[0].play()

JUMP = pg.mixer.Sound("assets/sounds/effects/jump.ogg")
EAT = pg.mixer.Sound("assets/sounds/effects/eat.ogg")
BREAK = pg.mixer.Sound("assets/sounds/effects/break.ogg")

JUMP.set_volume(0.05)
BREAK.set_volume(0.1)
