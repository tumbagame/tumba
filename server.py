import socket
from player import Player
from vector import Vector
from world import World
import blockprop
import netencode
import entity
import physics
import random
import json
import zlib
import chunking
import version

class Server:
    def __init__(self, port=2828):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True
        self.filename = "assets/saves/world.tumba"
        self.offlineplayers = {}
        trying = True
        port_offset = 0
        tries = 0
        while trying:
            if tries > 5:
                self.running = False
                trying = False
            try:
                self.sock.bind(("0.0.0.0", port + port_offset))
                trying = False
            except OSError as e:
                print("Error: Port already in use, changing port")
                with open("assets/settings.json", "r") as fp:
                    in_settings = json.loads(fp.read())
                in_settings["port"]+=1
                with open("assets/settings.json", "w") as fp:
                    fp.write(json.dumps(in_settings, indent=4))
                port_offset += 1
            

        
        self.sock.listen(5)
        self.loops = 0
        self.players = {}
        self.entities = []
        self.spawn_timer = 0



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
        out_dict["attack"] = netencode.decode_byte(decoder.pop_data(1))

        return out_dict

    def _update_entities(self, deltatime):
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
            if closest_distance > 64*32:
                ent.lifetime = 0
            for other_ent in self.entities:
                if other_ent.id != ent.id:

                    if physics.hitbox_collide(ent.position + ent.hitbox_offset, ent.hitbox_size, other_ent.position + other_ent.hitbox_offset, other_ent.hitbox_size):
                        if ent.gravity and ent.damage_cooldown <= 0 and not other_ent.is_hostile and not other_ent.is_scared:
                            ent.velocity = (ent.position - other_ent.position).norm() * physics.JUMP_HEIGHT
                            ent.health -= other_ent.damage
                            ent.damage_cooldown = 1

            x_acceleration = 0
            if ent.gravity:
                down_acceleration = physics.GRAVITY
            else:
                down_acceleration = 0
            if ent.is_hostile and ent.damage_cooldown < 0.1:
                if closest_distance < 8*32:
                    x_acceleration = physics.ENTITY_ACCELERATION  * (1 if (closest_player.position.x > ent.position.x) else -1)
            if ent.is_scared and ent.damage_cooldown < 0.1:
                if closest_distance < 8*32:
                    x_acceleration = physics.ENTITY_ACCELERATION  * (-1 if (closest_player.position.x > ent.position.x) else 1)

            if abs(ent.velocity.x) > physics.ENTITY_SPEED and ent.damage_cooldown < 0.1:
                ent.velocity.x = (ent.velocity.x / abs(ent.velocity.x)) * physics.ENTITY_SPEED
                
            vel = ent.velocity * deltatime + Vector(x_acceleration, down_acceleration) * 0.5 * deltatime * deltatime
            frame = ent.animation.get_frame(0.1)
            ent.position.y += vel.y
            standing = False
            if self.world.collide(ent.position + ent.hitbox_offset, ent.hitbox_size):
                ent.position.y -= vel.y
                ent.velocity.y = 0
                standing = True
            ent.position.x += vel.x
            if self.world.collide(ent.position + ent.hitbox_offset, ent.hitbox_size):
                ent.position.x -= vel.x
                ent.velocity.x = 0
                if (ent.is_hostile or ent.is_scared) and ent.gravity and standing:
                    ent.velocity.y = -physics.JUMP_HEIGHT

            ent.velocity += Vector(x_acceleration, down_acceleration) * deltatime

            ent.lifetime -= deltatime
            if ent.lifetime > 0 and ent.health > 0:
                next_entities.append(ent)
            elif ent.health < 1 and ent.drop != -1:
                closest_player.inventory.add_item(ent.drop)

            if ent.damage_cooldown >= 0:
                ent.damage_cooldown -= deltatime

        self.entities = next_entities

        def get_entity_distance(ent):
            if self.players:
                closest_player = self.players[list(self.players)[-1]]
                closest_distance = (closest_player.position - ent.position).length()
                for player in self.players:
                    dst = (self.players[player].position - ent.position).length() 
                    if dst < closest_distance:
                        closest_player = self.players[player]
                        closest_distance = dst
                return closest_distance
            return 0
        
        if len(self.entities) > 8:
            ent_sorted = sorted(self.entities, key = get_entity_distance)
            self.entities = ent_sorted[:8]

    # 2048 block size
    # 1024 byte chunk, 48 byte inventory
    def update(self, deltatime):
        

        self._update_entities(deltatime)

        self.spawn_timer += deltatime
        if self.spawn_timer > 30:
            for p in self.players:
                play = self.players[p]
                for ent in entity.ENTITIES:
                    can_spawn = int(self.players[p].position.y/32) in range(ent.spawn_min, ent.spawn_max)
                    if can_spawn and (random.randint(0,1000) * 0.001 < ent.spawn_rate):
                        new_ent = ent.clone()
                        for i in range(10):
                            random_pos = (Vector(random.randint(0,1000), random.randint(0,1000)) * 0.002 - Vector(1,1)).norm() * 128
                            new_ent.with_position(play.position + random_pos)
                            if not self.world.collide(new_ent.position + new_ent.hitbox_offset, new_ent.hitbox_size):
                                self.entities.append(new_ent)
                                break
                            
            self.spawn_timer = 0

        conn, addr = self.sock.accept()
        data = conn.recv(2048)
        parsed = self._parse(data)
        player_id = parsed["id"]
        if player_id not in self.players:
            self.players[player_id] = Player(
                player_id, parsed["name"], Vector(parsed["x"], parsed["y"])
            )
            if player_id in self.offlineplayers:
                self.players[player_id].deserialize(self.offlineplayers[player_id])
                del self.offlineplayers[player_id]
        else:
            self.players[player_id].position = Vector(parsed["x"], parsed["y"])

        self.players[player_id].packet_timer = 0
        new_players = {player_id: self.players[player_id]}
        for p in self.players:
            if p != player_id:
                self.players[p].packet_timer += deltatime
                if self.players[p].packet_timer < 10:
                    new_players[p] = self.players[p]
                else:
                    self.offlineplayers[p] = self.players[p].file_serialize()

        self.players = new_players

        to_attack = parsed["attack"]
        if to_attack != 255 and parsed["block"] not in [-1,-2]:
            if blockprop.BLOCKS[self.players[player_id].inventory.slots[parsed["block"]].item].damage > 1:
                self.players[player_id].inventory.remove_item(parsed["block"])
                self.entities.append(entity.ENTITIES[2].clone().with_position(self.players[player_id].position - (entity.ENTITIES[2].hitbox_size * 0.5) + Vector(16,32)).with_damage(blockprop.BLOCKS[self.players[player_id].inventory.slots[parsed["block"]].item].damage))

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
                if self.players[player_id].inventory.slots[block].has_item():
                    if self.players[player_id].inventory.slots[block].item == 10:
                        self.players[player_id].inventory.remove_item(block)
                    elif old_block == -1:
                        self.world.set_block(
                            int(parsed["bx"]),
                            int(parsed["by"]),
                            self.players[player_id].inventory.slots[block].item,
                            True
                        )
                        self.players[player_id].inventory.remove_item(block)
                    elif old_block == 46:
                        if self.players[player_id].inventory.slots[block].item == 8:
                            self.players[player_id].inventory.remove_item(block)
                            self.players[player_id].inventory.add_item(10)
                            
        
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

        player_data = b''
        for p in self.players:
            if p != player_id:
                player_data += self.players[p].serialize()

        if len(player_data) < 136:
            player_data += b'\x00' * (136-len(player_data))

        output_data = chunk_raw + inventory_raw + chunk_position_data + entity_data + player_data + netencode.encode_byte(len(self.entities))
        conn.sendall(output_data)
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



    def save_to_file(self):

        for p in self.players:
            self.offlineplayers[p] = self.players[p].file_serialize()

        

        out_bin = netencode.encode_short(version.SAVEVERSION)

        out_bin += netencode.encode_short(len(self.offlineplayers))
        for p in self.offlineplayers:
            out_bin += self.offlineplayers[p]

        out_bin += netencode.encode_int(self.world.generator.seed)
        for x,y in self.world.chunks:
            chunk = self.world.get_chunk(x,y)
            out_bin += netencode.encode_int(x) + netencode.encode_int(y)
            out_bin += chunk.serialize()

        with open(self.filename, "wb") as fp:
            fp.write(zlib.compress(out_bin))

    def load_from_file(self):
        try:
            with open(self.filename, "rb") as fp:
                in_bytes = zlib.decompress(fp.read())
        except Exception as e:
            print("No save file. Creating new world.")
            return
        save_decoder = netencode.PacketDecoder(in_bytes)
        save_version = netencode.decode_short(save_decoder.pop_data(2))

        player_count = netencode.decode_short(save_decoder.pop_data(2))
        for i in range(player_count):
            pdata = save_decoder.pop_data(49)
            self.offlineplayers[pdata[0]] = pdata
        
        self.world = World(True, netencode.decode_int(save_decoder.pop_data(4)))
        while not save_decoder.is_empty():
            chunk_x = netencode.decode_int(save_decoder.pop_data(4))
            chunk_y = netencode.decode_int(save_decoder.pop_data(4))
            chunk_data = save_decoder.pop_data(1024)
            chunk = chunking.Chunk()
            chunk.load_bytes(chunk_data)
            self.world.set_chunk_reference(chunk_x,chunk_y,chunk)