from itertools import product
from random import choice


class MonopolyProbabilities():
    """It calculates the probability of finishing at a particular land after a roll through a Montecarlo simulation.

    Monopoly has 40 squares called lands (we enumerate them starting from 0),
    and the players move around them using two dice.
    You can find a Monopoly board at this link, it will be helpful:
    https://c8.alamy.com/comp/BF7EFX/monopoly-board-game-BF7EFX.jpg

    Without extra variables, the task of this function would be easy if Monopoly didn't have some rules that
    make this harder:
    When you go on land 30 you always finish at land 10.
    When you go on Community Chest(lands 2, 17, 23) you draw a card, 2/16 cards will move you:
        1.  Advance to GO
        2.  Go to JAIL
    When you go on Community Chest you draw a card, 10/16 cards will move you:
        1.  Advance to GO
        2.  Go to JAIL
        3.  Go to C1
        4.  Go to E3
        5.  Go to H2
        6.  Go to R1
        7.  Go to next R (railway company)
        8.  Go to next R
        9.  Go to next U (utility company)
        10. Go back 3 squares.
    These are the only rules that this function considers.
    """

    def __init__(self):
        self.__make_dice_possibilities()
        self.appearances_of_each_land = {key: 0 for key in range(40)}

    def __make_dice_possibilities(self):
        all_faces_of_dice = range(1, 7)
        all_combination_of_two_dices = list(product(all_faces_of_dice, all_faces_of_dice))
        self.dice_possibilities = list(map(sum, all_combination_of_two_dices))

    def __call__(self):
        """It returns probabilities"""
        self.__run_simulation()
        probabilities = self.__make_probabilities()
        return probabilities

    def __run_simulation(self):
        land = 0
        for _ in range(10**6):
            roll = choice(self.dice_possibilities)
            land = (land+roll) % 40
            land = self.__get_land_considering_variables(land)
            self.appearances_of_each_land[land] += 1

    def __get_land_considering_variables(self, land):
        if land == 30:
            return 10
        if land == 2:
            return choice([0, 10]+[2 for _ in range(14)])
        if land == 17:
            return choice([0, 10]+[17 for _ in range(14)])
        if land == 23:
            return choice([0, 10]+[23 for _ in range(14)])
        if land == 7:
            return choice([0, 10, 11, 24, 39, 5, 15, 15, 12, 4]+[7 for _ in range(6)])
        if land == 22:
            return choice([0, 10, 11, 24, 39, 5, 25, 25, 28, 19]+[22 for _ in range(6)])
        if land == 33:
            return choice([0, 10, 11, 24, 39, 5, 35, 35, 12, 29]+[33 for _ in range(6)])
        return land

    def __make_probabilities(self):
        probabilities = dict()
        for land, appearances in self.appearances_of_each_land.items():
            probabilities[land] = f"{round((appearances/10**6)*100, 2)}%"
        return probabilities


print(MonopolyProbabilities()())
