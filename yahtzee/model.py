
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

  UPPER_BONUS_POINTS   = 35
  YAHTZEE_BONUS_POINTS = 100

  MIN_DICE_FACES = 6
  MAX_DICE_FACES = len(numberWords)



  @staticmethod
  def numToWord(num):
    """ Convert an integer to it's name equivalent """
    return Scorecard.numberWords[num].capitalize()
    
  
  def __init__(self, numberOfDiceFaces=6):
    
    # CHECK: we support the number of dice faces
    if numberOfDiceFaces < Scorecard.MIN_DICE_FACES or numberOfDiceFaces > Scorecard.MAX_DICE_FACES:
      raise ValueError("dice faces must be between {} and {}"
                        .format(Scorecard.MIN_DICE_FACES, Scorecard.MAX_DICE_FACES))
    
    # generate sections for each dice face
    upperRows = []
    for num in range(1, numberOfDiceFaces+1):
      upperRows.append((Scorecard.numToWord(num), None))
    upperRows.append(("Upper Total", None))
    upperRows.append(("Upper Bonus", None))
    
    # lower scoring sections
    lowerRows = [
      ("Three of a Kind", None),
      ("Four of a Kind",  None),
      ("Full House",      None),
      ("Small Straight",  None),
      ("Large Straight",  None),
      ("Chance",          None),
      ("Yahtzee",         None),
      ("Yahtzee Bonus",   None),
      ("Lower Total",     None),
    ]
    
    # store info
    self.numberOfDiceFaces = numberOfDiceFaces
    
    # store the scorecard
    self.scorecardUpper = upperRows
    self.scorecardLower = lowerRows
    
    # calculate the upper section's bonus threshold
    self.upperBonusThreshold = sum(list(range(1, self.numberOfDiceFaces + 1))) * 3
    
    
    
  def getRowNames(self):
    """ Return the names of all the scorecard rows, including the totals """
    upperNames = [x[0] for x in self.scorecardUpper]# + ["Upper Total"]
    lowerNames = [x[0] for x in self.scorecardLower]# + ["Lower Total"]
    return upperNames + lowerNames
  
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
    return self.scorecardUpper + self.scorecardLower
    
    #for row in self.scorecardUpper:
    
  
  def getRowScore(self, rowName):
    """ Get the score for the <rowName> row """
  
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
  
  
  def setScore(self, rowName, score):
    """ Set the score for the <rowName> row and update the total """
    
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
  
  
  def _updateUpperScore(self):
    """ Calculate and store the total score for the upper section """
  
    # CHECK: total and bonus are at the end
    if self.scorecardUpper[-1] != "Upper Total" or self.scorecardUpper[-2] != "Upper Bonus":
      raise ValueError("scorecard layout is not as expected")
  
    # add up in individual scores
    total = 0
    for row in self.scorecardUpper[:-2]:
      if row[1] is not None:
        total += row[-1]
    
    # see if the bonus should be added
    if total >= self.upperBonusThreshold:
      self.scorecardUpper[-2][1] = Scorecard.UPPER_BONUS_POINTS
      total += Scorecard.UPPER_BONUS_POINTS
      
    else:
      self.scorecardUpper[-2][1] = None
    
    # store the new total score
    self.scorecardUpper[-1][1] = total
  
  
  def _updateLowerScore(self):
    """ Calculate and store the total score for the lower section """
    
    # CHECK: total is at the end
    if self.scorecardLower[-1] != "Lower Total":
      raise ValueError("scorecard layout is not as expected")
    
    # add up in individual scores
    total = 0
    for row in self.scorecardLower[:-1]:
      if row[1] is not None:
        total += row[-1]
    
    # store the new score
    self.scorecardLower[-1][1] = total
    
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
  
  MIN_NUM_DICE = 5
  MAX_NUM_DICE = 9
  
  MIN_DICE_FACES = 6
  MAX_DICE_FACES = 20
  
  def __init__(self, numberOfDice=5, numberOfDiceFaces=6):
    
    # CHECK: number of dice
    if not (Game.MIN_NUM_DICE <= numberOfDice <= Game.MAX_NUM_DICE):
      raise ValueError("number of dice must be between {} and {}".format(Game.MIN_NUM_DICE, Game.MAX_NUM_DICE))

    # CHECK: number of dice faces
    if not (Game.MIN_DICE_FACES <= numberOfDiceFaces <= Game.MAX_DICE_FACES):
      raise ValueError("number of dice faces must be between {} and {}".format(Game.MIN_DICE_FACES, Game.MAX_DICE_FACES))
    
    self.numberOfDice      = numberOfDice
    self.numberOfDiceFaces = numberOfDiceFaces

    self.players = []
    
    # keep track of the current player and their remaining turns
    self.curentPlayerIndex = None
    self.remainingTurns    = None
    
    # list of current values of the dice
    self.diceValues = [None] * numberOfDice
    
    # list of player-held dice
    self.heldDice = [False] * numberOfDice
  
  def getDiceValues(self):
    """ Current dice values """
    return self.diceValues
  
  def getCurrentPlayer(self):
    return self.players[self.curentPlayerIndex]
  
  def holdDie(self, diceNum):
    """ Hold this die """
    self.heldDice[diceNum] = True
  
  def releaseDie(self, diceNum):
    """ Release (un-hold) this die """
    self.heldDice[diceNum] = False
  
  def rollDice(self):
    """ Roll the non-held dice """
    
    # CHECK: there are turns remaining
    if self.remainingTurns < 1:
      raise SystemError("trying to roll dice when there are no turns left")
    
    # get the indices of the non-held dice
    freeDiceIndices = [iDice for iDice, isHeld in enumerate(self.heldDice) if not isHeld]
    
    # roll this number of dice
    newRolls = self._rollFreeDice(len(freeDiceIndices))
    
    # assign the new dice rolls to the free dice
    for iRoll, diceVal in enumerate(newRolls):
      self.diceValues[freeDiceIndices[iRoll]] = diceVal
    
    # decrement number of turns left
    self.remainingTurns -= 1
  
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
  
  