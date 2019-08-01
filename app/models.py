from app import app, db
import datetime
from decimal import Decimal

#########################################################
#                         Models                        #
#########################################################
class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    points = db.Column(db.Numeric)
    goal = db.Column(db.Integer, default = 700)
    negThoughts = db.Column(db.Integer, default = 0)
    CBTs = db.Column(db.Integer, default = 0)

    def cash(self) -> str:
        return '${:,.2f}'.format(self.points / 100)

    def percent(self) -> str:
        return '{:,.2f}%'.format(100 * self.points / self.goal)

class CBT(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    A = db.Column(db.String,  nullable = False)
    B = db.Column(db.String,  nullable = False)
    C = db.Column(db.String,  nullable = False)
    D = db.Column(db.String,  nullable = False)
    E = db.Column(db.String,  nullable = False)
    when = db.Column(db.DateTime, default=datetime.datetime.now)



class BG(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    BG = db.Column(db.Integer,  nullable = False)
    insulin = db.Column(db.Integer,  nullable = False)
    when = db.Column(db.DateTime, default=datetime.datetime.now)

    def color(self) -> str:
        if 80 < self.BG < 120:
            return "table-success"
        elif self.BG <= 160:
            return "table-warning"
        else:
            return "table-danger"

class WeightLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Integer,  nullable = False)
    when = db.Column(db.DateTime, default=datetime.datetime.now)

class PointsLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    points = db.Column(db.Numeric,  nullable = False)
    message = db.Column(db.String,  nullable = False)
    when = db.Column(db.DateTime, default=datetime.datetime.now)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Integer,  nullable = False)
    cost = db.Column(db.Integer, nullable=False)
    purchased = db.Column(db.Boolean, default=False)


class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    carbs = db.Column(db.Integer,  nullable = False)

class FoodLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    carbs = db.Column(db.Integer,  nullable = False)
    when = db.Column(db.DateTime, default=datetime.datetime.now)

class Boardgame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    lastPlayed = db.Column(db.DateTime)
    minPlayers = db.Column(db.Integer,  nullable = False)
    maxPlayers = db.Column(db.Integer,  nullable = False)
    #boardgame subcategory / expansion ???
    eugeneRating = db.Column(db.Integer)
    annieRating = db.Column(db.Integer)
    #isCoop
    #Player type: 2 player, 3-5, party
    #    bggid
    #play time
    #iswallofshame
    #genre - eurogame, ameritash, party game

class BoardgameLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    boardgame_id = db.Column(db.Integer,  nullable = False)
    when = db.Column(db.DateTime, default=datetime.datetime.now)
    notes = db.Column(db.String)
    no_players = db.Column(db.Integer,  nullable = False)
    #winner
    #eugenepoints
    #annie points



class Daily(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    subtype = db.Column(db.String, nullable = True)
    availableAfter = db.Column(db.Integer, nullable = False, default = 0)
    availableUntil = db.Column(db.Integer, nullable = False, default = 24)
    completed = db.Column(db.Boolean, default = False, nullable = False)
    completedLast = db.Column(db.DateTime)
    points = db.Column(db.Integer, nullable = False, default = 0)
    isWork = db.Column(db.Boolean, default = False)

    def json(self):
        return '{"name": "' + self.name + '",\n"id":'+str(self.id)+'}'

class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    reps = db.Column(db.Integer, default = 1)
    sets = db.Column(db.Integer, default = 1)
    weight = db.Column(db.Integer, default = 0)
    vest = db.Column(db.Boolean, default = False)
    completed = db.Column(db.Boolean, default = False)

    def json(self) -> str:
        return '{"name": "' + self.name + '",\n"id":'+str(self.id)+'}'

#########################################################
#                          Stats                        #
#########################################################


class DailyStats():
    def __init__(self, dailies):
        hour = datetime.datetime.now().hour
        self.completedCount = len(list(filter(lambda x: (x.completed == True), dailies)))
        self.missedCount =  len(list(filter(lambda x: (x.completed == False and hour > x.availableUntil), dailies)))
        self.availableCount =  len(list(filter(lambda x: (hour >= x.availableAfter), dailies)))
        self.questCount = self.availableCount + self.missedCount
        self.completedPercent = str(int(100.0 * self.completedCount / self.availableCount))
        self.missedPercent = str(int(100.0 * self.missedCount / self.availableCount))

class FoodStats():
    def __init__(self, foodLogs):
        self.carbs = 0
        self.max = 135
        for log in foodLogs:
            self.carbs += log.carbs

        hour = datetime.datetime.now().hour

        if hour <= 10:
            thirds = 1
        elif hour <= 16:
            thirds = 2
        else:
            thirds = 3

        self.percent = int(100 * self.carbs / self.max)
        #Prorated percent of carbs based on part of day.
        self.curPercent = int(100 * self.carbs / (self.max * thirds / 3))

        if self.curPercent <= 90:
            self.color = "bg-success"
        elif self.curPercent <= 112:
            self.color = "bg-warning"
        else:
            self.color = "bg-danger"

def addPoints(db, points: Decimal, message: str = "No message set") -> None:
    player = db.session.query(Player).get(1)   
    player.points += points
    db.session.commit()

    db.session.add(PointsLog(points=points, message = message))
    db.session.commit()


