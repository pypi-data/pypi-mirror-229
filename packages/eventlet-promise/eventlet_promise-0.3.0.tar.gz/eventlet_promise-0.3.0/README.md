# Eventlet Promise
This package implements a Javascript-like Promise to use for eventlet threads.

```python
from typing import Callable

import eventlet as hub
from eventlet_promise.promise import Promise

def executor_(resolveFunc : Callable[[Any], None], rejectFunc : Callable[[Any], None]):
        t1, t2 = 5, 6
        # print(t1 := 10 * random())
        hub.spawn_after(t1, lambda: print('\tResolving') or resolveFunc(t1))
        hub.spawn_after(t2, lambda: print('\tRejecting') or rejectFunc(TimeoutError("Timed out")))

# promise = Promise(None)
promise = Promise(executor_)
new_promise = promise.then()
attached = Promise.resolve(new_promise).then(lambda x: x + 1).then(lambda x: x + 1)
p1 = Promise.resolve(1).then(2).then()
p2 = Promise.reject(1).then(2, 2).then().then()
p3 = p1.then()
p_all = Promise.all([p1, p3, new_promise, promise])
p_settled = Promise.allSettled([p1, p2, p3, new_promise, promise])
p_any = Promise.any([p2, promise.then(), new_promise, promise])
p_race = Promise.race([new_promise.then(), new_promise.then()])

while True:
    print(promise)
    print(new_promise)
    print(attached)
    print(p1)
    print(p2)
    print(p3)
    print('all', p_all)
    print('allSettled', p_settled)
    print('any', p_any)
    print('race', p_race)

    hub.sleep(0)	# to allow other eventlet coroutines to work.
    hub.sleep(2)	# so that you don't see all scroll by.
```