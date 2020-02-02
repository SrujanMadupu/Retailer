import logging

log_bolo = logging.getLogger(__name__)

f_handler = logging.FileHandler('bolo.log')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

f_handler.setLevel(logging.DEBUG)
f_handler.setFormatter(f_format)

log_bolo.addHandler(f_handler)
