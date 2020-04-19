
import itertools
import random

import numpy as np
import pandas as pd

class Scores:
  
  @staticmethod
  def newBlankScoreCard(numberOfDiceFaces=6):
    """ Return a new, blank scorecard """
    
    # general sections
    sections = {
      "three of a kind": None,
      "four of a kind":  None,
      "full house":      None,
      "small straight":  None,
      "large straight":  None,
      "chance":          None,
      "yahtze":          None,
    }
    
    # generate sections for each dice face
    for num in range(1, numberOfDiceFaces+1):
      sections[num] = None
    
    return sections
  
  
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
  
  @staticmethod
  def calculatePossibleScore(diceValues, sections=None):
    """
    # What are the possible scores given the dice values
    #
    # diceValues: (list) of dice values to use
    # sections:   (list) name of section(s) to calculate, default is all
    """
    
    results = Scores.newBlankScoreCard()
    
    # filter the results so we only calculate for the sections we want
    if sections is not None:
      results = {k:v for k,v in results.items() if k in sections}

    diceValues.sort()
    
    diceCounts = pd.Series(diceValues).value_counts()
    uniqueSortedDice = sorted(diceCounts.index.to_list())
    

    has3OfAKind = (diceCounts > 2).any()
    has4OfAKind = (diceCounts > 3).any()
    hasYahtzee  = len(diceCounts) == 1

    hasFullHouse = Scores.hasFullHouse(diceCounts)
    
    hasSmallStraight = Scores.hasStraight(uniqueSortedDice, len(diceValues)-1)
    haslargeStraight = Scores.hasStraight(uniqueSortedDice, len(diceValues))

  @staticmethod
  def _calcHighestNumberOfKind(diceValues):
    """ Return the  """
    pass
  
  def __init__(self, playerList):
    
    if not isinstance(playerList, list):
      raise TypeError("playerList must be a list")
    
    for player in playerList:
      if not isinstance(player, str):
        raise TypeError("player names must all be strings")
    
    if len(playerList) < 1:
      raise ValueError("must have at least one player")
    
    # create a score card for each player, key-ed to their name
    self.scorecards = {player: Scores.newBlankScoreCard() for player in playerList}
    
  def getNumberOfPlayers(self):
    return len(self.scorecards)
  
  
class Model:
  
  def __init__(self, numberOfDice=5, numberOfDiceFaces=6):
    self.numberOfDice      = numberOfDice
    self.numberOfDiceFaces = numberOfDiceFaces
  
  
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
  
  def hasStarted(self):
    """ Has the game started """
    pass
  
  def addPlayer(self, name):
    pass
  
  def removePlayer(self, name):
    pass
  
  