import pygame as pg
import control

letters = {
    pg.K_a: "a",
    pg.K_b: "b",
    pg.K_c: "c",
    pg.K_d: "d",
    pg.K_e: "e",
    pg.K_f: "f",
    pg.K_g: "g",
    pg.K_h: "h",
    pg.K_i: "i",
    pg.K_j: "j",
    pg.K_k: "k",
    pg.K_l: "l",
    pg.K_m: "m",
    pg.K_n: "n",
    pg.K_o: "o",
    pg.K_p: "p",
    pg.K_q: "q",
    pg.K_r: "r",
    pg.K_s: "s",
    pg.K_t: "t",
    pg.K_u: "u",
    pg.K_v: "v",
    pg.K_w: "w",
    pg.K_x: "x",
    pg.K_y: "y",
    pg.K_z: "z",
    pg.K_0: "0",
    pg.K_1: "1",
    pg.K_2: "2",
    pg.K_3: "3",
    pg.K_4: "4",
    pg.K_5: "5",
    pg.K_6: "6",
    pg.K_7: "7",
    pg.K_8: "8",
    pg.K_9: "9",
    pg.K_SPACE: " "
}

class Typer:
    def __init__(self):
        self.trigger = control.BoolTrigger()
    def get_char(self,keyboard):
        triggered = self.trigger.is_triggered(bool(keyboard))
        if triggered:
            if keyboard[0] in letters:
                return letters[keyboard[0]]
        return ''