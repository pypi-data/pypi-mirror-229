import sys
import logging

from im_swagger_spy.base import SwaggerBaseSpy


logging.basicConfig(
    level=logging.INFO,
    format=' '.join([
        '[%(asctime)s]',
        '[%(levelname)s]',
        '[%(name)s]',
        '%(message)s',
        '(%(filename)s:%(lineno)s)'
    ])
)

logger = logging.getLogger(__name__)

if sys.argv[1] == 'build':
    cli = SwaggerBaseSpy.build_report()
else:
    cli = lambda: logger.warning(f'Unknown command: {sys.argv}')
