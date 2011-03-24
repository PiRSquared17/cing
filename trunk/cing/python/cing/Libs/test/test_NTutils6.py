"""
Unit test execute as:
python -u $CINGROOT/python/cing/Libs/test/test_NTutils6.py
"""

from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.core.classes2 import ResonanceList
from unittest import TestCase
import unittest

class AllChecks(TestCase):
    os.chdir(cingDirTmp)

    def testGetCallerName(self):
        self.failIf( getCallerName() != 'testGetCallerName')
        self.failIf( additionalTestRoutineByItself() != 'additionalTestRoutineByItself')

    def testGetUniqueName(self):
        resonanceSources = NTlist()
        resonanceSources.append(ResonanceList('a'))
        inputList           = ['b', 'a']
        expectedOutputList  = ['b', 'a_1']
        for i,input in enumerate(inputList):
            output = getUniqueName(resonanceSources, input)
            self.assertEqual( output, expectedOutputList[i])        
        self.assertEqual( getUniqueName(resonanceSources, 'a', nameFormat = '%s---%06d'), 'a---000001')

    def testFilterListByObjectClassName(self):
        l = ['a', 'b', 1.0, 2.0, 3.0, NTdict(), None, None, None, None ]
        ls = filterListByObjectClassName(l, 'str')
        self.assertEqual( len(ls), 2)
        lf = filterListByObjectClassName(l, 'float')
        self.assertEqual( len(lf), 3)
        ld = filterListByObjectClassName(l, 'NTdict')
        self.assertEqual( len(ld), 1)
#        ln = filterListByObjectClassName(l, 'NoneType')
        ln = filterListByObjectClassName(l, None) # NB don't use NoneType for this as the routine isn't that smart.
        self.assertEqual( len(ln), 4)

    def testgetListByName(self):
        lol = NTlist(ResonanceList('a'), ResonanceList('b'))
        l = getObjectByName(lol, 'b')
        self.assertTrue( l != None )
        self.assertTrue( l.name == 'b' )

def additionalTestRoutineByItself():
    return getCallerName() 

if __name__ == "__main__":
    cing.verbosity = cing.verbosityDebug
    unittest.main()
