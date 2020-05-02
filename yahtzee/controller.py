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
  
  DEFAULT_CONFIG = {
    "databaseFile":      "yahtzee.db",
    "playerName":        "Player One",
    "numberOfDice":      5,
    "numberOfDiceFaces": 6,
    "numberOfRolls":     3,
    "version":           1.0,
  }
  
  @staticmethod
  def createNewConfigFile(configFileLoc):
    """ Create a new config file at this location """

    # CHECK: file location doesn't already exist
    if os.path.exists(configFileLoc):
      raise FileExistsError("Cannot create a new config file as file already exists at {}".format(configFileLoc))
  
    # create a new, file and write the default data
    with open(configFileLoc, 'w') as f:
      yaml.safe_dump(Controller.DEFAULT_CONFIG, f)
      
      
  @staticmethod
  def _loadConfigFile(configFileLoc):
    """ Load in the data from the yaml config file """

    entryNames = ["databaseFile", "playerName", "numberOfDice",
                  "numberOfDiceFaces", "numberOfRolls", "version"]
    
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
    
    # if there's no config file, create a new one
    if not os.path.exists(configFileLoc):
      logger.debug("No config file found; creating a new one")
      Controller.createNewConfigFile(configFileLoc)
    
    self.configFileLoc = configFileLoc
  
    # load the config data from the config file
    self.configData = Controller._loadConfigFile(configFileLoc)

    # create a new game and GUI using the config data
    self.game = Game(playerNameList    = [self.configData["playerName"]],
                     numberOfDice      = self.configData["numberOfDice"],
                     numberOfDiceFaces = self.configData["numberOfDiceFaces"],
                     numberOfRolls     = self.configData["numberOfRolls"])
    self.gui = PyQtGUI(self, self.game)
    
    
  def newGame(self, forceNewGame=False):
    """ Start a new game """
    logger.debug("newGame: Starting a new game")
    
    # if there is already a game in progress, confirm with the user
    if not forceNewGame and self.game.getGameStatus() == Game.STATUS.RUNNING\
                        and not self.gui.confirmAction("Abandon game in progress?"):
      return
    
    # load the config data from the config file
    self.configData = Controller._loadConfigFile(self.configFileLoc)
    
    # create a new game and tell the GUI
    self.game = Game(playerNameList    = [self.configData["playerName"]],
                     numberOfDice      = self.configData["numberOfDice"],
                     numberOfDiceFaces = self.configData["numberOfDiceFaces"],
                     numberOfRolls     = self.configData["numberOfRolls"])
    self.gui.newGame(self.game)
    
  
  
  def aboutText(self, textFormat="richtext"):
    """ Text giving the game info """

    versionNumber = self.configData["version"]
    
    if textFormat == "richtext":
      return """Yahtzee v{}<p>By Stewart Denholm<p><a href=https://github.com/sdenholm>GitHub</a>"""\
        .format(versionNumber)
    else:
      return """Yahtzee v{}\nBy Stewart Denholm\nGitHub: github.com/sdenholm"""\
        .format(versionNumber)

  def howToPlayText(self, textFormat="richtext"):
    """ Text describing how to play the game """
  
    msg = """
    <h3>How to Play</h3><p>
    1) Fill in the blanks using the digits 1-9 to create regions, called polyominoes.<p>
    2) A region must contain as many cells as its number value e.g., three number 3s together will
    make a region, or four number 4s together, five number 5s, etc.<p>
    3) Regions with the same number cannot touch. For example, two regions of four 4s cannot
    be neighbours.<p>
    4) When the board is filled, you win!<p><p>
    <h3>Generating Boards</h3><p>
    To play, you must first generate boards:<p>
    1) From the menu, select [Boards]=>[Generate New Boards]<p>
    2) Choose the board dimensions, and how many boards to generate.<p>
    3) Click Generate.<p>
    When generation is done, select [File]=>[Load Random Board] from the main menu to play one of the boards.
    """
    
    msg = "Yahtzee, yo!"
    
    if textFormat == "richtext":
      return msg
    else:
      return msg.replace("<p>", "\n\n").replace("<h3>", "").replace("<\h3>", "")
    
  
  def run(self):
    self.gui.run()
  
  def configureDice(self):
    """ Setup the parameters for the dice """
    logger.debug("configureDice")
    
    # if there is already a game in progress, confirm with the user
    if self.game.getGameStatus() == Game.STATUS.RUNNING and \
        not self.gui.confirmAction("Abandon game in progress?"):
      return
    
    # get the new dice values from the user
    newDiceValues = self.gui.showDiceSetupWindow()
    logger.debug("configureDice: new dice values: {}".format(newDiceValues))
    
    # if we get new values
    if newDiceValues is not None:
      
      # update the config file
      Controller._updateConfigFile(self.configFileLoc, newDiceValues)
      
      # start a new game
      self.newGame(forceNewGame=True)
      
      
  
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
      
    
    