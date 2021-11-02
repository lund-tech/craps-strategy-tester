import random

SUPPORTED_BET_TYPES = ["Pass", "Place", "Field", "Pass Odds"]
FIELD_PAYOUT_ROLLS = [2, 3, 4, 9, 10, 11, 12]
FIELD_PAYOUTS = [2, 1, 1, 1, 1, 1, 3]
COMING_OUT_PAYOUT_ROLLS = [7, 11]
COMING_OUT_LOSING_ROLLS = [2, 3, 12]
PLACE_POSITIONS = [4, 5, 6, 8, 9, 10]
PLACE_PAYOUTS = [9/5, 7/5, 7/6, 7/6, 7/5, 9/5]
PLACE_ODDS_PAYOUTS = [2/1, 3/2, 6/5, 6/5, 3/2, 2/1]

def roll(n_dice=2, die_faces=6):
    results = []
    for n in range(n_dice):
        roll = random.randint(1,die_faces)
        results.append(roll)
    return sum(results)

class BetPosition:
    def __init__(self, bet_type, number_placed=None):
        self.type = str(bet_type)
        self.place_number = int(number_placed)
        if self.type not in SUPPORTED_BET_TYPES:
            raise ValueError(f"Bet Type {self.type} is not supported.")
        elif self.type == "Place" and self.place_number not in PLACE_POSITIONS:
            raise ValueError(f"A Place Bet cannot be made on {self.place_number}.")
        
        self.bet_value = 0
        self.on_payout = 0
        self.set_payout(False)

    def set_payout(self, point_on, roll=None):
        payout_multiplier = 0
        clear_after_pay = False
        if self.type == "Pass" and point_on == False:
            payout_multiplier = 1
        elif self.type == "Pass" and point_on == True:
            payout_multiplier = 2
            clear_after_pay = True
        elif self.type == "Field":
            position_index = FIELD_PAYOUT_ROLLS.index(roll)
            payout_multiplier = FIELD_PAYOUTS[position_index]
            clear_after_pay = True
        elif self.type == "Place" and point_on == True:
            position_index = PLACE_POSITIONS.index(self.place_number)
            payout_multiplier = PLACE_PAYOUTS[position_index]
        elif self.type == "Pass Odds" and point_on == True:
            position_index = PLACE_POSITIONS.index(self.place_number)
            payout_multiplier = PLACE_ODDS_PAYOUTS[position_index]
            clear_after_pay = True
        else:
            payout_multiplier = 0

        payout = self.bet_value * payout_multiplier
        self.on_payout = [payout, clear_after_pay]

    def pay_out(self):
        payout, clear_after_pay = self.on_payout
        if clear_after_pay == True:
            self.reset()
        return payout

    def reset(self):
        self.bet_value = 0

class Table:
    def __init__(self, minimum_bet):
        self.last_roll = None
        self.point_on = False
        self.point = None
        self.unit = minimum_bet
        self.all_bets = self.initialize_bets()

    def initialize_bets(self):
        self.pass_bet = BetPosition("Pass")
        self.pass_odds_bet = BetPosition("Pass Odds")
        self.field_bet = BetPosition("Field")
        self.place_4_bet = BetPosition("Place", 4)
        self.place_5_bet = BetPosition("Place", 5)
        self.place_6_bet = BetPosition("Place", 6)
        self.place_8_bet = BetPosition("Place", 8)
        self.place_9_bet = BetPosition("Place", 9)
        self.place_10_bet = BetPosition("Place", 10)
        self.all_place_bets = [self.place_4_bet, self.place_5_bet, self.place_6_bet, self.place_8_bet, self.place_9_bet, self.place_10_bet]

        return [self.pass_bet, self.pass_odds_bet, self.field_bet, self.place_4_bet, self.place_5_bet, self.place_6_bet, self.place_8_bet, self.place_9_bet, self.place_10_bet]

    def new_roll(self, roll):
        self.set_bet_payouts(roll)
        self.roll_winnings = 0
        self.handle_field(roll)
        if self.point_on == False:
            self.handle_coming_out_roll(roll)
        else:
            self.handle_point_on_roll(roll)
        self.bets_on_table = self.sum_all_bets()

        return self.point_on, self.point, self.roll_winnings, self.bets_on_table

    def handle_coming_out_roll(self, roll):
        if roll in COMING_OUT_PAYOUT_ROLLS:
            self.roll_winnings += self.pass_bet.payout()
        elif roll in COMING_OUT_LOSING_ROLLS:
            self.pass_bet.reset()
        else:
            self.point_on = True
            self.point = roll
            self.check_for_bet_on_point_place()

    def handle_point_on_roll(self, roll):
        if roll == self.point:
            self.roll_winnings += self.pass_bet.payout + self.pass_odds_bet.payout
            self.pass_bet.reset()
            self.point_on = False

    def handle_field(self, roll):
        if roll in FIELD_PAYOUT_ROLLS:
            self.roll_winnings += self.field_bet.payout()
        self.field_bet.reset()

    def check_for_bet_on_point_place(self):
        for index, place in enumerate(PLACE_POSITIONS):
            if place == self.point:
                place_to_clear = self.all_place_bets[index]
                self.roll_winnings += place_to_clear.bet_value
                place_to_clear.reset()

    def set_bet_payouts(self, roll):
        for bet in self.all_bets:
            bet.set_payout_multiplier(self.point_on, roll)

    def sum_all_bets(self):
        bet_total = 0
        for bet in self.all_bets:
            bet_total += bet.bet_value

        return bet_total