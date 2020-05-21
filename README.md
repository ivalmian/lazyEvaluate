# lazyevaluate: a micro library for lazy evaluation

Primary use is via lazyevaluate.LazyEvaluate which wraps the _LazyEvaluate class. It can be used as a decorator around a function, in which case it will replace the return value of the function with lazyEvaluate.Executor object. 

lazyevaluate.Executor will only execute the originally called function when the value is attempted to be retrieved. Evaluations of a given Executor are memoized, only the first one actually uses the function call (however used can make multiple Executors for given function/set of arguments).

Both LazyEvaluate and Executor have additional helper methods to deal with lazy evaluation

## Setup

You can setup with pip:

```
pip install <path to repo>
```

## Example

Code (see example_script.py):
```
from lazyEvaluate import LazyEvaluate, Executor

@LazyEvaluate
def fdiv(a,b):
    val=a/b
    print(f'{a}/{b}={val}')
    return val

print('Defining calls')
fdiv(4,5)
fdiv(54,5)
fdiv(43,5)
print('Executing calls')
fdiv.runAll()
print('Adding more calls')
call_id = fdiv(3,5)
print(f'Executing call_id {call_id}')
fdiv.run(call_id)
fdiv.runAll() #doesn't have anything to run so will do nothing

e = Executor(lambda: 5, eval_hook = lambda: print("Function evaluated"))
print(e)
print(e.value)
print(e)
e.value='hello'
print(e.value)
print(e)
```
Example output:
```
Defining calls
Executing calls
4/5=0.8
54/5=10.8
43/5=8.6
Adding more calls
Executing call_id Executor for fdiv, current state = States.NOT_EVALUATED
3/5=0.6
Executor for <lambda>, current state = States.NOT_EVALUATED
Function evaluated
5
Executor for <lambda>, current state = States.EVALUATED
hello
Executor for <lambda>, current state = States.MODIFIED
```

## Test

python -m lazyevaluate.test

OR 

install coverage (in test_requirements.txt) and execute

./run_test.sh