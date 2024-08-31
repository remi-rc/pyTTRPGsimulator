import logging


# Setup logging
def setup_logging(level=logging.INFO, log_filename="game_logs.log"):
    logger = logging.getLogger(__name__)
    logger.setLevel(level)

    if (
        not logger.hasHandlers()
    ):  # Prevent adding multiple handlers in interactive environments
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(level)

        # File handler
        fh = logging.FileHandler(log_filename)
        fh.setLevel(level)

        # Formatter
        formatter = logging.Formatter("%(message)s")
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)

        # Adding handlers to logger
        logger.addHandler(ch)
        logger.addHandler(fh)

    logger.info(
        f"#############################################################################################"
    )
    logger.info(
        f"Welcome to pyTTRPG simulator, a code created by Remi Necnor for the best TTRPG in the world !"
    )
    logger.info(f"Stay tuned on github at https://github.com/remi-rc/pyTTRPGsimulator")
    logger.info(f"Contact: remi.necnor@gmail.com")
    logger.info(f"Discord: remi_rc")
    logger.info(f"Have fun !")
    logger.info(
        f"#############################################################################################"
    )

    return logger


from .entity import *
from .attributes import *
from .damages import *
from .modifiers import *
from .items import *
from .actors import *
from .traits import *
from .weapon_styles import *
from .actions import *
from .combat import *
from .spells import *
from .combat_strategies import *
from .targeting_strategies import *
