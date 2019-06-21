"""
class to represent individual games
"""


class Game:

    def __init__(self):
        self.event = None
        self.site = None
        self.date = None
        self.round = None
        self.white = None
        self.black = None
        self.result = None
        self.variant = None
        self.w_elo = 0
        self.b_elo = 0
        self.moves = None
        self.timecont = 0
        self.end_time = None
        self.term = None

    def __repr__(self):
        return f"""
        Game object:
            Site: {self.site}
            Date: {self.date}
            Event: {self.event}
            Round: {self.round}
            White: {self.white}
            Black: {self.black}
            Result: {self.result}
            Variant: {self.variant}
            White elo: {self.w_elo}
            Black elo: {self.b_elo}
            Time Control: {self.timecont}
            End Time: {self.end_time}
            Termination: {self.term}
            Moves:
            {self.moves}
        """



