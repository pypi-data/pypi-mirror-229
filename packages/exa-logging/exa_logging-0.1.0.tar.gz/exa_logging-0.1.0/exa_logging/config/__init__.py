class Config:
    LOG_CONFIG = { 
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': { 
            'standard': { 
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                "datefmt": "%Y-%m-%d %H:%M:%s"
            },
            'json': {
                'class': 'exa_logging._JsonFormatter'
            }
        },
        'handlers': { 
            'default': { 
                'formatter': 'json',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': { 
            '': { 
                'handlers': ['default'],
                'level': 'INFO',
                'propagate': False
            },
        } 
    }
