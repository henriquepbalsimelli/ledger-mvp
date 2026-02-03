# app/core/logger.py
import logging

class ContextLogger(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        extra = self.extra.copy()
        kwargs["extra"] = {**kwargs.get("extra", {}), **extra}
        return msg, kwargs