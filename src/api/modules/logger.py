import time
import uuid

class Logger:    
    def __init__(self) -> None:
        self.uuid = uuid.uuid4()

    def print(self, level, message: str) -> None:
        # Print the message
        # Format
        # 2024-04-01 12:00:00 - INFO - Message
        print(f'{time.strftime("%Y-%m-%d %H:%M:%S%z")} - {level.upper()} - {self.uuid} - {message}')
    
    def info(self, message: str) -> None:
        self.print('info', message)
    
    def debug(self, message: str) -> None:
        self.print('debug', message)
    
    def error(self, message: str) -> None:
        self.print('error', message)
    
    def warn(self, message: str) -> None:
        self.print('warn', message)