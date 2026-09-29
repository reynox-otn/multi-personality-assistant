import logging

from gui import run_app, setup_logging

logger = logging.getLogger(__name__)


setup_logging()
logger.info("Application started.")


if __name__ == "__main__":
    run_app()
