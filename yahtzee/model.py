import logging
logger = logging.getLogger(__name__)

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


  MIN_DICE_FACES = 6
  MAX_DICE_FACES = len(numberWords)
  
  class ROW_NAME(Enum):
    UPPER_TOTAL     = "Upper Total"
    UPPER_BONUS     = "Upper Bonus"
    THREE_OF_A_KIND = "Three of a Kind"
    FOUR_OF_A_KIND  = "Four of a Kind"
    FULL_HOUSE      = "Full House"
    SMALL_STRAIGHT  = "Small Straight"
    LARGE_STRAIGHT  = "Large Straight"
    YAHTZEE         = "Yahtzee"
    YAHTZEE_BONUS   = "Yahtzee Bonus"
    LOWER_TOTAL     = "Lower Total"

  class POINTS(Enum):
    UPPER_BONUS    =  35
    FULL_HOUSE     =  25
    SMALL_STRAIGHT =  30
    LARGE_STRAIGHT =  40
    YAHTZEE        =  50
    YAHTZEE_BONUS  = 100
  
  class PointsCalculator:
  
    @staticmethod
    def _hasStraight(uniqueSortedDice, length):
      """ Is there a straight sequence of <length> dice within the list of unique, sorted dice"""
    
      # if we don't have enough dice for a straight
      if len(uniqueSortedDice) < length:
        return False
    
      # check if we can find a sequence in the list of unique, sorted dice
      for comb in itertools.combinations(uniqueSortedDice, length):
        if comb == tuple(range(comb[0], comb[0] + length)):
          return True
    
      # no dice
      return False
  
    @staticmethod
    def _hasFullHouse(diceCounts):
      """ Do we have a full house, i.e., only two unique dice values, with at least 2 of everything """
      return len(diceCounts.index) == 2 and (diceCounts > 1).all()
  
    @staticmethod
    def _calcOfAKindScore(num, kind, diceValues):
      """
      # Calculate score of X-of-a-kind, e.g., 3-of-a-kind
      #
      # num:        (int) hpw many of-a-kind
      # kind:       (int) dice value to look for <num> of
      # diceValues: (list) actual dice values to process
      #
      """
      valCounts = pd.Series(diceValues).value_counts()
    
      # if we don't have enough "kind"s, then score is 0
      #  -e.g., not enough 4s
      if valCounts.get(kind, 0) < num:
        return 0
    
      # if we have enough "kind"s, then score is sum of all dice
      return sum(diceValues)
  
    @staticmethod
    def _calcSingleDiceScore(kind, diceValues):
      """
      # Calculate score of a single dice value, e.g., upper section score for 3s
      #
      # kind:       (int) dice value to look at
      # diceValues: (list) actual dice values to process
      #
      """
      valCounts = pd.Series(diceValues).value_counts()
    
      # add together all the "kind" of dice we see
      return valCounts.get(kind, 0) * kind
    
    def _calcUpperSection(self, diceValue):
      """ score based on how many die of <diceValue> we have """
      return self.diceCounts.get(diceValue, 0) * diceValue
    
    def _calc3ofAKind(self):
      # 3-of-a-kind score is max of all available three-of-a-kinds
      #  -note: in normal, 5-dice game, this is overkill
      threeOfAKindScore = 0
      for threeOfAKind in self.diceCounts.index[self.diceCounts > 2]:
        threeOfAKindScore = max(threeOfAKindScore,
                                Scorecard.PointsCalculator._calcOfAKindScore(3, threeOfAKind, self.diceValues))
      return threeOfAKindScore
  
    def _calc4ofAKind(self):
      # 4-of-a-kind score is max of all available four-of-a-kinds
      #  -note: in normal, 5-dice game, this is overkill
      fourOfAKindScore = 0
      for fourOfAKind in self.diceCounts.index[self.diceCounts > 3]:
        fourOfAKindScore = max(fourOfAKindScore,
                               Scorecard.PointsCalculator._calcOfAKindScore(4, fourOfAKind, self.diceValues))
      return fourOfAKindScore
  
    def _calcFullHouse(self):
      # full house score
      hasFullHouse = Scorecard.PointsCalculator._hasFullHouse(self.diceCounts)
      fullHouseScore = Scorecard.POINTS.FULL_HOUSE.value if hasFullHouse else 0
      return fullHouseScore
  
    def _calcSmallStraight(self):
      # small straight score
      hasSmallStraight = Scorecard.PointsCalculator._hasStraight(self.uniqueSortedDice, len(self.diceSorted) - 1)
      smallStraightScore = Scorecard.POINTS.SMALL_STRAIGHT.value if hasSmallStraight else 0
      return smallStraightScore
  
    def _calcLargeStraight(self):
      # large straight score
      hasLargeStraight = Scorecard.PointsCalculator._hasStraight(self.uniqueSortedDice, len(self.diceSorted))
      largeStraightScore = Scorecard.POINTS.LARGE_STRAIGHT.value if hasLargeStraight else 0
      return largeStraightScore
    
    def _calcChance(self):
      """ Chance score """
      return sum(self.diceValues)
      
    def _calcYahtzee(self):
      """ Yahtzee score """
      return Scorecard.POINTS.YAHTZEE.value if len(self.diceCounts) == 1 else 0
    
    def _calcYahtzeeBonus(self):
      # yahtzee bonus
      canGetYahtzeeBonus = len(self.diceCounts) == 1 and\
                           self.scorecard.getRowScore("Yahtzee") is not None
      return Scorecard.POINTS.YAHTZEE_BONUS if canGetYahtzeeBonus else None
    
    
    def __init__(self, scorecard):
      self.scorecard = scorecard

      # dice info
      self.diceValues       = None
      self.diceSorted       = None
      self.diceCounts       = None
      self.uniqueSortedDice = None
      
      # score function mappings
      self.scoreFn = {
        "Three of a Kind": self._calc3ofAKind,
        "Four of a Kind":  self._calc4ofAKind,
        "Full House":      self._calcFullHouse,
        "Small Straight":  self._calcSmallStraight,
        "Large Straight":  self._calcLargeStraight,
        "Chance":          self._calcChance,
        "Yahtzee":         self._calcYahtzee,
        "Yahtzee Bonus":   self._calcYahtzeeBonus
      }
      
    def calculate(self, rowNameList, diceValues):
      """  """
      logger.debug("points calculate: {}, {}".format(rowNameList, diceValues))
      
      # sort and process dice
      self.diceValues       = diceValues
      self.diceSorted       = sorted(diceValues)
      self.diceCounts       = pd.Series(self.diceSorted).value_counts()
      self.uniqueSortedDice = sorted(self.diceCounts.index.to_list())
      
      def _isKnownWordNum(sectionName):
        """ Test if sectionName is a valid upper secion """
        try:
          Scorecard.wordToNum(sectionName)
          return True
        except KeyError:
          return False

      
      
      # name of known lower sections, i.e., those in our score mapping
      scoreFnRows = list(self.scoreFn.keys())

      # isolate the upper and lower section rows
      #  -lower rows are those known to our score mapping
      #  -upper rows are dynamic, so just assign remaining rows to upper and check them later
      lowerSectionRows = list(filter(lambda x: x in scoreFnRows, rowNameList))
      upperSectionRows = list(filter(lambda x: x not in lowerSectionRows, rowNameList)) #self.scorecard.getRowNames()))
      #upperSectionRows = filter(lambda x: x not in lowerSectionRows and _isKnownWordNum(x),
      #                            self.scorecard.getRowNames())

      logger.debug("points calculate: upperSectionRows: {}".format(upperSectionRows))
      logger.debug("points calculate: lowerSectionRows: {}".format(lowerSectionRows))
      
      ## CHECK: weren't given unknown rows
      #unknownRowNames = [x for x in rowNameList if x not in lowerSectionRows and x not in upperSectionRows]
      #if len(unknownRowNames) > 0:
      #  raise ValueError("Unknown row names were given: {}".format(unknownRowNames))

      results = {}

      # upper section calculations
      for sectionName in upperSectionRows:
        
        # convert row word to number
        try:
          sectionNum = Scorecard.wordToNum(sectionName)
          
        # raises KeyError if we have been passed an unknown row name
        except KeyError:
          raise KeyError("Unknown rowName was given: {}".format(sectionName))

        results[sectionName] = self._calcUpperSection(sectionNum)
      
      
      # lower section calculations
      for sectionName in lowerSectionRows:
        results[sectionName] = self.scoreFn[sectionName]()
      
      logger.debug("points calculate results: {}".format(results))
      return results
    
    
  
  @staticmethod
  def numToWord(num):
    """ Convert an integer to it's name equivalent """
    return Scorecard.numberWords[num].capitalize()
  
  @staticmethod
  def wordToNum(word):
    """ Convert an integer name equivalent back to its integer """
    wordLower = word.lower()
    for k,v in Scorecard.numberWords.items():
      if v == wordLower:
        return k
    raise KeyError("{} not present in mapping".format(wordLower))
    


  

  
  @staticmethod
  @functools.lru_cache(maxsize=32)
  def calcProb():
    pass
  
  
  @staticmethod
  def calculateTotalGameTurns(numberOfDiceFaces):
    """ How many turns will this game have for each player """
    return 7 + numberOfDiceFaces
  
  
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
    
    # store info
    self.numberOfDiceFaces = numberOfDiceFaces
    
    # store the scorecard
    self.scorecardUpper = scorecardUpper
    self.scorecardLower = scorecardLower
    
    # calculate the upper section's bonus threshold
    self.upperBonusThreshold = sum(list(range(1, self.numberOfDiceFaces + 1))) * 3
  
  
  def canScoreRow(self, rowName):
    """ Can we score, or update the score, in this row """
    return rowName in self._getFreeRows()
  

  def getAllScores(self):
    """ Return the full score card in order """

    totalScorecard = OrderedDict
    totalScorecard.update(self.scorecardUpper)
    totalScorecard.update(self.scorecardLower)
    return totalScorecard
  
  
  def getRowNames(self):
    """ Return the names of all the scorecard rows, including the totals """
    return list(self.scorecardUpper.keys()) + list(self.scorecardLower.keys())
  
  
  def getRowScore(self, rowName):
    """ Get the score for the <rowName> row """
    try:
      return self.scorecardUpper[rowName]
    except KeyError:
      return self.scorecardLower[rowName]
  
  
  def getPossibleScorecard(self, diceValues, rowNameList=None):
    """
    # What are the possible scores given the dice values
    #  -total and bonuses are always set to None
    #
    # diceValues:  (list) of dice values to use
    # rowNameList: (list) name of section(s) to calculate, default is all
    #
    """
    logger.debug("getPossibleScorecard: dice: {}, sections: {}".format(diceValues, rowNameList))
  
    # filter the rowNameList by free rows, or use all free rows if no rows
    # are specified
    freeRows = self._getFreeRows()
    if rowNameList is None:
      rowNameList = freeRows
    else:
      # rowNameList = [rowName for rowName in rowNameList if rowName in freeRows]
      rowNameList = list(filter(lambda x: x in freeRows, rowNameList))
  
    # create a points calculator and find the possible scores
    pointsCalc = Scorecard.PointsCalculator(self)
    scores = pointsCalc.calculate(rowNameList, diceValues)
  
    # create a new, blank scorecard and populate it with our results
    blankCard = Scorecard(self.numberOfDiceFaces)
    for rowName, rowScore in scores.items():
      blankCard.setScore(rowName, rowScore, updateTotals=False)
  
    return blankCard
  
  
  def getTotalScore(self):
    """ Calculate and return the total score """
    
    upperTotal = self.getRowScore(Scorecard.ROW_NAME.UPPER_TOTAL.value)
    if upperTotal is None:
      upperTotal = 0
    upperBonus = self.getRowScore(Scorecard.ROW_NAME.UPPER_BONUS.value)
    if upperBonus is None:
      upperBonus = 0
    lowerTotal = self.getRowScore(Scorecard.ROW_NAME.LOWER_TOTAL.value)
    if lowerTotal is None:
      lowerTotal = 0
    
    return upperTotal + upperBonus + lowerTotal
    
    
  def setScore(self, rowName, score, updateTotals=True):
    """
    # Set the score for the <rowName> row
    #
    # rowName:      (str) name of row to set
    # score:        (int) score to set
    # updateTotals: (bool) should we also update the section totals/bonuses
    #
    """
    logger.debug("_setScore: {} = {}".format(rowName, score))
    
    # if the rowName is in the upper section, store it
    if rowName in self.scorecardUpper:
      self.scorecardUpper[rowName] = score
      if updateTotals:
        self._updateUpperScore()
    
    # if the rowName is in the lower section, store it
    elif rowName in self.scorecardLower:
      self.scorecardLower[rowName] = score
      if updateTotals:
        self._updateLowerScore()
      
    # KeyError if the rowName isn't valid
    else:
      raise KeyError("unknown rowName: {}".format(rowName))
        
  
  def _updateUpperScore(self):
    """ Calculate and store the total score for the upper section """
    
    # upper row names
    upperKeys = list(self.scorecardUpper.keys())
    
    # CHECK: total and bonus are at the end
    if upperKeys[-2] != Scorecard.ROW_NAME.UPPER_TOTAL.value or\
       upperKeys[-1] != Scorecard.ROW_NAME.UPPER_BONUS.value:
      raise ValueError("scorecard layout is not as expected")
  
    # add up in individual scores
    total = 0
    for rowKey in upperKeys[:-2]:
      if self.scorecardUpper[rowKey] is not None:
        total += self.scorecardUpper[rowKey]
    
    # see if the bonus should be added
    if total >= self.upperBonusThreshold:
      self.scorecardUpper[upperKeys[-1]] = Scorecard.POINTS.UPPER_BONUS.value
    else:
      self.scorecardUpper[upperKeys[-1]] = None
    
    # store the new total score
    self.scorecardUpper[upperKeys[-2]] = total
  
  
  def _updateLowerScore(self):
    """ Calculate and store the total score for the lower section """

    lowerKeys = list(self.scorecardLower.keys())
    
    # CHECK: total is at the end
    if lowerKeys[-1] != Scorecard.ROW_NAME.LOWER_TOTAL.value:
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
  

  def _getFreeRows(self):
    """ Returns list of row names that can be scored """
    
    # ignore rows that base their value on something else
    ignoreRows = [Scorecard.ROW_NAME.UPPER_TOTAL.value,
                  Scorecard.ROW_NAME.UPPER_BONUS.value,
                  Scorecard.ROW_NAME.YAHTZEE_BONUS.value,
                  Scorecard.ROW_NAME.LOWER_TOTAL.value]
    
    # return any rows with no score, ignoring the "meta rows"
    return [rowName for rowName, rowScore in self.iterateOverScorecard()
             if rowScore is None and rowName not in ignoreRows]
    
  

    

class Player:
  def __init__(self, name, scorecard):
    self.name      = name
    self.scorecard = scorecard

  def getName(self):      return self.name
  def getScorecard(self): return self.scorecard


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

  def getHeldDice(self):
    """ Return the indices of the held dice """
    return [iDice for iDice, isHeld in enumerate(self.heldDice) if isHeld]


  def getPlayer(self, name):
    """ Return the player with the given name """
    for player in self.players:
      if player.getName() == name:
        return player
    return None
  
  def getTotalScores(self):
    """ Get the total scores for all players """
    return {player.getName(): player.getScorecard().getTotalScore() for player in self.players}
  
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
    # rowName: (str) name of row to score on
    #
    """
    logger.debug("score: {}".format(rowName))

    # get the current player's scorecard
    playerScorecard = self.getCurrentPlayer().getScorecard()
    
    # CHECK: row does already have a score
    #  -note: can score multiple times in a yahtzee or yahtzee bonus row
    if rowName not in ["Yahtzee", "Yahtzee Bonus"] and playerScorecard.getRowScore(rowName) is not None:
      raise SystemError("tried to score on an already scored row")
    
    # calculate the score for this row
    pointsCalc = Scorecard.PointsCalculator(playerScorecard)
    scores = pointsCalc.calculate([rowName], self.getDiceValues())
    
    # store the score
    playerScorecard.setScore(rowName, scores[rowName])
    
    
  def advanceTurn(self):
    """ End the turn of the current player and move on to the next """
    logger.debug("advanceTurn")
    
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
    #return [random.randint(1, self.numberOfDiceFaces) for _ in range(numberOfDice)]
    return [6 for _ in range(numberOfDice)]
  

  
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
  


  
  