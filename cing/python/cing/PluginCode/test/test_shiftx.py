from cing import cingDirTestsData
from cing import cingDirTmp
from cing import verbosityDebug
from cing import verbosityError
from cing import verbosityNothing
from cing.core.classes import Project
from cing.core.constants import BMRB
from cing.core.constants import CYANA
from cing.core.constants import PDB
from cing.core.constants import XPLOR
from unittest import TestCase
import cing
import os
import unittest

class AllChecks(TestCase):
 
    def testRun(self):
        pdbConvention = BMRB
#        entryId = "1brv" # Small much studied PDB NMR entry 
#        entryId = "2hgh_1model" # RNA-protein complex.
        entryId = "1brv_1model" 
#        entryId = "1tgq_1model" # withdrawn entry
#        entryId = "1YWUcdGMP" # Example entry from external user, Martin Allan
        
        if entryId.startswith("1YWUcdGMP"):
            pdbConvention = XPLOR
        if entryId.startswith("2hgh"):
            pdbConvention = CYANA
        if entryId.startswith("1tgq"):
            pdbConvention = PDB
        self.failIf( os.chdir(cingDirTmp), msg=
            "Failed to change to directory for temporary test files: "+cingDirTmp)
        project = Project( entryId )
        self.failIf( project.removeFromDisk())
        project = Project.open( entryId, status='new' )
        cyanaDirectory = os.path.join(cingDirTestsData,"cyana", entryId)
        pdbFileName = entryId+".pdb"
        pdbFilePath = os.path.join( cyanaDirectory, pdbFileName)
        
        project.initPDB( pdbFile=pdbFilePath, convention = pdbConvention )
        project.predictWithShiftx()
                
if __name__ == "__main__":
    cing.verbosity = verbosityNothing
    cing.verbosity = verbosityError
    cing.verbosity = verbosityDebug
    unittest.main()