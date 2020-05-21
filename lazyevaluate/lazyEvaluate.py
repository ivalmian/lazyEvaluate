'''
Author: Ilya Valmianski
Email: ivalmian@gmail.com
URL: https://github.com/ivalmian/lazyEvaluate

See LICENSE for license information

## lazyEvaluate is a micro library for lazy evaluation

Primary use is via LazyEvaluate which wraps the _LazyEvaluate class. It can be used as a decorator around a function,  
in which case it will replace the return value fo the function with lazyEvaluate.Executor object. lazyEvaluate.Executor
will only execute the originally called function when the value is attempted to be retrieved. Evaluations of a given Executor
are memoized, only the first one actually uses the function call (however used can make multiple Executors for given function/set of arguments).

Both LazyEvaluate and Executor have additional helper methods to deal with lazy evaluation
'''

import functools
from enum import Enum, auto
from typing import Union, Callable



class States(Enum):
    '''
    Enumeration of states of the Executor class

    States
    ---
    NOT_EVALUATED
        Operation hasn't been evaluated OR modified. If Executor is in this state and eval()/value is called
        then the op() will be executed. This will cause a transition to EVALUATED, and the op to be dropped.
        If delete_hook is provided then it will be called and the op uid will be provided

    EVALUATED
        Operation has been evaluated (not modified). Executor will return the result

    MODIFIED
        The value has been modified via assignment, the op is dropped and will not be evaluated
    '''
    NOT_EVALUATED = auto()
    EVALUATED = auto()
    MODIFIED = auto()


class Executor():
    '''
    Lazy executor for a callable operation. Has three possible states [NOT_EVALUTED, EVALUATED, MODIFIED], see lazyEvaluate.States for more details.

    Methods
    ---
    __init__
        Creates Executor object by passing an id and callable operation. Optionally pass eval_hook, which will 
        be called on evaluation (only happens on the first call).

    __repr__
        Creates a string stating the name executor is executing and the interval current state

    eval
        Evaluates the operation if in States.NOT_EVALUATED state and calls the eval_hook() and dropOp(), otherwise returns the value

    dropOp
        Sets self.op=None, idea is to drop reference to the operation (which might have a closure with lots of data)

    value
        Setter and getter. If used to get then run Executor.eval(). If used as setter then set value, change state to MODIFIED, and run dropOp(). Note: eval_hook() is not run.
    '''

    def __init__(self, op: Callable, uid: Union[None, int] = None, eval_hook: Union[None, Callable] = None, name: Union[None, str] = None):
        '''
        Creates the Executor object

        Args
        ---
        op: Callable
            Function (no arguments) to be evaluated lazily (will be evaluated on the first call of Executor.eval() or Executor.value, result cached afterwards). 
            Will not be evaluated at all if prior to first evaluation value is set to something else
        uid: int or None (Optional)
            Id of the object, for external housekeeping only
        eval_hook: Callable or None (Optional)
            To be called on first evaluation (not will not be called at all if Executor.value is set externally)
        name: String or None (Optional)
            If None will be defaulted to op.__name__. Name is used to gerenate Executor.__str__() string
        '''
        if name is None:
            name = op.__name__

        assert isinstance(op, Callable)
        assert uid is None or isinstance(uid, int) 
        assert eval_hook is None or isinstance(eval_hook, Callable)
        assert name is None or isinstance(name, str)

        self.op = op
        self.uid = uid
        self.result = None
        self.eval_hook = eval_hook
        self.state = States.NOT_EVALUATED
        self.name = name
        return

    def __str__(self):
        return f'Executor for {self.name}, current state = {self.state}'

    def eval(self):
        '''
        Evaluates if NOT_EVALUATED state and calls eval_hook and dropOp. Otherwise returns previously computed/set value.
        '''
        if self.state == States.NOT_EVALUATED:
            self.result = self.op()
            self.state = States.EVALUATED
            if isinstance(self.eval_hook, Callable):
                self.eval_hook()
            self.dropOp()
        return self.result

    def dropOp(self):
        self.op = None

    @property
    def value(self):
        '''
        Sets/gets value, if set it will use that value and not evaluate even if not previously evaluated
        '''
        return self.eval()

    @value.setter
    def value(self, v):
        self.result = v
        self.state = States.MODIFIED
        self.dropOp()
        return


def LazyEvaluate(_func: Union[None, Callable] = None,
                 *,
                 del_after_eval: bool = True):
    '''
    Wrapper around lazyEvaluate._LazyEvaluate decorator class 

    Allows passing no argument (in which case defauls are used) or with arguments

    Args
    ---
    del_after_eval: bool
        Whether to delete from list of calls after evaluation. 
        Note that even if not deleted additional calls will not cause new evaluations, the old result will be simply passed.

    '''
    assert _func is None or isinstance(_func, Callable)
    assert isinstance(del_after_eval, bool)

    if _func is None:
        return lambda func: _LazyEvaluate(func, del_after_eval)
    else:
        return _LazyEvaluate(_func, del_after_eval)


class _LazyEvaluate():
    '''
    Provides decorator for making functions evaluate lazily.

    Instead of returning their value instead return id, then 
    allow either executing by id or executing all at once.

    Methods
    ---
    __call__
        Adds function call with argument to _LazyEvaluate.calls dict, return Executor object. Executor object has a unique id and value property.
        If value property is read for the first time then the function is executed, subsequent reads will simply return the original result. 
        If the value property is set, then the function will not be evaluated on subsequent reads (instead it will return the assigned value) 
        Executor will delete a reference to itself from the current list of calls when evaluated if allow_del=True (LazyEvaluate option del_after_eval)
    run(call_id)
        Executes a particular function call (either by id or Executor) and returns its value
    runAll
        Executes all function calls in the dictionary
    delID
        If allow_del is set to True deletes given id (or extracts ID from executor)

    Example:
    ---
    See https://github.com/ivalmian/lazyEvaluate/blob/master/example_script.py

    '''

    def __init__(self, func: Callable, allow_del: bool = True):
        '''
        Creates a wrapped for func. Sets allow_del flag to enable deletion of call for calls dict when 
        _LazyEvaluate.delID is called
        '''
        assert isinstance(func, Callable) and isinstance(allow_del, bool)

        functools.update_wrapper(self, func)
        self.allow_del = allow_del
        self.func = func
        self.calls = dict()

    def __call__(self, *args, **kwargs):
        '''
        Adds function call to a dictionary of calls to be executed later
        returns the call_id by which the function will be called
        '''
        def op(): return self.func(*args, **kwargs)
        call_id = id(op)
        self.calls[call_id] = Executor(op,
                                       call_id,
                                       lambda: self.delID(call_id),
                                       name=self.func.__name__)
        return self.calls[call_id]

    def delID(self, call_id: Union[int, Executor]):
        '''
        If del_after_eval is set to true this deletes object from list
        '''

        assert isinstance(call_id, int) or isinstance(call_id, Executor)

        if isinstance(call_id, Executor):
            call_id = call_id.uid

        if self.allow_del:
            del self.calls[call_id]
        return

    def runAll(self):
        '''
        Runs all call_ids and returns a dictionary of call_ids 
        and returned function values

        Returns
        ---
        ret_vals: dict
        Dictionary of all lazily added function calls
        '''
        ret_vals = {k: f.value for k, f in list(
            self.calls.items())}  # we wrap in list() to enable deleting elements during evaluation
        return ret_vals

    def run(self, call_id: Union[int, Executor]):
        '''
        Runs a particular call_id and returns function value

        Args
        ---
        call_id
        Executes the function with id returned by __call__() and
        removes it from the dictionary of call to be evaluated

        Returns
        ---
        The return value of the function with call_id 
        '''

        assert isinstance(call_id, int) or isinstance(call_id, Executor)

        if isinstance(call_id, Executor):
            call_id = call_id.uid

        ret_val = self.calls[call_id].value
        return ret_val
