__author__ = 'Bobby'
import logging


class Logger():
    def __init__(self):
        self._loggers = {}

    def gimme_logger(self, name):
        """Create and return a logger that logs to both console and
        a
        TODO: AMQ route.
        :returns: an initialised :class:`~logging.Logger`
        """

        if name in self._loggers:
            return self._loggers[name]

        # Initialise new logger and optionally handlers
        logger = logging.getLogger(name)

        if not len(logger.handlers):  # Only add one set of handlers

            # Console logger with formatter
            console = logging.StreamHandler()
            fmt = logging.Formatter(
                    '%(asctime)s pid:%(process)d %(threadName)s:%(filename)s:%(lineno)s'
                    ' %(levelname)-8s %(message)s',
                    datefmt='%H:%M:%S')
            console.setFormatter(fmt)

            # Add handlers
            logger.addHandler(console)

        # Only logg INFO and above
        logger.setLevel(logging.INFO)
        self._loggers[name] = logger

        return logger
