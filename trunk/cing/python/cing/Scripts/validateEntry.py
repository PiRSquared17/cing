"""
Unit test
python $cingPath/PluginCode/test/test_validate.py
"""
from cing import verbosityDebug
from cing import verbosityNothing
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.core.classes import Project
from cing.core.constants import BMRB
from cing.core.constants import CYANA
from cing.core.constants import PDB
from cing.core.constants import XPLOR
import cing
import os
import sys

def main(entryId, *extraArgList):
    expectedNumberOfArguments = 4
    if len( extraArgList ) != expectedNumberOfArguments:
        NTerror("Got arguments: %s" % extraArgList )
        NTerror("Failed to get expected number of arguments: %d got %d"%( 
            expectedNumberOfArguments, len( extraArgList )))
        return True
    
    inputDir              = os.path.join( extraArgList[0], entryId )
    outputDir             = extraArgList[1]
    pdbConvention         = extraArgList[2] #@UnusedVariable
    restraintsConvention  = extraArgList[3]

    os.chdir(outputDir)
    
    project = Project( entryId )
    if project.removeFromDisk():
        NTerror("Failed to remove existing project (if present)")
        return True
        
    project = Project.open( entryId, status='new' )
    pdbFileName = entryId+".pdb"
#    pdbFilePath = os.path.join( inputDir, pdbFileName)
    pdbFilePath = os.path.join( inputDir, pdbFileName)
    
    if True:
        pdbConvention = BMRB
        if entryId.startswith("1YWUcdGMP"):
            pdbConvention = XPLOR
        if entryId.startswith("2hgh"):
            pdbConvention = CYANA
        if entryId.startswith("1tgq"):
            pdbConvention = PDB
    
    project.initPDB( pdbFile=pdbFilePath, convention = pdbConvention )
    NTdebug("Reading files from directory: " + inputDir)
    kwds = {'uplFiles': [ entryId ],
            'acoFiles': [ entryId ]              
              }
    
    if entryId.startswith("1YWUcdGMP"):
        del(kwds['acoFiles'])
        
    if os.path.exists( os.path.join(         inputDir, entryId+".prot")):
        if os.path.exists( os.path.join( inputDir, entryId+".seq" )):
            kwds['protFile'] = entryId
            kwds['seqFile']  = entryId
        else:
            NTerror("Failed to find the .seq file whereas there was a .prot file.")

    # Skip restraints if absent.
    if os.path.exists( os.path.join( inputDir, entryId+".upl")):
        project.cyana2cing(cyanaDirectory=inputDir, 
                           convention=restraintsConvention,
                           copy2sources = True,
                           **kwds )
    project.save()
    if project.validate():
        NTerror("Failed to validate project read")
        return True
    project.save()
        

if __name__ == "__main__":
    cing.verbosity = verbosityNothing
    cing.verbosity = verbosityDebug
    if main(*sys.argv[1:]):
        sys.exit(1)