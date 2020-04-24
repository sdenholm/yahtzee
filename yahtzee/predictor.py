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
  @functools.lru_cache(maxsize=64)
  def probExactlyXDice(numInstances, numDice, numDieFaces):
    """
    # Probability exactly <numInstances> occurennces of a dice value are
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
  def probAtLeastXDice(numInstances, numDice, numDieFaces):
    """
    # Probability at least <numInstances> occurennces of a dice value are
    # shown when <numDice> are thrown, each die having <numDieFaces> sides
    """
    
    # add up the probabilities that:
    #  -exactly <numInstances> values are shown
    # +
    #  -exactly <numInstances>-1 values are shown
    # +
    #  -exactly <numInstances>-2 values are shown
    # ....
    return sum([ProbabilityPredictor.probExactlyXDice(i, numDice, numDieFaces)
                  for i in range(numInstances,numDice+1)])

    
  @staticmethod
  def ofAKind(kind, diceValues, numDieFaces=6, numTurns=3, canHold=True):
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
    
    
    