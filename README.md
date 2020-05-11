# Tiny wrapper to make function lazy evaluatable

lazyEvaluate.lazyEvaluate wraps your function to make it lazy evaluatable. When you call the function instead of evaluating it, it returns a call_id and adds it to a dictionary of to-be-run functions. You can then force an evaluation of either a partiuclar call using run(call_id) method or evaluate all calls using runAll() method. 

## Example

Code:
```
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
fdiv.runAll()
print('Adding more calls')
call_id = fdiv(3,5)
print(f'Executing call_id {call_id}')
fdiv.run(call_id)
fdiv.runAll() #doesn't have anything to run so will do nothing
```
Example output:
```
Defining calls
Executing calls
4/5=0.8
54/5=10.8
43/5=8.6
Adding more calls
Executing call_id 139620766968432
3/5=0.6
```

## Test

python -m unittest lazyEvaluate_test.py