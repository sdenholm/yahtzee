import logging
logger = logging.getLogger(__name__)

import os
import threading
import time
import sys

import numpy as np

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
  
  def notifyStatus(self, text):
    """ Status notification; used or ignored, up to the GUI """
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


  class DEPBoardGeneratorDialog(QtWidgets.QDialog):
    
    class UserActions(object):
      
      @staticmethod
      def generateButtonPressed(dialog, gui):
        """ """
        
        startGenerationMsg = "Generate"
        stopGenerationMsg = "Stop"
        
        buttonText = dialog.sender().text()
        
        # if the user wants to stop an ongoing generation
        if buttonText == stopGenerationMsg:
          gui.controller.stopBoardGeneration()
          return
        
        # CHECK: row choice is valid
        rows = dialog.getRowChoice()
        if not rows.isdigit():
          dialog.setStatus("Rows must be a number")
          return
        
        # CHECK: column choice is valid
        columns = dialog.getColumnChoice()
        if not columns.isdigit():
          dialog.setStatus("Columns must be a number")
          return
        
        # CHECK: number of boards choice is valid
        numBoards = dialog.getNumBoardsChoice()
        if not numBoards.isdigit():
          dialog.notifyStatus("Number of boards must be a number")
          return
        elif not (0 < int(numBoards) < 1000):
          dialog.notifyStatus("Number of boards must be 1-999")
          return
        
        # set the button text to the stop message
        dialog.setGenerateButtonText(stopGenerationMsg)
        
        # generate the boards
        dialog.setStatus("Generating...")
        dialog.setProgress(0)
        
        # thread to update the progress bar
        def monitorStatus():
          while True:
            
            # get and display the progress
            status = gui.controller.getBoardGenerationStatus()
            progress = gui.controller.getBoardGenerationProgress()
            dialog.funcCall.emit(lambda: dialog.setStatus(status))
            dialog.funcCall.emit(lambda: dialog.setProgress(progress * 100))
            
            dialog.funcCall.emit(lambda: dialog.updateDatabaseCount())
            
            # exit if the generation thread has exited
            if not generatorThread.isAlive():
              # revert the button text to the start message
              dialog.funcCall.emit(lambda: dialog.setGenerateButtonText(startGenerationMsg))
              dialog.funcCall.emit(lambda: dialog.updateDatabaseCount())
              
              # update the database board count and notify the main window that
              # we added new boards
              # dialog.funcCall.emit(lambda: dialog.updateDatabaseCount())
              gui.funcCall.emit(lambda: gui.addedNewBoards())
              
              dialog.funcCall.emit(lambda: dialog.setStatus(gui.controller.getBoardGenerationStatus()))
              
              return
            
            time.sleep(0.5)
        
        # start board generation
        generatorThread = threading.Thread(target=gui.controller.generateBoards,
                                           args=(int(numBoards), int(rows), int(columns)))
        generatorThread.start()
        
        # create the monitoring thread
        monitorThread = threading.Thread(target=monitorStatus)
        monitorThread.start()
    
    # call gui function from other threads
    funcCall = QtCore.pyqtSignal(object)
    
    @QtCore.pyqtSlot(object)
    def remoteCall(self, func):
      """ Allows us to call GUI functions from other threads """
      func()
    
    def __init__(self, parent, gui):
      super().__init__(parent)
      
      # update dialog from a different thread
      self.funcCall.connect(self.remoteCall)
      
      # reference to our parent gui
      self.gui = gui
      
      self.setWindowTitle("Board Generator")
      self.resize(1, 1)
      
      self.setModal(True)
      self.setObjectName("Dialog")
      
      #########################################################################
      # from GUI designer:
      #########################################################################
      
      verticalLayout_3 = QtWidgets.QVBoxLayout(self)
      verticalLayout_2 = QtWidgets.QVBoxLayout()
      horizontalWidget_2 = QtWidgets.QWidget(self)
      horizontalLayout_3 = QtWidgets.QHBoxLayout(horizontalWidget_2)
      horizontalWidget = QtWidgets.QWidget(horizontalWidget_2)
      horizontalLayout = QtWidgets.QHBoxLayout(horizontalWidget)
      spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
      horizontalLayout.addItem(spacerItem)
      
      self.rowsLabel = QtWidgets.QLineEdit(horizontalWidget)
      self.rowsLabel.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
      horizontalLayout.addWidget(self.rowsLabel)
      
      label = QtWidgets.QLabel(horizontalWidget)
      
      horizontalLayout.addWidget(label)
      
      self.columnsLabel = QtWidgets.QLineEdit(horizontalWidget)
      self.columnsLabel.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
      horizontalLayout.addWidget(self.columnsLabel)
      
      spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
      horizontalLayout.addItem(spacerItem1)
      verticalWidget = QtWidgets.QWidget(horizontalWidget)
      
      verticalLayout = QtWidgets.QVBoxLayout(verticalWidget)
      spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
      verticalLayout.addItem(spacerItem2)
      
      label_4 = QtWidgets.QLabel(verticalWidget)
      label_4.setAlignment(QtCore.Qt.AlignCenter)
      verticalLayout.addWidget(label_4)
      
      horizontalLayout_2 = QtWidgets.QHBoxLayout()
      spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
      horizontalLayout_2.addItem(spacerItem3)
      
      self.inDatabaseLabel = QtWidgets.QLabel(verticalWidget)
      self.inDatabaseLabel.setStyleSheet(
        "background: white; border-style: outset; border-width: 3px; border-color: black;")
      self.inDatabaseLabel.setAlignment(QtCore.Qt.AlignCenter)
      horizontalLayout_2.addWidget(self.inDatabaseLabel)
      
      spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
      horizontalLayout_2.addItem(spacerItem4)
      verticalLayout.addLayout(horizontalLayout_2)
      horizontalLayout.addWidget(verticalWidget)
      spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
      horizontalLayout.addItem(spacerItem5)
      horizontalLayout.setStretch(0, 1000)
      horizontalLayout.setStretch(1, 1)
      horizontalLayout.setStretch(2, 1)
      horizontalLayout.setStretch(3, 1)
      horizontalLayout.setStretch(6, 1000)
      horizontalLayout_3.addWidget(horizontalWidget)
      verticalLayout_2.addWidget(horizontalWidget_2)
      spacerItem6 = QtWidgets.QSpacerItem(20, 800, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum)
      verticalLayout_2.addItem(spacerItem6)
      line_2 = QtWidgets.QFrame(self)
      line_2.setFrameShape(QtWidgets.QFrame.HLine)
      line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
      verticalLayout_2.addWidget(line_2)
      
      self.progressBar = QtWidgets.QProgressBar(self)
      self.progressBar.setProperty("value", 0)
      verticalLayout_2.addWidget(self.progressBar)
      
      self.statusLabel = QtWidgets.QLabel(self)
      verticalLayout_2.addWidget(self.statusLabel)
      
      horizontalLayout_4 = QtWidgets.QHBoxLayout()
      spacerItem7 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
      horizontalLayout_4.addItem(spacerItem7)
      horizontalLayout_6 = QtWidgets.QHBoxLayout()
      
      self.toGenerateLabel = QtWidgets.QLineEdit(self)
      self.toGenerateLabel.setAlignment(QtCore.Qt.AlignCenter)
      horizontalLayout_6.addWidget(self.toGenerateLabel)
      
      self.generateButton = QtWidgets.QPushButton(self)
      horizontalLayout_6.addWidget(self.generateButton)
      self.generateButton.clicked.connect(
        lambda: PyQtGUI.BoardGeneratorDialog.UserActions.generateButtonPressed(self, self.gui))
      
      horizontalLayout_4.addLayout(horizontalLayout_6)
      horizontalLayout_4.setStretch(0, 1000)
      horizontalLayout_4.setStretch(1, 1)
      verticalLayout_2.addLayout(horizontalLayout_4)
      line = QtWidgets.QFrame(self)
      line.setFrameShape(QtWidgets.QFrame.HLine)
      line.setFrameShadow(QtWidgets.QFrame.Sunken)
      verticalLayout_2.addWidget(line)
      horizontalLayout_5 = QtWidgets.QHBoxLayout()
      spacerItem8 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
      horizontalLayout_5.addItem(spacerItem8)
      
      self.timeElapsedLabel = QtWidgets.QLabel(self)
      self.timeElapsedLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
      horizontalLayout_5.addWidget(self.timeElapsedLabel)
      
      horizontalLayout_5.setStretch(0, 1000)
      verticalLayout_2.addLayout(horizontalLayout_5)
      verticalLayout_3.addLayout(verticalLayout_2)
      
      label_4.setText("In Database")
      label.setText("X")
      
      #########################################################################
      
      # set row and column labels to the current board dimensions
      self.rowsLabel.setText(str(gui.board.getBoardDimensions()[0]))
      self.columnsLabel.setText(str(gui.board.getBoardDimensions()[1]))
      
      # when the row/column choice is updated, update the "in database" label
      self.rowsLabel.textChanged.connect(self.updateDatabaseCount)
      self.columnsLabel.textChanged.connect(self.updateDatabaseCount)
      
      # default values for labels
      self.inDatabaseLabel.setText(" 0 ")
      self.toGenerateLabel.setText("10")
      self.timeElapsedLabel.setText("")
      self.statusLabel.setText("")
      
      # generate button
      self.generateButton.setText("Generate")
      self.generateButton.setFocus()
      
      # update the "in database" label
      self.updateDatabaseCount()
      
      # keep track of whether we are generating boards now
      self.generatingBoards = False
    
    def updateDatabaseCount(self):
      """ Update the status showing the number of row x colum boards we have in the database """
      
      try:
        
        # get the rows and columns
        rows = int(self.getRowChoice())
        columns = int(self.getColumnChoice())
        
        # find the board info for this board type
        boardsInfo = self.gui.controller.getBoardsInfo()
        if boardsInfo and boardsInfo.get((rows, columns), False):
          self.setInDatabaseStatus(boardsInfo[(rows, columns)]["length"])
        else:
          self.setInDatabaseStatus(0)
      
      except:
        self.setInDatabaseStatus(0)
    
    def setProgress(self, val):
      self.progressBar.setValue(val)
    
    def setStatus(self, text):
      self.statusLabel.setText(text)
    
    def getRowChoice(self):
      return self.rowsLabel.text()
    
    def getColumnChoice(self):
      return self.columnsLabel.text()
    
    def getNumBoardsChoice(self):
      return self.toGenerateLabel.text()
    
    def setInDatabaseStatus(self, value):
      if isinstance(value, int):
        self.inDatabaseLabel.setText(" " + str(value) + " ")
    
    def setGenerateButtonText(self, text):
      self.generateButton.setText(text)
  
  class UserActions(object):
    
    @staticmethod
    def cellClick(gui, cell, rowName, player):
      """ When a user clicks on the cell at <coordinates> """
      logger.debug("cellClick: {}, {}, {}".format(player.getName(), rowName, cell.text()))
      
      # score for the current player
      if player == gui.game.getCurrentPlayer():
        gui.controller.score(rowName)
    
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
        "Dice": gui.showDiceSetupWindow, #showBoardGeneratorWindow
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
        nameCell = self._createLabelCell(player.getName(), align=QtCore.Qt.AlignCenter)
        gridLayout.addWidget(nameCell, 0, iPlayer + 1)
        
        # remember the cell for this player's name
        playerNameCells[player.getName()] = nameCell
      
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
      
      
      
    
    def DEP_delLayout(self, layout=None):
      """ Delete all of the layout elements """
      
      if layout is None:
        layout = self.mainLayout
      
      while layout.count():
        child = layout.takeAt(0)
        widget = child.widget()
        
        if widget:
          layout.removeWidget(widget)
          widget.deleteLater()
        
        else:
          try:
            if child.count():
              self._delLayout(child)
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
      menuLayout = QtWidgets.QVBoxLayout()
      menuLayout.setAlignment(QtCore.Qt.AlignTop)
      
      # menu bar itself
      menubar = QtWidgets.QMenuBar()
      menubar.setNativeMenuBar(False)
      menubar.setStyleSheet("padding: 1px;")
      menuLayout.addWidget(menubar)
      
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
      for iDice in range(numDice):
        singleDice = self._createSingleDice(iDice)
        displayDice.append(singleDice)
        diceBox.addLayout(singleDice)

      

      
      
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
      
      return rollButton, displayDice, rollBox
    
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
    # define stylesheets for text and the game cells
    ###########################################################################
    
    # text styles
    #  -initial are underlined, others are normal
    self.TEXT_STYLE_NORMAL = ""
    self.TEXT_STYLE_INITIAL = " text-decoration: underline; "
    
    # player name styles
    defaultNameStyle = "border-style: outset; border-width: 1px; border-color: black; "
    self.PLAYER_NAME_INACTIVE = defaultNameStyle + " color: black; background: white; "
    self.PLAYER_NAME_ACTIVE   = defaultNameStyle + " color: black; background: aquamarine; "
    
    # score styles
    defaultScoreStyle = "border-style: outset; border-width: 1px; border-color: black; "
    self.SCORE_STYLE_NORMAL        = defaultScoreStyle + " background: white; color: black; "
    self.SCORE_STYLE_POSSIBLE      = defaultScoreStyle + " background: white; color: dodgerblue; "
    self.SCORE_STYLE_POSSIBLE_ZERO = defaultScoreStyle + " background: white; color: crimson; "
    self.SCORE_STYLE_TOTAL         = defaultScoreStyle + " background: linen; color: black; border-width: 1px;"
    
    # dice
    self.DICE_BLANK = "border-style: outset; color: white; background: crimson; "
    
    # roll button
    self.ROLL_BUTTON_STYLE = "border-style: solid; border-width: 2px; border-color: black;" + \
                             "color: black; background: lightsteelblue; "
    
    # main window
    self.MAIN_WINDOW_STYLE = " background: white; "
    
    # hold label
    defaultDicedStyle = "border-style: outset; "
    #self.DICE_IMAGE_FREE = defaultDicedStyle + " background: white; "
    self.DICE_LABEL_FREE = defaultDicedStyle + " background: white; "
    #self.DICE_IMAGE_HELD = defaultDicedStyle + " background: lightskyblue; "
    self.DICE_LABEL_HELD = defaultDicedStyle + " background: lightskyblue; "
    
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
    
    ###########################################################################
    # define keys
    ###########################################################################
    
    # backspace and delete
    self.DELETE_KEY_LIST = [16777219, 16777223]
    
    # 1 to 9
    self.NUMBER_KEY_LIST = list(range(49, 58))
    
    # 87: w
    # 65: a
    # 83: s
    # 68: d
    
    ###########################################################################
    # create the GUI
    ###########################################################################
    
    # application object
    self.app = QtWidgets.QApplication(sys.argv)
    
    self.mainWindow = QtWidgets.QWidget()
    self.mainWindow.setWindowTitle("Yahtzee")
    
    # register function for keyboard presses
    self.mainWindow.keyPressEvent = lambda event: PyQtGUI.UserActions.keyPressed(self, event)
    
    #self.appCreator = PyQtGUI.LayoutCreator(self, self.mainWindow)
    #self.appCreator.setlayout(self.game)
    
    # GUI elements we want to be able to update
    self.rollButton      = None
    self.displayDice     = None
    self.playerNameCells = None
    self.scoreCells      = None
    self.statusText      = None
    
    self.createLayout()
    
    # get links into elements we want to be able to change
    #self._getGameGrid = self.appCreator.getGameGrid
    #self._setStatusText = self.appCreator.setStatusText

    # self.notifyStatus = self.appCreator.setStatusText
    
    ###########################################################################
    
    # set and display the board
    #self.displayNewBoard(board)
  
  
  def createLayout(self):
    """ Create and layout all of the window elements """
    logger.debug("Creating layout")
    
    appCreator = PyQtGUI.LayoutCreator(self)

    # use a box layout for the other layouts
    mainLayout = QtWidgets.QVBoxLayout()
    self.mainWindow.setLayout(mainLayout)

    self.mainWindow.setStyleSheet(self.MAIN_WINDOW_STYLE)


    
    # remove any previous gui elements
    #appCreator._delLayout()
  
    # menu bar
    logger.debug("Creating layout: menu bar")
    menuLayout = appCreator.createMenuBar()
    mainLayout.insertLayout(0, menuLayout, 1)
  
    # scorecard
    logger.debug("Creating layout: scorecard")
    self.playerNameCells, self.scoreCells, scorecardLayout = appCreator.createScorecard(self.game.getAllPlayers())
    mainLayout.insertLayout(1, scorecardLayout, 1)
  
    # probability grid
    logger.debug("Creating layout: probability grid")
  
    # roll box
    logger.debug("Creating layout: roll box")
    self.rollButton, self.displayDice, rollBoxLayout = appCreator.createRollBox(self.game.getNumberOfDice())
    mainLayout.insertLayout(2, rollBoxLayout, 1)
  
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
  
  
  def DEP_updatePlayerNameCell(self, cell, isActivePlayer):
    """ Highlight player name """
    if isActivePlayer:
      cell.setStyleSheet(self.PLAYER_NAME_ACTIVE)
    else:
      cell.setStyleSheet(self.PLAYER_NAME_INACTIVE)

    
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
    logger.debug("updateScorecard: {}".format(playerList))
  
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
    # player name highlighting
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
    
  
  def gameComplete(self):
    """ Called when game is completed """
    logger.debug("gameComplete")
    
    totalScores = self.game.getTotalScores()
    
    # get and order the scores
    scores = [(name, score) for name,score in totalScores.items()]
    scores.sort(key=lambda x: x[1], reverse=True)
    
    # find the longest player name/score and get its character length
    maxNameLength  = max(map(len, list(totalScores.keys())))
    maxScoreLength = len(str(max(list(totalScores.values()))))
    
    # length of score line
    #  -name + colon + space + score
    lineLength = maxNameLength+2+maxScoreLength

    # assemble the score line for each player
    #  -<name>: <score>
    scoreMsg = ""
    for name, score in scores:
      nameStr  = (name + ":").ljust(maxNameLength+1, " ")
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

    self.notifyStatus(scoreMsg, title="Game Over", font=font)
  

  def confirmAction(self, text):
    """ Ask the user to confirm they want to do <the thing> """
    response = QtWidgets.QMessageBox.question(self.mainWindow, "Yahtzee",
                                              text, QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                              QtWidgets.QMessageBox.No)
    return response == QtWidgets.QMessageBox.Yes
  
  
  def notifyStatus(self, text, title="Yahtzee", font=None):
    """ Status notification; used or ignored, up to the GUI """
    #QtWidgets.QMessageBox.information(self.mainWindow, "Yahtzee",
    #                                  text, QtWidgets.QMessageBox.Ok)
    
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
