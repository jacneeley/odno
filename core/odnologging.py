'''Module for configuring logging.'''
import logging
import logging.config
import datetime

from src.globalconstants import __debugflg__, __project_root__

def _create_logger(name:str="ODNO", log_level="DEBUG") -> logging:
    '''
        Read loggerconfig file and then return logging object using module_name provided by client.
        
        parameters:
            * module_name -> str name of the module calling the function

        returns:
            * logging object constructed using the config file and module_name
    '''
    if __debugflg__():
        logging.config.fileConfig('logging.conf')
        logger = logging.getLogger(name)
        logger.setLevel(log_level)
        return logger

    if not __debugflg__():
        root = __project_root__()
        logging.basicConfig(filename=fr"{root}/.logs/{datetime.datetime.today().strftime('%m-%d-%Y')}.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)
        logger = logging.getLogger(name)
        return logger

class OneLogger(type):
    '''One instance of a logger for application life-time'''
    def __init__(cls, name, bases, attrs):
        super(OneLogger, cls).__init__(name, bases, attrs)
        cls.singleton_instance = None

    def __call__(cls, *args, **kwargs):
        if not cls.singleton_instance:
            cls.singleton_instance = super(OneLogger, cls).__call__(*args, **kwargs)

        return cls.singleton_instance

class _LogManager(object, metaclass=OneLogger):
    '''
        Create instance of logger.
    '''
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.log_level: str = None
            self.module_name: str = None
            self._initialized: bool = True
            self.logging: logging = _create_logger("ODNOLOGGER", "DEBUG")

    def log(self, log_level="INFO", msg: str="unknown log", e:Exception = None, module_name:str = "odno") -> None:
        '''Log message based on log_level'''
        if not hasattr(self, '_initialized'):
            raise NotImplementedError("Logger was not initialized...")

        self.module_name=module_name
        self.log_level = log_level
        lmsg = f"\n\t{self.module_name} - {self.log_level} - {msg}"

        match self.log_level:
            case "INFO":
                self.logging.info(lmsg)
            case "ERROR":
                self.logging.error(lmsg)
                if e:
                    self.logging.exception("Exception - Cause: (%s)", e)
            case "WARNING":
                self.logging.warning(lmsg)
            case "DEBUG":
                self.logging.debug(lmsg)
            case _:
                raise NotImplementedError("Logger was not initialized correctly as log_level could not be determined...")

odnologger = _LogManager()
