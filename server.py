import socket
from player import Player
from vector import Vector
from world import World
import blockprop
import netencode
import entity

class Server:
    def __init__(self, port=2828):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(("0.0.0.0", port))
        self.sock.listen(5)
        self.loops = 0
        self.players = {}

        self.world = World(True)

        self.offset_x = 0
        self.offset_y = 0
        self.tps = 1

    def shutdown(self):
        self.sock.close()

    def _parse(self, data):
        decoder = netencode.PacketDecoder(data)
        out_dict = {}
  
        out_dict["id"] = netencode.decode_byte(decoder.pop_data(1))
        out_dict["name"] = (decoder.pop_data(8)).decode()
        out_dict["x"] = netencode.decode_int(decoder.pop_data(4))
        out_dict["y"] = netencode.decode_int(decoder.pop_data(4))
        out_dict["set"] = bool(netencode.decode_byte(decoder.pop_data(1)))
        out_dict["bx"] = netencode.decode_int(decoder.pop_data(4))
        out_dict["by"] = netencode.decode_int(decoder.pop_data(4))
        out_dict["block"] = netencode.decode_short(decoder.pop_data(2))
        out_dict["craft"] = netencode.decode_short(decoder.pop_data(2))
        return out_dict

    # 2048 block size
    # 1024 byte chunk, 48 byte inventory
    def update(self, deltatime):


        conn, addr = self.sock.accept()
        data = conn.recv(2048)
        parsed = self._parse(data)
        player_id = parsed["id"]
        if player_id not in self.players:
            self.players[player_id] = Player(
                player_id, parsed["name"], Vector(parsed["x"], parsed["y"])
            )
        else:
            self.players[player_id].position = Vector(parsed["x"], parsed["y"])

        to_craft = parsed["craft"]
        if to_craft != -1:
            self.players[player_id].inventory.craft(to_craft)

        chunk_x = int((parsed["x"] - 512) / (32 * 32)) + self.offset_x
        chunk_y = int((parsed["y"] - 512) / (32 * 32)) + self.offset_y
        block = parsed["block"]

        if block != -2:
            old_block = self.world.get_block(int(parsed["bx"]), int(parsed["by"]))
            if block == -1:
                self.players[player_id].inventory.add_item(
                    blockprop.BLOCKS[old_block].drops, 1
                )
                self.world.set_block(int(parsed["bx"]), int(parsed["by"]), -1)
            else:
                if (
                    self.players[player_id].inventory.slots[block].has_item()
                    and old_block == -1
                ):
                    self.world.set_block(
                        int(parsed["bx"]),
                        int(parsed["by"]),
                        self.players[player_id].inventory.slots[block].item,
                    )
                    self.players[player_id].inventory.remove_item(block)

        chunk_raw = self.world.get_chunk(chunk_x, chunk_y).serialize()
        inventory_raw = self.players[player_id].inventory.serialize()
        chunk_position_data = netencode.encode_int(chunk_x) + netencode.encode_int(chunk_y)
        conn.sendall(chunk_raw + inventory_raw + chunk_position_data)
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
