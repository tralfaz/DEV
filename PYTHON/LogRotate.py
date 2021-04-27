import logging
import logging.handlers


# create logger
logger = logging.getLogger('simple_example')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

rfh = logging.handlers.RotatingFileHandler('rotated.log', maxBytes=100,
                                           backupCount=5)
rfh.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)
rfh.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)
logger.addHandler(rfh)

# 'application' code
for grp in xrange(10):
  logger.debug('debug message %s' % grp)
  logger.info('info message %s' % grp)
  logger.warn('warn message %s' % grp)
  logger.error('error message %s' % grp)
  logger.critical('critical message %s' % grp)

try:
  raise Exception('TEST ERROR')
except Exception as err:
  logger.exception('exception log message')
