import logging
import threading

logger = logging.getLogger(__name__)

import os
import time
import yaml
import datetime

import numpy as np

from concurrent import futures

from yahtzee.model import Game
from yahtzee.gui import PyQtGUI


class Controller:
  
  @staticmethod
  def _loadConfigFile(configFileLoc):
    """ Load in the data from the yaml config file """

    entryNames = ["database-file", "rows", "columns", "version"]
    
    # CHECK: file location exists
    if not os.path.exists(configFileLoc):
      raise FileNotFoundError("Cannot find config file at: {}".format(configFileLoc))
    
    # load the config data
    with open(configFileLoc, 'r') as f:
      configData = yaml.safe_load(f)
    
    # check we have the correct data
    for entry in entryNames:
      if configData.get(entry, None) is None:
        raise SystemError("Config file is missing an entry for {}".format(entry))
    
    return configData
  
  @staticmethod
  def _updateConfigFile(configFileLoc, newConfigData):
    """ Update an entry in the config file """
    
    # CHECK: file location exists
    if not os.path.exists(configFileLoc):
      raise FileNotFoundError("Cannot find config file at: {}".format(configFileLoc))
    
    # load the existing config data
    with open(configFileLoc, 'r') as f:
      configData = yaml.safe_load(f)
    
    # change the data
    configData.update(newConfigData)
    
    # write the data
    with open(configFileLoc, 'w') as f:
      yaml.safe_dump(configData, f)
  
  
  def __init__(self, configFileLoc):
    
    self.configFileLoc = configFileLoc
  
    # load the config data from the config file
    #self.configData = Controller._loadConfigFile(configFileLoc)

    # create a GUI
    self.game = Game()
    self.game.addPlayer("Stewart")
    self.game.addPlayer("Kali")
    
    """
    self.game.getPlayer("Stewart").getScorecard().setScore("Ones", 400)
    self.game.getPlayer("Stewart").getScorecard().setScore("Full House", 200)
    self.game.getPlayer("Kali").getScorecard().setScore("Threes", 33)
    """
    
    self.gui = PyQtGUI(self, self.game)
    
  
  def aboutText(self, textFormat="richtext"):
    
    if textFormat == "richtext":
      return "Yahtzee, yo!"
  
  def run(self):
    self.gui.run()
    
  def rollDice(self):
    """
    # Roll the dice. Used to:
    #  -start the game
    #  -start a player's turn
    #  -roll again during a player's turn
    #
    """
    
    ###########################################################################
    # CHECKS
    ###########################################################################
    
    # if the game has ended
    if self.game.getGameStatus() == Game.STATUS.FINISHED:
      self.gui.notifyStatus("Game has ended")
      return
    
    # if we don't have any rolls left
    if self.game.getRemainingRolls() < 1:
      self.gui.notifyStatus("No rolls remaining")
      return
    
    # if all the dice are held
    if len(self.game.getHeldDice()) == self.game.getNumberOfDice():
      self.gui.notifyStatus("Cannot roll if all dice are held")
      return


    ###########################################################################

    currentPlayer = self.game.getCurrentPlayer()
    
    # are we starting the game
    if self.game.getGameStatus() == Game.STATUS.NOT_STARTED:
      
      # make sure the GUI knows the current player
      self.gui.startPlayerTurn(currentPlayer)
    
      # set game as running
      self.game.setStatus(Game.STATUS.RUNNING)
    
    
    # roll the free dice
    self.game.rollDice()
    
    # update the gui on the current dice values
    self.gui.updateDice(self.game.getDiceValues())
    
    # update the gui on the current scorecard possibilities
    self.gui.updatePossibleScorecard([currentPlayer])
    
    
  def toggleDiceHeldStatus(self, diceNum):
    """ Hold/free a die """
    logger.debug("toggleDiceHeldStatus: {}".format(diceNum))
    
    # hold a free die, or free a held die
    self.game.setDiceHold(diceNum, diceNum not in self.game.getHeldDice())
    
    # let the GUI know which die are held
    self.gui.updateHeldDice(self.game.getHeldDice())

  
  def score(self, rowName):
    """ Submit a score based on the curent dice """
    logger.debug("score: {}".format(rowName))
    
    # CHECK: we can score this row
    if not self.game.getCurrentPlayer().getScorecard().canScoreRow(rowName):
      logger.debug("score: can't score {}".format(rowName))
      return
    
    # set the score for the given rowName based on the current dice values
    self.game.score(rowName)
    
    # update the score for this player
    self.gui.updateScorecard([self.game.getCurrentPlayer()])
    
    # advance the turn
    self.game.advanceTurn()

    # let the GUI know about the change of held dice and player
    self.gui.updateHeldDice(self.game.getHeldDice())
    self.gui.startPlayerTurn(self.game.getCurrentPlayer())
    
    # check if game is over
    if self.game.getGameStatus() == Game.STATUS.FINISHED:
      self.gui.gameComplete()
      
    
    