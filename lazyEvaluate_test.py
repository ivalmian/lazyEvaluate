import unittest
from lazyEvaluate import lazyEvaluate

@lazyEvaluate
def fdiv(a,b):
    val=a/b
    return val

class test_lazy_evaluate(unittest.TestCase):
    
    def test_runAll(self):
        fdiv(5,5)
        fdiv(5,2)
        fdiv(3,4)
        outputs = fdiv.runAll()
        expected_outputs = [5/5,5/2,3/4]
        for v1,v2 in zip(outputs.values(),expected_outputs):
            self.assertEqual(v1,v2)

    def test_run(self):
        first= fdiv(5,5)
        second=fdiv(5,2)

        self.assertEqual(fdiv.run(second),5/2)
        self.assertEqual(fdiv.run(first),5/5)
        


    