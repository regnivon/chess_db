import functools
import operator


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
        return """
        Game object:
            Site: {site}
            Date: {date}
            Event: {event}       
            Round: {round}  
            White: {white}
            Black: {black} 
            Result: {result} 
            Variant: {variant}
            White elo: {welo}  
            Black elo: {belo}   
            Time Control: {time}
            End Time: {end}
            Termination: {term}   
            Moves: 
            {moves}  
        """.format(site=self.site, date=self.date, event=self.event, round=self.round,
                   white=self.white, black=self.black, result=self.result,
                   welo=self.w_elo, belo=self.b_elo, variant=self.variant,
                   time=self.timecont, end=self.end_time, moves=self.moves, term=self.term
                   )
"""
    def __hash__(self):
        l = [self.w_elo, self.b_elo, self.date, self.end_time]
        hashes = [hash(x) for x in l]
        return functools.reduce(operator.xor, hashes, 0)
"""


