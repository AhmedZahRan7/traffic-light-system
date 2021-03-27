MAX_COUNTER = 4

class normalAgent:
    counter = 0
    way = 0

    def select_action(self, state, conn=None, vehicle_ids=None):
        self.counter += 1
        if self.counter >= MAX_COUNTER:
            self.counter = 0
            self.way = (self.way+1)%4
        return self.way