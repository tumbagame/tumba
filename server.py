import socket
from player import Player
from vector import Vector
from world import World
import time


class Server:
    def __init__(self, port=28):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(("0.0.0.0", port))
        self.sock.listen(5)
        self.loops = 0
        self.players = {}

        self.world = World(True)

        self.offset_x = 0
        self.offset_y = 0
        self.tps = 1

    def _parse(self, data):
        out_dict = {}
        pairs = data.split(",")
        for pair in pairs:
            key, val = pair.split(":")
            out_dict[key] = val
        out_dict["id"] = int(out_dict["id"])
        out_dict["x"] = float(out_dict["x"])
        out_dict["y"] = float(out_dict["y"])
        out_dict["set"] = out_dict["set"] == "1"
        out_dict["bx"] = int(out_dict["bx"])
        out_dict["by"] = int(out_dict["by"])
        out_dict["block"] = int(out_dict["block"])
        return out_dict

    def update(self, deltatime):
        conn, addr = self.sock.accept()
        data = conn.recv(2048)
        parsed = self._parse(data.decode())

        self.players[parsed["id"]] = Player(
            parsed["id"], parsed["name"], Vector(parsed["x"], parsed["y"])
        )

        chunk_x = int((parsed["x"] - 512) / (32 * 32)) + self.offset_x
        chunk_y = int((parsed["y"] - 512) / (32 * 32)) + self.offset_y
        if int(parsed["block"]) != -2:
            self.world.set_block(
                int(parsed["bx"]), int(parsed["by"]), int(parsed["block"])
            )

        chunk_raw = self.world.get_chunk(chunk_x, chunk_y).serialize()
        chunk_data = f"{round(self.tps,2)},{chunk_x},{chunk_y}"
        conn.sendall(chunk_raw + chunk_data.encode())
        conn.close()
        self.offset_x += 1
        if self.offset_x > 1:
            self.offset_x = -1
            self.offset_y += 1
        if self.offset_y > 1:
            self.offset_y = -1

        if deltatime < 0.001:
            self.tps = 99.99
        else:
            self.tps = 1.0 / (deltatime)
