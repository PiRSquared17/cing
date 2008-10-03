"""

GVprocheck( ranges=None, verbose = True )

Molecule:
    procheck: <Procheck> object

Residue
    procheck: NTdict instance with procheck values for this residue

"""
#@PydevCodeAnalysisIgnore
from cing.Libs.AwkLike import AwkLike
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.core.parameters import cingPaths
from cing.core.molecule import dots
import cing #@Reimport

import os #@Reimport

def procheckString2float( string ):
    """Convert a string to float, return None in case of value of 999.90
    """
    result = float( string )
    if result == 999.90:
        return None
    else:
        return result
    #end if
#end def


class gvProcheck:
    #TODO: subclass this from ExecuteProgram
    """
    From Jurgen:

    Column id
    ^ Fortran variable
    ^ ^        Explanation
    ##############################
    ###################################################
    1 NXRES    residue number in procheck
    2 AA3      residue name
    3 BRKSYM   chain id as in PDB file
    4 SEQBCD   resdiue id as in PDB file??
    5 SUMMPL   secondary structure classification (DSSP?)
    6 MCANGS 1 phi
    7 MCANGS 2 psi
    8 MCANGS 3 omega
    9 SCANGS 1 chi 1
    0 SCANGS 2 chi 2
    1 SCANGS 3 chi 3
    2 SCANGS 4 chi 4
    3 HBONDE   Hydrogen bond energy
    4 DSDSTS ? statistics?
    5 MCANGS ?
    6 BVALUE   Crystallographic B factor
    7 MCBVAL   Mainchain B value
    8 SCBVAL   Sidechain B value
    9 OOIS 1 ?
    0 OOIS 2 ?
    1 MCBSTD Main chain bond standard deviation?
    2 SCBSTD Side chain bond standard deviation?


    #0000000000000000000000000000000000000000000000000000000000000000000000
      55GLY A  62 T-147.73 -20.13-166.50 999.90 999.90 999.90 999.90  -0.87   0.00 999.90   0.00  0.000  0.000 11 38  0.000  0.000
      56ASP A  63 e -78.77 161.06-173.97 -56.24 -71.93 999.90 999.90  -0.76   0.00  34.42   0.00  0.000  0.000 13 50  0.000  0.000
      57ARG A  64 E-104.07 124.65 166.81 177.50-170.21 179.43-172.18  -2.12   0.00  37.30   0.00  0.000  0.000 12 56  0.000  0.000
      58VAL A  65 E -87.26 117.24 175.76-157.64 999.90 999.90 999.90  -3.33   0.00  33.46   0.00  0.000  0.000 14 67  0.000  0.000
      59LEU A  66 E -99.01 -36.19-179.02  50.71 149.42 999.90 999.90  -2.74   0.00  31.00   0.00  0.000  0.000 13 50  0.000  0.000
      95PRO!A 102   -69.35 999.90 999.90 -24.86 999.90 999.90 999.90   0.00   0.00  37.72   0.00  0.000  0.000  4 13  0.000  0.000
      96TYR!B 205   999.90 -55.02-171.34-143.34 -89.71 999.90 999.90   0.00   0.00  34.80   0.00  0.000  0.000  2  5  0.000  0.000
      97LEU B 206    61.37 179.80 171.30-145.66  66.98 999.90 999.90   0.00   0.00  31.07   0.00  0.000  0.000  3  5  0.000  0.000
    """
    procheckDefs = NTdict(
    #   field       (startChar, endChar, conversionFunction)
        line      = (  0,  4, int ),
        resName   = (  4,  7, str ),
        chain     = (  8,  9, str ),
        resNum    = ( 10, 13, int ),
        secStruct = ( 14, 15, str ),
        PHI       = ( 15, 22, procheckString2float ),
        PSI       = ( 22, 29, procheckString2float ),
        OMEGA     = ( 29, 36, procheckString2float ),
        CHI1      = ( 36, 43, procheckString2float ),
        CHI2      = ( 43, 50, procheckString2float ),
        CHI3      = ( 50, 57, procheckString2float ),
        CHI4      = ( 57, 64, procheckString2float )
    )

    def __init__(self, project ):
        """
        Procheck class allows running procheck_nmr and parsing of results
        """
        self.molecule     = project.molecule
        self.rootPath     = project.mkdir( project.molecule.name, project.moleculeDirectories.procheck  )
#        self.runProcheck  = ExecuteProgram( cing.paths.procheck_nmr,
#                                            rootPath = self.rootPath,
#                                            redirectOutput= False
#                                          )
        self.ranges  = None
        self.summary = None
    #end def

    def run(self, ranges=None ):
        NTmessage('==> Running procheck_nmr, ranges %s, results in "%s" ...', ranges, self.rootPath)

        # Convert the ranges and translate into procheck_nmr format
        selectedResidues = self.molecule.ranges2list( ranges )
        NTsort(selectedResidues, 'resNum', inplace=True)
        # reduce this sorted list to pairs start, stop
        self.ranges = selectedResidues[0:1]
        for i in range(0,len(selectedResidues)-1):
            if ((selectedResidues[i].resNum < selectedResidues[i+1].resNum - 1) or
                (selectedResidues[i].chain != selectedResidues[i+1].chain)
               ):
                self.ranges.append(selectedResidues[i])
                self.ranges.append(selectedResidues[i+1])
            #end if
        #end for
        self.ranges.append(selectedResidues[-1])
        NTdebug( 'Procheck ranges %d', self.ranges )
        #generate the ranges file
        path = os.path.join( self.rootPath, 'ranges')
        fp = open( path, 'w' )
        for i in range(0,len(self.ranges),2):
            fprintf( fp, 'RESIDUES %3d %2s  %3d %2s\n', self.ranges[i].resNum, self.ranges[i].chain.name,
                                                        self.ranges[i+1].resNum, self.ranges[i+1].chain.name
                   )
        #end for
        fp.close()

        #export a PDB file
        path = os.path.join( self.rootPath, self.molecule.name + '.pdb')
        #print path
        self.molecule.toPDBfile( path, convention=cing.PDB )

        # run procehck
        runProcheck  = ExecuteProgram( cingPaths.procheck_nmr,
                                       rootPath = self.rootPath,
                                       redirectOutput= True
                                    )
        runProcheck( self.molecule.name +'.pdb ranges' )
        del( runProcheck )

        # Parse results
        self.parseResult()
    #end def

    def _parseProcheckLine( self, line ):
        """
        Internal routine to parse a single line
        Return result, which is a dict type or None
        on error (i.e. too short line)
        """
    #    print ">>", line
        result = {}
        if (len(line) >= 64):
            for field,fieldDef in self.procheckDefs.iteritems():
                c1,c2,func = fieldDef
                result[ field ] = func(line[c1:c2])
            #end for
        else:
            return None
        #end if

    #    print result
        return result
    #end def

    def parseResult( self ):
        """
        Get summary

        Parse procheck .rin files and store result in procheck NTdict
        of each residue of mol

        """
        path = os.path.join( self.rootPath, sprintf('%s.sum', self.molecule.name) )
        fp = open( path, 'r' )
        if not fp:
            NTerror('gvProcheck.parseResult: %s not found', path)
        else:
            self.summary = ''.join(fp.readlines())
            fp.close()
        #end if

        for i in range(1,self.molecule.modelCount+1):
            path = os.path.join( self.rootPath, sprintf('%s_%03d.rin', self.molecule.name, i) )
            #print '> parsing >', path

            for line in AwkLike( path, minLength = 64, commentString = "#" ):
                result = self._parseProcheckLine( line.dollar[0] )
                chain   = result['chain']
                resNum  = result['resNum']
                residue = self.molecule.decodeNameTuple((cing.PDB,chain,resNum,None))
                if not residue:
                    NTerror('Procheck.parseResult: residue not found (%s,%d)', chain, resNum )
                else:

                    residue.setdefault( 'procheck', NTstruct() )
                    for field,value in result.iteritems():
                        residue.procheck.setdefault( field, NTlist() )
                        residue.procheck[field].append( value )
                    #end for
                #end if
                del( result )
            #end for
        #end for
    #end def
#end class



def procheck_old( project, ranges=None ):
    """
    Adds <Procheck> instance to molecule. Run procheck and parse result
    """
    if not project.molecule:
        NTerror('ERROR procheck: no molecule defined\n')
        return None
    #end if

    if project.molecule.has_key('procheck'):
        del(project.molecule.procheck)
    #end if

    pcheck = gvProcheck( project )
    if not pcheck: return None

    pcheck.run( ranges=ranges )
    project.molecule.procheck = pcheck

    return project.molecule.procheck
#end def

from math import sqrt
from cing.Libs.NTutils import NTfill, NTlist, printf, fprintf, sprintf, getDeepByKeys
from cing.Libs.fpconst import NaN, isNaN

#import yasaramodule as yasara

def mkYasaraMacros( project ):
    """
    Generate the Yasara macros in the moleculeDirectories.yasara dir.
    """
    if not project.molecule:
        NTerror('mkYasaraMacros: no molecule defined')
        return
    #end if
    mkYasaraByResidueMacro(project, ['procheck','gf'],
                           minValue=-3.0,maxValue=1.0,
                           reverseColorScheme=True,
                           path=project.moleculePath('yasara','gf.mcr')
                          )

    mkYasaraByResidueMacro(project, ['Qshift','backbone'],
                           minValue=0.0,maxValue=0.05,
                           reverseColorScheme=False,
                           path=project.moleculePath('yasara','Qshift.mcr')
                          )

    mkYasaraByResidueROGMacro(project,path=project.moleculePath('yasara','rog.mcr'))
#end def


def mkMacros( project ):
    """
    Generate the macros in the moleculeDirectories.macros dir.
    """
    # Only one kind thus far
    NTmessage('==> Generating Macros')
    mkYasaraMacros(project)
#end def


def _calcQshift( atmList ):
    """
    Calculate Qshift value for list of atoms
    """
    # for each model + av + heavyatom + proton + bb
    sumDeltaSq    = 0.0
    sumMeasuredSq = 0.0
    for atm in atmList:
        if atm.has_key('shiftx') and len(atm.shiftx)>0 and atm.isAssigned():
            atm.shiftx.average()
            measured = atm.shift()
            sumMeasuredSq += measured**2
            # delta with shiftx average
            sumDeltaSq = (measured-atm.shiftx.av)**2
            #print atm, measured, av
#            sumDeltaSq[project.molecule.modelCount] += (av-measured)**2
#            if not atm.isProton():
#                sumDeltaSq[project.molecule.modelCount+1] += (av-measured)**2
#            if atm.isProton():
#                #print atm, measured, av
#                sumDeltaSq[project.molecule.modelCount+2] += (av-measured)**2
#            if not atm.isBackbone():
#                sumDeltaSq[project.molecule.modelCount+3] += (av-measured)**2
        #end if
    #end for

    if sumMeasuredSq >0.0:
            Qshift=sqrt(sumDeltaSq/sumMeasuredSq)
    else:
            Qshift=NaN

    return Qshift
#end def

def calcQshift( project, tmp=None ):
    """Calculate per residue Q factors between assignment and shiftx results
    """
    if not project.molecule:
        NTdebug('calcQshift: no molecule defined')
        return None
    #end if
    NTdetail('==> calculating Q-factors for chemical shift')
    for res in project.molecule.allResidues():
        atms = res.allAtoms()
        bb = NTlist()
        heavy = NTlist()
        protons = NTlist()
        res.Qshift  = NTdict(allAtoms = None, backbone=None, heavyAtoms=None, protons=None,
                             residue = res,
                             __FORMAT__ = \
dots + ' shiftx Qfactor %(residue)s ' + dots + """
allAtoms:   %(allAtoms)6.3f
backbone:   %(backbone)6.3f
heavyAtoms: %(heavyAtoms)6.3f
protons:    %(protons)6.3f"""

                        )

        for a in atms:
            if a.isBackbone(): bb.append(a)
            if a.isProton(): protons.append(a)
            else: heavy.append(a)
        #end for

        res.Qshift.allAtoms   = _calcQshift( atms )
        res.Qshift.backbone   = _calcQshift( bb )
        res.Qshift.heavyAtoms = _calcQshift( heavy )
        res.Qshift.protons    = _calcQshift( protons )
    #end for
#end def


def mkYasaraByResidueMacro( project, keys,
                            minValue=0.0, maxValue=1.0, reverseColorScheme=False,
                            path=None
                           ):

    NTdebug('mkYasaraByResidueMacro: keys: %s, minValue: %s maxValue: %s', keys, minValue, maxValue)

    if path:
        stream = open( path, 'w')
    else:
        stream = sys.stdout
    #end if

    fprintf( stream, 'Console off\n' )
    fprintf( stream, 'ColorRes All, Gray\n' )
    fprintf( stream, 'PropRes All, -999\n' )
    if reverseColorScheme:
        fprintf( stream, 'ColorPar Property Min,red,%f\n', minValue )
        fprintf( stream, 'ColorPar Property Max,blue,%f\n', maxValue )
    else:
        fprintf( stream, 'ColorPar Property Min,blue,%f\n', minValue )
        fprintf( stream, 'ColorPar Property Max,red,%f\n', maxValue )

    for res in project.molecule.allResidues():
        value = getDeepByKeysOrAttributes( res, *keys )
#        if res.has_key(property) and res[property] != None and not isNaN(res[property]):
        if value != None and not isNaN(value):
            fprintf( stream,'PropRes Residue %d,%.4f\n', res.resNum, value)
    #end for

    fprintf( stream, 'ColorAll Property\n' )
    fprintf( stream, 'Console on\n' )

    if path:
        stream.close()
#end def

def mkYasaraByResidueROGMacro( project, path=None ):
    if path:
        stream = open( path, 'w')
#     else:
#         stream = sys.stdout
#     #end if

    if path:
        fprintf( stream, 'Console off\n' )
        fprintf( stream, 'ColorRes  All, Gray\n')
    else:
        yasara.Console('off')
        yasara.ColorRes( 'All, Gray' )


    YasaraColorDict = dict( green=240, orange=150, red=120)

    for res in project.molecule.allResidues():
        cmd = sprintf('residue %d,%s', res.resNum, YasaraColorDict[res.rogScore.colorLabel] )
        if path:
            fprintf( stream, 'ColorRes %s\n', cmd )
        else:
            yasara.ColorRes( cmd )
    #end for

    if path:
        fprintf( stream, 'Console on\n' )
        stream.close()
    else:
        yasara.Console('on')
#end def



"""
======================COPYRIGHT/LICENSE START==========================

ValidationBasic.py: Part of the CcpNmr Analysis program

Copyright (C) 2004 Wayne Boucher and Tim Stevens (University of Cambridge)

=======================================================================

This file contains reserved and/or proprietary information
belonging to the author and/or organisation holding the copyright.
It may not be used, distributed, modified, transmitted, stored,
or in any way accessed, except by members or employees of the CCPN,
and by these people only until 31 December 2005 and in accordance with
the guidelines of the CCPN.

A copy of this license can be found in ../../../license/CCPN.license.

======================COPYRIGHT/LICENSE END============================

for further information, please contact :

- CCPN website (http://www.ccpn.ac.uk/)

- email: ccpn@bioc.cam.ac.uk

- contact the authors: wb104@bioc.cam.ac.uk, tjs23@cam.ac.uk
=======================================================================

If you are using this software for academic purposes, we suggest
quoting the following references:

===========================REFERENCE START=============================
R. Fogh, J. Ionides, E. Ulrich, W. Boucher, W. Vranken, J.P. Linge, M.
Habeck, W. Rieping, T.N. Bhat, J. Westbrook, K. Henrick, G. Gilliland,
H. Berman, J. Thornton, M. Nilges, J. Markley and E. Laue (2002). The
CCPN project: An interim report on a data model for the NMR community
(Progress report). Nature Struct. Biol. 9, 416-418.

Wim F. Vranken, Wayne Boucher, Tim J. Stevens, Rasmus
H. Fogh, Anne Pajon, Miguel Llinas, Eldon L. Ulrich, John L. Markley, John
Ionides and Ernest D. Laue. The CCPN Data Model for NMR Spectroscopy:
Development of a Software Pipeline. Accepted by Proteins (2004).

===========================REFERENCE END===============================

"""

VALID_VALUE_TYPE_ATTRS = {type(0.0): 'floatValue',
                          type(1): 'intValue',
                          type('a'): 'textValue',
                          type(True): 'booleanValue'}


# # # # # # #  C I N G  E X A M P L E  # # # # # # #

def storeRogScores(ccpnEnsemble, scores, context='CING'):
   # Assumes scores in same order as residues

   keyword    = 'ROG'
   definition = 'Overall per-residue validation score for display. ROG=Red/Orange/Green'
   synonym    = 'Residue ROG Score'

   validStore = getEnsembleValidationStore(ccpnEnsemble, context,
                                           keywords=[keyword, ],
                                           definitions=[definition, ],
                                           synonyms=[synonym, ])

   residues = []
   for chain in ccpnEnsemble.sortedCoordChains():
     residues.extend(chain.sortedResidues())

   storeResidueValidations(validStore, context, keyword, residues, scores)

# # # # # # # # # # # # # # # # # # # # # # # # # # #



def getEnsembleValidationStore(ensemble, context, keywords,
                               definitions=None, synonyms=None):
  """Descrn: Get a CCPN object to store validation results for an ensemble
             in a given program context. Requires a list of keywords which will
             be used in this context. Allows optional lists of definitions and
             user-friendly synonyms for these keywords.
     Inputs: MolStructure.StructureEnsemble, Word, List of Words,
             List of Lines, List of Words
     Output: StructureValidation.StructureValidationStore
  """

  memopsRoot = ensemble.root
  eid = '%s_%s' % (context, ensemble.guid)
  validStore = ensemble.findFirstStructureValidationStore(name=eid)

  if validStore is None:
    validStore = memopsRoot.newStructureValidationStore(name=eid,
                                      structureEnsemble=ensemble)

  validStore.nmrProject = memopsRoot.currentNmrProject

  keywordStore = memopsRoot.findFirstKeywordDefinitionStore(context=context)

  if not keywordStore:
    keywordStore = memopsRoot.newKeywordDefinitionStore(context=context)

  for i, keyword in enumerate(keywords):
    keywordDefinition = keywordStore.findFirstKeywordDefinition(keyword=keyword)

    if not keywordDefinition:
      keywordDefinition = keywordStore.newKeywordDefinition(keyword=keyword)

    if definitions and (i < len(definitions)):
      keywordDefinition.explanation = definitions[i]

    if synonyms and (i < len(synonyms)):
      keywordDefinition.name = synonyms[i]

  return validStore


def getValidationObjects(validStore, className, context, keyword):
  """Descrn: Find a given class of validation objects in a validation store
             in a given (program) context, with a given keyword.
     Inputs: StructureValidation.StructureValidationStore, Word, Word, Word
     Output: List of StructureValidation.Validations
  """
  return validStore.findAllValidationResults(context=context,
                                             keyword=keyword,
                                             className=className)


def replaceValidationObjects(validStore, className, keyword, context, dataList):
  """Descrn: Store validation data as CCPN validation objects,
             overwriting all previous records of such information
             in the validation store object. Finds a given class of
             validation objects a given keyword in a given context.
             The input data list is a 2-tuple containing a list of the
             CCPN objects validated and the value associated with that
             validation. Note that the validated CCPN object types must
             match the type required by the validation object className.
             *NOTE* this is a slow function and should often be replaced
             with a class-specific equivalent.
     Inputs: StructureValidation.StructureValidationStore, Word, Word, Word,
             List of 2-Tuples of (List of CCPN objects, )
     Output: None
  """

  for validObj in getValidationObjects(validStore, className, keyword, context):
    validObj.delete()

  newObject = getattr(validStore, 'new%s' % className)

  validatedObjAttr = None

  for validatedObjects, value in dataList:
    validObj = newObject(context=context, keyword=keyword)

    if not validatedObjAttr:
      for role in validObj.metaclass.roles:
        if role.locard == 0:
          validatedObjAttr = role.name

    if validatedObjAttr:
      setattr(validObj, validatedObjAttr, validatedObjects)

    valueAttr = VALID_VALUE_TYPE_ATTRS.get(type(value), 'textValue')
    setattr(validObj, valueAttr, value)


def getResidueValidation(validStore, residue, context, keyword):
  """Descrn: Get any existing residue validation results from a CCPN
             validation store which have the given keywords in the
             given (program) context.
             *NOTE* This function may be quicker than using the generic
             getValidationObjects() because the link is queried from the
             validated object, not the validation store, which often
             has fewer total validation objects.
     Inputs: StructureValidation.StructureValidationStore,
             MolStructure.Residue, Word, Word
     Output: StructureValidation.ResidueValidation
  """

  # Define data model call to find exting result
  findValidation = residue.findFirstResidueValidation

  validObj = findValidation(structureValidationStore=validStore,
                            context=context, keyword=keyword)

  return validObj


def storeResidueValidations(validStore, context, keyword, residues, scores):
  """Descrn: Store the per-residue scores for a an ensemble within
             CCPN validation objects.
             *NOTE* This function may be quicker than using the generic
             replaceValidationObjects() because it is class specifc
     Inputs: StructureValidation.StructureValidationStore,
             List of MolStructure.Residues, List if Floats
     Output: List of StructureValidation.ResidueValidations
  """

  validObjs = []

  # Define data model call for new result
  newValidation = validStore.newResidueValidation

  for i, residue in enumerate(residues):

    score = scores[i]

    # Find any existing residue validation objects
    validObj = getResidueValidation(validStore, residue, context, keyword)

    # Validated object(s) must be in a list
    residueObjs = [residue, ]

    # Make a new validation object if none was found
    if not validObj:
      validObj = newValidation(context=context, keyword=keyword,
                               residues=residueObjs)

    # Set value of the score
    validObj.floatValue = score

    validObjs.append(validObj)

  return validObjs


def storeValidationInCcpn( project, residue ):
    """
    Store ROG result in ccpn
    Return ccpn residueValidation obj on succes or None on error
    """

    print '>',residue.ccpn.className; residue.ccpn
    context = 'CING'
    keyword = 'ROGscore'

    ccpnMolSystem = project.molecule.ccpn
    ccpnEnsemble  = ccpnMolSystem.findFirstStructureEnsemble()

    if not project.has_key('ccpnValidationStore'):

        project.ccpnValidationStore = getEnsembleValidationStore(ensemble = ccpnEnsemble,
                                                                 context  = context,
                                                                 keywords = [keyword]
                                                                )
    #end if

    ccpnEnsembleResidue = None
    for ccpnChain in ccpnEnsemble.coordChains:
      ccpnEnsembleResidue = ccpnChain.findFirstResidue(residue=residue.ccpn)
      if ccpnEnsembleResidue:
        break

    if not ccpnEnsembleResidue:
      return

    # Find any existing residue validation objects
    validObj = getResidueValidation(project.ccpnValidationStore, ccpnEnsembleResidue, context=context, keyword=keyword)

    # Validated object(s) must be in a list
    residueObjs = [ccpnEnsembleResidue, ]

    # Make a new validation object if none was found
    if not validObj:
      newValidation = project.ccpnValidationStore.newResidueValidation
      validObj = newValidation(context=context, keyword=keyword,
                               residues=residueObjs)

    # Set value of the score
    validObj.textValue = residue.rogScore.colorLabel
    validObj.details   = '\n'.join(residue.rogScore.commentList)

    return validObj
#end def

def exportValidation2ccpn( project ):

    for residue in project.molecule.allResidues():
        if not storeValidationInCcpn( project, residue):
            print 'bummer'


# register the functions
methods  = [(procheck_old, None),
            (mkYasaraByResidueROGMacro,None),
            (mkYasaraByResidueMacro,None),
            (mkYasaraMacros,None),
            (mkMacros,None),
            (exportValidation2ccpn, None)

           ]
#saves    = []
restores = [(calcQshift,None)
           ]
#exports  = []
