class BoolTrigger:
    def __init__(self):
        self.prev_state = False

    def is_triggered(self, state):
        if state != self.prev_state:
            self.prev_state = state
            if state:
                return True

        return False
