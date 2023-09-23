import sys

from loguru import logger

logger.remove()
if 'win' in sys.platform:
    logger.add(sys.stdout, level='DEBUG')
else:
    logger.add(sys.stdout, format="{message}", level='INFO')

if __name__ == '__main__':
    print(sys.platform)
