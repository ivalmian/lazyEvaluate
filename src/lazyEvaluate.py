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
from typing import Union, Callable, List, Dict, Any


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

    def __init__(self, f: Callable,
                 args: List[Any] = [],
                 kwargs: Dict[Any] = {},
                 on_call_hooks: Union[None, List[Callable]] = None,
                 on_eval_hooks: Union[None, List[Callable]] = None,
                 on_modified_no_eval_hooks: Union[None, List[Callable]] = None,
                 on_modified_after_eval_hooks: Union[None, List[Callable]] = None,
                 on_modified_after_mod: Union[None, List[Callable]] = None,
                 uid: Union[None, int, str] = None):
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

        assert callable(f)
        assert uid is None or isinstance(uid, int) or isinstance(uid, str)
        assert isinstance(args, list)
        assert isinstance(kwargs, dict)
        for hooks in [on_call_hooks, on_eval_hooks, on_modified_no_eval_hooks, on_modified_after_eval_hooks, on_modified_after_mod]:
            assert hooks is None or all(callable(h) for h in hooks)

        self.f = f
        self.args = args
        self.kwargs = kwargs
        self.uid = uid if uid is not None else id(f)
        self.f_name = f.__name__

        self.result = None

        self.on_call_hooks = on_call_hooks
        self.on_eval_hooks = on_eval_hooks
        self.on_modified_no_eval_hooks = on_modified_no_eval_hooks
        self.on_modified_after_eval_hooks = on_modified_after_eval_hooks
        self.on_modified_after_mod = on_modified_after_mod

        self.state = States.NOT_EVALUATED

        if self.on_call_hooks:
            for hook in self.on_call_hooks:
                hook(self)

        return

    def __str__(self):
        return f'<Executor for {self.f_name} @ {self.uid}, current state = {self.state}>'

    def eval(self):
        '''
        Evaluates if NOT_EVALUATED state and calls eval_hook and dropOp. Otherwise returns previously computed/set value.
        '''
        if self.state == States.NOT_EVALUATED:
            self.result = self.f(*self.args, **self.kwargs)
            self.state = States.EVALUATED
            if self.on_eval_hooks:
                for hook in self.on_eval_hooks:
                    hook(self)

        return self.result

    @property
    def value(self):
        '''
        Sets/gets value, if set it will use that value and not evaluate even if not previously evaluated
        '''
        return self.eval()

    @value.setter
    def value(self, v):
        self.result = v
        if self.state == States.NOT_EVALUATED:
            self.state = States.MODIFIED
            if self.on_modified_no_eval_hooks:
                for hook in self.on_modified_no_eval_hooks:
                    hook(self)
        elif self.state == States.EVALUATED:
            self.state = States.MODIFIED
            if self.on_modified_after_eval_hooks:
                for hook in self.on_modified_after_eval_hooks:
                    hook(self)
        elif self.state == States.MODIFIED:
            self.state = States.MODIFIED
            if self.on_modified_after_mod:
                for hook in self.on_modified_after_mod:
                    hook(self)
        else:
            raise Exception(f'{self}.state has improver value {self.state}')
        return


def LazyEvaluate(_func: Union[None, Callable] = None,
                 *,
                 on_call_hooks: Union[None, List[Callable]] = None,
                 on_eval_hooks: Union[None, List[Callable]] = None,
                 on_modified_no_eval_hooks: Union[None, List[Callable]] = None,
                 on_modified_after_eval_hooks: Union[None, List[Callable]] = None,
                 on_modified_after_mod: Union[None, List[Callable]] = None,
                 uid: Union[None, Callable] = None):
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

    for hooks in [on_call_hooks, on_eval_hooks, on_modified_no_eval_hooks, on_modified_after_eval_hooks, on_modified_after_mod]:
        assert hooks is None or all(callable(h) for h in hooks)

    assert uid is None or callable(uid)

    if _func is None:
        return lambda func: _LazyEvaluate(func, on_call_hooks, on_eval_hooks, on_modified_no_eval_hooks, on_modified_after_eval_hooks, on_modified_after_mod, uid)
    else:
        return _LazyEvaluate(_func, on_call_hooks, on_eval_hooks, on_modified_no_eval_hooks, on_modified_after_eval_hooks, on_modified_after_mod, uid)


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

    def __init__(self,
                 func: Union[None, Callable] = None,
                 on_call_hooks: Union[None, List[Callable]] = None,
                 on_eval_hooks: Union[None, List[Callable]] = None,
                 on_modified_no_eval_hooks: Union[None, List[Callable]] = None,
                 on_modified_after_eval_hooks: Union[None, List[Callable]] = None,
                 on_modified_after_mod: Union[None, List[Callable]] = None,
                 uid: Union[None, Callable] = None):
        '''
        Creates a wrapped for func.
        '''

        functools.update_wrapper(self, func)
        self.on_call_hooks = on_call_hooks
        self.on_eval_hooks = on_eval_hooks
        self.on_modified_no_eval_hooks = on_modified_no_eval_hooks
        self.on_modified_after_eval_hooks = on_modified_after_eval_hooks
        self.on_modified_after_mod = on_modified_after_mod
        self.uid = uid
        self.func = func

    def __call__(self, *args, **kwargs):
        '''
        Adds function call to a dictionary of calls to be executed later
        returns the call_id by which the function will be called
        '''

        call_id = None if self.uid is None else self.uid()
        op = Executor(self.func,
                      args, kwargs,
                      self.on_call_hooks,
                      self.on_eval_hooks,
                      self.on_modified_no_eval_hooks,
                      self.on_modified_after_eval_hooks,
                      self.on_modified_after_mod, call_id)
        return op

