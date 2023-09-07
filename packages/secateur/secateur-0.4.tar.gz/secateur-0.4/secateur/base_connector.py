from sqlalchemy import *
import datetime
import logging

logging.basicConfig(level=logging.INFO, filename="secateur.log", filemode="a")

class BaseConnector:
    """
    Doc-string for BaseConnector class.
    """
    def __init__(
        self,
        url=None,
        engine=None,
        connection=None,
        already_exist=False,
        debug_mode=True,
        verbose=True,
        log=True
    ):
        if already_exist:
            self.engine = engine
            self.connection = connection
        else:
            self.engine = create_engine(url)
            self.connection = self.engine.connect()
        self.debug_mode = debug_mode
        self.verbose = verbose
        self.log = log
        logging.info(f"{str(datetime.datetime.now())} | START")
        if self.debug_mode:
            print("DEBUG MODE IS ACTIVE\n")
            logging.info("DEBUG MODE IS ACTIVE")

    def execute(self, query: str) -> list:
        """
        Doc-string for execute() method.
        """
        self.connection.begin()
        try:
            if not self.debug_mode or query.upper().split()[0] == "SELECT":
                result = self.connection.execute(text(query))
                self.connection.commit()
            if self.verbose:
                print(f"{query} | DONE\n")
            if self.log:
                logging.info(f"{str(datetime.datetime.now())} | {query} | DONE")
            try:
                return result.fetchall()
            except:
                self.connection.commit()
                return "DONE"
        except Exception as Error:
            self.connection.rollback()
            if self.verbose:
                print(f"{query} | FAILED | {Error.args}\n")
            if self.log:
                logging.error(f"{str(datetime.datetime.now())} | {query} | FAILED | {Error.args}")
            return "FAILED"

    def close(self) -> None:
        """
        Doc-string for close() method.
        """
        self.connection.close()
        self.engine.dispose()
        logging.info(f"{str(datetime.datetime.now())} | FINISH\n")