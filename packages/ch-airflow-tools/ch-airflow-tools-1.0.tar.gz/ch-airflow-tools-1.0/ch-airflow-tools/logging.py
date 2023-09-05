import logging

class AirflowLoggerHandler(logging.FileHandler):
    def emit(self, record):
        try:
            new_record = record
            super(AirflowLoggerHandler, self).emit(record)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)

# Example usage
if __name__ == "__main__":
    # Set up the logger
    airflow_logger_handler = AirflowLoggerHandler("log.txt")
    airflow_logger_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    airflow_logger_handler.setFormatter(formatter)

    # Add the handler to the root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(airflow_logger_handler)

    # Log some messages
    logging.debug("This is a debug message")
    logging.info("This is an info message")
    logging.warning("This is a warning message")
    logging.error("This is an error message")
    logging.critical("This is a critical message")
