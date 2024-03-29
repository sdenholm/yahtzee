import logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

from controller import Controller


if __name__ == "__main__":
  
  # test imports
  try:
    import yaml
    import numpy
    import PyQt5
    import pandas
  except ImportError as err:
    print("ERROR: Importing failed. Run 'pip3 install -r requirements.txt' to install requirements")
    raise err
  
  app = Controller("config.yaml")
  app.run()