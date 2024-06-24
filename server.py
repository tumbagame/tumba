import socket
from player import Player
from vector import Vector
from world import World
import blockprop
import netencode
import entity
import physics
import random
class Server:
    def __init__(self, port=2828):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True
        try:
            self.sock.bind(("0.0.0.0", port))
        except OSError as e:
            self.running = False
            print("Error: Port already in use")
        
        self.sock.listen(5)
        self.loops = 0
        self.players = {}
        self.entities = []


        for _ in range(1):
            self.entities.append(entity.ENTITIES[1].clone().with_position(Vector(random.randint(-320, 320),-5*32)))

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
        next_entities = []
        for ent in self.entities:
            closest_player = Player(0, "", Vector(0,0))
            closest_distance = 9999
            if self.players:
                closest_player = self.players[list(self.players)[-1]]
                closest_distance = (closest_player.position - ent.position).length()
                for player in self.players:
                    dst = (self.players[player].position - ent.position).length() 
                    if dst < closest_distance:
                        closest_player = self.players[player]
                        closest_distance = dst

            

            if ent.gravity:
                down_acceleration = physics.GRAVITY
            if ent.is_hostile:
                if closest_distance < 8*32:
                    ent.velocity.x = physics.ENTITY_SPEED * (1 if (closest_player.position.x > ent.position.x) else -1)
            
            vel = ent.velocity * deltatime + Vector(0, down_acceleration) * 0.5 * deltatime * deltatime
            frame = ent.animation.get_frame(0.1)
            ent.position.y += vel.y
            standing = False
            if self.world.collide(ent.position, Vector(frame.get_width(), frame.get_height())):
                ent.position.y -= vel.y
                ent.velocity.y = 0
                standing = True
            ent.position.x += vel.x
            if self.world.collide(ent.position, Vector(frame.get_width(), frame.get_height())):
                ent.position.x -= vel.x
                ent.velocity.x = 0
                if ent.is_hostile and ent.gravity and standing:
                    ent.velocity.y = -physics.JUMP_HEIGHT

            ent.velocity += Vector(0, down_acceleration) * deltatime

            ent.lifetime -= deltatime
            if ent.lifetime > 0 and ent.health > 0:
                next_entities.append(ent)

        self.entities = next_entities



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
                self.world.set_block(int(parsed["bx"]), int(parsed["by"]), -1, True)
            else:
                if (
                    self.players[player_id].inventory.slots[block].has_item()
                    and old_block == -1
                ):
                    self.world.set_block(
                        int(parsed["bx"]),
                        int(parsed["by"]),
                        self.players[player_id].inventory.slots[block].item,
                        True
                    )
                    
                    self.players[player_id].inventory.remove_item(block)
        
        chunk_raw = self.world.get_chunk(chunk_x, chunk_y).serialize()
        inventory_raw = self.players[player_id].inventory.serialize()
        chunk_position_data = netencode.encode_int(chunk_x) + netencode.encode_int(chunk_y)
        entity_data = b''
        entity_sorted = sorted(self.entities, key =  lambda x: (x.position - self.players[player_id].position).length())
        for index in range(8):
            if index < len(entity_sorted):
                entity_data += entity_sorted[index].serialize()
            else:
                entity_data += entity.ENTITIES[0].serialize()
        conn.sendall(chunk_raw + inventory_raw + chunk_position_data + entity_data)
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
