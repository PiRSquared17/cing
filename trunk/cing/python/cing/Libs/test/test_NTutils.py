"""
Unit test execute as:
python $cingPath/Scripts/test/test_cyana2cing.py
"""
from cing import NaNstring
from cing import cingDirTestsData
from cing import cingDirTestsTmp
from cing import cingPythonDir
from cing import verbosityError
from cing.Libs.NTutils import NTdict
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import convert2Web
from cing.Libs.NTutils import findFiles
from cing.Libs.NTutils import printDebug
from cing.Libs.NTutils import val2Str
from cing.core.parameters import cingPaths
from unittest import TestCase
import cing
import os
import unittest

class AllChecks(TestCase):

    def testPrints(self):
#        printException("Now in testPrints")
#        printError("test")
        pass
    
    def testFind(self):
        self.assertTrue( os.path.exists( cingPythonDir) and os.path.isdir(cingPythonDir ) )
        self.failIf( os.chdir(cingPythonDir), msg=
            "Failed to change to test directory for data: "+cingPythonDir)
        namepattern, startdir = "CVS", cingPythonDir
        nameList = findFiles(namepattern, startdir)
        self.assertTrue( len(nameList) > 10 ) 
#        for name in nameList:
#            print name

    def testConvert2Web(self):
        fn = "pc_nmr_11_rstraints.ps"
        self.assertTrue( os.path.exists( cingDirTestsData) and os.path.isdir(cingDirTestsData ) )
        inputPath = os.path.join(cingDirTestsData,fn)
        outputPath = cingDirTestsTmp
        self.failIf( os.chdir(outputPath), msg=
            "Failed to change to temporary test directory for data: "+outputPath)
        fileList = convert2Web( cingPaths.convert, cingPaths.ps2pdf, inputPath, outputDir=outputPath ) 
        printDebug( "Got back from convert2Web output file names: " + `fileList`)
        self.assertNotEqual(fileList,True)
        if fileList != True:
            for file in fileList: 
                self.assertNotEqual( file, None)

    def testCircularAverage(self):
        lol = [  [   5,  15,   10],
                [  345,   5,  355],
                 [   5, 345,  355],
                  [180,-180, None],
                   [90, -70,   10]]
        for cycle in lol:
            v1, v2, cav = cycle            
            angleList = NTlist()
            angleList.append(v1)
            angleList.append(v2)
            result = angleList.cAverage(0, 360, 0, None)
            self.failUnless(result)
            circularAverage,_circularVariance,_n = result
            if cav != None:
                self.assertAlmostEqual(circularAverage, cav, places=5)
                
    def testCircularAverage2(self):
        angleList = NTlist()
        angleList.append(1)
        result = angleList.cAverage(0, 360, 0, None)
        self.failUnless(result)
        circularAverage,_circularVariance,_n = result
        self.assertAlmostEqual(circularAverage, 1, places=5)
                
    def testCircularAverage3(self):
        angleList = NTlist()
        result = angleList.cAverage(0, 360, 0, None)
        self.failUnless(result)
        _circularAverage,_circularVariance,_n = result
                
            
#        double[][] testValues = new double[][] {
#                {    5,  15,   10},
#                {  345,   5,   20},
#                 {   5, 345,  -20},
#                  {180, 180,    0},
#                   {90, -70, -160}                
#        };

    def testGeneral(self):
        s = NTdict(aap='noot', mies=1)
        s.setdefault('mies',2)
        s.setdefault('kees',[])
        s.kees = [0, 1, 3]
        s.name ='ss'
  
        b = s.copy()
 
        p = s.popitem() 
        while p:
            p = s.popitem()
        s.update( b  )

        
    def testNTaverage(self):
        l = NTlist( 4, 9, 11, 12, 17, 5, 8, 12, 14 )
        (av,sd,n) = l.average()
        printDebug((av,sd,n))
        self.assertAlmostEqual( av, 10.22, places=1) # verified in Excel stddev function.
        self.assertAlmostEqual( sd,  4.18, places=1) 
        self.assertEquals(       n, 9) 

        l = NTlist( 1,None,1,1 )
        (av,sd,n) = l.average()
        printDebug((av,sd,n))
        self.assertAlmostEqual( av,   1.0, places=1) 
        self.assertAlmostEqual( sd,   0.0, places=1) 
        self.assertEquals(       n, 3) 
        
        l = NTlist( 1,2 )
        (av,sd,n) = l.average()
        printDebug((av,sd,n))
        self.assertAlmostEqual( av,   1.5, places=1) 
        self.assertAlmostEqual( sd, 0.707, places=2) 
        self.assertEquals(       n, 2) 
        
        l = NTlist( 1 )
        (av,sd,n) = l.average()
        printDebug((av,sd,n))
        self.assertAlmostEqual( av,   1.0, places=1) 
        self.assertEquals(      sd,  None) 
        self.assertEquals(       n,   1) 
        
        l = NTlist()
        (av,sd,n) = l.average()
        printDebug((av,sd,n))
        self.assertEquals(      av,  None) 
        self.assertEquals(      sd,  None) 
        self.assertEquals(       n,   0) 

    def testValueToFormattedString(self):
        self.assertEquals( val2Str(None,"%5.2f",None),NaNstring)
        self.assertEquals( val2Str(None,"%5.2f",5),   "%5s" % NaNstring)
        self.assertEquals( val2Str(6.3, "%5.2f",5),   " 6.30")
        self.assertEquals( val2Str(6.3, "%.2f"),      "6.30")
        self.assertEquals( val2Str(6.3, "%03d"),      "006")
        
if __name__ == "__main__":
    cing.verbosity = verbosityError
#    cing.verbosity = verbosityDebug
    unittest.main()
