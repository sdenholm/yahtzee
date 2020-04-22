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
    self.gui  = PyQtGUI(self, self.game)
    
  
  def aboutText(self, textFormat="richtext"):
    
    if textFormat == "richtext":
      return "Yahtzee, yo!"
  
  def run(self):
    self.gui.run()
    
  def rollDice(self):
    print("rollDice")
    
  def holdDice(self, diceNum):
    print("holdDice", "-", diceNum)