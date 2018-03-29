import logging

friend_logger = logging.getLogger('FRIEND')

formatter = logging.Formatter('[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s')

stream_handler = logging.StreamHandler()
file_handler1 = logging.FileHandler('log/friend.log', 'a', 'utf-8')
# stream_handler.setFormatter(formatter)
file_handler1.setFormatter(formatter)

# friend_logger.addHandler(stream_handler)
friend_logger.addHandler(file_handler1)
friend_logger.setLevel(logging.DEBUG)





