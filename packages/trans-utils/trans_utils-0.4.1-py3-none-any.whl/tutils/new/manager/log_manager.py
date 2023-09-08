from .loggers import MultiLogger


class DummyLogger:    
    def __init__(self, *args, **kwargs) -> None:
        return
    
    def add_scalars(self, *args, **kwargs):
        return

    def __call__(self, *args, **kwargs):
        return 

    def _set_FileHandler(logger, *args, **kwargs):
        return

    def set_logger_dir(self, *args, **kwargs):
        return


class LoggerManager:
    
    def get_logger(self, config, is_master=True):
        config_base = config['base']
        config_logger = config['logger']
        if is_master:
            logger = MultiLogger(logdir=config_base['runs_dir'], 
                                record_mode=config_logger.get('record_mode', None), 
                                tag=config_base['tag'], 
                                extag=config_base.get('experiment', None),
                                action=config_logger.get('action', 'k'),) # backup config.yaml
            return logger
        else:
            return DummyLogger