#!/usr/bin/env python
# pylint: disable=invalid-name,missing-docstring,unused-import,unused-variable,unused-argument,line-too-long
# pylint: disable=too-many-locals,unnecessary-pass,pointless-string-statement,using-constant-test
# pylint: disable=multiple-statements,logging-fstring-interpolation,multiple-imports,wrong-import-position
# pylint: disable=import-outside-toplevel

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Generic, List, TypeVar

from eventlet.event import Event
import eventlet as hub

from eventlet_promise.utils import LockList
# from .log import CRITICAL, DEBUG, ERROR, INFO, LOG, WARNING, pf

def raise_(reason):
    if isinstance(reason, Exception):
        raise reason
    raise Exception(reason)     # pylint: disable=broad-exception-raised

class Thenable(ABC):
    _counter = 0
    _clsThreads = LockList()

    def __init__(self):
        self.name = __class__._counter
        __class__._counter += 1
        self._state = 'pending'
        self._fate = 'unresolved'
        self._value = None
        self._event = Event()
        self._callbacks = LockList()
        self._threads = LockList[Event]()
        self._observables = LockList()

    def execute(self, executor):
        return executor(self._resolve, self._reject)

    def waitExecute(self, func : Callable[[Any], None], *args):
        def waiter():
            self._event.wait()
            func(*args)
            self._threads.remove(hub.getcurrent())
        thread = hub.spawn(waiter)
        self._threads.append(thread)
        return thread

    def _resolve(self, result, _overrideResolved=False):
        if not self.isPending():
            return
        if not _overrideResolved and self.isResolved():
            self._resolveAttached()
            return
        if result is self:
            self._reject(TypeError(f'{self.__class__.__name__} resolved with itself'))
            return
        if isinstance(result, Thenable):
            self.referenceTo(result)
            return
        self._settle('fulfilled', result)

    def _reject(self, reason, _overrideResolved=False):
        if not self.isPending():
            return
        if not _overrideResolved and self.isResolved():
            self._resolveAttached()
            return
        self._settle('rejected', reason)
        # raise_(reason)            # disable this to prevent unhandled rejections

    def _settle(self, state, value):
        self._state = state
        self._fate = 'resolved'
        self._value = value
        self._event.send()
        self._executeCallbacks()

    def _executeCallbacks(self):
        idx = 0
        while idx < len(self._callbacks):
            if self._callbacks[idx]():
                self._callbacks.pop(idx)
                idx -= 1
            idx += 1

    def _resolveAttached(self):
        if self.isPending() and self.isResolved():
            self._value : Thenable
            if self._value.isPending():
                return
            # wait for the saved promise (the one that self is so attached to) to settle (for someone else?;)
            Thenable.allSettled([self._value])\
                .finally_(lambda x: x[0]['value'] if x[0]['status'] == 'fulfilled' else x[0]['reason'])\
                .then(lambda x: self._resolve(x, True), lambda x: self._reject(x, True))
            hub.sleep(0)

    def addCallback(self, callback : Callable[[], bool]):
        self._callbacks.append(callback)

    def addThread(self, thread : hub.greenthread.GreenThread):
        self._threads.append(thread)

    def removeThread(self, thread : hub.greenthread.GreenThread):
        self._threads.remove(thread)

    def addObservable(self, observable : 'Thenable'):
        self._observables.append(observable)

    def referenceTo(self, thenable : 'Thenable', onFulfilled=None, onRejected=None):
        if self.isResolved():   # called from self._resolve before&for resolving (at end of this fn)
            # print(f'Warning: {self} is already resolved to value={self._value}.\
            #     \n Using above value instead of {thenable}.')
            thenable = self._value
        thenable.addCallback(lambda: thenable.then(
            lambda x: self._resolve(onFulfilled(x), True),
            lambda x: self._reject(onRejected(x), True)
        ))
        self._fate = 'resolved'
        self._value = thenable

    def isResolved(self):
        return self._fate == 'resolved'

    def isFulfilled(self):
        return self._state == 'fulfilled'

    def isRejected(self):
        return self._state == 'rejected'

    def isPending(self):
        return self._state == 'pending'

    def isSettled(self):
        return self._state != 'pending'

    def getValue(self):
        return self._value

    def getState(self):
        return self._state

    @staticmethod
    @abstractmethod
    def resolve(value : Any):
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def reject(reason : Any):
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def all(promises : List):
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def allSettled(promises : List):
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def any(promises : List):
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def race(promises : List):
        raise NotImplementedError()

    @abstractmethod
    def then(self, onFulfilled : Callable[[Any], Any] = None, onRejected : Callable[[Any], Any] = None):
        raise NotImplementedError()

    @abstractmethod
    def catch(self, onRejected : Callable[[Any], Any] = None):
        raise NotImplementedError()

    @abstractmethod
    def finally_(self, onFinally : Callable[[Any], Any] = None):
        raise NotImplementedError()

    # def __str__(self):
    #     return f"<{__class__.__name__}{self.name, self._state, self._value},\n\t{pf(self._callbacks)}>"

    def __repr__(self):
        value = self._value
        fmt = f'<{self.__class__.__name__}' + '({}, {}, {})>'
        def fmt_(value):
            if isinstance(value, Thenable):
                return fmt.format(value.name, value.getState(), fmt_(value.getValue()))
            return value
        return f'<{self.__class__.__name__} {self.name, self._state, self._fate, fmt_(value), len(self._callbacks), len(self._threads)}>'
