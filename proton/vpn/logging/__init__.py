"""
Proton VPN Logging API.
"""
import datetime
import logging
import os
from logging.handlers import RotatingFileHandler
from proton.utils.environment import VPNExecutionEnvironment


def _format_log_attributes(category, subcategory, event, optional, msg):
    """Format the log message as per Proton VPN guidelines.

        param category: Category of a log, uppercase.
        :type category: string
        param subcategory: Subcategory of a log, uppercase (optional).
        :type subcategory: string
        param event: Event of a log, uppercase.
        :type event: string
        param optional: Additional contextual data (optional).
        :type optional: string
        param msg: The message, should contain all necessary details that
            help better understand the reason behind the message.
        :type msg: string
    """
    _category = f"{category}" if category else ""
    _subcategory = f".{subcategory}" if subcategory else ""
    _event = f":{event}" if event else ""
    _optional = f" | {optional}" if optional else ""

    _msg = ""
    if msg:
        _msg = f" | {msg}" if event else f"{msg}"

    return f"{_category.upper()}{_subcategory.upper()}{_event.upper()}{_msg}{_optional}"


class ProtonAdapter(logging.LoggerAdapter):
    """Adapter to add the allowed Proton attributes"""
    ALLOWED_PROTON_ATTRS = ["category", "subcategory", "event", "optional"]

    def process(self, msg, kwargs):
        # Obtain all Proton logging attributes from kwargs.
        # Note that they should be removed from the kwargs dict as well
        # before delegating to logging.Logger. Otherwise, logging.Logger
        # would raise an error due to unrecognized kwargs.
        category = kwargs.pop("category", None)
        subcategory = kwargs.pop("subcategory", None)
        event = kwargs.pop("event", None)
        optional = kwargs.pop("optional", None)

        return _format_log_attributes(category, subcategory, event, optional, msg), kwargs


def getLogger(name):  # noqa # pylint: disable=C0103
    """
    Returns the logger with the specified name, wrapped in a
    logging.LoggerAdapter which adds the Proton attributes to the log message.

    The allowed proton attributes are: category, subcategory, event and optional.

    Usage:
    .. highlight:: python
    .. code-block:: python

        import proton.vpn.core_api.vpn_logging as logging

         # 1. config should be called asap, but only once.
        logging.config("my_log_file")

        # 2. Get a logger per module.
        logger = logging.getLogger(__name__)

        # 3. Use any of the logger methods (debug, warning, info, error, exception,..)
        # passing the allowed Proton attributes (or not).
        logger.info(
            "my message",
            category="my_category",
            subcategory="my_subcategory",
            event="my_event",
            optional="optional stuff"
        )

    The resulting log message should look like this:

    2022-09-20T07:59:27.393743 | INFO | MY_CATEGORY.MY_SUBCATEGORY:MY_EVENT
    | my message | optional stuff
    """
    return ProtonAdapter(logging.getLogger(name), extra={})


def config(filename, logdirpath=None):
    """Configure root logger.

        param filename: Log filename without extension.
        :type filename: string
        param logdirpath: Path to log file (optional).
        :type logdirpath: string
    """
    logger = logging.getLogger()
    logging_level = logging.INFO

    if filename is None:
        raise ValueError("Filename must be set")

    filename = filename + ".log"

    logdirpath = logdirpath or VPNExecutionEnvironment().path_logs
    log_filepath = os.path.join(logdirpath, filename)

    _formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(message)s",
    )
    _formatter.formatTime = (
        lambda record, datefmt=None: datetime.datetime.utcnow().isoformat()
    )

    # Starts a new file at 3MB size limit
    _handler_file = RotatingFileHandler(
        log_filepath, maxBytes=3145728, backupCount=3
    )
    _handler_file.setFormatter(_formatter)

    # Handler to log to console
    _handler_console = logging.StreamHandler()
    _handler_console.setFormatter(_formatter)

    # Only log debug when using PROTON_VPN_DEBUG=true
    if os.environ.get("PROTON_VPN_DEBUG", "false").lower() == "true":
        logging_level = logging.DEBUG

    # Only log to terminal when using PROTON_VPN_LIVE=true
    if not _handler_console:
        logger.warning("Console logger is not set.")

    if os.environ.get("PROTON_VPN_LOG_TERMINAL", "false").lower() == "true":
        logger.addHandler(_handler_console)

    logger.setLevel(logging_level)
    if _handler_file:
        logger.addHandler(_handler_file)


__all__ = ["getLogger", "config"]
