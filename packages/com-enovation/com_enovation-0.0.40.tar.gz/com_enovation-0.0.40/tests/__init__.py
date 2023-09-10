import logging.config

logging.basicConfig(
    format='%(levelname)s [%(asctime)s]: %(message)s',
    level=logging.WARNING
)

logging.info('com.enovation: tests logging initialized')