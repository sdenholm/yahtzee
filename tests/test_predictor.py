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
    diceValues = [None]*3
    res3 = ProbabilityPredictor.ofAKind(1, diceValues, numDieFaces=6, numTurns=1, canHold=True)
    print(res3)
    