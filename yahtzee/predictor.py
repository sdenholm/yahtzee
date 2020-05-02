import logging
logger = logging.getLogger(__name__)

import itertools
import random

from collections import OrderedDict

import functools

from fractions import Fraction

from math import comb

import numpy as np
import pandas as pd
  
class ProbabilityPredictor:
  
  @staticmethod
  @functools.lru_cache(maxsize=256)
  def probExactlyXDice(numInstances, numDice, numDieFaces):
    """
    # Probability exactly <numInstances> occurrences of a dice value are
    # shown when <numDice> are thrown, each die having <numDieFaces> sides
    """
    
    # probability die value will be shown
    probOccur = Fraction(1, numDieFaces)
    
    # probability exactly <numInstances> of this die value appearing is:
    #  -total number of ways this can occur given the number of dice we have
    # *
    #  -probability this value appears <numInstances> times
    # *
    #  -probability this value DOESN'T appear the remaining times
    #
    return comb(numDice, numInstances) * (probOccur ** numInstances) * ((1-probOccur) ** (numDice-numInstances))
  
  
  @staticmethod
  @functools.lru_cache(maxsize=256)
  def probAtLeastXDice(numInstances, numDice, numDieFaces):
    """
    # Probability at least <numInstances> occurrences of a dice value are
    # shown when <numDice> are thrown, each die having <numDieFaces> sides
    """
    
    # add up the probabilities that:
    #  -exactly <numInstances> values are shown
    # +
    #  -exactly <numInstances>-1 values are shown
    # +
    #  -exactly <numInstances>-2 values are shown
    # +
    # ....
    return sum([ProbabilityPredictor.probExactlyXDice(i, numDice, numDieFaces)
                  for i in range(numInstances,numDice+1)])


  @staticmethod
  def DEPrangeOfAKind(numDice, kind, numDieFaces=6):
    """
    # Probability of getting 1-<numOccurrences> of <kind> dice values
    #  -e.g., when rolling 5 dice, probability of getting 1, 2, 3, 4 or 5 "4"s
    #
    #
    """
    
    # current number of <kind> we have
    currentNum = diceCount.get(kind, 0)
    
    # calculate the chance of getting X of <kind>
    #  -e.g., for kind=3 with 5 dice, probability of getting 1x3, 2x3, 3x3, 4x3, 5x3
    for numOccurrences in range(1, numDice + 1):
    
      # if we already have this number of <kind> then probability is 1.0
      if currentNum >= numOccurrences:
        prob[numOccurrences] = Fraction(1)
    
      # else, calculate the probability of rolling the number of <kind> needed
      # with the dice we have available
      else:
      
        # if we can hold the current <kind> dice we have, then we only need to
        # roll for the remaining number of <kind> we need
        numKindNeeded    = numOccurrences - currentNum
        numAvailableDice = numDice - currentNum
      
        # probability of getting the number of <kind> we need, given the dice we have
        prob[numOccurrences] = ProbabilityPredictor.probAtLeastXDice(numKindNeeded,
                                                                     numAvailableDice,
                                                                     numDieFaces)
  
    return prob


  @staticmethod
  def ofAKind(kind, diceValues, turnsRemaining, numDieFaces=6, canHold=True):
    """  """
  
    numDice = len(diceValues)
    
    diceCount = pd.Series(diceValues).value_counts()
    
    # current number of <kind> we have
    currentNum = diceCount.get(kind, 0)
    
    """
    prob 5-of-a-kind of 1s:
    -prob(getting 5 | got exactly 4 before) + prob(getting 5 | got exactly 3 before) +
    
    p(5|0) + p(4|1) + p(3|2) + p(2|3) + p(1|4) + p(5)
    
    """
    
    
    
    
    
    probSum = 0
    for numOccurrences in range(numDice):
    
      pA = ProbabilityPredictor.probAtLeastXDice(numDice-numOccurrences, numDice-numOccurrences, numDieFaces=6)
      pB = ProbabilityPredictor.probExactlyXDice(numOccurrences, numDice, numDieFaces=6)
      print("{}: {} * {}".format(numOccurrences, pA, pB))
      probSum += pA * pB
    
    return probSum
    
    prob = {}

    # prob getting X of a kind next turn
    #prob[1] = 1.0 if currentNum >= 1 else ProbabilityPredictor.probAtLeastXDice(1, numDice, numDieFaces)
    
    # calculate the chance of getting X of <kind>
    #  -e.g., for kind=3 with 5 dice, probability of getting 1x3, 2x3, 3x3, 4x3, 5x3
    for numOccurrences in range(1, numDice+1):
      
      # if we already have this number of <kind> then probability is 1.0
      if currentNum >= numOccurrences:
        prob[numOccurrences] = Fraction(1)
        
      # else, calculate the probability of rolling the number of <kind> needed
      # with the dice we have available
      else:
        
        # if we can hold the current <kind> dice we have, then we only need to
        # roll for the remaining number of <kind> we need
        numKindNeeded    = numOccurrences - currentNum if canHold else numOccurrences
        numAvailableDice = numDice - currentNum        if canHold else numDice
        
        # probability of getting the number of <kind> we need, given the dice we have
        prob[numOccurrences] = ProbabilityPredictor.probAtLeastXDice(numKindNeeded,
                                                                     numAvailableDice,
                                                                     numDieFaces)
    
    return prob
    
    # probability for each turn
    probs = {}
    
    for iTurn in range(1, turnsRemaining+1):
      
      # prob getting X of a kind this turn
      
      probs[iTurn] = {}
    
      for numOccurences in range(1, numDice + 1):
        probs[iTurn][numOccurences] = ProbabilityPredictor.probAtLeastXDice(numOccurences, numDice, numDieFaces)


  @staticmethod
  def OLDofAKind(kind, diceValues, numDieFaces=6, numTurns=3, canHold=True):
    """  """

    numDice = len(diceValues)
    
    # probability for each turn
    probs = {}
    
    for iTurn in range(numTurns):
      
      probs[iTurn] = {}
      
      for numOccurences in range(1, numDice+1):
        probs[iTurn][numOccurences] = ProbabilityPredictor.probAtLeastXDice(numOccurences, numDice, numDieFaces)

    
    
    #probKind = Fraction(1,6)
    
    #diceCounts = pd.Series(diceValues).value_counts()
    
    #currNum = diceCounts.get(kind, 0)
    #diceRemaining = numDice - currNum
    
    return probs
    
    
    