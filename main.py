import pandas as pd
from dataclasses import dataclass, field
import random

# assumes smartness (narrow guesses after eliminations, considers own hand in guess)

NUM_STARTING_PLAYERS = 5
PLAYS = (0, 5)
SEED = 20240101

@dataclass
class Player:
    id: int
    plays: set[int] = PLAYS
    current_hand: int = 0
    current_guess: int = 0
    record: dict[int, int] = field(default_factory=
                                   lambda : {x: 0 for x in range(1, NUM_STARTING_PLAYERS + 1)})
    
    def generate_hand(self) -> int:
        self.current_hand = self.plays[random.randint(0, len(self.plays) - 1)]
        return self.current_hand
    
    def random_hand(self) -> int:
        return self.plays[random.randint(0, len(self.plays) - 1)]

    def guess(self, num_players: int) -> int:
        """Guess always happens after hand generation"""
        others_hands = sum([self.random_hand() for _ in range(num_players - 1)])
        self.current_guess = self.current_hand + others_hands
        return self.current_guess
    
    def win(self, nth_place: int) -> None:
        self.record[nth_place] += 1
    
@dataclass
class Game:
    players: list[Player]
    next_winner: int = 1
    next_player: int = 0
    is_done: bool = False
    record: dict[int, int] = field(default_factory=
                                   lambda : {x: 0 for x in range(1, NUM_STARTING_PLAYERS + 1)})

    def __post_init__(self) -> None:
        self.alive_players = self.players[:]

    def round(self) -> None:
        guesser = self.alive_players[self.next_player]
        sum_hands = 0
        for player in self.alive_players:
            sum_hands += player.generate_hand()
        
        guess = guesser.guess(len(self.alive_players))

        if guess == sum_hands:
            guesser.win(self.next_winner)
            self.record[self.next_winner] = guesser.id
            self.next_winner += 1
            self.alive_players = [player for player in self.alive_players if player.id != guesser.id]
            self.next_player = self.next_player % len(self.alive_players)
        
        else: 
            self.next_player = (self.next_player + 1) % len(self.alive_players)
        
        self.check_done()
        
    def check_done(self) -> bool:
        if len(self.alive_players) == 1:
            player = self.alive_players[0]
            player.record[NUM_STARTING_PLAYERS] += 1
            self.record[self.next_winner] = player.id
            self.is_done = True
        return self.is_done
    

def play_game(players: list[Player]) -> Game:
    g = Game(players=players)
    while not g.is_done:
        g.round()
    return g

def simulate(num_simulations: int) -> list[Player]:
    players = []
    for i in range(NUM_STARTING_PLAYERS):
        p = Player(id = i + 1)
        players.append(p)
    for _ in range(num_simulations):
        g = play_game(players)
        # print(g.record)

    return players


def main() -> pd.DataFrame:
    player_states = simulate(10000)
    first_place = [player.record.get(1, 0) for player in player_states]
    second_place = [player.record.get(2, 0) for player in player_states]
    third_place = [player.record.get(3, 0) for player in player_states]
    fourth_place = [player.record.get(4, 0) for player in player_states]
    fifth_place = [player.record.get(5, 0) for player in player_states]
    results = pd.DataFrame({
        "1st Place": first_place,
        "2nd Place": second_place,
        "3rd Place": third_place,
        "4th_Place": fourth_place,
        "5th Place": fifth_place,
    })
    
    return results

if __name__ == "__main__":
    main()