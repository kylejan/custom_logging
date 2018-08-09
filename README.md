# Customize Python Logging Handlers

### KylejanTimedRotatingFileHandler

```python
# Rotating File Every 5 Seconds

import logzero
from logzero import logger
from custom_logging.handlers import KylejanTimedRotatingFileHandler

log_handler = KylejanTimedRotatingFileHandler('./logs/', 'writer.log', 's', 5)
logger.addHandler(log_handler)
logzero.formatter(logzero.LogFormatter(fmt='[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d] %(message)s'), True)

# Log File Rotate Result
# logs/2018-08-09_12_58_48--writer.log
# logs/2018-08-09_12_58_53--writer.log
```
