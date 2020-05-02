import unittest

import random

import numpy as np

from yahtzee.predictor import ProbabilityPredictor


class test_ProbabilityPredictor(unittest.TestCase):
  
  # perform all tests in this class
  TEST_ALL = True

  @unittest.skipIf(not TEST_ALL, " not part of individual test")
  def test_Operations(self):
    res = ProbabilityPredictor.probExactlyXDice(1,3,6)
    print(res)
    print(float(res))
    
    print("at least 1")
    
    res2 = ProbabilityPredictor.probAtLeastXDice(2,3,6)
    print(res2)
    print(float(res2))

    print("of a kind")
    diceValues = [None]*5
    res3 = ProbabilityPredictor.ofAKind(1, diceValues, numDieFaces=6, numTurns=1, canHold=True)
    print(res3)
    
  @unittest.skipIf(not TEST_ALL, " not part of individual test")
  def test_ofAKind(self):
    
    kind           = 3
    diceValues     = [1, 2, 2, 3, 4]
    turnsRemaining = 1
    numDieFaces    = 6
    canHold        = True
    res = ProbabilityPredictor.ofAKind(kind, diceValues, turnsRemaining,
                                       numDieFaces=numDieFaces, canHold=canHold)
    
    print(res)
    #print(["{}: {}".format(k, v.numerator/v.denominator) for k,v in res.items()])
    