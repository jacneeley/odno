'''OdnoException - Custom Exception that inherits from Exception'''
from core.odnologging import odnologger

MODULE_NAME = "odnoexceptions"

class OdnoException(Exception):
    '''Capture Exceptions potentially caused by the user.'''
    def __init__(self, message="error", e:Exception=Exception("Unknown Error")):
        super().__init__(message, e)
        self.message = message
        self._exception = e

        odnologger.log(log_level="ERROR", msg=self.message, e=self._exception, module_name=MODULE_NAME)


    def handle_exception(
        self,
        description:str = "Unknown Error",
        caller:str = "") -> None:
        '''Capture Exception and log it.'''

        if self:
            odnologger.log(log_level="ERROR", msg=self.message, e=self)
            msg = f'{description} occurred in {caller} (Exception: {self._exception})'
            odnologger.log(log_level="ERROR", msg=msg)
        
        else:
            raise NotImplementedError("Failed to implement OdnoException...")


    def __str__(self):
        return f"OdnoException: {self.message} (Caused by {self.__cause__})"

    def __repr__(self):
        return super().__str__()
