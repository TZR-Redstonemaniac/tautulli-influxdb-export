import logging

logging.basicConfig(format='[%(asctime)s] %(levelname)s - %(message)s')


class ExceptionHandler:
    def __init__(self, message, program):
        self.message = message
        self.program = program

    def Debug(self):
        if self.message == "Invalid apikey":
            logging.error(f"{self.program}'s API key is invalid")
        else:
            logging.error(f"{self.message} for {self.program}")


class CustomException(Exception):
    pass
