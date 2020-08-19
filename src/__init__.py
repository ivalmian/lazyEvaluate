'''
Author: Ilya Valmianski
Email: ivalmian@gmail.com
URL: https://github.com/ivalmian/lazyEvaluate

See LICENSE for license information

## lazyevaluate is a micro library for lazy evaluation

Primary use is via LazyEvaluate which wraps the _LazyEvaluate class. It can be used as a decorator around a function,  
in which case it will replace the return value of the function with lazy_evaluate.Executor object. lazy_evaluate.Executor
will only execute the originally called function when the value is attempted to be retrieved. Evaluations of a given Executor
are memoized, only the first one actually uses the function call (however one can make multiple Executors for given function/set of arguments).

Executor tracks the state it is using States enum. Possible States are NOT_EVALUATED, EVALUATED, MODIFIED. One can pass a list of hooks
to either LazyEvaluate wrapper or directly to Executor which will be called upon each of the possible actions:

1. None -> NOT_EVALUATED              : on_init_hooks
2. NOT_EVALUATED -> EVALUATED         : on_eval_hooks
3. NOT_EVALUATED -> MODIFIED          : on_modified_no_eval_hooks
4. EVALUTED -> MODIFIED               : on_modified_after_eval_hooks
5. MODIFIED -> MODIFIED               : on_modified_after_mod_hooks
 
For some built-in hooks see .hooks
For examples see https://github.com/ivalmian/lazyEvaluate/blob/master/examples
'''

from .lazy_evaluate import LazyEvaluate, Executor, States
from .version import __version__