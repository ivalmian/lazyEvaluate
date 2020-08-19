'''
Author: Ilya Valmianski
Email: ivalmian@gmail.com
URL: https://github.com/ivalmian/lazyEvaluate

See LICENSE for license information

## lazyevaluate is a micro library for lazy evaluation

Primary use is via LazyEvaluate which wraps the _LazyEvaluate class. It can be used as a decorator around a function,  
in which case it will replace the return value fo the function with lazyevaluate.Executor object. lazyevaluate.Executor
will only execute the originally called function when the value is attempted to be retrieved. Evaluations of a given Executor
are memoized, only the first one actually uses the function call (however used can make multiple Executors for given function/set of arguments).

Both LazyEvaluate and Executor have additional helper methods to deal with lazy evaluation
'''

from .lazyEvaluate import LazyEvaluate, Executor, States
from .version import __version__