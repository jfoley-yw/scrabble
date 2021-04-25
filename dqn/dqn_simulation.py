from scrabbler.simulation import Simulation

class DQNSimulation(Simulation):
    def simulate_step(self, action):
        self.exectute_turn(action)
        self.player = 1 - self.player

    def exectute_turn(self, action):
        print("########################## Player %d turn ############################"%(self.player + 1))
        # print("Bag: %s" % "".join(self.bag))
        # print("Player %d rack pre-draw: %s" % (self.player + 1, self.players[self.player].get_rack()))

        self.make_move(action)
        self.generate_new_rack()

    def is_rack_empty(self):
        return self.players[0].is_rack_empty() or self.players[1].is_rack_empty()
