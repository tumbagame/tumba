import blockprop


class InventorySlot:
    def __init__(self, item=-1, count=0):
        self.item = item
        self.count = count

    def has_item(self):
        return self.item != -1 and self.count > 0

    def __repr__(self):
        return f"[{self.item}, {self.count}]"


class Inventory:
    def __init__(self):
        self.slots = [InventorySlot() for _ in range(24)]

    def add_item(self, item, count=1):
        if item == -1 or count == 0:
            return
        first_open_spot = -1
        for i, slot in enumerate(self.slots):
            if not slot.has_item() and first_open_spot == -1:
                first_open_spot = i

            if slot.item == item:
                slot.count += count
                return

        if first_open_spot != -1:
            self.slots[first_open_spot].item = item
            self.slots[first_open_spot].count = count

    def block_getter(self, index):
        return lambda: self.slots[index]

    def serialize(self):
        out_data = []
        for slot in self.slots:
            out_data.append(slot.item if slot.has_item() else 255)
            out_data.append(slot.count if slot.has_item() else 0)
        return bytes(out_data)

    def load(self, in_bytes):
        for i in range(24):
            item_raw = in_bytes[i * 2 : i * 2 + 2]
            self.slots[i].item = -1 if (item_raw[0] == 255) else item_raw[0]
            self.slots[i].count = item_raw[1]
