import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s]: %(message)s'
)


logger = logging.getLogger(name='BookShop')



file_handler = logging.FileHandler('bookshop.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - [%(levelname)s]: %(message)s'))
logger.addHandler(file_handler)