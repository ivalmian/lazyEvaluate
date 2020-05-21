#pylint: disable=no-member
import unittest
from .. import LazyEvaluate, Executor

@LazyEvaluate(del_after_eval=False)
def fdiv(a,b):
    val=a/b
    return val

@LazyEvaluate(del_after_eval=True)
def fdiv_del(a,b):
    val=a/b
    return val

@LazyEvaluate()
def fdiv_del2(a,b):
    val=a/b
    return val

class test_lazy_evaluate(unittest.TestCase):
    
    def test_Executor(self):
        ex = Executor(lambda: 5, uid=5, eval_hook=lambda: print('evaluated'),name='5')
        self.assertEqual(str(ex), 'Executor for 5, current state = States.NOT_EVALUATED')
        self.assertEqual(ex.uid,5)
        self.assertEqual(ex.value,5)    
        self.assertEqual(str(ex), 'Executor for 5, current state = States.EVALUATED')
        ex.value ='hello'
        self.assertEqual(ex.value,'hello')
        self.assertEqual(str(ex), 'Executor for 5, current state = States.MODIFIED')

    def test_Executor_default_options(self):
        ex = Executor(lambda: 5)
        self.assertEqual(ex.value,5)    
       

    def test_LazyEvaluate_delID(self):
        k=fdiv(5,3)
        fdiv.delID(k)

    def test_LazyEvaluate_runAll(self):
        execs =[None]*3
        execs[0] =fdiv(5,5)
        execs[1] =fdiv(5,2)
        execs[2] =fdiv(3,4)
        outputs = fdiv.runAll()
        expected_outputs = [5/5,5/2,3/4]
        for ex,exp_output in zip(execs,expected_outputs):
            self.assertEqual(outputs[ex.uid],exp_output)
            self.assertEqual(ex.value,exp_output)
        self.assertGreaterEqual(len(fdiv.calls),3) #number of calls should be 3 or greater since del_after_eval=False

    def test_LazyEvaluate_runAll_del(self):
        execs =[None]*3
        execs[0] =fdiv_del(5,5)
        execs[1] =fdiv_del(5,2)
        execs[2] =fdiv_del(3,4)
        outputs = fdiv_del.runAll()
        expected_outputs = [5/5,5/2,3/4]
        for ex,exp_output in zip(execs,expected_outputs):
            self.assertEqual(outputs[ex.uid],exp_output)
            self.assertEqual(ex.value,exp_output)
        self.assertEqual(len(fdiv_del.calls),0) #number of calls should be 0 since del_after_eval=True


    def test_LazyEvaluate_runAll_del2(self):
        execs =[None]*3
        execs[0] =fdiv_del2(5,5)
        execs[1] =fdiv_del2(5,2)
        execs[2] =fdiv_del2(3,4)
        outputs = fdiv_del2.runAll()
        expected_outputs = [5/5,5/2,3/4]
        for ex,exp_output in zip(execs,expected_outputs):
            self.assertEqual(outputs[ex.uid],exp_output)
            self.assertEqual(ex.value,exp_output)
        self.assertEqual(len(fdiv_del2.calls),0) #number of calls should be 0 since del_after_eval=True

    def test_LazyEvaluate_run(self):
        first= fdiv(5,5)
        second=fdiv(5,2)

        self.assertEqual(fdiv.run(second),5/2)
        self.assertEqual(fdiv.run(first),5/5)
        self.assertEqual(first.value,5/5) 

    def test_LazyEvaluate_Executor_state_changes(self):
        s = fdiv(1,2)
        self.assertEqual(str(s), 'Executor for fdiv, current state = States.NOT_EVALUATED')
        self.assertEqual(s.value,0.5)
        self.assertEqual(str(s), 'Executor for fdiv, current state = States.EVALUATED')
        s.value ='hello'
        self.assertEqual(s.value,'hello')
        self.assertEqual(str(s), 'Executor for fdiv, current state = States.MODIFIED')


    