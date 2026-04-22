'''Module for configuring logging.'''
import logging
import logging.config

def create_logger(module_name:str) -> logging:
    '''
        Read loggerconfig file and then return logging object using module_name provided by client.
        
        parameters:
            * module_name -> str name of the module calling the function

        returns:
            * logging object constructed using the config file and module_name
    '''
    logging.config.fileConfig('logging.conf')
    return logging.getLogger(module_name)
