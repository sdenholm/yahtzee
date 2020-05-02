import logging
logger = logging.getLogger(__name__)

import threading
import time
import sys

import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets


class GUI(object):
  
  def confirmAction(self, text):
    """ Ask the user to confirm they want to do <the thing> """
    raise NotImplementedError("subclass must implement")
  
  def gameComplete(self):
    """ Called when game is completed """
    raise NotImplementedError("subclass must implement")
  
  def newGame(self, game):
    """ Reset the GUI and start a new game """
    raise NotImplementedError("subclass must implement")
  
  def notifyStatus(self, text):
    """ Status notification; used or ignored, up to the GUI """
    raise NotImplementedError("subclass must implement")
  
  def requestNewPlayerName(self, existingPlayers=None):
    """
    # Ask the user for the name of the new player to add
    #  -returns new name or None
    #
    # existingPlayers: (list) of existing player names to exclude
    """
    raise NotImplementedError("subclass must implement")
  
  def requestDiceSetup(self):
    """
    # Ask the user for info on the new dice setup
    #  -returns new values or None
    """
    raise NotImplementedError("subclass must implement")
  
  def run(self):
    """ Start GUI """
    raise NotImplementedError("subclass must implement")
  
  def startPlayerTurn(self, player):
    """ Start this player's turn """
    raise NotImplementedError("subclass must implement")

  def updateDice(self, diceValues):
    """ Show the current values of the dice """
    raise NotImplementedError("subclass must implement")

  def updateHeldDice(self, heldDiceIndices):
    """ Show the held dice as <heldDiceIndices> """
    raise NotImplementedError("subclass must implement")
  
  def updatePossibleScorecard(self, playerList):
    """ Show the possible scores given the current dice values """
    raise NotImplementedError("subclass must implement")

  def updateScorecard(self, playerList):
    """ Update the scorecard scores """
    raise NotImplementedError("subclass must implement")


  

  
  
  



class PyQtGUI(GUI, QtCore.QObject):
  """
  """

  class DiceSetupWindow(QtWidgets.QDialog):
    
    class UserActions(object):
      
      @staticmethod
      def cancelPressed(dialog):
        """ Called when cancel is pressed """
        logger.debug("DiceSetupWindow: cancel pressed")
        
        # wipe the stored values
        dialog.values = {}
        
        # close dialog
        dialog.close()
      
        # text of button
        # name = gui.sender().text()

      @staticmethod
      def okayPressed(dialog):
        """ Called when okay is pressed """
        logger.debug("DiceSetupWindow: okay pressed")
        
        # check entered values are acceptable
        #if not dialog.userEntriesAcceptable():
        #  return
        
        # get the user's entries, making sure they're acceptable
        enteredValues = dialog.getUserEntries()
        if enteredValues is None:
          dialog.notify("Entered values are not valid")
          return
        
        # store the values and exit
        logger.debug("DiceSetupWindow: user's new values: {}".format(enteredValues))
        dialog.setValues(**enteredValues)
        dialog.close()
        
        # text of button
        # name = gui.sender().text()
    
    # call gui function from other threads
    funcCall = QtCore.pyqtSignal(object)
    
    
    

    
    @QtCore.pyqtSlot(object)
    def remoteCall(self, func):
      """ Allows us to call GUI functions from other threads """
      func()
    
    
    def __init__(self, parent, numberOfDiceInfo, numberOfDiceFacesInfo, numberOfRollsInfo):
      super().__init__(parent)
      
      # dice info
      self.numberOfDiceInfo      = numberOfDiceInfo
      self.numberOfDiceFacesInfo = numberOfDiceFacesInfo
      self.numberOfRollsInfo     = numberOfRollsInfo

      
      # update dialog from a different thread
      self.funcCall.connect(self.remoteCall)
      
      # holds values the user sets in the dialog box
      self.values = {}
      
      # reference to entries user makes
      self.numDiceInput  = None
      self.numFacesInput = None
      self.numRollsInput = None
      
      # create the layout
      self._createLayout()
    
    
    def _createLayout(self):
      """ Piece the layout together """
      
      self.setWindowTitle("Dice Setup")
      self.resize(1, 1)
  
      self.setModal(True)
      self.setObjectName("Dialog")
      
      
      windowLayout = QtWidgets.QVBoxLayout()
      
      #numberOfDice = 5, numberOfDiceFaces = 6, numberOfRolls
      
      #########################################################################
      # labels and text entry boxes
      #########################################################################

      minDice  = self.numberOfDiceInfo["min"]
      maxDice  = self.numberOfDiceInfo["max"]
      minFaces = self.numberOfDiceFacesInfo["min"]
      maxFaces = self.numberOfDiceFacesInfo["max"]
      minRolls = self.numberOfRollsInfo["min"]
      maxRolls = self.numberOfRollsInfo["max"]
      
      # labels
      labelLayout   = QtWidgets.QVBoxLayout()
      numDiceLabel  = QtWidgets.QLabel("Number of Dice {}-{}:".format(minDice, maxDice))
      numFacesLabel = QtWidgets.QLabel("Number of Faces {}-{}:".format(minFaces, maxFaces))
      numRollsLabel = QtWidgets.QLabel("Number of Rolls {}-{}:".format(minRolls, maxRolls))
      labelLayout.addWidget(numDiceLabel)
      labelLayout.addWidget(numFacesLabel)
      labelLayout.addWidget(numRollsLabel)
      
      # value entry
      inputLayout   = QtWidgets.QVBoxLayout()
      self.numDiceInput  = QtWidgets.QLineEdit()
      self.numDiceInput.setText(str(self.numberOfDiceInfo["curr"]))
      self.numFacesInput = QtWidgets.QLineEdit()
      self.numFacesInput.setText(str(self.numberOfDiceFacesInfo["curr"]))
      self.numRollsInput = QtWidgets.QLineEdit()
      self.numRollsInput.setText(str(self.numberOfRollsInfo["curr"]))
      inputLayout.addWidget(self.numDiceInput)
      inputLayout.addWidget(self.numFacesInput)
      inputLayout.addWidget(self.numRollsInput)
      
      # layout labels and their entries
      inputSelectionLayout = QtWidgets.QHBoxLayout()
      inputSelectionLayout.addLayout(labelLayout, 1)
      inputSelectionLayout.addLayout(inputLayout, 1000)

      #########################################################################
      # buttons
      #########################################################################
      
      # okay and cancel buttons
      cancelButton = QtWidgets.QPushButton("Cancel")
      okayButton   = QtWidgets.QPushButton("Okay")

      buttonLayout = QtWidgets.QHBoxLayout()
      buttonLayout.addStretch(10000)
      buttonLayout.addWidget(cancelButton)
      buttonLayout.addWidget(okayButton)
      
      # connect buttons to events
      cancelButton.clicked.connect(lambda: PyQtGUI.DiceSetupWindow.UserActions.cancelPressed(self))
      okayButton.clicked.connect(lambda: PyQtGUI.DiceSetupWindow.UserActions.okayPressed(self))
      
      
      #########################################################################
      # final layout assembly
      #########################################################################
      
      windowLayout.addLayout(inputSelectionLayout, 1)
      windowLayout.addStretch(1000)
      windowLayout.addLayout(buttonLayout, 1)
      
      self.setLayout(windowLayout)

      # fix the window size
      #  -need to wait for a bit so all elements can be set and sized
      def fn():
        time.sleep(0.1)
        self.funcCall.emit(lambda: self.setFixedSize(self.size()))
      threading.Thread(target=fn).start()


    def notify(self, text, title="Yahtzee", font=None):
      """ Display a message to the user """
  
      # create the info box
      msgBox = QtWidgets.QMessageBox(self)
      msgBox.setIcon(QtWidgets.QMessageBox.Information)
      msgBox.setWindowTitle(title)
      msgBox.setText(text)
      msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
  
      # set the text font
      if font is not None:
        msgBox.setFont(font)
  
      msgBox.exec()
    
    
    def getUserEntries(self):
      """ Return the user's entries, or None if any are invalid """
      
      # get the text entries
      try:
        numDice = int(self.numDiceInput.text())
        numFaces = int(self.numFacesInput.text())
        numRolls = int(self.numRollsInput.text())
      except ValueError:
        logger.debug("getUserEntries: not ints")
        return None
  
      # are all the values within acceptable ranges
      numDiceValid  = self.numberOfDiceInfo["min"] <= numDice <= self.numberOfDiceInfo["max"]
      numFacesValid = self.numberOfDiceFacesInfo["min"] <= numFaces <= self.numberOfDiceFacesInfo["max"]
      numRollsValid = self.numberOfRollsInfo["min"] <= numRolls <= self.numberOfRollsInfo["max"]
      logger.debug("getUserEntries: valid: {}".format([numDiceValid, numFacesValid, numRollsValid]))
      
      # return the results if all are valid
      if numDiceValid and numFacesValid and numRollsValid:
        return {
          "numberOfDice":      numDice,
          "numberOfDiceFaces": numFaces,
          "numberOfRolls":     numRolls
        }
      else:
        return None
    
    
    def getValues(self):
      """ Called by the GUI to return the user's new values """
      return self.values if len(self.values) > 0 else None
    
    
    def setValues(self, numberOfDice=None, numberOfDiceFaces=None, numberOfRolls=None):
      """ Set one or more dice values """
      if numberOfDice      is not None: self.values["numberOfDice"]      = numberOfDice
      if numberOfRolls     is not None: self.values["numberOfRolls"]     = numberOfRolls
      if numberOfDiceFaces is not None: self.values["numberOfDiceFaces"] = numberOfDiceFaces

  
  class NewPlayerWindow(QtWidgets.QDialog):
  
    class UserActions(object):
    
      @staticmethod
      def cancelPressed(dialog):
        """ Called when cancel is pressed """
        logger.debug("NewPlayerWindow: cancel pressed")
      
        # wipe the stored name
        dialog.name = None
      
        # close dialog
        dialog.close()
    
      @staticmethod
      def okayPressed(dialog):
        """ Called when okay is pressed """
        logger.debug("NewPlayerWindow: okay pressed")
        
        # get the new name, making sure it's acceptable
        newName = dialog.getUserEntry()
        if newName is None:
          return
      
        # store the new name and exit
        logger.debug("NewPlayerWindow: new player name: {}".format(newName))
        dialog.newName = newName
        dialog.close()

    # call gui function from other threads
    funcCall = QtCore.pyqtSignal(object)

    @QtCore.pyqtSlot(object)
    def remoteCall(self, func):
      """ Allows us to call GUI functions from other threads """
      func()

    def __init__(self, parent, existingPlayerNames, minNameLength=None, maxNameLength=None):
      super().__init__(parent)
      
      # name info
      self.existingPlayerNames = existingPlayerNames
      self.minNameLength = minNameLength
      self.maxNameLength = maxNameLength
    
      # holds new, chosen name
      self.newName = None
      
      # remember reference to text box
      self.nameInput = None
      
      # update dialog from a different thread
      self.funcCall.connect(self.remoteCall)
      
      # create the layout
      self._createLayout()
    
    
    def _createLayout(self):
      """ Piece the layout together """
    
      self.setWindowTitle("Enter Player's Name")
      self.resize(1, 1)
    
      self.setModal(True)
      self.setObjectName("Dialog")
    
      windowLayout = QtWidgets.QVBoxLayout()

      #########################################################################
      # text entry box
      #########################################################################

      self.nameInput = QtWidgets.QLineEdit()
      
      #########################################################################
      # buttons
      #########################################################################
    
      # okay and cancel buttons
      cancelButton = QtWidgets.QPushButton("Cancel")
      okayButton = QtWidgets.QPushButton("Okay")
    
      buttonLayout = QtWidgets.QHBoxLayout()
      buttonLayout.addStretch(10000)
      buttonLayout.addWidget(cancelButton)
      buttonLayout.addWidget(okayButton)
    
      # connect buttons to events
      cancelButton.clicked.connect(lambda: PyQtGUI.NewPlayerWindow.UserActions.cancelPressed(self))
      okayButton.clicked.connect(lambda: PyQtGUI.NewPlayerWindow.UserActions.okayPressed(self))
    
      #########################################################################
      # final layout assembly
      #########################################################################

      windowLayout.addStretch(1000)
      windowLayout.addWidget(self.nameInput, 1)
      windowLayout.addLayout(buttonLayout, 1)
    
      self.setLayout(windowLayout)
    
      # fix the window size
      #  -need to wait for a bit so all elements can be set and sized
      def fn():
        time.sleep(0.1)
        self.funcCall.emit(lambda: self.setFixedSize(self.size()))
    
      threading.Thread(target=fn).start()
    
    
    def notify(self, text, title="Yahtzee", font=None):
      """ Display a message to the user """
  
      # create the info box
      msgBox = QtWidgets.QMessageBox(self)
      msgBox.setIcon(QtWidgets.QMessageBox.Information)
      msgBox.setWindowTitle(title)
      msgBox.setText(text)
      msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
  
      # set the text font
      if font is not None:
        msgBox.setFont(font)
  
      msgBox.exec()

    def getUserEntry(self):
      """ Return the new player name, or None if it's invalid """
      
      newName = self.nameInput.text()
      
      # CHECK: name is a string
      if not isinstance(newName, str):
        self.notify("Name is not a valid string")
        return None
      
      # CHECK: length is valid
      if not (self.minNameLength <= len(newName) <= self.maxNameLength):
        self.notify("Name length must be between {}-{}".format(self.minNameLength, self.maxNameLength))
        return None

      # CHECK: name is unique
      if newName in self.existingPlayerNames:
        self.notify("Name is already in use")
        return None
      
      # all good
      return newName
    
    
    def getName(self):
      """ Return the new player name """
      return self.newName
    
  class UserActions(object):
    
    @staticmethod
    def cellClick(gui, cell, rowName, player):
      """ When a user clicks on the cell at <coordinates> """
      logger.debug("cellClick: {}, {}, {}".format(player.getName(), rowName, cell.text()))
      
      # score for the current player
      if player == gui.game.getCurrentPlayer():
        gui.controller.score(rowName)

    @staticmethod
    def addPlayerClicked(gui):
      """ Called whenever "add player" is clicked """
      logger.debug("addPlayerClicked")
      
      # call controller
      gui.controller.addPlayer()

    @staticmethod
    def editPlayerClicked(gui, playerName):
      """ Called whenever we try to edit a player """
      logger.debug("removePlayerClicked")

      # text of cell
      #name = gui.sender().text()
      
      # call controller
      gui.controller.editPlayer(playerName)
    
    
    @staticmethod
    def holdPressed(gui, diceIndex):
      """ Called whenever hold is pressed """
      logger.debug("holdPressed: {}".format(diceIndex))
      
      # text of button
      #name = gui.sender().text()
      
      #print(gui.sender().objectName())
      #print(gui.sender().objectName().split("-")[1])
      
      
      # get the hold button pressed
      #holdButtonNum = gui.sender().objectName().split("-")[1]
      
      # call controller
      gui.controller.toggleDiceHeldStatus(diceIndex)


    @staticmethod
    def rollPressed(gui):
      """ Called whenever roll is pressed """
      logger.debug("rollPressed")
      gui.controller.rollDice()

    
    @staticmethod
    def keyPressed(gui, event):
      """ Called when the user presses a key """
      
      key = event.key()
      
      # ignore anything that's not a number 1-9 or delete
      if key not in gui.DELETE_KEY_LIST and key not in gui.NUMBER_KEY_LIST:
        return
      
      # convert the key pressed to its value (delete is 0)
      if key in gui.DELETE_KEY_LIST:
        key = 0
      else:
        key = int(chr(key))
      
      # if we have a selected cell then update it
      if gui.selectedCell:
        gui.controller.updateBoard(x=gui.selectedCell.x,
                                   y=gui.selectedCell.y,
                                   value=key)
    
    @staticmethod
    def menuFile(gui):
      """ Called whenever a file menu item is clicked """
      
      name = gui.sender().text()
      
      # function to call for each menu option
      actionMap = {
        "New Game": gui.controller.newGame,
        "Quit":     sys.exit
      }
      
      # call menu function
      action = actionMap.get(name, None)
      if action is not None:
        action()
    
    @staticmethod
    def menuConfig(gui):
      """ Called whenever a board menu item is clicked """
      
      name = gui.sender().text()
      
      # function to call for each menu option
      actionMap = {
        "Dice": gui.controller.configureDice, #showBoardGeneratorWindow
      }
      
      # call menu function
      action = actionMap.get(name, None)
      
      # clicked on a board dimension option, so set the dimensions
      if action is not None:
        action()
    
    @staticmethod
    def menuHelp(gui):
      """ Called whenever a help menu item is clicked """
      
      name = gui.sender().text()
      
      # function to call for each menu option
      actionMap = {
        "How to Play": gui.showHowToPlay,
        "About":       gui.showAbout,
      }
      
      # call menu function
      action = actionMap.get(name, None)
      if action is not None:
        action()
  
  class LayoutCreator(object):
    
    def __init__(self, gui):
      
      self.gui = gui
      
      """
      # use a box layout for the other layouts
      self.mainLayout = QtWidgets.QVBoxLayout()
      self.mainWindow.setLayout(self.mainLayout)

      self.mainWindow.setStyleSheet(self.gui.MAIN_WINDOW_STYLE)
      
      # GUI elements we want to be able to update
      self.displayDice = None
      self.scoreCells  = None
      self.statusText  = None
      """
      
    # def setGameGridCell(self, row, column, value):
    #  self.gameGrid[row][column].setText(value)
    
    
    def _createPlayerNameCell(self, playerName):
      """ Create the cell for a player's name """

      # cell is a label
      cell = QtWidgets.QLabel(playerName)
      cell.setAlignment(QtCore.Qt.AlignCenter)
      cell.setScaledContents(True)
      
      # set style
      cell.setStyleSheet(self.gui.SCORE_STYLE_NORMAL)
      
      # font for cell text
      font = QtGui.QFont()
      font.setPointSize(12)
      cell.setFont(font)

      # can't "click" labels, so register a click with a mouse event
      cell.mousePressEvent = lambda event: PyQtGUI.UserActions.editPlayerClicked(self.gui, playerName)
      
      return cell
    
    
    def _createLabelCell(self, contents, align=QtCore.Qt.AlignLeft):
      """ Create an individual grid cell """

      # cell is a label
      cell = QtWidgets.QLabel(contents)
      cell.setAlignment(align)
      cell.setScaledContents(True)

      if "Lower" in contents or "Upper" in contents:
        cell.setStyleSheet(self.gui.SCORE_STYLE_TOTAL)
      else:
        cell.setStyleSheet(self.gui.SCORE_STYLE_NORMAL)

      # font for cell text
      font = QtGui.QFont()
      font.setPointSize(12)
      cell.setFont(font)

      return cell
    
    
    def _createAddPlayerCell(self):
      """ Create the "add player" button-cell """

      # cell is a label
      cell = QtWidgets.QLabel("+")
      cell.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
      cell.setScaledContents(True)
      
      # set style
      cell.setStyleSheet(self.gui.ADD_PLAYER_CELL_STYLE)
      
      # font for cell text
      font = QtGui.QFont()
      font.setPointSize(14)
      font.setBold(True)
      cell.setFont(font)

      # can't "click" labels, so register a click with a mouse event
      cell.mousePressEvent = lambda event: PyQtGUI.UserActions.addPlayerClicked(self.gui)
      
      return cell
    
    
    def _createProbabilityCell(self, align=QtCore.Qt.AlignCenter):
      """
      # Create a score cell
      #
      # score:   (int) current score
      # rowName: (str) row in scorecard
      # player:  (Player) the scorecard belongs to
      # x:       (int) x-axis grid position of cell
      # y:       (int) y-axis grid position of cell
      #
      """

      # make None scores blank
      prob = "@"# if score is None else str(score)

      # cell is a label
      cell = QtWidgets.QLabel(prob)
      cell.setAlignment(align)
      cell.setScaledContents(True)

      cell.setStyleSheet(self.gui.PROBABILITY_STYLE_NORMAL)
      # cell.setMinimumWidth(222)

      # font for cell text
      font = QtGui.QFont()
      font.setPointSize(12)
      cell.setFont(font)

      # can't "click" labels, so register a click with a mouse event
      #cell.mousePressEvent = lambda event: PyQtGUI.UserActions.cellClick(self.gui, cell, rowName, player)
      return cell
    
    
    def _createScoreCell(self, score, rowName, player, align=QtCore.Qt.AlignCenter):
      """
      # Create a score cell
      #
      # score:   (int) current score
      # rowName: (str) row in scorecard
      # player:  (Player) the scorecard belongs to
      # x:       (int) x-axis grid position of cell
      # y:       (int) y-axis grid position of cell
      #
      """

      # make None scores blank
      score = "" if score is None else str(score)

      # cell is a label
      cell = QtWidgets.QLabel(score)
      cell.setAlignment(align)
      cell.setScaledContents(True)

      if "Lower" in rowName or "Upper" in rowName:
        cell.setStyleSheet(self.gui.SCORE_STYLE_TOTAL)
      else:
        cell.setStyleSheet(self.gui.SCORE_STYLE_NORMAL)
      # cell.setMinimumWidth(222)

      # font for cell text
      font = QtGui.QFont()
      font.setPointSize(12)
      cell.setFont(font)

      # can't "click" labels, so register a click with a mouse event
      cell.mousePressEvent = lambda event: PyQtGUI.UserActions.cellClick(self.gui, cell, rowName, player)
      return cell

    def createScorecard(self, players):
      """ Display the scorecards of the players"""
      
      if len(players) < 1:
        raise ValueError("trying to display the scorecards of 0 players")

      # grid layout for grid...
      gridLayout = QtWidgets.QGridLayout()
      gridLayout.setSpacing(0)
      
      # get the names of the scorecard rows (same for each player)
      rowNames = players[0].getScorecard().getRowNames()
      

      
      # populate the label column
      for iLabel, label in enumerate(rowNames):
        gridLayout.addWidget(self._createLabelCell(label), iLabel+1, 0)
      
      # populate player names row
      playerNameCells = {}
      for iPlayer, player in enumerate(players):
        nameCell = self._createPlayerNameCell(player.getName())
        gridLayout.addWidget(nameCell, 0, iPlayer + 1)#, alignment=QtCore.Qt.AlignCenter)
        
        # remember the cell for this player's name
        playerNameCells[player.getName()] = nameCell
      
      # add the "add player" button-cell
      addPlayerCell = self._createAddPlayerCell()
      gridLayout.addWidget(addPlayerCell, 0, len(playerNameCells)+1)
      
      # create empty score cells
      scoreCells = {}
      for iPlayer, player in enumerate(players):
        
        # this player's scorecard
        scorecard = player.getScorecard()
        
        # remember the score cells for this player
        scoreCells[player] = {}
        
        # display the current score
        for iRow, rowName in enumerate(scorecard.getRowNames()):
          currScore = scorecard.getRowScore(rowName)
          scoreCell = self._createScoreCell(currScore, rowName, player)
          gridLayout.addWidget(scoreCell, iRow+1, iPlayer+1)
          
          # remember this cell
          scoreCells[player][rowName] = scoreCell

      return playerNameCells, scoreCells, gridLayout
      
      
      
    @staticmethod
    def deleteLayout(layout):
      """ Delete all of the layout elements """
      
      while layout.count():
        child = layout.takeAt(0)
        widget = child.widget()
        
        if widget:
          layout.removeWidget(widget)
          widget.deleteLater()
        
        else:
          try:
            if child.count():
              PyQtGUI.LayoutCreator.deleteLayout(child)
              child.deleteLater()
          except:
            pass
      
      # for i in reversed(range(self.mainLayout.count())):
      #  self.mainLayout.itemAt(i).setParent(None)
      
      # remove any previous gui elements
      # while self.mainLayout.count() > 0:
      #  self.mainLayout.takeAt(0)
    
    def DEPsetlayout(self, game):
      
      # remove any previous gui elements
      self._delLayout()
      
      # menu bar
      menuLayout = self.createMenuBar()
      self.mainLayout.insertLayout(0, menuLayout, 1)
      
      # scorecard
      self.scoreCells, scorecardLayout = self.createScorecard(game.getAllPlayers())
      self.mainLayout.insertLayout(1, scorecardLayout, 1)
      
      # probability grid
      
      # roll box
      self.displayDice, rollBoxLayout = self.createRollBox(game.getNumberOfDice())
      self.mainLayout.insertLayout(2, rollBoxLayout, 1)
      
      # game grid
      #self.gameGrid, gridLayout = self.createGrid(rows=rows, columns=columns)
      #self.mainLayout.insertLayout(1, gridLayout, 1000)
      
      # controls
      #controls = self.createControls()
      #self.mainLayout.insertLayout(2, controls, 1)
      
      # set window size
      #  -need to wait for a bit for all past elements to be removed
      #def fn():
      #  time.sleep(0.1)
      #  self.gui.funcCall.emit(lambda: self.gui.mainWindow.setWindowState(QtCore.Qt.WindowNoState))
      #  self.gui.funcCall.emit(lambda: self.gui.mainWindow.resize(35 * rows, 35 * columns))
      
      #threading.Thread(target=fn).start()
    
    
    def createMenuBar(self):
      """ Create the menu bar GUI elements"""
      
      # layout
      menuLayout = QtWidgets.QHBoxLayout()
      menuLayout.setAlignment(QtCore.Qt.AlignTop)
      
      # menu bar itself
      menubar = QtWidgets.QMenuBar()
      menubar.setNativeMenuBar(False)
      menubar.setStyleSheet(self.gui.MENU_BAR_STYLE)
      menuLayout.addWidget(menubar)
      menuLayout.addStretch(1000)
      
      ###########################################################################
      # file
      ###########################################################################
      
      fileMenu = menubar.addMenu("File")
      fileMenu.addAction("New Game", lambda: PyQtGUI.UserActions.menuFile(self.gui))
      fileMenu.addSeparator()
      fileMenu.addAction("Quit", lambda: PyQtGUI.UserActions.menuFile(self.gui))
      
      ###########################################################################
      # config
      ###########################################################################
      
      configMenu = menubar.addMenu("Config")
      configMenu.addAction("Dice", lambda: PyQtGUI.UserActions.menuConfig(self.gui))
      

      
      ###########################################################################
      # help
      ###########################################################################
      
      helpMenu = menubar.addMenu("Help")
      helpMenu.addAction("How to Play", lambda: PyQtGUI.UserActions.menuHelp(self.gui))
      helpMenu.addAction("About",       lambda: PyQtGUI.UserActions.menuHelp(self.gui))
      
      return menuLayout

    
    def _createSingleDice(self, diceIndex):
      
      diceLabel = QtWidgets.QLabel(objectName="image")
      diceLabel.setAlignment(QtCore.Qt.AlignCenter)
      diceLabel.setScaledContents(True)
      #diceLabel.setStyleSheet(self.gui.DICE_IMAGE_FREE)
      diceLabel.setStyleSheet(self.gui.DICE_BLANK)
      diceLabel.setText("#")
      
      #imgLoc = os.path.join("imgs", "dice-{}.png".format(diceIndex + 1))
      #pixmap = QtGui.QPixmap(imgLoc)
      #diceLabel.setPixmap(pixmap)
      
      # font for cell text
      font = QtGui.QFont()
      font.setPointSize(14)
      font.setBold(True)
      diceLabel.setFont(font)
      
      diceLabel.setMinimumWidth(50)
      diceLabel.setMaximumWidth(50)
      
      diceLabel.setMinimumHeight(50)
      diceLabel.setMaximumHeight(50)

      holdLabel = QtWidgets.QLabel("-", objectName="button")

      holdLabel.setAlignment(QtCore.Qt.AlignCenter)
      holdLabel.setScaledContents(True)
      holdLabel.setStyleSheet(self.gui.DICE_LABEL_FREE)

      # can't "click" labels, so register a click with a mouse event
      diceLabel.mousePressEvent = lambda event: PyQtGUI.UserActions.holdPressed(self.gui, diceIndex)
      holdLabel.mousePressEvent = lambda event: PyQtGUI.UserActions.holdPressed(self.gui, diceIndex)

      # holdButton = QtWidgets.QPushButton("Hold", objectName="hold-{}".format(iDice))
      # holdButton.clicked.connect(lambda: PyQtGUI.UserActions.buttonPressed(self.gui))

      singleDiceBox = QtWidgets.QVBoxLayout()
      singleDiceBox.addWidget(diceLabel, 100, alignment=QtCore.Qt.AlignCenter)
      singleDiceBox.addWidget(holdLabel, 1)

      return singleDiceBox
    
    
    def createRollBox(self, numDice):
      """ Create the control buttons at the bottom of the window """

      displayDice = []
      
      # create each die and put it in the diceBox
      diceBox = QtWidgets.QHBoxLayout()
      diceBox.insertStretch(0, 10000)
      for iDice in range(numDice):
        singleDice = self._createSingleDice(iDice)
        displayDice.append(singleDice)
        diceBox.addLayout(singleDice)
      diceBox.insertStretch(numDice+1, 10000)
      

      
      
      # create the button to roll the dice
      #  -starts the game at the start
      rollButton = QtWidgets.QPushButton("Start")
      
      # font for roll button
      rollFont = QtGui.QFont()
      rollFont.setPointSize(16)
      rollButton.setFont(rollFont)
      
      # style
      rollButton.setStyleSheet(self.gui.ROLL_BUTTON_STYLE)
      
      rollButton.clicked.connect(lambda: PyQtGUI.UserActions.rollPressed(self.gui))
      buttonBox = QtWidgets.QHBoxLayout()
      buttonBox.addWidget(rollButton, 1000)
      #rollBox.setStretch(0, 1)
      #rollBox.setStretch(1, 1000)

      # put the dice box and roll button into the rollBox
      rollBox = QtWidgets.QVBoxLayout()
      rollBox.addLayout(diceBox)
      rollBox.addLayout(buttonBox)#, alignment=QtCore.Qt.AlignCenter)
      
      # put horizontal stretchers around the roll box so it maintains its shape
      rollBoxUnstretcher = QtWidgets.QHBoxLayout()
      rollBoxUnstretcher.insertStretch(0, 10000)
      rollBoxUnstretcher.addLayout(rollBox)
      rollBoxUnstretcher.insertStretch(2, 10000)
      
      return rollButton, displayDice, rollBoxUnstretcher
  
  
    def createProbabilityGrid(self, players, numDiceFaces):
      """ Grid for displaying the probabilities for each row"""
      
      # grid layout for grid...
      gridLayout = QtWidgets.QGridLayout()
      gridLayout.setSpacing(0)
      
      
      
      # get the names of the scorecard rows (same for each player)
      #  -skip total and bonus
      upperRowNames = players[0].getScorecard().getRowNames(section="upper")[:-2]
  
      # populate the rowName column
      for iLabel, label in enumerate(upperRowNames):
        gridLayout.addWidget(self._createLabelCell(label), iLabel + 1, 0)
  
      # populate dice count row
      for iDice in range(1, numDiceFaces+1):
        nameCell = self._createLabelCell(str(iDice), align=QtCore.Qt.AlignCenter)
        gridLayout.addWidget(nameCell, 0, iDice)
        
      # create the probability grid
      probCells = {}
      for iRow, rowName in enumerate(upperRowNames):
  
        probCells[rowName] = {}
        
        for diceNum in range(1, numDiceFaces+1):
          
          probCells[rowName][diceNum] = self._createProbabilityCell()
          gridLayout.addWidget(probCells[rowName][diceNum], iRow+1, diceNum)
      
      
      return probCells, gridLayout
  
    @staticmethod
    def resizeScorecard(scorecardLayout):
      """ Dynamically resize the scorecard so the name columns are consistent """
      
      # minimum width on each side of the name
      widthBorder = 4
      
      # assemble the list of widgets in the player name row
      nameWidgetList = []
      while True:
        element = scorecardLayout.itemAtPosition(0, len(nameWidgetList)+1)
        if element is None:
          break
        else:
          nameWidgetList.append(element.widget())
      
      # drop the last widget as it's the "add player" cell
      nameWidgetList = nameWidgetList[:-1]
      
      # set all widgets to the same width as the widest widget
      maxWidth = max([x.width() for x in nameWidgetList])
      for widget in nameWidgetList:
        widget.setMinimumWidth(maxWidth + widthBorder*2)

  
  # call gui function from other threads
  funcCall = QtCore.pyqtSignal(object)

  @QtCore.pyqtSlot(object)
  def remoteCall(self, func):
    """ Allows us to call GUI functions from other threads """
    func()
  
  
  # initial setup
  def __init__(self, controller, game):
    """ GUI initialisation """
    
    super().__init__()
    
    # update GUI from a different thread
    self.funcCall.connect(self.remoteCall)
    
    # references to controller and model
    self.controller = controller
    self.game       = game
    
    
    ###########################################################################
    # define stylesheets for GUI elements and text
    ###########################################################################
    
    # text styles
    #  -initial are underlined, others are normal
    self.TEXT_STYLE_NORMAL = ""
    self.TEXT_STYLE_INITIAL = " text-decoration: underline; "
    
    # player name styles
    defaultNameStyle = "border-style: outset; border-width: 1px; border-color: black; "
    self.PLAYER_NAME_INACTIVE = defaultNameStyle + " color: black; background: white; "
    self.PLAYER_NAME_ACTIVE   = defaultNameStyle + " color: black; background: aquamarine; "
    
    # add player button-cell
    self.ADD_PLAYER_CELL_STYLE = "border-style: solid; border-width: 1px; border-color: black; background: white; "
    
    # score styles
    defaultScoreStyle = "border-style: outset; border-width: 1px; border-color: black; "
    self.SCORE_STYLE_NORMAL        = defaultScoreStyle + " background: white; color: black; "
    self.SCORE_STYLE_POSSIBLE      = defaultScoreStyle + " background: white; color: dodgerblue; "
    self.SCORE_STYLE_POSSIBLE_ZERO = defaultScoreStyle + " background: white; color: crimson; "
    self.SCORE_STYLE_TOTAL         = defaultScoreStyle + " background: linen; color: black; border-width: 1px;"
    
    # probability grid style
    defaultProbStyle = "border-style: outset; border-width: 1px; border-color: black; "
    self.PROBABILITY_STYLE_NORMAL = defaultProbStyle + " background: white; color: black; "
    
    # dice
    self.DICE_BLANK = "border-style: outset; color: white; background: crimson; "
    
    # roll button
    self.ROLL_BUTTON_STYLE = "border-style: solid; border-width: 2px; border-color: black;" + \
                             "color: black; background: lightsteelblue; "
    
    # main window
    self.MAIN_WINDOW_STYLE = " "#background: white; "
    
    # table
    self.TABLE_STYLE = " background: forestgreen; "
    
    # menu bar
    self.MENU_BAR_STYLE = "padding: 0px; background: white; "
    
    # hold label
    defaultDicedStyle = "border-style: outset; "
    self.DICE_LABEL_FREE = defaultDicedStyle + " background: white; "
    self.DICE_LABEL_HELD = defaultDicedStyle + " background: lightskyblue; "
    
    """
    # group cell styles
    self.CELL_STYLE_1 = defaultScoreStyle + "background: powderblue;"
    self.CELL_STYLE_2 = defaultScoreStyle + "background: bisque;"
    self.CELL_STYLE_3 = defaultScoreStyle + "background: khaki;"
    self.CELL_STYLE_4 = defaultScoreStyle + "background: lightskyblue;"
    self.CELL_STYLE_5 = defaultScoreStyle + "background: aquamarine;"
    self.CELL_STYLE_6 = defaultScoreStyle + "background: thistle;"
    self.CELL_STYLE_7 = defaultScoreStyle + "background: palegoldenrod;"
    self.CELL_STYLE_8 = defaultScoreStyle + "background: lightsteelblue;"
    self.CELL_STYLE_9 = defaultScoreStyle + "background: palegreen;"
    
    # invalid group styles
    self.CELL_STYLE_INVALID = defaultScoreStyle + "background: crimson;"
    """

    
    ###########################################################################
    # create the GUI
    ###########################################################################
    
    # application object
    self.app = QtWidgets.QApplication(sys.argv)
    
    self.mainWindow = QtWidgets.QWidget()
    self.mainWindow.setWindowTitle("Yahtzee")
    
    # GUI elements we want to be able to update
    self.mainLayout       = None
    self.rollButton       = None
    self.displayDice      = None
    self.playerNameCells  = None
    self.probabilityCells = None
    self.scoreCells       = None
    self.statusText       = None
    
    # create the GUI elements
    self.createLayout()
  
  
  def createLayout(self):
    """ Create and layout all of the window elements """
    logger.debug("createLayout")
    
    
    ###########################################################################
    # main window setup
    ###########################################################################
    
    # if this is the first time we're creating the layout
    if self.mainLayout is None:
      
      # use a box layout for the other layouts
      self.mainLayout = QtWidgets.QVBoxLayout()
      self.mainWindow.setLayout(self.mainLayout)
    
    # else, delete all the elements from the existing layout
    else:
      logger.debug("createLayout: deleting existing layout")
      PyQtGUI.LayoutCreator.deleteLayout(self.mainLayout)
    
    
    # main stylesheet
    self.mainWindow.setStyleSheet(self.MAIN_WINDOW_STYLE)
    
    
    ###########################################################################
    # layout main elements
    ###########################################################################
    
    # get a layout creator
    appCreator = PyQtGUI.LayoutCreator(self)
    
  
    # menu bar
    logger.debug("Creating layout: menu bar")
    menuLayout = appCreator.createMenuBar()
    self.mainLayout.insertLayout(0, menuLayout, 1)

    # probability grid
    logger.debug("Creating layout: probability grid")
    self.probabilityCells, probGridLayout = appCreator.createProbabilityGrid(self.game.getAllPlayers(),
                                                                             self.game.getNumberOfDiceFaces())
    # roll box
    logger.debug("Creating layout: roll box")
    self.rollButton, self.displayDice, rollBoxLayout = appCreator.createRollBox(self.game.getNumberOfDice())
   
    # scorecard
    logger.debug("Creating layout: scorecard")
    self.playerNameCells, self.scoreCells, scorecardLayout = appCreator.createScorecard(self.game.getAllPlayers())
   
    # left side:
    #  -top: probability grid
    #  -bot: roll box
    leftLayout  = QtWidgets.QVBoxLayout()
    leftLayout.insertLayout(0, probGridLayout, 1)
    leftLayout.insertStretch(1, 10000)
    leftLayout.insertLayout(2, rollBoxLayout, 1)
    
    # right side:
    #  -full: scorecard
    rightLayout = QtWidgets.QVBoxLayout()
    rightLayout.insertLayout(0, scorecardLayout, 100)
    
    # game-table elements
    #  -left stuff on left, right on right
    #  -make it a widget so we can style it
    tableLayout = QtWidgets.QHBoxLayout()
    tableLayout.insertLayout(0, leftLayout, 100)
    tableLayout.insertLayout(1, rightLayout, 1)
    #
    tableWidget = QtWidgets.QWidget()
    tableWidget.setLayout(tableLayout)
    tableWidget.setStyleSheet(self.TABLE_STYLE)
    
    
    self.mainLayout.insertWidget(1, tableWidget, 100)
    
    
    #appCreator.resizeScorecard(scorecardLayout)

    # resize the window elements after they have been displayed
    #  -need to wait for a bit so all elements can be set and sized
    def fn():
      time.sleep(0.1)
      self.funcCall.emit(lambda: PyQtGUI.LayoutCreator.resizeScorecard(scorecardLayout))
      
    threading.Thread(target=fn).start()
    
    
    
    # game grid
    # self.gameGrid, gridLayout = self.createGrid(rows=rows, columns=columns)
    # self.mainLayout.insertLayout(1, gridLayout, 1000)
  
    # controls
    # controls = self.createControls()
    # self.mainLayout.insertLayout(2, controls, 1)
  
    # set window size
    #  -need to wait for a bit for all past elements to be removed
    # def fn():
    #  time.sleep(0.1)
    #  self.gui.funcCall.emit(lambda: self.gui.mainWindow.setWindowState(QtCore.Qt.WindowNoState))
    #  self.gui.funcCall.emit(lambda: self.gui.mainWindow.resize(35 * rows, 35 * columns))

    # threading.Thread(target=fn).start()


  
  
  def _updateDiceImage(self, diceIndex, diceValue):
    """
    # Set the dice image to the given value
    #  -diceValue of -1 means blank
    #
    #
    #
    """
    
    # get the image that corresponds to the dice values
    #imgLoc = os.path.join("imgs", "dice-{}.png".format(diceValue))
    #pixmap = QtGui.QPixmap(imgLoc)
  
    # isolate the image-showing label and update the image
    diceLabel = self.displayDice[diceIndex].itemAt(0).widget()

    diceLabel.setStyleSheet(self.DICE_BLANK)
    diceValue = "#" if diceValue == -1 else str(diceValue)
    diceLabel.setText(diceValue)

    # imgLoc = os.path.join("imgs", "dice-{}.png".format(diceIndex + 1))
    # pixmap = QtGui.QPixmap(imgLoc)
    # diceLabel.setPixmap(pixmap)

    # font for cell text
    #font = QtGui.QFont()
    #font.setPointSize(14)
    #font.setBold(True)
    #diceLabel.setFont(font)
    
    
    #diceLabel.setPixmap(pixmap)
  
  
  def _updateHeldDice(self, diceIndex, isHeld):
    """ Update the image of held or free dice """
  
    diceLabel = self.displayDice[diceIndex].itemAt(0).widget()
    holdLabel = self.displayDice[diceIndex].itemAt(1).widget()
  
    if isHeld:
      #diceLabel.setStyleSheet(self.DICE_IMAGE_HELD)
      holdLabel.setStyleSheet(self.DICE_LABEL_HELD)
      holdLabel.setText("Held")
    else:
      #diceLabel.setStyleSheet(self.DICE_IMAGE_FREE)
      holdLabel.setStyleSheet(self.DICE_LABEL_FREE)
      holdLabel.setText("-")
  
    
  def _updateRollButton(self, text):
    """ Set the text in on the roll button """
    self.rollButton.setText(text)
  
  def _updatePossibleScorecardCell(self, cell, rowName, rowScore):
    """ Display a possible score in the given cell """
    
    # different styles for zero and non-zero scores
    style = self.SCORE_STYLE_POSSIBLE_ZERO if rowScore is None or rowScore == 0 else self.SCORE_STYLE_POSSIBLE
    cell.setStyleSheet(style)
    
    # surround values with dashes to better differentiate from actual scores
    rowScore = "" if rowScore is None else "--" + str(rowScore) + "--"
    cell.setText(rowScore)


  def _updateScorecardCell(self, cell, rowName, rowScore):
    """ Display a score in the given cell """
    
    # different styles for total and bonus rows
    if "Lower" in rowName or "Upper" in rowName:
      cell.setStyleSheet(self.SCORE_STYLE_TOTAL)
    else:
      cell.setStyleSheet(self.SCORE_STYLE_NORMAL)
    
    # no scores are just blank
    rowScore = "" if rowScore is None else str(rowScore)
    cell.setText(rowScore)


  def updateDice(self, diceValues):
    """ Show the current values of the dice """
    logger.debug("updateDice: {}".format(diceValues))
    
    # update the given dice values
    for iDice, diceVal in enumerate(diceValues):
      if diceVal is not None:
        self._updateDiceImage(iDice, diceVal)
    
    # dice change (always?) means a roll was done, so update roll button
    self._updateRollButton("Roll ({})".format(self.game.getRemainingRolls()))
    

  def updateHeldDice(self, heldDiceIndices):
    """ Update the display to show the currently held and free dice """
    logger.debug("updateHeldDice: {}".format(heldDiceIndices))
  
    for diceIndex in range(self.game.getNumberOfDice()):
      self._updateHeldDice(diceIndex, diceIndex in heldDiceIndices)
      


    
    
  def updatePossibleScorecard(self, playerList):
    """ Show the possible scores given the current dice values """
  
    for player in playerList:
      
      # get the possible scores given the current dice values
      possibleScorecard = player.getScorecard().getPossibleScorecard(self.game.getDiceValues())
      
      # display the possible scores
      for rowName, rowScore in possibleScorecard.iterateOverScorecard():
  
        cellToUpdate = self.scoreCells[player][rowName]
        
        # skip None: rows already filled in, totals, bonuses
        if rowScore is None:
          continue

        # update the score cell
        #   -skip 0 scores: unless we're out of rolls
        if rowScore == 0 and self.game.getRemainingRolls() > 0:
          currentScore = player.getScorecard().getRowScore(rowName)
          self._updateScorecardCell(cellToUpdate, rowName, currentScore)
        else:
          self._updatePossibleScorecardCell(cellToUpdate, rowName, rowScore)
  
  
  def updateScorecard(self, playerList):
    """ Update the scorecard scores """
    logger.debug("updateScorecard: {}".format([x.getName() for x in playerList]))
  
    for player in playerList:
      for rowName, rowScore in player.getScorecard().iterateOverScorecard():
        # convert rowScore to string equivalent
        rowScore = "" if rowScore is None else str(rowScore)
      
        # update the score cell
        cellToUpdate = self.scoreCells[player][rowName]
        self._updateScorecardCell(cellToUpdate, rowName, rowScore)

  def startPlayerTurn(self, player):
    """ Start this player's turn """
  
    # name of current player
    currPlayerName = player.getName()
    
    ###########################################################################
    # highlight player name
    ###########################################################################
    
    # show the current player's name as active, and the others as inactive
    for playerName, playerCell in self.playerNameCells.items():
      if playerName == currPlayerName:
        playerCell.setStyleSheet(self.PLAYER_NAME_ACTIVE)
      else:
        playerCell.setStyleSheet(self.PLAYER_NAME_INACTIVE)
    
    
    ###########################################################################
    # reset dice
    ###########################################################################
    
    # no held dice
    self.updateHeldDice([])
    
    # no dice images
    for iDice in range(len(self.game.getDiceValues())):
      self._updateDiceImage(iDice, -1)
    
    
    ###########################################################################
    # reset roll button
    ###########################################################################
    
    self._updateRollButton("Roll ({})".format(self.game.getRemainingRolls()))
    
  
  @staticmethod
  def _assembleFinalScoreMessage(totalScores):
    """ Create a final score message to show the player(s) """
    
    # get and order the scores
    scores = [(name, score) for name, score in totalScores.items()]
    scores.sort(key=lambda x: x[1], reverse=True)
  
    # find the longest player name/score and get its character length
    maxNameLength = max(map(len, list(totalScores.keys())))
    maxScoreLength = len(str(max(list(totalScores.values()))))
  
    # length of score line
    #  -name + colon + space + score
    lineLength = maxNameLength + 2 + maxScoreLength
  
    # assemble the score line for each player
    #  -<name>: <score>
    scoreMsg = ""
    for name, score in scores:
      nameStr = (name + ":").ljust(maxNameLength + 1, " ")
      scoreStr = str(score).rjust(maxScoreLength, " ")
      scoreMsg += nameStr + " " + scoreStr + "\n"
  
    # bookend the score message with dashes
    scoreMsg = "".ljust(lineLength, "-") + "\n" + scoreMsg + "".ljust(lineLength, "-")
  
    # font for scores
    font = QtGui.QFont("TypeWriter")
    font.setStyleHint(QtGui.QFont.TypeWriter)
    font.setFixedPitch(True)
    font.setPointSize(15)
    font.setBold(True)
    
    # return the final message and the font
    return scoreMsg, font
  
  
  def gameComplete(self):
    """ Called when game is completed """
    logger.debug("gameComplete")
    
    # assemble the score message and its font
    scoreMsg, font = self._assembleFinalScoreMessage(self.game.getTotalScores())
    
    # notify the user of the final scores
    self.notifyStatus(scoreMsg, title="Game Over", font=font)
    
    
  def newGame(self, game):
    """ Reset the GUI and start a new game """
    
    self.game = game
    self.createLayout()
  
  
  def confirmAction(self, text, title="Yahtzee", font=None):
    """ Ask the user to confirm they want to do <the thing> """
    
    # create the question box
    msgBox = QtWidgets.QMessageBox(self.mainWindow)
    msgBox.setIcon(QtWidgets.QMessageBox.Question)
    msgBox.setWindowTitle(title)
    msgBox.setText(text)
    msgBox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
    msgBox.setDefaultButton(QtWidgets.QMessageBox.No)

    # set the text font
    if font is not None:
      msgBox.setFont(font)
    
    # returns True if the user chooses "yes"
    return msgBox.exec() == QtWidgets.QMessageBox.Yes
    
    
  
  
  def notifyStatus(self, text, title="Yahtzee", font=None):
    """ Status notification; used or ignored, up to the GUI """
    
    # create the info box
    msgBox = QtWidgets.QMessageBox(self.mainWindow)
    msgBox.setIcon(QtWidgets.QMessageBox.Information)
    msgBox.setWindowTitle(title)
    msgBox.setText(text)
    msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
    
    # set the text font
    if font is not None:
      msgBox.setFont(font)

    msgBox.exec()
  
  
  def run(self):
    """ Enter the main loop of the GUI """
    
    self.mainWindow.show()
    sys.exit(self.app.exec_())
  

  def requestNewPlayerName(self, existingPlayers=None):
    """
    # Ask the user for the name of the new player to add
    #  -returns new name or None
    #
    # existingPlayers: (list) of existing player names to exclude
    """

    # create the new player name window
    newPlayerWindow = PyQtGUI.NewPlayerWindow(self.mainWindow,
                                              existingPlayerNames=existingPlayers,
                                              minNameLength=self.game.MIN_PLAYER_NAME_LENGTH,
                                              maxNameLength=self.game.MAX_PLAYER_NAME_LENGTH)

    # display the window and get the new name, if any
    newPlayerWindow.exec()
    return newPlayerWindow.getName()

  def requestDiceSetup(self):
    """
    # Ask the user for info on the new dice setup
    #  -returns new values or None
    #
    # Show the window for configuring the dice
    """
    
    # assemble the current dice info
    numberOfDiceInfo = {
      "curr": self.game.getNumberOfDice(),
      "min":  self.game.MIN_NUM_DICE,
      "max":  self.game.MAX_NUM_DICE
    }
    numberOfDiceFacesInfo = {
      "curr": self.game.getNumberOfDiceFaces(),
      "min":  self.game.MIN_DICE_FACES,
      "max":  self.game.MAX_DICE_FACES
    }
    numberOfRollsInfo = {
      "curr": self.game.getNumberOfRolls(),
      "min":  self.game.MIN_NUM_ROLLS,
      "max":  self.game.MAX_NUM_ROLLS
    }
    
    # create the dice setup window
    diceSetup = PyQtGUI.DiceSetupWindow(self.mainWindow, numberOfDiceInfo,
                                        numberOfDiceFacesInfo, numberOfRollsInfo)
    
    # display the setup window and get the results
    diceSetup.exec()
    return diceSetup.getValues()
    
  
  
  def showHowToPlay(self):
    """ Display the dialog that discribes how to play """
    msgBox = QtWidgets.QMessageBox(self.mainWindow)
    msgBox.setWindowTitle("How to Play")
    msgBox.setTextFormat(QtCore.Qt.RichText)
    msgBox.setText(self.controller.howToPlayText("richtext"))
    msgBox.exec()
  
  
  def showAbout(self):
    """ Display the "about" dialog """
    msgBox = QtWidgets.QMessageBox(self.mainWindow)
    msgBox.setWindowTitle("About")
    msgBox.setTextFormat(QtCore.Qt.RichText)
    msgBox.setText(self.controller.aboutText("richtext"))
    msgBox.exec()
