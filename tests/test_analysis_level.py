import unittest
import cast.analysers.test
from cast.analysers import filter
import cast.analysers.log 



class Test(unittest.TestCase):


     def testName(self):
        analysis = cast.analysers.test.JEETestAnalysis()
        
        analysis.add_selection('src/package1')
        analysis.add_dependency('com.castsoftware.internal.platform')
        analysis.set_verbose()
        analysis.run()
        
        
      
        
       
    

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

