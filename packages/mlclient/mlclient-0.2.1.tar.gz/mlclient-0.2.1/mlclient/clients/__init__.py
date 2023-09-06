"""The ML Clients package.

This package contains Python API to connect with MarkLogic server using carious clients.
It contains the following modules

    * ml_client
        The ML Client module.
    * logs_client
        The ML Logs Client module.

This package exports the following classes:
    * MLClient
        A low-level class used to send simple HTTP requests to a MarkLogic instance.
    * MLResourceClient
        A MLClient subclass calling ResourceCall implementation classes.
    * MLResourcesClient
        A MLResourceClient subclass supporting REST Resources of the MarkLogic server.
    * MLResponseParser
        A MarkLogic HTTP response parser.
    * LogsClient
        An MLResourceClient calling /manage/v2/logs endpoint.
    * LogType
        An enumeration class representing MarkLogic log types.

Examples
--------
>>> from mlclient.clients import MLResourceClient
"""
from .ml_client import (MLClient, MLResourceClient, MLResourcesClient,
                        MLResponseParser)
from .logs_client import LogsClient, LogType

__all__ = ["LogType", "LogsClient",
           "MLClient", "MLResourceClient", "MLResourcesClient",
           "MLResponseParser"]
