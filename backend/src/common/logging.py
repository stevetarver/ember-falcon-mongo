import datetime
import os
import sys
import logging
import platform
import threading
import structlog

from .build_info import BuildInfo

'''
Logger and LoggerMixin should be the only access to the logging system.

OVERVIEW:
These classes do several things required by Analytics ELK stack:
- provide the right flavor of ISO8601 timestamp
- provide source coordinates: app name, version, hostname
- remap default log record keys to match existing platform logging conventions
- censors passwords
- ensures well-formed json: k-v pairs, newlines escaped, etc.

Note: malformed log records will be dropped during ingestion

The Logger class provides the same interface as the stdlib logging package.
The LoggerMixin class exposes this interface with '_' prefixes to indicate
a protected member.

You can run the logging package in 'local' mode that prints human readable,
colored logs, and 'pd' mode that prints json lines for forwarding to ELK.
To run in local dev mode:
    LOG_MODE=LOCAL ./run_api

FORMATTING:
Your log message should be the first argument using "".format()
    self._info('Health server listening at: {}'.format(self._server.url))
If you use the old method of formatting log messages:
    self._info('Health server listening at: %s', self._server.url)
the additional parameters will show under key positional_args instead of being
inserted into the log message. Sometimes these args are just dropped - depending
on configuration.

You can add key-value pairs to a log record:
    self._info("Stopping health server...", foo="bar", baz="wombat")

For exceptions, you can get the exception name with
    type(exc).__name__
If you provide the exception as an additional k-v pair named exc_info, a traceback
will be added to the log record.
Putting this all together, you can show the exception type, msg, and traceback
with something like:
    self._error("During shutdown, worker raised {}: {}".format(type(exc).__name__, exc), exc_info=exc)

NOTES:
    When testing new log entries, ensure that you view log output with and
    without LOG_MODE=LOCAL - they are not perfectly aligned - one may
    cause an error where the other does not.
'''
# Globals cached for efficiency
# TODO: need some way to get a pod/node identifier instead of host - or perhaps that will work
BI = BuildInfo()
HOST = platform.node().split('.')[0]


def initialize_logging() -> None:
    """
    Initialize the stdlib logging package for proper structlog use.
    This should be called once for each application
    :return:
    """
    # Initialize the logging facility for this service
    debug = os.environ.get('DEBUG', 'false') != 'false'
    logging.basicConfig(level='DEBUG' if debug else 'INFO',
                        stream=sys.stdout,
                        format="%(message)s")


def add_app_info(_, __, event_dict: dict) -> dict:
    """
    Add application level keys to the event dict
    """
    event_dict['logServiceType'] = BI.service_type
    event_dict['logServiceName'] = BI.service_name
    event_dict['logServiceVersion'] = BI.version
    event_dict['logServiceInstance'] = HOST
    event_dict['logThreadId'] = threading.current_thread().getName()
    return event_dict


def add_logger_name(logger, _, event_dict: dict) -> dict:
    """
    Add the logger name to the event dict - using loggerName consistent
    with existing platform logging.
    """
    # TODO: is this still needed - why do we need a loggerName if we include class
    record = event_dict.get("_record")
    if record is None:
        event_dict["loggerName"] = logger.name
    else:
        event_dict["loggerName"] = record.name
    return event_dict


def add_timestamp(_, __, event_dict: dict) -> dict:
    """
    Add timestamp to the event dict - using an Analyitics appropriate time stamp

    CLC Analytics requires timestamps to be of form: YYYY-MM-DDTHH:MM:SS.sssZ
    python 3.5 strftime does not have millis; strftime is implemented on by the
    C library on the target OS - trying for something that is portable
    """
    now = datetime.datetime.utcnow()
    millis = '{:3d}'.format(int(now.microsecond / 1000))
    event_dict["timestamp"] = "%s.%sZ" % (now.strftime('%Y-%m-%dT%H:%M:%S'), millis)
    return event_dict


def censor_password(_, __, event_dict: dict) -> dict:
    """
    Hide any passwords that appear in log entries
    """
    pw = event_dict.get('password')
    if pw:
        event_dict['password'] = '*CENSORED*'
    return event_dict


def cleanup_keynames(_, __, event_dict: dict) -> dict:
    """
    Final processing to ensure log record key names meet Analytics requirements
    """
    event_dict['logMessage'] = event_dict['event']
    del event_dict['event']
    return event_dict


# To enable human readable, colored, positional logging, set LOG_MODE=LOCAL
if os.getenv('LOG_MODE', 'JSON') == 'LOCAL':
    structlog.configure_once(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S.%f"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
# Otherwise, use JSON encoding for PD
else:
    structlog.configure_once(
        processors=[
            add_app_info,
            add_logger_name,
            add_timestamp,
            censor_password,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            cleanup_keynames,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


class LoggerMixin:
    """
    A structured logger that is mixed in to each class

    The mixin methods follow structlog method signatures

    To record an exception in the log: exception type, message, and traceback
        self._error("During shutdown, worker raised {} exception: {}".format(type(exc).__name__, exc), exc_info=exc)

    http://www.structlog.org/en/stable/
    """
    # TODO: zipkin / logguid distributed tracing
    #    http://www.structlog.org/en/stable/thread-local.html
    @property
    def _logger(self):
        if not getattr(self, '__logger__', None):
            self.__logger__ = structlog.get_logger(type(self).__name__)
        return self.__logger__

    def _debug(self, msg, *args, **kwargs) -> None:
        self._logger.debug(msg, *args, level="Debug", **kwargs)

    def _error(self, msg, *args, **kwargs) -> None:
        self._logger.error(msg, *args, level="Error", **kwargs)

    def _info(self, msg, *args, **kwargs) -> None:
        self._logger.info(msg, *args, level="Info", **kwargs)

    def _warning(self, msg, *args, **kwargs) -> None:
        self._logger.warning(msg, *args, level="Warn", **kwargs)


class Logger(LoggerMixin):
    """
    An instantiable class allowing non-protected access to the LoggerMixin methods.
    Intended for use with functions (things without classes).
    When using this class, you must supply a logger name; by convention, the dotted
    package path.
    """
    def __init__(self, name):
        """
        :param name: required logger name - use dotted package path
        """
        if name is not None and not getattr(self, '__logger__', None):
            self.__logger__ = structlog.get_logger(name)

    def debug(self, msg, *args, **kwargs) -> None:
        self._logger.debug(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs) -> None:
        self._logger.error(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs) -> None:
        self._logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs) -> None:
        self._logger.warning(msg, *args, **kwargs)


class GunicornLogger(object):
    """
    A stripped down version of
        https://github.com/benoitc/gunicorn/blob/master/gunicorn/glogging.py
    to provide structlog logging in gunicorn

    Add the following to gunicorn start command to use this class
        --logger-class app.common.logging.GunicornLogger
    """
    def __init__(self, cfg):
        initialize_logging()
        self._logger = structlog.get_logger('gunicorn.error')
        self.cfg = cfg

    def critical(self, msg, *args, **kwargs) -> None:
        self._logger.error(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs) -> None:
        self._logger.error(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs) -> None:
        self._logger.warning(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs) -> None:
        self._logger.info(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs) -> None:
        self._logger.debug(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs) -> None:
        self._logger.exception(msg, *args, **kwargs)

    def log(self, lvl, msg, *args, **kwargs) -> None:
        self._logger.log(lvl, msg, *args, **kwargs)

    def access(self, resp, req, environ, request_time) -> None:
        pass # we don't support access logs

    def reopen_files(self) -> None:
        pass # we don't support files

    def close_on_exec(self) -> None:
        pass # we don't support files
