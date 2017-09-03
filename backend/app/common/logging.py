# -*- coding: utf-8 -*-
"""
Logger and LoggerMixin should be the only access to the logging system for
service code.

These classes do several things required by Analytics ELK stack:
    * provide the right flavor of ISO8601 timestamp
    * provide source coordinates: app name, version, hostname
    * remap default log record keys to match existing platform logging conventions
    * censors passwords
    * ensures well-formed json: k-v pairs, newlines escaped, etc.

Note: malformed log records will be dropped during ingestion

The Logger class provides the same interface as the stdlib logging package.
The LoggerMixin class exposes this interface with '_' prefixes to indicate
a protected member.

You can run the logging package in 'local' mode that prints human readable,
colored logs, and 'pd' mode that prints json lines for forwarding to ELK.
To run in local dev mode::

    LOG_MODE=LOCAL ./run_api

FORMATTING:
    Your log message should be the first argument using "".format()::

        self._info('Health server listening at: {}'.format(self._server.url))

    If you use the old method of formatting log messages::

        self._info('Health server listening at: %s', self._server.url)

    the additional parameters will show under key positional_args instead of being
    inserted into the log message. Sometimes these args are just dropped - depending
    on configuration.

    You can add key-value pairs to a log record::

        self._info("Stopping health server...", foo="bar", baz="wombat")

    For exceptions, you can get the exception name with::

        type(exc).__name__

    If you provide the exception as an additional k-v pair named exc_info, a traceback
    will be added to the log record.

    Putting this all together, you can show the exception type, msg, and traceback
    with something like::

        self._error("During shutdown, worker raised {}: {}".format(type(exc).__name__, exc),
                    exc_info=exc)

NOTES:
    * When testing new log entries, ensure that you view log output with and
      without LOG_MODE=LOCAL - they are not perfectly aligned - one may
      cause an error where the other does not.
"""
import datetime
import logging
import os
import platform
import sys
import threading

import structlog

from .build_info import BuildInfo

class LogEntryProcessor:
    """
    Provide log entry processors as well as cached values that are expensive
    to create and thread local storage for request level variables.
    """
    # TODO: need some way to get a pod/node identifier instead of host - or perhaps that will work
    _HOST = platform.node().split('.')[0]
    _BI = BuildInfo()
    _TLS = threading.local()

    @staticmethod
    def get_request_id() -> str:
        if hasattr(LogEntryProcessor._TLS, "request_id"):
            return LogEntryProcessor._TLS.request_id
        return None

    @staticmethod
    def set_request_id(request_id: str) -> None:
        LogEntryProcessor._TLS.request_id = request_id

    @staticmethod
    def add_app_info(_, __, event_dict: dict) -> dict:
        """
        Add application level keys to the event dict
        """
        event_dict['logGitHubRepoName'] = LogEntryProcessor._BI.repo_name
        event_dict['logServiceType'] = LogEntryProcessor._BI.service_type
        event_dict['logServiceName'] = LogEntryProcessor._BI.service_name
        event_dict['logServiceVersion'] = LogEntryProcessor._BI.version
        event_dict['logServiceInstance'] = LogEntryProcessor._HOST
        event_dict['logThreadId'] = threading.current_thread().getName()
        if LogEntryProcessor.get_request_id():
            # We are also used by the gunicorn logger so this may not be set
            event_dict['logRequestId'] = LogEntryProcessor.get_request_id()
        return event_dict

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def censor_password(_, __, event_dict: dict) -> dict:
        """
        Hide any passwords that appear in log entries
        """
        if event_dict.get('password'):
            event_dict['password'] = '*CENSORED*'
        return event_dict

    @staticmethod
    def cleanup_keynames(_, __, event_dict: dict) -> dict:
        """
        Final processing to ensure log record key names meet Analytics requirements
        """
        event_dict['logMessage'] = event_dict['event']
        del event_dict['event']
        return event_dict


def initialize_logging() -> None:
    """
    Initialize our logging system:
    * the stdlib logging package for proper structlog use
    * structlog processor chain, etc.

    This should be called once for each application

    NOTES:
    * To enable human readable, colored, positional logging, set LOG_MODE=LOCAL
      Note that this hides many of the boilerplate log entry elements that is
      clutter for local development.
    """
    debug = os.environ.get('DEBUG', 'false') != 'false'
    logging.basicConfig(level='DEBUG' if debug else 'INFO',
                        stream=sys.stdout,
                        format="%(message)s")

    if os.getenv('LOG_MODE', 'JSON') == 'LOCAL':
        chain = [
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S.%f"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer()
        ]
    else:
        chain = [
            LogEntryProcessor.add_app_info,
            LogEntryProcessor.add_logger_name,
            LogEntryProcessor.add_timestamp,
            LogEntryProcessor.censor_password,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            LogEntryProcessor.cleanup_keynames,
            structlog.processors.JSONRenderer()
        ]

    structlog.configure_once(
        processors=chain,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


class LoggerMixin:
    """
    A structured logger that is mixed in to each class

    The mixin methods follow structlog method signatures

    To record an exception in the log: exception type, message, and traceback::

        self._error("During shutdown, worker raised {} exception: {}".format(
                    type(exc).__name__, exc), exc_info=exc)
    """
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

    Add the following to gunicorn start command to use this class::

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
