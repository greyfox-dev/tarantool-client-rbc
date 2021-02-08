# -*- coding: utf-8 -*-
'''
This module provides SelectedConnection class with automatic switch
between tarantool instances and basic Round-Robin strategy
and with selection instances with specific roles.
'''

import logging
from tarantool.mesh_connection import MeshConnection
from tarantool.error import (
    NetworkError,
    DatabaseError,
    ConfigurationError
)

from tarantool.request import (
    RequestEval
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class SelectedConnection(MeshConnection):
    def __init__(self, need_read_only=True, **kwargs):
        self.need_read_only = need_read_only
        super(SelectedConnection, self).__init__(**kwargs)

    @property
    def info(self):
        request = RequestEval(self, 'return box.info', [])
        try:
            resp = self._send_request_wo_reconnect(request)
        except DatabaseError as db_exception:
            msg = 'Got "%s" error, skipped addresses updating' % str(db_exception)
            logger.error(msg)
            return

        if not resp.data or not resp.data[0] or not isinstance(resp.data[0], dict):
            msg = "Got incorrect response instead of URI list, " + \
                  "skipped addresses updating"
            logger.warning(msg)
            return

        return resp.data[0]

    @property
    def is_read_only(self):
        try:
            is_read_only = self.info['ro']
        except KeyError as key_error:
            is_read_only = None
            logger.error('Cant get read only status: {}'.format(key_error))

        return is_read_only

    def connect(self):
        for _ in range(len(self.strategy.addrs)):
            try:
                super(SelectedConnection, self).connect()
                if self.is_read_only is not None and self.is_read_only == self.need_read_only:
                    return

                self.close()
                logger.info('Switch node {}:{} cause need read-only or read-write'.format(self.host, self.port))
            except NetworkError as network_exception:
                logger.warning('Network error while connect: {}'.format(network_exception))

            self._set_next_instance()

        raise ConfigurationError('Cant find appropriate node')

    def _opt_reconnect(self):
        last_error = None
        for _ in range(len(self.strategy.addrs)):
            try:
                super(MeshConnection, self)._opt_reconnect()
                if (last_error is None or
                        self.is_read_only is not None and self.is_read_only == self.need_read_only):
                    return
                else:
                    last_error = ConfigurationError('Cant find appropriate node')

                self.close()
                logger.info('Switch node {}:{} cause need read-only or read-write'.format(self.host, self.port))
            except NetworkError as network_exception:
                last_error = network_exception
                logger.error('Network error while reconnect: {}'.format(network_exception))

            self._set_next_instance()

        if last_error:
            raise last_error

    def _set_next_instance(self):
        addr = self.strategy.getnext()
        self.host = addr["host"]
        self.port = addr["port"]
