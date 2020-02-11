from pk import *

class Move:
    def __init__(self):
        self.name = 'None'
        self.type = 0
        self.pp = 0
        self.power = 0
        self.accuracy = 0
        self.category = 0
        self.description = 'None'

    def initializeParameters(self, name, type, cat, power, acc, pp, effect, desc):
        self.name = name
        self.type = PkType[type]
        self.pp = pp
        self.power = power
        self.accuracy = acc
        self.category = PkMoveCategory[cat]
        self.description = desc
    
    def __str__(self):
        return ('Name: %s' % self.name +
            '\nType: %i (%s)' % (self.type, PkIType[self.type].capitalize()) +
            '\nPP: %i' % self.pp +
            '\nPower: %i' % self.power +
            '\nAccuracy: %i' % self.accuracy +
            '\nCategory: %i (%s)' % (self.category, PkIMoveCategory[self.category].capitalize()) +
            # '\nDamage: %i (%s)' % (self.damage, PkIMoveDamage[self.damage]) +
            '\nDescription: %s' % self.description)

moves = [Move()]
moves_map = {}
