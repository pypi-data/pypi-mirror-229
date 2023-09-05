import datetime, logging
from structlog import wrap_logger
from structlog.processors import JSONRenderer

def wrap_logger_airflow(logger):
    logger = wrap_logger(
        logger,
        processors=[
            add_timestamp,
            JSONRenderer(indent=1, sort_keys=True)
        ]
    )
    return logger

def add_timestamp(_, __, event_dict):
        event_dict['timestamp'] = datetime.datetime.utcnow()
        return event_dict

# Example usage
if __name__ == "__main__":
    # Set up the logger
    airflow_logger = wrap_logger_airflow(logging.getLogger(__name__))

    # Log some messages
    airflow_logger.debug("This is a debug message")
    airflow_logger.info("This is an info message")
    airflow_logger.warning("This is a warning message")
    airflow_logger.error("This is an error message")
    airflow_logger.critical("This is a critical message")
