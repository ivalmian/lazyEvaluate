import functools

class lazyEvaluate():
    '''
    Provides decorator for making functions evaluate lazily.

    Instead of returning their value instead return id, then 
    allow either executing by id or executing all at once.

    Methods
    ---
    __call__
        Adds function call with argument to dict, 
        return key to that call
    run(call_id)
        Executes a particular function call and returns its value
    runAll
        Executes all function calls in the dictionary

    Example:

    @lazyEvaluate
    def fdiv(a,b):
        val=a/b
        print(f'{a}/{b}={val}')
        return val

    print('Defining calls')
    fdiv(4,5)
    fdiv(54,5)
    fdiv(43,5)
    print('Executing calls')
    fdiv.executeAll()
    print('Adding more calls')
    call_id = fdiv(3,5)
    print(f'Executing call_id {call_id}')
    fdiv.execute(call_id)
    fdiv.executeAll()

    Example output:

    Defining calls
    Executing calls
    4/5=0.8
    54/5=10.8
    43/5=8.6
    Adding more calls
    Executing call_id 139620766968432
    3/5=0.6

    '''
    def __init__(self,func):
        functools.update_wrapper(self, func)
        self.func = func
        self.calls = dict()
    
    def __call__(self, *args, **kwargs):
        '''
        Adds function call to a dictionary of calls to be executed later
        returns the call_id by which the function will be called
        '''
        c = lambda: self.func(*args,**kwargs)
        self.calls[id(c)]=c
        return id(c)

    def runAll(self):
        '''
        Runs all call_ids and returns a dictionary of call_ids 
        and returned function values

        Returns
        ---
        ret_vals: dict
        Dictionary of all lazily added function calls
        '''
        ret_vals = {k:f() for k,f in self.calls.items()}
        self.calls=dict()
        return ret_vals

    def run(self,call_id):
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
        ret_val = self.calls[call_id]()
        del self.calls[call_id]
        return ret_val