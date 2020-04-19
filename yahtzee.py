import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

from yahtzee.controller import Controller

# test imports
try:
  import yaml
  import numpy
  import PyQt5
  import scipy
except ImportError as err:
  print("ERROR: Importing failed. Run 'pip3 install -r requirements.txt' to install requirements")
  raise err

app = Controller("config.yaml")
app.run()