"""Utilities for working with CCPN/FC"""

from ccpnmr.format.converters.PseudoPdbFormat import PseudoPdbFormat
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTmessageNoEOL
from cing.Libs.NTutils import NTwarning
from cing.Libs.NTutils import getDeepByKeysOrDefault
from cing.Libs.pdb import defaultPrintChainCode
from cing.Scripts.FC.constants import KEYWORDS
from cing.Scripts.FC.constants import READ_COORDINATES
from cing.Scripts.utils import printSequenceFromPdbFile
from glob import glob

def reportDifference(ccpnProject, fn):
    printSequenceFromCcpnProject(ccpnProject)
    printSequenceFromPdbFile(fn)

def printSequenceFromCcpnProject(ccpnProject):
    molSystem = ccpnProject.findFirstMolSystem()
    firstChain = molSystem.findFirstChain()
#    print 'Code [%s], name [%s]' % (firstChain.code, firstChain.molecule.name)

    fastaString = ''

    for res in firstChain.sortedResidues():
        code1Letter = res.molResidue.chemComp.code1Letter
        if not code1Letter:
          code1Letter = defaultPrintChainCode

        fastaString += code1Letter
        NTmessageNoEOL('%s%s' % (res.ccpCode, res.seqCode))
        if not (res.seqCode % 50):
            NTmessage('')
    NTmessage('')
    NTmessage("Sequence from CCPN project:")
    NTmessage(fastaString)

def importPseudoPdb(ccpnProject, inputDir, guiRoot, allowPopups=1, minimalPrompts=0, verbose=1, **presets):
    NTdebug("Using presets %s" % `presets`)
    formatPseudoPdb = PseudoPdbFormat(ccpnProject, guiRoot, verbose=verbose, minimalPrompts=minimalPrompts, allowPopups=allowPopups)
    nmrProject = ccpnProject.currentNmrProject
#        nmrProject = project.newNmrProject(name=project.name)
    structureEnsemble = ccpnProject.findFirstStructureEnsemble()
    if structureEnsemble:
        NTmessage("Removing first found structureEnsemble")
        structureEnsemble.delete()
    else:
        NTwarning("No structureEnsemble found; can't remove it.")

    structureGenerationList = nmrProject.sortedStructureGenerations()
    if not structureGenerationList:
        NTdebug("No or empty structureGenerationList; creating a new one.")
        nmrProject.newStructureGeneration()
        structureGenerationList = nmrProject.sortedStructureGenerations()
    structureGeneration = structureGenerationList[0]
#        structureGeneration = nmrProject.findFirstStructureGeneration()
#        structureGeneration = nmrProject.newStructureGeneration()
    if not structureGeneration:
        NTerror("Failed to find or create structureGeneration")
        return True

    globPattern = inputDir + '/*.pdb'
    fileList = glob(globPattern)
    NTdebug("From %s will read files: %s" % (globPattern, fileList))
    if len(fileList) != 1:
        NTerror("Failed to find single PDB file; instead found list: %s" % `fileList`)
        return True

    keywds = getDeepByKeysOrDefault(presets, {}, READ_COORDINATES, KEYWORDS)
    NTdebug("From getDeepByKeysOrDefault keywds: %s" % `keywds`)
    reportDifference(ccpnProject, fileList[0])

    status = formatPseudoPdb.readCoordinates(fileList, strucGen=structureGeneration, linkAtoms=0, swapFirstNumberAtom=1,
        minimalPrompts=minimalPrompts, verbose=verbose, **keywds)
    if not status: # can return None or False on error
        NTerror("Failed to formatPseudoPdb.readCoordinates")
        return True # returns True on error


#TODO: is this needed?
#    status = formatPseudoPdb.linkResonances(
#                  forceDefaultChainMapping = 1,
#                  globalStereoAssign = 1,
#                  setSingleProchiral = 1,
#                  setSinglePossEquiv = 1,
#                  strucGen = structureGeneration,
#                  allowPopups=allowPopups, minimalPrompts=minimalPrompts, verbose=verbose, **keywds )
#    if not status: # can return None or False on error
#        NTerror("Failed to formatPseudoPdb.linkResonances")
#        return True # returns True on error

