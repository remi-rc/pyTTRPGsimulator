import logging


# Setup logging
def setup_logging(level=logging.INFO):
    logger = logging.getLogger(__name__)
    logger.setLevel(level)

    if (
        not logger.hasHandlers()
    ):  # Prevent adding multiple handlers in interactive environments
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(level)

        # Formatter
        # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        formatter = logging.Formatter("%(message)s")
        ch.setFormatter(formatter)

        # Adding handler to logger
        logger.addHandler(ch)

    return logger


from .damages import *
from .modifiers import *
from .items import *
from .actors import *
from .conditions import *
from .weapon_styles import *
from .actions import *
from .combat import *
from .spells import *
from .strategy import *
