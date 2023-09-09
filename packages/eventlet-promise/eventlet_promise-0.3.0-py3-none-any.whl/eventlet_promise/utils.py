#!/usr/bin/env python
# pylint: disable=invalid-name,missing-docstring,unused-import,unused-variable,unused-argument,line-too-long
# pylint: disable=too-many-locals,unnecessary-pass,pointless-string-statement,using-constant-test
# pylint: disable=multiple-statements,logging-fstring-interpolation,multiple-imports,wrong-import-position
# pylint: disable=import-outside-toplevel

from typing import Generic, TypeVar

import eventlet as hub

_T = TypeVar('_T')

class LockList(list, Generic[_T]):
    class Full(Exception):
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__lock = hub.BoundedSemaphore(1)
        self._maxsize = 0

    def maxSize(self):
        return self._maxsize

    def setMaxSize(self, size):
        self._maxsize = size

    def append(self, obj):
        with self.__lock:
            super().append(obj)

    def put(self, obj):
        if self._maxsize > 0 and len(self) >= self._maxsize:
            raise LockList.Full('List is full')
        self.append(obj)
        return len(self) - 1

    def pop(self, index) -> _T:
        with self.__lock:
            return super().pop(index)

    def __len__(self) -> int:
        with self.__lock:
            return super().__len__()
