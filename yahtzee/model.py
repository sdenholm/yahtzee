
import itertools
import random

from collections import OrderedDict

import functools

import numpy as np
import pandas as pd

from enum import Enum

class Scorecard:
  
  numberWords = {
    1: "ones",  2: "twos",   3: "threes", 4: "fours",  5: "fives",
    6: "sixes", 7: "sevens", 8: "eights", 9: "nines", 10: "tens",
    11: "elevens",  12: "twelves",    13: "thirteens", 14: "fourteens", 15: "fifteens",
    16: "sixteens", 17: "seventeens", 18: "eighteens", 19: "nineteens", 20: "twenties"
  }

  UPPER_BONUS_POINTS   = 35
  YAHTZEE_BONUS_POINTS = 100

  MIN_DICE_FACES = 6
  MAX_DICE_FACES = len(numberWords)



  @staticmethod
  def numToWord(num):
    """ Convert an integer to it's name equivalent """
    return Scorecard.numberWords[num].capitalize()
  
  @staticmethod
  @functools.lru_cache(maxsize=32)
  def calcProb():
    pass
  
  def __init__(self, numberOfDiceFaces=6):
    
    # CHECK: we support the number of dice faces
    if numberOfDiceFaces < Scorecard.MIN_DICE_FACES or numberOfDiceFaces > Scorecard.MAX_DICE_FACES:
      raise ValueError("dice faces must be between {} and {}"
                        .format(Scorecard.MIN_DICE_FACES, Scorecard.MAX_DICE_FACES))

    
    
    # generate sections for each dice face
    scorecardUpper = OrderedDict()
    for num in range(1, numberOfDiceFaces+1):
      scorecardUpper.update({Scorecard.numToWord(num): None})
    scorecardUpper.update({"Upper Total": None})
    scorecardUpper.update({"Upper Bonus": None})
    
    
    ## generate sections for each dice face
    #upperRows = []
    #for num in range(1, numberOfDiceFaces+1):
    #  upperRows.append((Scorecard.numToWord(num), None))
    #upperRows.append(("Upper Total", None))
    #upperRows.append(("Upper Bonus", None))
    
    # lower scoring sections
    scorecardLower = OrderedDict()
    scorecardLower.update({
      "Three of a Kind": None,
      "Four of a Kind":  None,
      "Full House":      None,
      "Small Straight":  None,
      "Large Straight":  None,
      "Chance":          None,
      "Yahtzee":         None,
      "Yahtzee Bonus":   None,
      "Lower Total":     None,
    })
    #lowerRows = [
    #  ("Three of a Kind", None),
    #  ("Four of a Kind",  None),
    #  ("Full House",      None),
    #  ("Small Straight",  None),
    #  ("Large Straight",  None),
    #  ("Chance",          None),
    #  ("Yahtzee",         None),
    #  ("Yahtzee Bonus",   None),
    #  ("Lower Total",     None),
    #]
    
    # store info
    self.numberOfDiceFaces = numberOfDiceFaces
    
    # store the scorecard
    self.scorecardUpper = scorecardUpper
    self.scorecardLower = scorecardLower
    
    # calculate the upper section's bonus threshold
    self.upperBonusThreshold = sum(list(range(1, self.numberOfDiceFaces + 1))) * 3
  
  
  @staticmethod
  def calculateTotalGameTurns(numberOfDiceFaces):
    """ How many turns will this game have for each player """
    return 7 + numberOfDiceFaces
  
  def getRowNames(self):
    """ Return the names of all the scorecard rows, including the totals """
    #upperNames = [x[0] for x in self.scorecardUpper]
    #lowerNames = [x[0] for x in self.scorecardLower]
    return list(self.scorecardUpper.keys()) + list(self.scorecardLower.keys())
  
  #def getRowCount(self):
  #  return len(self.scorecardUpper) + len(self.scorecardLower)
  
  
  def getAllScores(self):
    """ Return the score card in order, with the total columns calculated """
    
    """
    scores = [] + self.scorecardUpper
    upperTotal = ("Upper Total", sum([x for _,x in self.scorecardUpper if x is not None]))
    scores.append(upperTotal)
    
    scores = scores + self.scorecardLower
    lowerTotal = ("Lower Total", sum([x for _,x in self.scorecardLower if x is not None]))
    scores.append(lowerTotal)
    """
    totalScorecard = OrderedDict
    totalScorecard.update(self.scorecardUpper)
    totalScorecard.update(self.scorecardLower)
    #return self.scorecardUpper + self.scorecardLower
    return totalScorecard

    #for row in self.scorecardUpper:
    
  
  def getRowScore(self, rowName):
    """ Get the score for the <rowName> row """
    
    try:
      return self.scorecardUpper[rowName]
    except KeyError:
      return self.scorecardLower[rowName]
    
    """
    # search the lower part of the score card
    for iRow, row in enumerate(self.scorecardLower):
      if row[0] == rowName:
        return self.scorecardLower[iRow][1]
  
    # search the upper part of the score card
    for iRow, row in enumerate(self.scorecardUpper):
      if row[0] == rowName:
        return self.scorecardUpper[iRow][1]
  
    # can't find matching rowName
    raise ValueError("unknown row name: {}".format(rowName))
    """
  
  def setScore(self, rowName, score):
    """ Set the score for the <rowName> row and update the total """
    
    # if the rowName is in the upper section, store it
    if rowName in self.scorecardUpper:
      self.scorecardUpper[rowName] = score
      
    # else, try and store it in the lower section, raising a KeyError if
    # the rowName isn't valid
    else:
      self.scorecardLower[rowName] = score
      
    
    """
    # search the lower part of the score card
    for iRow, row in enumerate(self.scorecardLower):
      if row[0] == rowName:
        
        # update the individual and total scores
        self.scorecardLower[iRow][1] = score
        self._updateLowerScore()
        return

    # search the upper part of the score card
    for iRow, row in enumerate(self.scorecardUpper):
      if row[0] == rowName:
        
        # update the individual and total scores
        self.scorecardUpper[iRow][1] = score
        self._updateUpperScore()
        return
      
    # can't find matching rowName
    raise ValueError("unknown row name: {}".format(rowName))
    """
  
  def _updateUpperScore(self):
    """ Calculate and store the total score for the upper section """
    
    upperKeys = list(self.scorecardUpper.keys())
    
    # CHECK: total and bonus are at the end
    if self.scorecardUpper[upperKeys[-1]] != "Upper Total" or\
       self.scorecardUpper[upperKeys[-2]] != "Upper Bonus":
      raise ValueError("scorecard layout is not as expected")
  
    # add up in individual scores
    total = 0
    for rowKey in upperKeys[:-2]:
      if self.scorecardUpper[rowKey] is not None:
        total += self.scorecardUpper[rowKey]
    
    # see if the bonus should be added
    if total >= self.upperBonusThreshold:
      self.scorecardUpper[upperKeys[-2]] = Scorecard.UPPER_BONUS_POINTS
      total += Scorecard.UPPER_BONUS_POINTS
      
    else:
      self.scorecardUpper[upperKeys[-2]] = None
    
    # store the new total score
    self.scorecardUpper[upperKeys[-1]] = total
  
  
  def _updateLowerScore(self):
    """ Calculate and store the total score for the lower section """

    lowerKeys = list(self.scorecardLower.keys())
    
    # CHECK: total is at the end
    if self.scorecardLower[lowerKeys[-1]] != "Lower Total":
      raise ValueError("scorecard layout is not as expected")
    
    # add up in individual scores
    total = 0
    for rowKey in lowerKeys[:-1]:
      if self.scorecardLower[rowKey] is not None:
        total += self.scorecardLower[rowKey]
    
    # store the new score
    self.scorecardLower[lowerKeys[-1]] = total
  
  
  def iterateOverScorecard(self):
    """ Iterate over all the scorecard entries """
    for k,v in self.scorecardUpper.items():
      yield k,v
    for k,v in self.scorecardLower.items():
      yield k,v
  
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

  
  def getPossibleScorecard(self, diceValues, sections=None):
    """
    # What are the possible scores given the dice values
    #
    # diceValues: (list) of dice values to use
    # sections:   (list) name of section(s) to calculate, default is all
    """
    
    results = Scorecard(self.numberOfDiceFaces)

    results.setScore("Full House", 25)
    print("results", results)
    return results
    
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

  def getName(self):              return self.name
  def getScorecard(self):         return self.scorecard
  #def getPossibleScorecard(self): return self.scorecard.getPossibleScorecard()


class Game:
  
  MIN_NUM_DICE = 5
  MAX_NUM_DICE = 9
  
  MIN_DICE_FACES = 6
  MAX_DICE_FACES = 20
  
  class STATUS(Enum):
    NOT_STARTED = 0
    RUNNING     = 1
    FINISHED    = 2
  
  

  
  def __init__(self, numberOfDice=5, numberOfDiceFaces=6, numberOfRolls=3):
    
    # CHECK: number of dice
    if not (Game.MIN_NUM_DICE <= numberOfDice <= Game.MAX_NUM_DICE):
      raise ValueError("number of dice must be between {} and {}".format(Game.MIN_NUM_DICE, Game.MAX_NUM_DICE))

    # CHECK: number of dice faces
    if not (Game.MIN_DICE_FACES <= numberOfDiceFaces <= Game.MAX_DICE_FACES):
      raise ValueError("number of dice faces must be between {} and {}".format(Game.MIN_DICE_FACES, Game.MAX_DICE_FACES))
    
    # game config info
    self.numberOfDice      = numberOfDice
    self.numberOfDiceFaces = numberOfDiceFaces
    self.numberOfRolls     = numberOfRolls
    
    self.players    = []
    self.gameStatus = Game.STATUS.NOT_STARTED
    
    # the number of turns in the game
    self.turnsPerPlayer = Scorecard.calculateTotalGameTurns(self.numberOfDiceFaces)
    self.totalGameTurns = None
    
    # keep track of the current player and their remaining turns
    self.currentPlayerIndex = None
    self.remainingRolls     = self.numberOfRolls
    
    # list of current values of the dice
    self.diceValues = [None] * numberOfDice
    
    # list of player-held dice
    self.heldDice = [False] * numberOfDice
    
    

  def getAllPlayers(self):      return self.players
  def getCurrentPlayer(self):   return self.players[self.currentPlayerIndex]
  def getDiceValues(self):      return self.diceValues
  def getGameStatus(self):      return self.gameStatus
  def getNumberOfDice(self):    return self.numberOfDice
  def getNumberOfPlayers(self): return len(self.players)
  def getNumberOfRolls(self):   return self.numberOfRolls
  def getRemainingRolls(self):  return self.remainingRolls

  def getPlayer(self, name):
    """ Return the player with the given name """
    for player in self.players:
      if player.getName() == name:
        return player
    return None
  
  def getHeldDice(self):
    """ Return the indices of the held dice """
    return [iDice for iDice, isHeld in enumerate(self.heldDice) if isHeld]
  
  
  
  
  def getScorePossibilities(self):
    """
    # Based on the current values of the dice, what are the score possibilities
    # for each of the free scorecard rows
    """
    return self.getCurrentPlayer().getScorecard().getScorePossibilities(self.getDiceValues())
  
  def setDiceHold(self, diceNum, isHeld):
    """ Hold or release this die """
    
    # can only hold a die after the first roll
    canHold = self.getGameStatus() == Game.STATUS.RUNNING and self.getRemainingRolls() < self.getNumberOfRolls()
    self.heldDice[diceNum] = isHeld and canHold
  
  
  def setStatus(self, status):
    """ Set the status of the current game """
    
    if status not in Game.STATUS:
      raise ValueError("status {} is not a valid status".format(status))
    self.gameStatus = status
  
  def score(self, rowName):
    """
    # Apply the appropriate score to the <rowName> row, given the current diceVales
    #
    # rowName:    (str) name of row to score on
    #
    """
    
    """
    # CHECK: we were given enough dice
    if len(diceValues) != self.numberOfDice:
      raise ValueError("wrong number of dice")
    
    # CHECK: dice values aren't larger than our max
    maxDiceVal = max(diceValues)
    if maxDiceVal > self.numberOfDiceFaces:
      raise ValueError("dice value {} is larger than the max allowable dice value {}"
                        .format(maxDiceVal, self.numberOfDiceFaces))
    """
    
    # get the current player's scorecard
    playerScorecard = self.getCurrentPlayer().getScorecard()
    
    # get the score value for this row and these dice values
    scoreValue = playerScorecard.scoreValue(rowName, self.getDiceValues())
    if scoreValue is None:
      raise SystemError("tried to score on an already scored row")
    
    # set the score value
    playerScorecard.setScore(rowName, scoreValue)
    
    
  def advanceTurn(self):
    """ End the turn of the current player and move on to the next """
    
    # next player
    self.currentPlayerIndex = (self.currentPlayerIndex + 1) % self.getNumberOfPlayers()
    
    # reset turns
    self.remainingRolls = self.numberOfRolls
    
    # reset dice
    self.diceValues = [None] * self.numberOfDice
    self.heldDice   = [False] * self.numberOfDice
    
    # decrement the number of game turns and check if the game is over
    self.totalGameTurns -= 1
    if self.totalGameTurns == 0:
      self.setStatus(Game.STATUS.FINISHED)
      
  
  def rollDice(self):
    """ Roll the non-held dice """
    
    # CHECK: there are turns remaining
    if self.remainingRolls < 1:
      raise SystemError("trying to roll dice when there are no turns left")
    
    
    
    # get the indices of the non-held dice
    freeDiceIndices = [iDice for iDice, isHeld in enumerate(self.heldDice) if not isHeld]
    
    # roll this number of dice
    newRolls = self._rollFreeDice(len(freeDiceIndices))
    
    # assign the new dice rolls to the free dice
    for iRoll, diceVal in enumerate(newRolls):
      self.diceValues[freeDiceIndices[iRoll]] = diceVal
    
    # update the players possible scorecard
    
    
    # decrement number of turns left
    self.remainingRolls -= 1
  
  
  def _rollFreeDice(self, numberOfDice):
    """ Roll <numberOfDice> dice """
    
    # no dice
    if numberOfDice < 1:
      return []
    
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
    if self.getGameStatus() != Game.STATUS.NOT_STARTED:
      raise SystemError("can't add a player after the game has started")
    
    # create a new player with a blank scorecard
    player = Player(playerName, Scorecard(self.numberOfDiceFaces))
    self.players.append(player)
    
    # if this is the first player, make it their turn
    if self.getNumberOfPlayers() == 1:
      self.currentPlayerIndex = 0
    
    # update the total number of game turns
    self.totalGameTurns = self.turnsPerPlayer * self.getNumberOfPlayers()


  def removePlayer(self, playerName):
    """ Remove the player <playerName> from the game """
    
    # CHECK: player name is a string
    if not isinstance(playerName, str):
      raise TypeError("player name must be a string")
    
    # CHECK: game hasn't started
    if self.getGameStatus() != Game.STATUS.NOT_STARTED:
      raise SystemError("can't remove a player after the game has started")
    
    # remove the player and decrement the number of total game turns
    for player in self.players:
      if player.name == playerName:
        self.players.remove(player)
        self.totalGameTurns = self.turnsPerPlayer * self.getNumberOfPlayers()
        return
    
    # player wasn't found
    raise ValueError("player {} is not part of this game".format(playerName))
  


  
  