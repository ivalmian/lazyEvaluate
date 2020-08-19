'''
lazyevaluate.lazy_evaluate
---

Contains the following objects:

    States
    Executor
    LazyEvaluate
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
        Operation hasn't been evaluated OR modified.
       
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
        Creates Executor object by passing function to be called, args, kwargs, lists of hooks on state transitions, and optional uid generation callabl (otherwise uid=id(self)). Calls all callables in on_init_hooks

    __repr__
        Returns a string with name, uid, and current state

    eval
        If in States.NOT_EVALUATED state evaluates the function and calls all callables in on_eval_hooks. Returns self.result

    value
        Setter and getter. If used to get then run Executor.eval(). If used as setter then set value, change state to MODIFIED, runs as 
        appropriate callables in on_modified_no_eval_hooks, on_modified_after_eval_hooks, on_modified_after_mod_hooks

    Examples:
    ---
    See https://github.com/ivalmian/lazyEvaluate/blob/master/examples
    '''

    def __init__(self, f: Callable,
                 args: List[Any] = [],
                 kwargs: Dict[Any] = {},
                 on_init_hooks: Union[None, List[Callable]] = None,
                 on_eval_hooks: Union[None, List[Callable]] = None,
                 on_modified_no_eval_hooks: Union[None, List[Callable]] = None,
                 on_modified_after_eval_hooks: Union[None, List[Callable]] = None,
                 on_modified_after_mod_hooks: Union[None, List[Callable]] = None,
                 uid: Union[None, Callable] = None):
        '''
        Creates the Executor object. All list of hooks callables wil be called and passed self as sole argument.

        Args
        ---
        f: Callable
            Function to be evaluated lazily (will be evaluated on the first call of Executor.eval() or Executor.value, result cached afterwards). 
            Will not be evaluated at all if prior to first evaluation value is set to something else
        args: List[Any]
            Will be passed as f(*args,**kwargs)
        kwargs: Dict[Any]
            Will be passed as f(*args,**kwargs)
        on_init_hooks: Union[None, List[Callable]]
            Callables that will be called after init passing self as argument
        on_eval_hooks: Union[None, List[Callable]]
            Callables that will be called when evaluating f (states transition NOT_EVALUATED -> EVALUATED)
        on_modified_no_eval_hooks: Union[None, List[Callable]]
            Callables that will be called when modifying and states transitioning NOT_EVALUATED -> MODIFIED
        on_modified_after_eval_hooks: Union[None, List[Callable]]
            Callables that will be called when modifying and states transitioning EVALUATED -> MODIFIED
        on_modified_after_mod_hooks: Union[None, List[Callable]]
            Callables that will be called when modifying and states transitioning MODIFIED -> MODIFIED
        uid: Union[None, Callable]
            If None will used id(self), otherwise will call uid() to get unique id for Executor object
        '''

        assert callable(f)
        assert uid is None or callable(uid)
        assert isinstance(args, list)
        assert isinstance(kwargs, dict)
        for hooks in [on_init_hooks, on_eval_hooks, on_modified_no_eval_hooks, on_modified_after_eval_hooks, on_modified_after_mod_hooks]:
            assert hooks is None or all(callable(h) for h in hooks)

        self.f = f
        self.args = args
        self.kwargs = kwargs
        self.uid = uid() if uid is not None else id(self)
        self.f_name = f.__name__

        self.result = None

        self.on_init_hooks = on_init_hooks
        self.on_eval_hooks = on_eval_hooks
        self.on_modified_no_eval_hooks = on_modified_no_eval_hooks
        self.on_modified_after_eval_hooks = on_modified_after_eval_hooks
        self.on_modified_after_mod_hooks = on_modified_after_mod_hooks

        self.state = States.NOT_EVALUATED

        if self.on_init_hooks:
            for hook in self.on_init_hooks:
                hook(self)

        return

    def __repr__(self):
        return f'<Executor for {self.f_name} @ {self.uid}, current state = {self.state}>'

    def eval(self):
        '''
        Evaluates if NOT_EVALUATED state and calls on_eval_hooks. Otherwise returns previously computed/set value.
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
        Gets value by looking at eval
        '''
        return self.eval()

    @value.setter
    def value(self, v):
        '''
        Sets value by looking at eval. Handles the following transitions and calls appropriate hooks

        1. NOT_EVALUATED -> MODIFIED          : on_modified_no_eval_hooks
        2. EVALUTED -> MODIFIED               : on_modified_after_eval_hooks
        3. MODIFIED -> MODIFIED               : on_modified_after_mod_hooks
        '''

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
            if self.on_modified_after_mod_hooks:
                for hook in self.on_modified_after_mod_hooks:
                    hook(self)
        else:
            raise Exception(f'{self}.state has improver value {self.state}')
        return


def LazyEvaluate(_func: Union[None, Callable] = None,
                 *,
                 on_init_hooks: Union[None, List[Callable]] = None,
                 on_eval_hooks: Union[None, List[Callable]] = None,
                 on_modified_no_eval_hooks: Union[None, List[Callable]] = None,
                 on_modified_after_eval_hooks: Union[None, List[Callable]] = None,
                 on_modified_after_mod_hooks: Union[None, List[Callable]] = None,
                 uid: Union[None, Callable] = None):
    '''  
    Wrapper around lazyEvaluate._LazyEvaluate decorator class 

    Allows passing no argument (in which case defauls are used) or with arguments. 
    All list of hooks callables wil be called and passed self as sole argument.
    See lazy_evaluate.Executor for more details.

    Args
    ---
    on_init_hooks: Union[None, List[Callable]]
        Callables that will be called after init passing self as argument
    on_eval_hooks: Union[None, List[Callable]]
        Callables that will be called when evaluating f (states transition NOT_EVALUATED -> EVALUATED)
    on_modified_no_eval_hooks: Union[None, List[Callable]]
        Callables that will be called when modifying and states transitioning NOT_EVALUATED -> MODIFIED
    on_modified_after_eval_hooks: Union[None, List[Callable]]
        Callables that will be called when modifying and states transitioning EVALUATED -> MODIFIED
    on_modified_after_mod_hooks: Union[None, List[Callable]]
        Callables that will be called when modifying and states transitioning MODIFIED -> MODIFIED
    uid: Union[None, Callable]
        If None will used id(self), otherwise will call uid() to get unique id for Executor object

    Examples:
    ---
    See https://github.com/ivalmian/lazyEvaluate/blob/master/examples

    '''
    assert _func is None or isinstance(_func, Callable)

    for hooks in [on_init_hooks, on_eval_hooks, on_modified_no_eval_hooks, on_modified_after_eval_hooks, on_modified_after_mod_hooks]:
        assert hooks is None or all(callable(h) for h in hooks)

    assert uid is None or callable(uid)

    if _func is None:
        return lambda func: _LazyEvaluate(func, on_init_hooks, on_eval_hooks, on_modified_no_eval_hooks, on_modified_after_eval_hooks, on_modified_after_mod_hooks, uid)
    else:
        return _LazyEvaluate(_func, on_init_hooks, on_eval_hooks, on_modified_no_eval_hooks, on_modified_after_eval_hooks, on_modified_after_mod_hooks, uid)


class _LazyEvaluate():
    '''
    Provides decorator for making functions evaluate lazily.

    Instead of returning their value instead return id, then 
    allow either executing by id or executing all at once.

    Examples:
    ---
    See https://github.com/ivalmian/lazyEvaluate/blob/master/examples

    '''

    def __init__(self,
                 func: Union[None, Callable] = None,
                 on_init_hooks: Union[None, List[Callable]] = None,
                 on_eval_hooks: Union[None, List[Callable]] = None,
                 on_modified_no_eval_hooks: Union[None, List[Callable]] = None,
                 on_modified_after_eval_hooks: Union[None, List[Callable]] = None,
                 on_modified_after_mod_hooks: Union[None, List[Callable]] = None,
                 uid: Union[None, Callable] = None):
        '''
        Creates a wrapped for func.
        '''

        functools.update_wrapper(self, func)
        self.on_init_hooks = on_init_hooks
        self.on_eval_hooks = on_eval_hooks
        self.on_modified_no_eval_hooks = on_modified_no_eval_hooks
        self.on_modified_after_eval_hooks = on_modified_after_eval_hooks
        self.on_modified_after_mod_hooks = on_modified_after_mod_hooks
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
                      self.on_init_hooks,
                      self.on_eval_hooks,
                      self.on_modified_no_eval_hooks,
                      self.on_modified_after_eval_hooks,
                      self.on_modified_after_mod_hooks, call_id)
        return op

