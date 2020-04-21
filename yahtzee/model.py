
import itertools
import random

import numpy as np
import pandas as pd

class Scorecard:
  
  numberWords = {
    1: "ones",  2: "twos",   3: "threes", 4: "fours",  5: "fives",
    6: "sixes", 7: "sevens", 8: "eights", 9: "nines", 10: "tens",
    11: "elevens",  12: "twelves",    13: "thirteens", 14: "fourteens", 15: "fifteens",
    16: "sixteens", 17: "seventeens", 18: "eighteens", 19: "nineteens", 20: "twenties"
  }
  
  MIN_DICE_FACES = 6
  MAX_DICE_FACES = len(numberWords)

  def __init__(self, numberOfDiceFaces=6):
    
    # CHECK: we support the number of dice faces
    if numberOfDiceFaces < Scorecard.MIN_DICE_FACES or numberOfDiceFaces > Scorecard.MAX_DICE_FACES:
      raise ValueError("dice faces must be between {} and {}"
                        .format(Scorecard.MIN_DICE_FACES, Scorecard.MAX_DICE_FACES))
    
    # general scoring sections
    lowerRows = [
      ("Three of a kind", None),
      ("Four of a kind",  None),
      ("Full House",      None),
      ("Small Straight",  None),
      ("Large Straight",  None),
      ("Chance",          None),
      ("Yahtzee",         None),
    ]
    
    # generate sections for each dice face
    upperRows = []
    for num in range(1, numberOfDiceFaces+1):
      upperRows.append((Scorecard.numberWords[num], None))
    
    # store the scorecard
    self.scorecard = upperRows + lowerRows
    
    self.numberOfDiceFaces = numberOfDiceFaces
    
  def getRowNames(self):
    return [x[0] for x in self.scorecard]
  
  def getRowCount(self): return len(self.scorecard)
  
  @staticmethod
  def hasStraight(uniqueSortedDice, length):
    """ Is there a straight sequence of <length> dice within the list of unique, sorted dice"""
    
    # if we don't have enough dice for a straight
    if len(uniqueSortedDice) < length:
      return False
    
    # check if we can find a sequence in the list of unique, sorted dice
    for comb in itertools.combinations(uniqueSortedDice, length):
      if comb == tuple(range(comb[0], comb[0]+length)):
        return True
    
    # no dice
    return False
  
  @staticmethod
  def hasFullHouse(diceCounts):
    """ Do we have a full house, i.e., only two unique dice values """
    return len(diceCounts.index) == 2
  
  
  def calculatePossibleScore(self, diceValues, sections=None):
    """
    # What are the possible scores given the dice values
    #
    # diceValues: (list) of dice values to use
    # sections:   (list) name of section(s) to calculate, default is all
    """
    
    results = Scorecard(self.numberOfDiceFaces)
    
    # filter the results so we only calculate for the sections we want
    if sections is not None:
      results = {k:v for k,v in results.items() if k in sections}

    diceValues.sort()
    
    diceCounts = pd.Series(diceValues).value_counts()
    uniqueSortedDice = sorted(diceCounts.index.to_list())
    

    has3OfAKind = (diceCounts > 2).any()
    has4OfAKind = (diceCounts > 3).any()
    hasYahtzee  = len(diceCounts) == 1

    hasFullHouse = Scorecard.hasFullHouse(diceCounts)
    
    hasSmallStraight = Scorecard.hasStraight(uniqueSortedDice, len(diceValues) - 1)
    haslargeStraight = Scorecard.hasStraight(uniqueSortedDice, len(diceValues))

  @staticmethod
  def _calcHighestNumberOfKind(diceValues):
    """ Return the  """
    pass
  
  

class Player:
  def __init__(self, name, scorecard):
    self.name      = name
    self.scorecard = scorecard
    
  def getName(self):      return self.name
  def getScorecard(self): return self.scorecard

class Game:
  
  def __init__(self, numberOfDice=5, numberOfDiceFaces=6):
    self.numberOfDice      = numberOfDice
    self.numberOfDiceFaces = numberOfDiceFaces

    self.players = []
  
  def rollDice(self, numberOfDice):
    """ Roll <numberOfDice> dice """
    
    if numberOfDice < 1:
      raise ValueError("have to roll at least 1 die")
    
    # make sure we can roll this many dice
    if numberOfDice > self.numberOfDice:
      raise SystemError("tried to roll {} dice, but only have {} in the game"
                          .format(numberOfDice, self.numberOfDice))
    
    # roll the dice
    return [random.randint(1, self.numberOfDiceFaces) for _ in range(numberOfDice)]
  

  
  def addPlayer(self, playerName):
    """ Add a player called <playerName> to the game """
    
    # CHECK: player name is a string
    if not isinstance(playerName, str):
      raise TypeError("player name must be a string")
    
    # CHECK: player name is unique
    if playerName in [x.name for x in self.players]:
      raise ValueError("player name is already taken")
    
    # CHECK: game hasn't started
    if self.hasStarted():
      raise SystemError("can't add a player after the game has started")
    
    # create a new player with a blank scorecard
    scorecard = Scorecard(self.numberOfDiceFaces)
    player    = Player(playerName, scorecard)
    self.players.append(player)
  

  def removePlayer(self, playerName):
    """ Remove the player <playerName> from the game """
    
    # CHECK: player name is a string
    if not isinstance(playerName, str):
      raise TypeError("player name must be a string")
    
    # CHECK: game hasn't started
    if self.hasStarted():
      raise SystemError("can't remove a player after the game has started")
    
    # remove the player
    for player in self.players:
      if player.name == playerName:
        self.players.remove(player)
        return
    
    # player wasn't found
    raise ValueError("player {} is not part of this game".format(playerName))
  

  def getNumberOfPlayers(self):
    return len(self.players)
  
  def getPlayers(self): return self.players
  
  def hasStarted(self):
    """ Has the game started """
    pass
  
  