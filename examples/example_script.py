from lazyevaluate import LazyEvaluate, Executor

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