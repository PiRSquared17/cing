"""
Adds validation methods
----------------  Methods  ----------------


validate(   )
checkForSaltbridges( toFile = False )


----------------  Attributes generated  ----------------


Molecule:
    rmsd: RmsdResult object containing positional rmsd values



Residue:
    rmsd: RmsdResult object containing positional rmsd values

    distanceRestraints: NTlist instance containing all distance restraints of this residue, sorted on violation count over 0.3A.

    saltbridges: NTlist instances of (potential) saltbridges

Atom:
    validateAssignment: NTlist instance with potential warnings/errors concerning the assignment of this atom

    shiftx, shiftx.av, shiftx.sd: NTlist instance with shiftx predictions, average and sd
"""
from cing import CHARS_PER_LINE_OF_PROGRESS
from cing import NaNstring
from cing import cingPythonCingDir
from cing import cingRoot
from cing.Libs.Imagery import convert2Web
from cing.Libs.NTplot import NTplot
from cing.Libs.NTplot import NTplotSet
from cing.Libs.NTplot import boxAttributes
from cing.Libs.NTplot import lineAttributes
from cing.Libs.NTplot import plusPoint
from cing.Libs.NTutils import NTcodeerror
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTdict
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTfill
from cing.Libs.NTutils import NTlimit
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTmessageNoEOL
from cing.Libs.NTutils import NTsort
from cing.Libs.NTutils import NTvalue
from cing.Libs.NTutils import NTwarning
from cing.Libs.NTutils import formatList
from cing.Libs.NTutils import fprintf
from cing.Libs.NTutils import getDeepByKeys
from cing.Libs.NTutils import getDeepByKeysOrDefault
from cing.Libs.NTutils import list2asci
from cing.Libs.NTutils import removedir
from cing.Libs.NTutils import sprintf
from cing.Libs.NTutils import val2Str
from cing.Libs.cython.superpose import NTcVector #@UnresolvedImport
from cing.Libs.fpconst import NaN
from cing.Libs.peirceTest import peirceTest
from cing.PluginCode.Whatif import C12CHK_STR
from cing.PluginCode.Whatif import RAMCHK_STR
from cing.PluginCode.Whatif import VALUE_LIST_STR
from cing.PluginCode.Whatif import WHATIF_STR
from cing.PluginCode.Whatif import criticizeByWhatif
from cing.PluginCode.Whatif import histJaninBySsAndCombinedResType
from cing.PluginCode.Whatif import histJaninBySsAndResType
from cing.PluginCode.Whatif import histRamaBySsAndCombinedResType
from cing.PluginCode.Whatif import histRamaBySsAndResType
from cing.PluginCode.Whatif import wiPlotList
from cing.core.classes import AtomList
from cing.core.classes import HTMLfile
from cing.core.classes import htmlObjects
from cing.core.constants import COLOR_ORANGE
from cing.core.constants import PDB
from cing.core.molecule import Residue
from cing.core.molecule import dots
from cing.core.parameters import cingPaths
from cing.core.parameters import htmlDirectories
from cing.core.parameters import moleculeDirectories
import cing
import math
import os
import shelve
import shutil
import sys

NotAvailableText = 'Not available'
OpenText         = 'Open'
#def printm( fps, fmt, *args ):
#    """
#    Print to list of filepointers (fps) using format and args.
#    Skip element of fp if it is None
#    """
#    for fp in fps:
#        if fp != None:
#            fprintf( fp, fmt, *args )
#        #end if
#    #end for
##end def

dbaseFileName = os.path.join( cingPythonCingDir,'PluginCode','data', 'phipsi_wi_db.dat' )
dbase = shelve.open( dbaseFileName )
#        histCombined               = dbase[ 'histCombined' ]
#histRamaBySsAndResType         = dbase[ 'histRamaBySsAndResType' ]
#    histBySsAndCombinedResType = dbase[ 'histBySsAndCombinedResType' ]
dbase.close()

def setupValidation( project, ranges=None, doProcheck=True, doWhatif=True ):
    """
    Run the initial validation calculations or programs.
    returns None on success or True on failure.
    """


    validateDihedrals(  project  )
    validateModels(     project  )

    project.predictWithShiftx()
    project.validateAssignments(toFile=True)
    project.checkForSaltbridges(toFile=True)
    project.validateRestraints( toFile=True)
    project.calculateRmsd(      ranges=ranges)

    if cingPaths.whatif == 'PLEASE_ADD_EXECUTABLE_HERE':
        doWhatif = False

    if cingPaths.procheck_nmr == 'PLEASE_ADD_EXECUTABLE_HERE':
        doProcheck = False

    if not doWhatif:
        NTmessage('Skipping because not doWhatif')
    else:
        project.runWhatif()

    if not doProcheck:
        NTmessage('Skipping because not doProcheck')
    else:
        project.procheck( ranges=ranges)
    project.criticizeByAll()
    project.summary(doWhatif, doProcheck)
#end def

def criticizeByAll( project ):
    project.criticize()
    criticizeByWhatif( project )

def summary( project, doWhatif, doProcheck ):
    if not project.molecule:
        NTerror('Strange, there was no molecule in this project')
        return

    fname = project.path(project.molecule.name, project.moleculeDirectories.analysis,'summary.txt')
    fp = open( fname, 'w' )
    NTmessage( '==> summary, output to %s', fname)

    msg = sprintf( '%s\n', project.format() )


    msg += sprintf( '%s\n', project.molecule.format() )
    if project.molecule.has_key('rmsd' ):
        msg += sprintf( '\n%s\n', project.molecule.rmsd.format() )
    for drl in project.distances + project.dihedrals + project.rdcs:
        msg += sprintf( '\n%s\n', drl.format() )

    level = 'residue'
    cStringList = [ 'green', 'orange', 'red' ]
    c = NTlist( 0, 0, 0 ) # Counts for green, orange and red.
    cL = NTlist( NTlist(), NTlist(), NTlist() )
    for residue in project.molecule.allResidues():
        if residue.rogScore.isRed():
            c[2] += 1
            cL[2].append( residue )
        elif residue.rogScore.isOrange():
            c[1] += 1
            cL[1].append( residue )
        else:
            c[0] += 1
            cL[0].append( residue )
#    cAll = c.sum()*1.0
    total = reduce(lambda x, y: x+y+0.0, c) # total expressed as a float because of 0.0
    if total <= 0:
        msgTmp = 'Funny, no residues encountered'
        NTwarning(msgTmp)
        msg += msgTmp
    else:
        p = map( lambda x: 100*x/total, c)
        msg += '----------- CING %s analysis -----------' % level
        msg += """
Color  Count (Percentage)
*------*-----*-----------
Green:   %3d (%3.0f)
Orange:  %3d (%3.0f)
Red:     %3d (%3.0f)
       -----------
Total    %3d (100)\n""" % ( c[0], p[0], c[1], p[1], c[2], p[2], total )
# To result in:
#Green:   28 ( 28%)
#Orange:  37 ( 37%)
#Red:     35 ( 35%)
#       -----------
#Total   100 (100%)
        # by request of Nadia write out the actual residues

        idx = 0
        for residueList in cL:
            color = cStringList[idx]
            idx += 1
            # Map residues to a string representation 'en masse'
            residueListStr = map( Residue.toString, residueList)
            tmpStr = 'Residues colored %6s: [' % color
            tmpStr += ' '.join( residueListStr )
            tmpStr += ']\n'
            msg += tmpStr

    wiSummary = getDeepByKeys(project.molecule, 'wiSummary') # Hacked bexause should be another procheck level inbetween.
    if wiSummary:
        msg += '\n' + wiSummary
    else:
        if doWhatif:
            NTerror('Failed to find whatif summary ')

    pcSummary = getDeepByKeys(project.molecule, 'pcSummary') # Hacked bexause should be another procheck level inbetween.
    if pcSummary:
        msg += '\n' + pcSummary +'\nThe above summary of ProcheckNMR might be incomplete'
    else:
        if doProcheck:
            NTerror('Failed to find procheck summary')

    fprintf( fp, msg )
    fp.close()
#end def


class RmsdResult( NTdict ):
    """Class to store rmsd results
    """
    def __init__(self, modelList, ranges, comment='' ):
        NTdict.__init__( self,
                         __CLASS__       = 'RmsdResult',
                         backbone        = NTfill(0.0, len(modelList)),
                         backboneCount   = 0,
                         backboneAverage = NTvalue( 0.0, 0.0, fmt='%5.3f (+- %5.3f)' ),
                         heavyAtoms      = NTfill(0.0, len(modelList)),
                         heavyAtomsCount = 0,
                         heavyAtomsAverage = NTvalue( 0.0, 0.0, fmt='%5.3f (+- %5.3f)' ),
                         models          = modelList,
                         closestToMean   = 0,
                         ranges          = ranges,
                         comment         = comment
                       )
    #end def

    def _closest(self):
        """Internal routine to calculate the model closest to mean
        """
        c = zip(self.heavyAtoms, self.models)
        c.sort()
        self.closestToMean = c[0][1]
    #end def

    def _average(self):
        """Calculate the averages
        """
        self.backboneAverage.value, self.backboneAverage.error, _n = self.backbone.average()
        self.heavyAtomsAverage.value, self.heavyAtomsAverage.error, _n = self.heavyAtoms.average()
    #end def

    def __str__(self):
        return sprintf('<RmsdResult %s>', self.comment)

    def format(self):
        return sprintf('%s %s %s\n' +\
                       'backboneAverage:    %s\n'  +\
                       'heavyAtomsAverage:  %s\n'  +\
                       'models:             %s\n' +\
                       'backbone:          [%s]\n' +\
                       'heavyAtoms:        [%s]\n' +\
                       'closestToMean:      model %d',
                       dots, self, dots,
                       str(self.backboneAverage),
                       str(self.heavyAtomsAverage),
                       self.models.format('%5d '),
                       self.backbone.format(fmt='%5.3f '),
                       self.heavyAtoms.format(fmt='%5.3f '),
                       self.closestToMean
                      )
    #end def
#end class


def calculateRmsd( project, ranges=None, models = None   ):
    """
    Calculate the positional rmsd's. Store in rmsd attributes of molecule and residues
    return rmsd result of molecule, or None on error

    """

    if not project.molecule:
        NTerror('Error calculateRmsd: undefined molecule\n')
        return None
    #end if

    if project.molecule.modelCount == 0:
        NTerror('Error calculateRmsd: no coordinates for %s\n', project.molecule)
        return None
    #end if

    selectedResidues = project.molecule.ranges2list( ranges )
    selectedModels   = project.molecule.models2list( models )

    project.molecule.rmsd = RmsdResult( selectedModels, selectedResidues, comment='Residues ' + list2asci( selectedResidues.zap('resNum')) )
    for res in project.molecule.allResidues():
        res.rmsd = RmsdResult( selectedModels,  NTlist( res ), comment = res.name )
    #end for

    NTmessage("==> Calculating rmsd's ")

    num = 0 # number of evaluated models (does not have to coincinde with model
            # since we may supply an external list
    shownWarningCount1 = 0
#            shownWarningCount2 = 0
    for model in selectedModels:
        NTmessageNoEOL(".")
        if model % 80 == 0 and model != 0:
            NTmessageNoEOL("\n")
        project.molecule.rmsd.backbone[num]   = 0.0
        project.molecule.rmsd.backboneCount   = 0
        project.molecule.rmsd.heavyAtoms[num] = 0.0
        project.molecule.rmsd.heavyAtomsCount = 0

        for res in project.molecule.allResidues():
            res.rmsd.backbone[num]   = 0.0
            res.rmsd.backboneCount   = 0
            res.rmsd.heavyAtoms[num] = 0.0
            res.rmsd.heavyAtomsCount = 0
            # calculate rmsd over backbone atms for this residue
            for atm in res.allAtoms():
                d=None
                if atm.meanCoordinate:
                    d=0.0
                    tmp0 = atm.coordinates[model][0]-atm.meanCoordinate[0]
                    tmp1 = atm.coordinates[model][0]-atm.meanCoordinate[0]
                    tmp2 = atm.coordinates[model][0]-atm.meanCoordinate[0]
                    d += tmp0*tmp0
                    d += tmp1*tmp1
                    d += tmp2*tmp2

#                    for i in ['x','y','z']: #JFD speed this up by unlooping if needed.
#                        tmp = atm.coordinates[modelId][i]-atm.meanCoordinate[i]
#                        d += tmp*tmp
                    #end for
                #end if

                # rmsd over backbone atms for this residue
                if atm.hasProperties('backbone','notproton'):
                    if d==None:
                        if shownWarningCount1 < 10:
                            NTerror('Error calculateRmsd: expected coordinates1 for atom %s', atm)
                        elif shownWarningCount1 == 10:
                            NTerror('and so on')
                        shownWarningCount1 += 1
                    else:
                        res.rmsd.backbone[num] += d
                        res.rmsd.backboneCount += 1
                    #end if
                #endif

                # rmsd over all atms for this residue
                if atm.hasProperties('notproton'):
                    if d==None:
#                        shownWarningCount2 += 1
#                        if shownWarningCount2 < 10:
#                            NTerror('Error calculateRmsd: expected coordinates2 for atom %s\n', atm)
#                        elif shownWarningCount2 == 10:
#                            NTerror('and so on\n')
                        pass
                    else:
                        res.rmsd.heavyAtoms[num] += d
                        res.rmsd.heavyAtomsCount += 1
                    #end if
                #endif
            #end for

            # sum for the rmsd of selected residues
            if res in selectedResidues:
                project.molecule.rmsd.backbone[num]   += res.rmsd.backbone[num]
                project.molecule.rmsd.backboneCount   += res.rmsd.backboneCount
                project.molecule.rmsd.heavyAtoms[num] += res.rmsd.heavyAtoms[num]
                project.molecule.rmsd.heavyAtomsCount += res.rmsd.heavyAtomsCount
            #end if

            # calculate rmsd for the model of this residue
            res.rmsd.backbone[num]   = math.sqrt(res.rmsd.backbone[num]/max(res.rmsd.backboneCount,1))
            res.rmsd.heavyAtoms[num] = math.sqrt(res.rmsd.heavyAtoms[num]/max(res.rmsd.heavyAtomsCount,1))
        #end for

        # rmsd of selected residues for this model
        project.molecule.rmsd.backbone[num]   = math.sqrt(project.molecule.rmsd.backbone[num]/max(project.molecule.rmsd.backboneCount,1))
        project.molecule.rmsd.heavyAtoms[num] = math.sqrt(project.molecule.rmsd.heavyAtoms[num]/max(project.molecule.rmsd.heavyAtomsCount,1))

        # Increment the evaluated number of models
        num += 1
    #end for
    NTmessage("")

    if shownWarningCount1 > 10:
        NTerror('Error calculateRmsd: expected coordinates1 for '+`shownWarningCount1`+' atoms\n')
#            if shownWarningCount2 > 10:
#                NTerror('Error calculateRmsd: expected coordinates2 for '+`shownWarningCount2`+' atoms')

    # get the closest to mean models and averages
    for res in project.molecule.allResidues():
        res.rmsd._closest()
        res.rmsd._average()
    #end for
    project.molecule.rmsd._closest()
    project.molecule.rmsd._average()

    NTdebug(" done\n")

    return project.molecule.rmsd
#end def

def validateRestraints( project, toFile = True)   :
    """
    Calculate rmsd's and violation on restraints
    """

#    fps = []
#    fps.append( sys.stdout )

    if not project.molecule: return

    msg = ""
    msg += sprintf('%s\n', project.format() )

    # distances and dihedrals
    for res in project.molecule.allResidues():
        res.distanceRestraints = NTlist()
        res.dihedralRestraints = NTlist()
    #end for

    # distances
    for drl in project.distances:
        drl.analyze()
        msg += sprintf( '%s\n', drl.format())
        drl.sort('violMax').reverse()
        msg += sprintf( '%s Sorted on Maximum Violations %s\n', dots, dots)
        msg += sprintf( '%s\n', formatList( drl[0:min(len(drl),30)] ) )

        drl.sort('violCount3').reverse()
        # omit restraints that have a violation less than cut off.  NEW FEATURE REQUEST
        msg += sprintf( '%s Sorted on Violations > 0.3 A %s\n', dots, dots)
        theList = drl[0:min(len(drl),30)]
#        NTdebug("Found list: " + `theList`)
        msg += sprintf( '%s\n', formatList( theList ) )

        # Sort restraints on a per-residue basis
        for restraint in drl:
            for atm1,atm2 in restraint.atomPairs:
                atm1.residue.distanceRestraints.add( restraint ) #AWSS
                atm2.residue.distanceRestraints.add( restraint ) #AWSS
            #end for
        #end for
    #end for

    # dihedrals
    for drl in project.dihedrals:
        drl.analyze()
        msg += sprintf( '%s\n', drl.format())
        drl.sort('violMax').reverse()
        msg += sprintf( '%s Sorted on Maximum Violations %s\n', dots, dots)
        msg += sprintf( '%s\n', formatList( drl[0:min(len(drl),30)] ) )

        drl.sort('violCount3').reverse()
        msg += sprintf( '%s Sorted on Violations > 3 degree %s\n', dots, dots)
        msg += sprintf( '%s\n', formatList( drl[0:min(len(drl),30)] ) )

        # sort the restraint on a per residue basis
        for restraint in drl:
            restraint.atoms[2].residue.dihedralRestraints.add( restraint ) #AWSS
        #end for
    #end for

    # Process the per residue restraints data
    msg += sprintf( '%s Per residue scores %s\n', dots, dots )
    count = 0
    for res in project.molecule.allResidues():

        if len(res.distanceRestraints):
            # Sort on violation count
            NTsort(res.distanceRestraints, 'violCount3', inplace=True )
            res.distanceRestraints.reverse()

            # Calculate rmsd of restraints per residue
            sumsq = 0.0
            n = 0
            for d in res.distanceRestraints:
                sumsq = d.violations.sumsq( sumsq )
                n += len(d.violations)
            #end for
            if n == 0:
                NTwarning('No DRs so no rmsd')
            else:
                res.distanceRestraints.rmsd = math.sqrt(sumsq/n)
            res.distanceRestraints.violCount1 = res.distanceRestraints.zap('violCount1').sum()
            res.distanceRestraints.violCount3 = res.distanceRestraints.zap('violCount3').sum()
            res.distanceRestraints.violCount5 = res.distanceRestraints.zap('violCount5').sum()
        else:
            res.distanceRestraints.rmsd = 0.0
            res.distanceRestraints.violCount1 = 0
            res.distanceRestraints.violCount3 = 0
            res.distanceRestraints.violCount5 = 0
        #end if

        # print every 10 lines
        if not count % 30:
            msg += sprintf('%-18s %15s  %15s   %s\n', '--- RESIDUE ---', '--- PHI ---', '--- PSI ---', '-- dist 0.1A 0.3A 0.5A   rmsd --')
        #end if
        if res.has_key('PHI'):
            phi = NTvalue( res.PHI.cav, res.PHI.cv, fmt='%7.1f %7.2f' )
        else:
            phi = NTvalue( '-', '-', fmt='%7s %7s' )
        #end if
        if res.has_key('PSI'):
            psi = NTvalue( res.PSI.cav, res.PSI.cv, fmt='%7.1f %7.2f' )
        else:
            psi = NTvalue( '-', '-', fmt='%7s %7s' )
        #end if
        try:
            msg += sprintf( '%-18s %-15s  %-15s      %3d %4d %4d %4d  %6.3f\n',
                 res, phi, psi,
                 len(res.distanceRestraints),
                 res.distanceRestraints.violCount1,
                 res.distanceRestraints.violCount3,
                 res.distanceRestraints.violCount5,
                 res.distanceRestraints.rmsd
                   )
        except:
            NTerror("No coordinates for residue %s\n", res)
        count += 1
    #end for
    NTdebug(msg)
    if toFile:
        #project.mkdir(project.directories.analysis, project.molecule.name)
        fname = project.path(project.molecule.name, project.moleculeDirectories.analysis,'restraints.txt')
        fp = open( fname, 'w' )
        NTmessage( '==> validateRestraints, output to %s', fname)
        fprintf(fp, msg)
    #end if
#end def

def checkForSaltbridges( project, cutoff = 5, toFile=False)   :
    """
    Routine to analyze all potential saltbridges involving E,D,R,K and H residues.
    Initiates an NTlist instances as saltbridges attribute for all residues.

    Returns a NTlist with saltbridge summaries.

    Optionally print output to file in analysis directory of project.
    """
    if toFile:
        #project.mkdir(project.directories.analysis, project.molecule.name)
        fname = project.path(project.molecule.name, project.moleculeDirectories.analysis,'saltbridges.txt')
        fp = open( fname, 'w' )
        NTmessage( '==> checkSaltbridges, output to %s', fname)
    else:
        fp = None
    #end if

    if toFile:
        fprintf( fp, '%s\n', project.molecule.format() )
    NTmessage(     '%s', project.molecule.format() )

    residues1 = project.molecule.residuesWithProperties('E') + \
                project.molecule.residuesWithProperties('D')

    residues2 = project.molecule.residuesWithProperties('R') + \
                project.molecule.residuesWithProperties('K') + \
                project.molecule.residuesWithProperties('H')

    # initialize
    for res in project.molecule.allResidues():
        res.saltbridges = NTlist()
    #end for

    s = None
    result = NTlist()
    for res1 in residues1:
        for res2 in residues2:
            #print '>>', res1, res2
            s = validateSaltbridge(res1,res2)
            if s:
                if (s.types[4][1] <= cutoff):    # less then cutoff 'not observed'
                    if toFile:
                        fprintf(fp, '%s\n', s.format() )
#                    NTdebug(    '%s\n', s.format() )
                    res1.saltbridges.append( s )
                    res2.saltbridges.append( s )
                    result.append( s )
                #end if
            #end if
        #end for
    #end for

    if s:
        if toFile:
            fprintf( fp, '%s\n', s.comment )
        NTdebug(     '%s\n', s.comment )
    #end if

    if toFile:
        fp.close()
    sys.stdout.flush()
    #end if

    return result
#end def

def validateSaltbridge( residue1, residue2 ):
    """
    ValidateSaltbridge( residue1, residue2 )

    Validate presence of saltbridge, CC-Bridge, NO-bridge, or ion-pair beteween residue1 and residue2
    Ref: Kumar, S. and Nussinov, R. Biophys. J. 83, 1595-1612 (2002)

    residue1, residue2: Residue instances of type E,D,H,K,R

    Arbitrarily set the criteria for ion-pair r,theta to be within 2 sd of average,
    else set type to none.

    Returns summary NTdict or None on error
    """

    # Definitions of the centroids according to the paper
    centroids = NTdict(
        E = ['OE1','OE2'],
        D = ['OD1','OD2'],
        H = ['CG','ND1','CD2','CE1', 'NE2'],
        K = ['NZ'],
        R = ['NE','CZ','NH1','NH2']
    )
    donorAcceptor = NTdict(
        E = ['OE1','OE2'],
        D = ['OD1','OD2'],
        H = ['ND1','NE2'],
        K = ['NZ'],
        R = ['NE','NH1','NH2']
    )

    if residue1 == None:
        NTerror('validateSaltbridge: undefined residue1\n')
        return None
    #end if
    if residue2 == None:
        NTerror('validateSaltbridge: undefined residue2\n')
        return None
    #end if

    modelCount = residue1.chain.molecule.modelCount
    if modelCount == 0:
        NTerror('validateSaltbridge: no structure models\n')
        return None
    #end if

    if residue1.db.shortName not in ['E','D','H','K','R']:
        NTerror('validateSaltbridge: invalid residue %s, should be E,D,H,K, or R', residue1)
        return None
    #end if


    if residue2.db.shortName not in ['E','D','H','K','R']:
        NTerror('validateSaltbridge: invalid residue %s, should be E,D,H,K, or R', residue2)
        return None
    #end if

    for residue in [residue1, residue2]:
        for atmName in centroids[residue.db.shortName]:
            atm = residue[atmName]
            if len(atm.coordinates) == 0:
                NTerror('validateSaltbridge: no coordinates for atom %s', atm)
                return None
            #end if
        #end for
    #end for

    # get the vectors c1, c1a, c2, c2a for each model and compute the result
    result  = NTlist()
    summary = NTdict(
        residue1 = residue1,
        residue2 = residue2,
        comment  = """
Ref: Kumar, S. and Nussinov, R. Biophys. J. 83, 1595-1612 (2002)
Arbitrarily set the criteria for ion-pair (r,theta) to be within
2 sd ~ 2*(1.2A,39) of average (7.6A,118), else set type to 'not observed'.
""",
        __FORMAT__ = '------------------ Saltbridge ------------------\n' +\
                     'residues:          %(residue1)s %(residue2)s\n' +\
                     'r (av,sd,min,max): (%(rAv).1f, %(rSd).1f, %(min).1f, %(max).1f)\n' +\
                     'theta (av,sd):     (%(thetaAv).1f, %(thetaSd).1f)\n' +\
                     'types:             %(types)s'
    )
    types = ['saltbridge','C-C bridge','N-O bridge','ion pair','not observed']
    counts = NTfill(0,5)

    # get the vectors c1, c1a, c2, c2a for each model and compute the result
    for model in range( modelCount ):
        #c1 is geometric mean of centroid atms
        c1 = NTcVector(0,0,0)
        for atmName in centroids[residue1.db.shortName]:
            atm = residue1[atmName]
            c1 += atm.coordinates[model].e
        #end for
        # not yet: c1 /= len(centroids[residue1.db.shortName])
        for j in range(3):
            c1[j] /= len(centroids[residue1.db.shortName])

        try:
            c1a = residue1['CA'].coordinates[model].e
        except:
            break

        #c2 is geometric mean of centroid atms
        c2 = NTcVector(0,0,0)
        for atmName in centroids[residue2.db.shortName]:
            atm = residue2[atmName]
            c2 += atm.coordinates[model].e
        #end for
        # not yet: c2 /= len(centroids[residue2.db.shortName])
        for j in range(3):
            c2[j] /= len(centroids[residue2.db.shortName])

        c2a = residue2['CA'].coordinates[model].e

        #print '>>', c1, c2
        r = c2-c1
        rl = r.length()
        theta = 180.0 - (c1-c1a).angle(c2-c2a)

        # Check criteria
        criterium1 = (rl < 4.0)
        count = 0
        for atmName1 in donorAcceptor[residue1.db.shortName]:
            atm1 = residue1[atmName1]
            for atmName2 in donorAcceptor[residue2.db.shortName]:
                atm2 = residue2[atmName2]
                d = (atm1.coordinates[model].e-atm2.coordinates[model].e).length()
                if d < 4.0:
                    count += 1
                #print '>', atm1,atm2,d,count

        criterium2 = count>0
        if   criterium1 and criterium2:
            type = 0
        elif criterium1 and not criterium2:
            type = 1
        elif not criterium1 and criterium2:
            type = 2
        elif not criterium1 and not criterium2 and rl < 7.6+2.1*2 and 118-39*2< theta and theta < 118+39*2:
            type = 3
        else:
            type = 4

        counts[type] += 1

        data = NTdict(
            residue1   = residue1,
            residue2   = residue2,
            model      = model,
            r          = rl,
            theta      = theta,
            criterium1 = criterium1,
            criterium2 = criterium2,
            type       = types[type],

            __FORMAT__ = '--- saltbridge analysis %(residue1)s-%(residue2)s ---\n' +\
                         'model: %(model)d\n' +\
                         'type:  %(type)s\n' +\
                         'r (A): %(r).1f\n' +\
                         'theta: %(theta).1f\n' +\
                         'criteria: %(criterium1)s, %(criterium2)s\n'
        )


        result.append(data)
    #end for

    summary.result = result
    summary.rAv, summary.rSd, summary.modelCount = result.zap('r').average()
    summary.min   = min( result.zap('r') )
    summary.max   = max( result.zap('r') )
    summary.thetaAv, summary.thetaSd, _n = result.zap('theta').average()
    summary.types = zip( types,counts)
    if not summary.rSd:
        summary.rSd = -999.9 # wait until we have a standard approach for dealing with Nans. TODO:
    if not summary.thetaSd:
        summary.thetaSd = -999.9 # wait until we have a standard approach for dealing with Nans. TODO:
    return summary
#end def
Residue.checkSaltbridge = validateSaltbridge

#==============================================================================
def checkHbond( donorH, acceptor,
                minAngle = 100.0, maxAngle=225.0, maxDistance = 3.0,
                fraction = 0.5
              ):
    """
    Check for presence of H-bond between donorH proton and acceptor.

    H-bond is present for a particular conformer if:
        heavyAtom-donorH-acceptor angle between minAngle and maxAngle
        and adonorH-acceptor distance < maxDistance.

    H-bond is accepted when H-bond is present in at least fraction of
    the models in the ensemble.
    """

    if not donorH or not donorH.isProton():
        NTerror('checkHbond: non-proton donor %s\n', donorH )
        return None
    #end if

    if not acceptor:
        NTerror('checkHbond: undefined acceptor %s\n', donorH )
        return None
    #end if

    result = NTdict( __FORMAT__ = '=== H-bond %(donor)s - %(donorH)s - %(acceptor)s ===\n' +\
                                    'accepted: %(accepted)s (%(acceptedCount)d out of %(modelCount)d)\n' +\
                                    'distance: %(distance).2f  +- %(distanceSD).2f\n' +\
                                    'angle:    %(angle).1f  cv: %(angleCV).2f\n'
                     )
    result.donor         = donorH.topology()[0]
    result.donorH        = donorH
    result.acceptor      = acceptor
    result.minAngle      = minAngle
    result.maxAngle      = maxAngle
    result.maxDistance   = maxDistance
    result.fraction      = fraction
    result.distance      = NaN
    result.distanceSD    = 0.0
    result.angle         = NaN
    result.angleCV       = 0.0
    result.accepted      = False

    result.av, result.sd, _mind, _maxd = donorH.distance( acceptor )
    result.cav, result.cv = donorH.angle( result.donor, acceptor,
                                          radians=False
                                        )

    result.data           = map( None, donorH.distances, donorH.angles )
    result.acceptedModels = NTlist()
    result.acceptedCount  = 0
    result.modelCount     = 0
    distances             = NTlist()    # make copies to calculate averages of accepted
    angles                = NTlist()    # make copies to calculate averages of accepted
    for d,a in result.data:
        if d <= maxDistance and a >= minAngle and a <= maxAngle:
            result.acceptedModels.append( (result.modelCount, d, a ) )
            result.acceptedCount += 1
            distances.append( d )
            angles.append( a )
        #end if
        result.modelCount += 1
    #end for
    if len(distances) > 0: result.distance, result.distanceSD, _n = distances.average()
    if len(angles) > 0: result.angle, result.angleCV, _n = angles.cAverage()
    result.accepted = ((float(len( result.acceptedModels)) / float(len( result.data ))) >= fraction)
    del distances
    del angles
    return result
#end def
cing.Atom.checkHbond = checkHbond


MULTIPLE_ASSIGNMENT             = 'MULTIPLE_ASSIGNMENT'
MISSING_PROTON_ASSIGNMENT       = 'MISSING_PROTON_ASSIGNMENT'
MISSING_HEAVY_ATOM_ASSIGNMENT   = 'MISSING_HEAVY_ATOM_ASSIGNMENT'
INVALID_STEREO_ASSIGNMENT       = 'INVALID_STEREO_ASSIGNMENT'

def validateAssignments( project, toFile = True   ):
    """
    Validate the assignments; check for potential problems and inconsistencies
    Add's NTlist instance with strings of warning description to each atom as
    validateAssignment attribute

    return a NTlist of atoms with errors.
    Generate output in moleculeName/Cing/validateAssignments.txt if toFile is True.

    return None on code error.
    """
    NTmessage("Starting validateAssignments")
    funcName = validateAssignments.func_name
    result = NTlist()
    if project.molecule.resonanceCount == 0:
        NTdebug("No resonance assignments read so no real validation on it can be done. Let's try anyway.")
#        return result

    for atm in project.molecule.allAtoms():
        atm.validateAssignment = NTlist()
        if atm.isAssigned():
            # Check database
            #print '===>', atm
            if not atm.db.shift:
                dummy = atm.pseudoAtom()
                if dummy.db.shift:
                    av = dummy.db.shift.average
                    sd = dummy.db.shift.sd
                else:
                    NTerror("%s: '%s' not in in DB SHIFTS\n", funcName, atm)
                    continue
                #end if
            else:
                av = atm.db.shift.average
                sd = atm.db.shift.sd
            #end if

            shift = atm.shift()

            # Check the shift against the database
            delta = math.fabs(shift - av) / sd
            if delta > 3.0:
                string = sprintf('%s: %.2f ppm is %.1f*sd away from average (%.2f,%.2f)',
                                 'SHIFT', shift, delta, av, sd
                                )
#                NTmessage('%-20s %s', atm, string)
                result.append( atm )
                atm.validateAssignment.append(string)
            #end if

            # Check if not both realAtom and pseudoAtom are assigned
            if atm.hasPseudoAtom() and atm.pseudoAtom().isAssigned():
                string = sprintf('%s: atm also has %s assigned', MULTIPLE_ASSIGNMENT, atm.pseudoAtom() )
#                NTmessage('%-20s %s', atm, string)
                result.append( atm )
                atm.validateAssignment.append(string)
            #end if

            # Check if not pseudoAtom and realAtom are assigned
            if atm.isPseudoAtom():
                for a in atm.realAtoms():
                    if a.isAssigned():
                        string = sprintf('%s: atm also has %s assigned', MULTIPLE_ASSIGNMENT, a )
#                        NTmessage('%-20s %s', atm, string)
                        result.append( atm )
                        atm.validateAssignment.append(string)
                    #end if
                #end for
            #end if

            # Check if all realAtoms are assigned in case there is a pseudo atom
            if atm.hasPseudoAtom():
                for a in atm.pseudoAtom().realAtoms():
                    if not a.isAssigned():
                        string = sprintf('%s: expected also %s to be assigned.', MISSING_PROTON_ASSIGNMENT, a )
#                        NTmessage('%-20s %s', atm, string )
                        result.append( atm )
                        atm.validateAssignment.append(string)
                    #end if
                #end for
            #end if

            # Check for protons with unassigned heavy atoms
            if atm.isProton():
                heavyAtm = atm.topology()[0]
                if not heavyAtm.isAssigned():
                    string = sprintf('%s: expected %s to be assigned', MISSING_HEAVY_ATOM_ASSIGNMENT, heavyAtm )
#                    NTmessage('%-20s %s', atm, string )
                    result.append( atm )
                    atm.validateAssignment.append(string)
                #end if
            #end if atm.isProton()
        else:
            # Atm is not assigned but stereo assignment is set
            if atm.isStereoAssigned():
                string = sprintf('%s: expected %s to be assigned', INVALID_STEREO_ASSIGNMENT, atm )
                result.append( atm )
                atm.validateAssignment.append(string)
            #end if
        #end if atm.isAssigned():

        if atm.validateAssignment:
            atm.rogScore.setMaxColor( COLOR_ORANGE, atm.validateAssignment )
        #end if
    #end for
#    for atm in result:
#        # check for shiftx averages
#        sav = None
#        ssd = None
#        dav = None
#        dsd = None
#        if atm.has_key('shiftx'):
#            sav = atm.shiftx.av
#            ssd = atm.shiftx.sd
#        if atm.db.has_key('shift'):
#            dav = atm.db.shift.average
#            dsd = atm.db.shift.sd
#        # m is for mine
#        mavStr = val2Str(atm.resonances().value, "%7.2f", 7, nullValue = NOSHIFT)
#        msdStr = val2Str(atm.resonances().error, "%7.2f", 7, nullValue = NOSHIFT)
#        savStr = val2Str(sav, "%7.2f", 7)
#        ssdStr = val2Str(ssd, "%7.2f", 7)
#        savStr = val2Str(sav, "%7.2f", 7)
#        davStr = val2Str(dsd, "%7.2f", 7)
#        NTdebug('%s %s %s\n' +\
#               'shift:    %7s %7s \n' +\
#               'shiftx:   %7s %7s \n' +\
#               'database: %7s %7s \n',
#                dots, atm, dots,
#                mavStr, msdStr,
#                savStr, ssdStr,
#                savStr, davStr)
#        NTwarning(atm.validateAssignment.format('%s') )
#    #end for

    if toFile:
        #path = project.mkdir( project.directories.analysis, project.molecule.name )
        fname = project.path(project.molecule.name, project.moleculeDirectories.analysis, 'validateAssignments.txt')
        fp = open( fname,'w' )
        if not fp:
            NTerror("Failed to open for writing: " + fname)
            return None
        NTmessage("Writing assignment validation to: " + fname)
        for atm in project.molecule.allAtoms():
            sav     = None
            ssd     = None
            delta   = None
            rdelta  = None
            dav     = None
            dsd     = None
            value   = None
            error   = None

            if atm.has_key('shiftx') and len(atm.shiftx) > 0:
                sav = atm.shiftx.av
                ssd = atm.shiftx.sd
            if atm.isAssigned() and sav:
                delta = atm.resonances().value - sav
                rdelta = 1.0
                if ssd > 0.0:
                    rdelta = sav/ssd
            if atm.db.shift:
                dav = atm.db.shift.average
                dsd = atm.db.shift.sd
            if atm.resonances():
                value = atm.resonances().value
                error = atm.resonances().error

            savStr     = val2Str(sav,   '%6.2f', 6 )
            ssdStr     = val2Str(ssd,   '%6.2f', 6 )
            deltaStr   = val2Str(delta, '%6.2f', 6 )
            rdeltaStr  = val2Str(rdelta,'%6.2f', 6 )
            davStr     = val2Str(dav,   '%6.2f', 6 )
            dsdStr     = val2Str(dsd,   '%6.2f', 6 )
            valueStr   = val2Str(value, '%6.2f', 6 ) # was sometimes set to a NOSHIFT
            if valueStr==NaNstring:
                error=None
            errorStr   = val2Str(error, '%6.2f', 6 )

            fprintf(fp,'%-18s (%6s %6s)   (shiftx: %6s %6s)   (delta: %6s %6s)   (db: %6s %6s)   %s\n',
                    atm,
                    valueStr,
                    errorStr,
                    savStr, ssdStr,
                    deltaStr, rdeltaStr,
                    davStr, dsdStr,
                    atm.validateAssignment.format()
                   )
        #end for
        fp.close()
        NTmessage('==> validateAssignments: result to "%s"', fname)
    #end if

    return result
#end def

def restoreDihRestraintInfo(project):
    """To restore restraint.residue and restraint.angle"""
    for dihRestraintList in project.dihedrals:
        for dihRestraint in dihRestraintList:
            residue, angle, _val3 = dihRestraint.retrieveDefinition()
            if angle:
                dihRestraint.residue = residue
                dihRestraint.angle = '%s_%i' % (angle, residue.resNum)
            else:
                dihRestraint.residue = dihRestraint.atoms[2].residue #'Invalid'
                dihRestraint.angle = 'Discarted'
# end def

def validateDihedrals(self):
    """Validate the dihedrals of dihedralList for outliers and cv using pierceTest.
    Return True on error.
    """

    if not self.molecule:
        return True
    if not self.molecule.modelCount:
        return True

    restoreDihRestraintInfo(self)

    for res in self.molecule.allResidues():
        for dihed in res.db.dihedrals.zap('name'):
            if not dihed in res:
                continue
            if not res.has_key(dihed):
                continue

            d = res[dihed]
            if not d: # skip dihedrals without values e.g. n terminal phi.
                continue
#            print res, dihed, d

            plotpars = self.plotParameters.getdefault(dihed,'dihedralDefault')

            cav, _cv, _n = d.cAverage(min=plotpars.min, max=plotpars.max)
            NTlimit( d, cav-180.0, cav+180.0 )

            goodAndOutliers = peirceTest( d )
            if not goodAndOutliers:
                NTcodeerror("in validateDihedrals: error from peirceTest")
                return True
            d.good, d.outliers = goodAndOutliers

            d.limit(          plotpars.min, plotpars.max )
            d.cAverage(       plotpars.min, plotpars.max )
            d.good.limit(     plotpars.min, plotpars.max, byItem=1 )
            d.good.cAverage(  plotpars.min, plotpars.max, byItem=1 )
            d.outliers.limit( plotpars.min, plotpars.max, byItem=1 )
            if False:
                NTmessage( '--- Residue %s, %s ---', res, dihed )
                NTmessage( 'good:     %2d %6.1f %4.3f',
                           d.good.n, d.good.cav, d.good.cv )
                NTmessage( 'outliers: %2d models: %s',
                           len(d.outliers), d.outliers.zap(0) )
#end def

def validateModels( self)   :
    """Validate the models on the basis of the dihedral outliers
    """

    if not self.molecule:
        NTerror("Skipping validateModels because no molecule")
        return True
    if not self.molecule.modelCount:
        NTerror("Skipping validateModels because no model")
        return True

    backbone = ['PHI','PSI','OMEGA']

#    self.validateDihedrals(    )
    # self.models keeps track of the number of outliers per model.
    self.models = NTdict()
    for m in range(self.molecule.modelCount):
        self.models[m] = 0

    for res in self.molecule.allResidues():
#        for dihed in res.db.dihedrals.zap('name'):
        for dihed in backbone:
#            print res, dihed
#            if dihed in res and res[dihed] != None:
            if dihed in res and res[dihed]:
                d = res[dihed] # NTlist object
                try: # Looks like d doesn't always have good; TODO check why this can be so.
                    if not d.good:
                        continue
                except:
                    continue
                for m in d.outliers.zap( 0 ):    #get all modelId of outliers
                    self.models[m] += 1
            #end if
        #end for
    #end for
    for m, count in self.models.items():
        NTdebug('Model %2d: %2d backbone dihedral outliers', m, count )
#end def

def makeDihedralHistogramPlot( project, residue, dihedralName, binsize = 5 ):
    '''
    Return NTplot instance with histogram of dihedralName
    or None on error.
    '''
    if project == None:
        return None
    if dihedralName not in residue:
        return None
    if residue[dihedralName] == None:
        return None

    bins       = 360/binsize
    plotparams = project.plotParameters.getdefault(dihedralName,'dihedralDefault')
#    NTdebug( 'residue: '+`residue`)
    angle = residue[dihedralName] # A NTlist
#    NTdebug( 'angle: ' + `angle`)
    ps = NTplotSet() # closes any previous plots
    ps.hardcopySize = (600,369)
    plot = NTplot( title  = residue._Cname(1),
      xRange = (plotparams.min, plotparams.max),
      xTicks = range(int(plotparams.min), int(plotparams.max+1), plotparams.ticksize),
      xLabel = dihedralName,
      yLabel = 'Occurence')
    ps.addPlot(plot)

#    Note that the good and outliers come from:
#    d.good, d.outliers = peirceTest( d )
    if not angle.__dict__.has_key('good'):
        NTcodeerror("No angle.good plots added. Skipping makeDihedralHistogramPlot for %s %s." % (
                    residue, dihedralName))
        return None
#    NTdebug( 'angle.good: ' + `angle.good`)
    plot.histogram( angle.good.zap(1),
                    plotparams.min, plotparams.max, bins,
                    attributes = boxAttributes( fillColor=plotparams.color ))
    if not angle.__dict__.has_key('outliers'):
        NTcodeerror("No angle.outliers plots added. Skipping makeDihedralHistogramPlot for %s %s." % (
                    residue, dihedralName))
        return None
#    NTdebug( 'angle.outliers: ' + `angle.outliers`)
    plot.histogram( angle.outliers.zap(1),
                plotparams.min, plotparams.max, bins,
                attributes = boxAttributes( fillColor=plotparams.outlier )
                  )
    ylim = plot.get_ylim()
    ylimMax = 5.0 # Just assume.
    if ylim:
        ylimMax = ylim[1]

    # AWSS
    # Let's check if for this 'angle' there is a dihedral restraint
    aAv  = angle.cav
    width = 4.0
    dr = _matchDihedrals(residue, dihedralName)
    alpha=0.3
    if dr:
#        NTdebug("dr: " + dr.format())
        bounds = NTlist(dr.lower, dr.upper)
        bounds.limit(plotparams.min, plotparams.max)
        if bounds[0] < bounds[1]: # single box
            point = (bounds[0], 0) # lower left corner of only box.
            sizes = (bounds[1]-bounds[0],ylimMax)
            plot.box(point, sizes, boxAttributes(fillColor=plotparams.lower, alpha=alpha))
        else: # two boxes
            # right box
            point = (bounds[0], 0) # lower left corner of first box.
            sizes = (plotparams.max-bounds[0],ylimMax)
            plot.box(point, sizes, boxAttributes(fillColor=plotparams.lower, alpha=alpha))
            point = (plotparams.min, 0) # lower left corner of second box.
            sizes = (bounds[1]-plotparams.min,ylimMax)
            plot.box(point, sizes, boxAttributes(fillColor=plotparams.lower, alpha=alpha))


    # Always plot the cav line
    plot.line( (aAv, 0), (aAv, ylimMax),
               lineAttributes(color=plotparams.average, width=width) )
    return ps



def makeDihedralPlot( project, residueList, dihedralName1, dihedralName2,
                      plotTitle = None ):
    '''Return NTplotSet instance with plot of dihedralName1 vrs dihedralName2 or
       None on error
       Called with: eg ['PHI',  'PSI',  'Ramachandran', 'PHI_PSI']

       Note that residue can also be a list of residues. A single plot will
       be created for all together were the appropriate background histograms
       will be picked.

       Return None on error or ps on success.
    '''

    if not project:
        NTerror( 'in makeDihedralPlot called without project' )
        return None
    if not residueList:
        NTerror( 'makeDihedralPlot called without residues in list' )
        return None

    # Set residue to first residue. For looping over multiple residues the var
    # res will be used.
    residue = residueList[0]
    # Note if all types are the same for selection of background.
#    allSameResType = True
#    for res in residueList:
#        if res.resName != residue.resName:
#            allSameResType = False
#            break
    isSingleResiduePlot = len(residueList) == 1

    if not plotTitle:
        if isSingleResiduePlot:
            plotTitle = residue._Cname(1)
        else:
            plotTitle = '%d residues'


    if dihedralName1 not in residue or residue[dihedralName1] == None:
#        NTdebug( 'in makeDihedralPlot not in residue dihedral 1: '+dihedralName1 )
        return None

    if dihedralName2 not in residue or residue[dihedralName2] == None:
#        NTdebug( 'in makeDihedralPlot not in residue dihedral 2: '+dihedralName2 )
        return None

#    NTdebug("Creating a 2D dihedral angle plot for plotItem: %s %s %s", residue, dihedralName1, dihedralName2)

    plotparams1 = project.plotParameters.getdefault(dihedralName1,'dihedralDefault')
    plotparams2 = project.plotParameters.getdefault(dihedralName2,'dihedralDefault')

    ps =NTplotSet() # closes any previous plots
    ps.hardcopySize = (500,500)
    plot = NTplot( title  = plotTitle,
      xRange = (plotparams1.min, plotparams1.max),
      xTicks = range(int(plotparams1.min), int(plotparams1.max+1), plotparams1.ticksize),
      xLabel = dihedralName1,
      yRange = (plotparams2.min, plotparams2.max),
      yTicks = range(int(plotparams2.min), int(plotparams2.max+1), plotparams2.ticksize),
      yLabel = dihedralName2)
    ps.addPlot(plot)

    if dihedralName1=='PHI' and dihedralName2=='PSI':
        histBySsAndCombinedResType = histRamaBySsAndCombinedResType
        histBySsAndResType         = histRamaBySsAndResType
    elif dihedralName1=='CHI1' and dihedralName2=='CHI2':
        histBySsAndCombinedResType = histJaninBySsAndCombinedResType
        histBySsAndResType         = histJaninBySsAndResType
    else:
        NTcodeerror("makeDihedralPlot called for non Rama/Janin")
        return None

    histList = []
    ssTypeList = histBySsAndResType.keys() #@UndefinedVariable
    ssTypeList.sort()
    # The assumption is that the derived residues can be represented by the regular.
    resNamePdb = getDeepByKeysOrDefault(residue, residue.resName, 'nameDict', PDB)
    if len( resNamePdb ) > 3: # The above line doesn't work. Manual correction works 95% of the time.
        resNamePdb = resNamePdb[:3]  # .pdb files have a max of 3 chars in their residue name.
#    NTdebug('Looked up residue.resName %s to resNamePdb %s' % ( residue.resName,resNamePdb ))

    for ssType in ssTypeList:
        hist = getDeepByKeys(histBySsAndCombinedResType,ssType)
        if isSingleResiduePlot:
            hist = getDeepByKeys(histBySsAndResType,ssType,resNamePdb)
        if hist != None:
#            NTdebug('Appending for ssType %s and resNamePdb %s' % ( ssType,resNamePdb ))
            histList.append(hist)
    if histList:
#        NTdebug('Will do dihedralComboPlot')
        plot.dihedralComboPlot(histList)



    # Plot restraint ranges for single residue plots.
    for res in residueList:
        if isSingleResiduePlot:
            # res is equal to residue
            dr1 = _matchDihedrals(res, dihedralName1)
            dr2 = _matchDihedrals(res, dihedralName2)

            if dr1 and dr2:
                lower1, upper1 = dr1.lower, dr1.upper
                lower2, upper2 = dr2.lower, dr2.upper
            elif dr1:
                lower1, upper1 = dr1.lower, dr1.upper
                lower2, upper2 = plotparams2.min, plotparams2.max
            elif dr2:
                lower2, upper2 = dr2.lower, dr2.upper
                lower1, upper1 = plotparams1.min, plotparams1.max

            if dr1 or dr2:
                plot.plotDihedralRestraintRanges2D(lower1, upper1,lower2, upper2)

        d1 = res[dihedralName1]
        d2 = res[dihedralName2]

        if not (len(d1) and len(d2)):
#            NTdebug( 'in makeDihedralPlot dihedrals had no defining atoms for 1: %s or', dihedralName1 )
#            NTdebug( 'in makeDihedralPlot dihedrals had no defining atoms for 2: %s'   , dihedralName2 )
            return None
        d1cav = d1.cav
        d2cav = d2.cav

        # Plot data points on top for painters algorithm without alpha blending.
        myPoint = plusPoint.copy()
        myPoint.pointColor = 'green'
        myPoint.pointSize = 6.0
        myPoint.pointEdgeWidth = 1.0
        if res.resName == 'GLY':
            myPoint.pointType = 'triangle'
        if res.resName == 'PRO':
            myPoint.pointType = 'square'

        plot.points( zip( d1, d2 ), attributes=myPoint )

        # Plot the cav point for single residue plots.
        if isSingleResiduePlot:
            myPoint = myPoint.copy()
            myPoint.pointSize = 8.0
            myPoint.pointType = 'circle'
            myPoint.pointColor = 'blue'
            myPoint.fill = False
            plot.point( (d1cav, d2cav),myPoint )

    return ps
#end def



def _matchDihedrals(residue, dihedralName):
    for dr in residue.dihedralRestraints:
        if dr.angle == '%s_%i' % (dihedralName, residue.resNum):
            return dr
    return None
#end def

def setupHtml(project):
    '''Description: create all folders and subfolders related to a Cing.Molecule
               under Molecul/HTML directory and initiatilise attribute html
               for the due Cing objects.
       Inputs: list of Cing.Molecules, Cing.Peaks, Cing.Distances and
               Cing.Dihedrals
       Output: returns None on success or True on failure.
    '''

    HTMLfile.killHtmlObjects()

    # values for residue table
    ncols = 10
    width = '75px' # reserve some space per residue in chain table
    top = '#_top'

    # initialize project html page
    project.htmlLocation = (project.path('index.html'), top)
    project.html = HTMLfile( project.htmlLocation[0],
                                  title = 'Project ' + project.name )

    htmlPath = os.path.join(cingRoot,cingPaths.html)
    for f in os.listdir( htmlPath ):
        htmlFile = os.path.join(htmlPath,f)
        if os.path.isfile(htmlFile):
            shutil.copy( htmlFile, project.path() )

    project.html.header('h1', 'Project: ' + project.name)

    # A list of all objects that will be in project/index.html
    project.mainPageObjects = NTdict()

    # Do Molecules HTML pages
    for molecule in project.molecules:
        if not project.molecule.modelCount:
            NTerror('setupHtml(): No structural models\n' )
            return True
        #end if

        #create new folders for Molecule/HTML
        htmlPath = project.htmlPath()
        if os.path.exists( htmlPath ):
            removedir( htmlPath )
        os.makedirs( htmlPath )
        NTdebug("htmlPath: %s" % htmlPath)
        for subdir in htmlDirectories.values():
            project.mkdir( project.molecule.name, moleculeDirectories.html, subdir )

        if hasattr(molecule, 'html'):
            del(molecule['html'])

        molecule.htmlLocation = (project.htmlPath('index.html'), top)
        NTdebug("molecule.htmlLocation[0]: %s" % molecule.htmlLocation[0])
        molecule.html = HTMLfile( molecule.htmlLocation[0],
                                  title = 'Molecule ' + molecule.name )

    for molecule in project.molecules:
        index = project.molecules.index(molecule)
#        molecule = project[molecule]
        molecule.html.header('h1', 'Molecule: ' + molecule.name)

        previous = None
        next = None
        lastMoleculeIndex = len(project.molecules) - 1
        if index > 0:
            previous = project[ project.molecules[index-1] ]

        if index < lastMoleculeIndex:
            next = project[ project.molecules[index+1] ]

        molecule.html.insertHtmlLink(     molecule.html.header, molecule, project, text='Home' )
        if previous:
            molecule.html.insertHtmlLink( molecule.html.header, molecule, previous,text='Previous' )
        molecule.html.insertHtmlLink(     molecule.html.header, molecule, project, text='UP' )
        if next:
            molecule.html.insertHtmlLink( molecule.html.header, molecule, next,    text='Next' )

        molecule.html.main('h1','Residue-based analysis')

        if project.mainPageObjects.has_key('Molecules'):
            project.mainPageObjects['Molecules'].append(molecule)
        else:
            project.mainPageObjects['Molecules'] = [molecule]

        for chain in molecule.allChains():
            #Create the directory for this chain
            chaindir = project.htmlPath(chain.name)
            if not os.path.exists( chaindir ):
                os.mkdir( chaindir )

            #if hasattr(chain, 'html'): del(chain['html'])
            if chain.has_key('html'):
                del(chain.html)
            chain.htmlLocation = ( os.path.join(chaindir,'index.html'), top )
            chain.html = HTMLfile(chain.htmlLocation[0],
                                       title='%s %s'%(molecule.name,chain.name))

        for chain in molecule.allChains():

            moleculeMain = molecule.html.main
            molecule.html.insertHtmlLinkInTag( 'h1', moleculeMain, molecule,
                                            chain, text='Chain %s' % chain.name)

            residues = chain.allResidues()
            if not residues:
                break

            #Chain page
            chainHeader = chain.html.header
            chainHeader('h1', '%s %s' % (molecule.name, chain.name))

            chain.html.insertHtmlLink( chainHeader, chain, project,
                                       text = 'Home' )

            # Refs to move to previous, next chain or UP
            previous = chain.sibling(-1)
            next = chain.sibling(1)
            if previous:
                chain.html.insertHtmlLink( chainHeader, chain, previous,
                                           text=previous._Cname(-1))
            #end if
            chain.html.insertHtmlLink( chainHeader, chain, molecule,
                                           text='UP')
            if next:
                chain.html.insertHtmlLink( chainHeader, chain, next,
                                           text=next._Cname(-1))
            #end if

            # Html objs that share residues tables elements
            htmlList = [ molecule, chain ]

            # make a table with residue links
            r0 = residues[0]
            r1 = r0.resNum
            r2 = r0.resNum/ncols *ncols + ncols-1
            for obj in htmlList:
                if obj.html == chain.html: obj.html.main('h1','Residues')
                obj.html.main('table', closeTag=False)
                obj.html.main('tr', closeTag=False)
                obj.html.main( 'td',sprintf('%d-%d',r1,r2), style="width: %s" %
                               width )
            for dummy in range( r0.resNum%ncols ):
                for obj in htmlList:
                    obj.html.main('td', style="width: %s" % width)

            for res in residues:
                # Create the directory for this residue
                resdir = project.htmlPath(chain.name, res.name)
                if not os.path.exists( resdir ):
                    os.mkdir( resdir )
                #end if

                #if hasattr(res, 'html'): del(res['html'])
                if res.has_key('html'):
                    del(res.html)

                res.htmlLocation = ( os.path.join(resdir,'index.html'), top )
                res.html = HTMLfile( res.htmlLocation[0], title=res.name )
            #end for over res in residues

            for res in residues:
                if res.resNum%ncols == 0:
                    r1 = res.resNum/ncols *ncols
                    r2 = r1+ncols-1
                    for obj in htmlList:
                        obj.html.main('tr', openTag=False)
                        obj.html.main('tr', closeTag=False)
                        obj.html.main( 'td',sprintf('%d-%d',r1,r2),
                                       style="width: %s" % width )

                # add residue to table
                for obj in htmlList:
                    objMain = obj.html.main
                    objMain('td', style="width: %s" % width, closeTag=False)
                    obj.html.insertHtmlLink(objMain, obj, res, text=res.name)
                    objMain('td', openTag=False)

                # Create a page for each residue

                # generate html file for this residue
                resHeader = res.html.header
                resHeader('h1', res._Cname(-1) )
                res.html.insertHtmlLink( resHeader, res, project, text = 'Home' )

                # Refs to move to previous, next residue or UP
                previous = res.sibling(-1)
                next = res.sibling(1)
                if previous:
                    res.html.insertHtmlLink( resHeader, res, previous,text = previous._Cname(-1) )
                res.html.insertHtmlLink(     resHeader, res, chain,   text = 'UP' )
                if next:
                    res.html.insertHtmlLink( resHeader, res, next,    text = next._Cname(-1) )
            #end for over res in residues

            for obj in htmlList:
                obj.html.main('tr', openTag=False)
                obj.html.main('table', openTag=False)
            #end for over obj in htmlList

        molecule.html.main('h1', 'Model-based analysis')
        molecule.html.main( 'p', molecule.html._generateTag('a', 'Models page',
                                            href='models.html', newLine=False) )

        molecule.html.main('h1', 'Structure-based analysis')
        molecule.html.main( 'p', molecule.html._generateTag('a', 'Salt bridges',
            href='../../../'+project.moleculePath('analysis')+'/saltbridges.txt', newLine=False) )

    #end for

    # NEW FEATURE: setup Models page

    # Do Peaks HTML pages
    for peakList in project.peaks:

        plLink = project.htmlPath( htmlDirectories.peaks,
                                   peakList.name+'.html' )

        peakList.htmlLocation = ( plLink, top )
        peakList.html = HTMLfile( peakList.htmlLocation[0],
                                       title = 'Peak List ' + peakList.name )

    for peakList in project.peaks:

        index = project.peaks.index(peakList)

        peakHeader = peakList.html.header
        peakHeader('h1', 'Peak List: ' + peakList.name)

        previous = None
        next = None

        if index > 0:
            try: previous = project.peaks[index-1]
            except: pass

        try: next = project.peaks[index+1]
        except: pass

        peakList.html.insertHtmlLink( peakHeader, peakList, project,
                                       text = 'Home' )

        if previous:
            peakList.html.insertHtmlLink( peakHeader, peakList, previous,
                                          text = 'Previous')
        #end if

        peakList.html.insertHtmlLink( peakHeader, peakList, project,
                                      text = 'UP')

        if next:
            peakList.html.insertHtmlLink( peakHeader, peakList, next,
                                          text = 'Next')
        #end if

        if project.mainPageObjects.has_key('Peaks'):
            project.mainPageObjects['Peaks'].append(peakList)
        else:
            project.mainPageObjects['Peaks'] = [peakList]
        #end if

        #count = 0
        for peak in peakList:
            count = peak.peakIndex #count += 1
            peakTag = 'o'+str(peak.__OBJECTID__) #str(peak.peakIndex) #
            peak.htmlLocation = ( plLink, '#' + peakTag )
            peakMain = peakList.html.main
            #peakMain( 'h2', peakList.html._generateTag('a', 'Peak %i'
            #          % count, id = peakTag, newLine=False) )
            peakMain( 'h2', 'Peak %i' % count, id = peakTag )

            peakMain('ul', closeTag=False)
            peakMain('li', 'Positions: %s' % peak.positions.__str__())
            peakMain('li', 'Height: %.3e (%.3e)' % ( peak.height.value,
                                                     peak.height.error))
            peakMain('li', 'Volume: %.3e (%.3e)' % ( peak.volume.value,
                                                     peak.volume.error))
            peakMain('li', 'Atoms:', closeTag=False)
            for resonance in peak.resonances:
                if resonance:
                    residue = resonance.atom._parent
                    resonanceAtomName = "%s.%s" % ( residue.name,
                                                    resonance.atom.name )
                    peakList.html.insertHtmlLink( peakMain, peakList, residue,
                                                  text = resonanceAtomName )
                else:
                    peakMain('b', 'None')
                #end if
            #end for
            peakMain('li', openTag=False)
            peakMain('ul', openTag=False)
        #end for
    #end for

    # For all RestraintList
    allRestraintList = project.distances + project.dihedrals

    for restraintList in allRestraintList:

        RLLink = project.htmlPath( htmlDirectories.restraints,
                                   restraintList.name+'.html' )
        restraintList.htmlLocation = ( RLLink, top )
        restraintList.html = HTMLfile( restraintList.htmlLocation[0],
                                         title = 'Restraints List ' +
                                         restraintList.name )

    for restraintList in allRestraintList:

        index = allRestraintList.index(restraintList)

        RLLink = restraintList.htmlLocation[0]

        restrHeader = restraintList.html.header
        restrHeader('h1', 'Restraints List: '+ restraintList.name)

        previous = None
        next = None

        if index > 0:
            try: previous = allRestraintList[index-1]
            except: pass

        try: next = allRestraintList[index+1]
        except: pass

        restraintList.html.insertHtmlLink( restrHeader, restraintList, project,
                                           text = 'Home' )

        if previous:
            restraintList.html.insertHtmlLink( restrHeader, restraintList,
                                               previous, text = 'Previous' )
        #end if

        restraintList.html.insertHtmlLink( restrHeader, restraintList,
                                           project, text = 'UP' )

        if next:
            restraintList.html.insertHtmlLink( restrHeader, restraintList,
                                               next, text = 'Next' )
        #end if

        if project.mainPageObjects.has_key('Restraints'):
            project.mainPageObjects['Restraints'].append(restraintList)
        else:
            project.mainPageObjects['Restraints'] = [restraintList]
        #end if

        restrMain = restraintList.html.main
        restrMain('h3', restraintList.formatHtml())

        if str(type(restraintList)).count('DistanceRestraintList'):
            #count = 0
            for restraint in restraintList:
                count = restraint.id #count += 1
#                NTdebug('restraint count %d colorLabel: %s' % ( count, restraint.colorLabel))
                tag = 'o'+str(restraint.__OBJECTID__)
                restraint.htmlLocation = ( RLLink, '#' + tag )

                #restrMain('h2', restraintList.html._generateTag( 'a',
                #     'Distance Restraint %i' % count, id = tag, newLine=False) )

                restrMain('h2', 'Restraint ', id = tag, closeTag=False)
                # Strangely JFD doesn't know how to get the coloring into the next text
                # without creating a html link. So just put in a self reference.
                restraintList.html.insertHtmlLink(restrMain,restraintList,restraint,'%i'%count)
                restrMain('h2', openTag=False)
#                restrMain('h2', 'Distance Restraint %i' % count, id = tag)
                restrMain('ul', closeTag=False)
                restrMain('li', 'Pair of Atoms:', closeTag=False)

                if len(restraint.atomPairs) < 1:
                    restrMain('b', 'None')

                for atomPair in restraint.atomPairs:
                    res1 = atomPair[0]._parent
                    res2 = atomPair[1]._parent
#                    atomName1 = "(%s.%s.%s," % ( chn1.name, res1.name, atomPair[0].name )
                    atomName1 = "(" + atomPair[0].toString() +','
                    atomName2 =       atomPair[1].toString() +')'

                    restraintList.html.insertHtmlLink( restrMain, restraintList,
                                                       res1, text = atomName1 )
                    restraintList.html.insertHtmlLink( restrMain, restraintList,
                                                       res2, text = atomName2 )
                #end for
                restrMain('li', 'Lower/Upper: %.2f / %.2f' % (restraint.lower,
                                                              restraint.upper))
                restrMain('li', 'Average (Min/Max):  %.3e (%.3e / %.3e)'
                                 % (restraint.av, restraint.min, restraint.max))
                restrMain('li', 'ViolCount3: %i' % restraint.violCount3)

                restrMain('li', 'Viol Average / SD / Max: %s / %s / %s' %
                        (       val2Str(restraint.violAv,  "%.2f"),
                                val2Str(restraint.violSd,  "%.2f"),
                                val2Str(restraint.violMax, "%.2f") ))
                restraint.rogScore.createHtmlForComments(restrMain)
                #restrMain('li', openTag=False)
                restrMain('ul', openTag=False)
            #end for
        elif str(type(restraintList)).count('DihedralRestraintList'):
            for restraint in restraintList:
                count = restraint.id
                tag = 'o'+str(restraint.__OBJECTID__)
                restraint.htmlLocation = ( RLLink, '#' + tag )
                restrMain = restraintList.html.main

                #restrMain('h2', restraintList.html._generateTag( 'a',
                #      'Dihedral Restraint %i' % count, id = tag, newLine=False))
                restrMain('h2', 'Restraint ',  id = tag, closeTag=False)
                restraintList.html.insertHtmlLink(restrMain,restraintList,restraint,'%i'%count)
                restrMain('h2', openTag=False)

                restrMain('ul', closeTag=False)
                restrMain( 'li', 'Torsional Angle Atoms:', closeTag=False )
                if len(restraint.atoms) < 1:
                    restrMain('b','None')
                ind = 0
                for atom in restraint.atoms:
                    res = atom._parent
                    atomName = atom.toString() +','
#                    atomName = "%s.%s," % ( res.name, atom.name )
                    if ind == 0:
                        atomName = '(' + atomName
                    if ind == 3:
                        atomName = atomName[:-1] + ')'
                    restraintList.html.insertHtmlLink( restrMain, restraintList,
                                                       res, text = atomName )
                    ind += 1
                #end for
                restrMain('li', openTag=False)
                restrMain('li', 'Lower/Upper: %.2f / %.2f' % (restraint.lower,
                                                              restraint.upper))
                restrMain('li', 'Average (CV):  %.2f (%.2f)'
                                 % (restraint.cav, restraint.cv))
                restrMain('li', 'ViolCount3: %i' % restraint.violCount3)
                restrMain('li', 'Viol Average / SD / Max: %s / %s / %s' % (
                    val2Str(restraint.violAv,  "%.2f"),
                    val2Str(restraint.violSd,  "%.2f"),
                    val2Str(restraint.violMax, "%.2f") ))

#                 val1, val2, _val3 = restraint.retrieveDefinition()
#                 restraint.residue = val1
#                 restraint.angle = '%s_%i' % (val2, val1.resNum)

                restrMain('li', 'Angle Name:', closeTag=False)
                restraintList.html.insertHtmlLink( restrMain, restraintList,
                                       restraint.residue, text=restraint.angle )
                restrMain('li', openTag=False)
                restrMain('ul', openTag=False)
            #end for
        #end if
    #end for

    # For the atom list.
    atomList = AtomList(project) # instantiated only for this purpose locally.
    RLLink = project.htmlPath( htmlDirectories.atoms, 'atoms.html' )
    atomList.htmlLocation = ( RLLink, top )
    atomList.html = HTMLfile( atomList.htmlLocation[0], title = 'Atom List ' + atomList.name )
    RLLink = atomList.htmlLocation[0]
    atomHeader = atomList.html.header
    atomHeader('h1', 'Atom List: '+ atomList.name)
    atomList.html.insertHtmlLink( atomHeader, atomList, project,
                                       text = 'Home' )
    atomList.html.insertHtmlLink( atomHeader, atomList,
                                       project, text = 'UP' )
    project.mainPageObjects['Atoms'] = [ atomList ]

    atomMain = atomList.html.main

    atomMain('h3', closeTag=False)
    refItem = os.path.join( project.moleculePath('analysis'),'validateAssignments.txt')
    abstractResource = NTdict()
    abstractResource.htmlLocation = ( refItem, top )
    if os.path.exists(refItem):
        atomList.html.insertHtmlLink( atomMain, atomList, abstractResource, text = 'Assignments' )
#        atomMain('a',  'Assignments', href = os.path.join( "../..", refItem))
    else:
        atomMain('a',  NotAvailableText)
    atomMain('h3', openTag=False)

    atomMain('h3', atomList.formatHtml())
    for atom in atomList:
        count = atom.id
        tag = 'o'+str(atom.__OBJECTID__)
        atom.htmlLocation = ( RLLink, '#' + tag )

        #restrMain('h2', atomList.html._generateTag( 'a',
        #     'Distance Restraint %i' % count, id = tag, newLine=False) )

        atomMain('h2', 'Atom ', id = tag, closeTag=False)
        atomList.html.insertHtmlLink(atomMain,atomList,atom,'%i'%count)
        atomMain('h2', openTag=False)
        atomMain('ul', closeTag=False)
        atomMain('li', 'Atom: (', closeTag=False)
        res = atom._parent
        atomList.html.insertHtmlLink( atomMain, atomList, res, text = res.toString() )
        atomMain('i', '.'+atom.name + ')') # weirdly it didn't work to put this text in the next statement...
        # The text was put after the </li>
        atomMain('li', '', openTag=False)

        sav     = None
        ssd     = None
        delta   = None
        rdelta  = None
        dav     = None
        dsd     = None
        value   = None
        error   = None

        if atom.has_key('shiftx') and len(atom.shiftx) > 0:
            sav = atom.shiftx.av
            ssd = atom.shiftx.sd
        if atom.isAssigned() and sav:
            delta = atom.resonances().value - sav
            rdelta = 1.0
            if ssd > 0.0:
                rdelta = sav/ssd
        if atom.db.shift:
            dav = atom.db.shift.average
            dsd = atom.db.shift.sd
        if atom.resonances():
            value = atom.resonances().value
            error = atom.resonances().error

        savStr     = val2Str(sav,   '%6.2f', 6 )
        ssdStr     = val2Str(ssd,   '%6.2f', 6 )
        deltaStr   = val2Str(delta, '%6.2f', 6 )
        rdeltaStr  = val2Str(rdelta,'%6.2f', 6 )
        davStr     = val2Str(dav,   '%6.2f', 6 )
        dsdStr     = val2Str(dsd,   '%6.2f', 6 )
        valueStr   = val2Str(value, '%6.2f', 6 ) # was sometimes set to a NOSHIFT
        if valueStr==NaNstring:
            error=None
        errorStr   = val2Str(error, '%6.2f', 6 )

#        fprintf(fp,'%-18s (%6s %6s)   (shiftx: %6s %6s)   (delta: %6s %6s)   (db: %6s %6s)   %s\n',
#                atm,
#                valueStr,
#                errorStr,
#                savStr, ssdStr,
#                deltaStr, rdeltaStr,
#                davStr, dsdStr,
#                atm.validateAssignment.format()
#               )

        atomMain('li', 'Chemical shift: (%6s %6s)' % (valueStr, errorStr))
        atomMain('li', 'SHIFTX shift: (%6s %6s)' % (savStr, ssdStr))
        atomMain('li', 'delta shift: (%6s %6s)' % (deltaStr, rdeltaStr))
        atomMain('li', 'db shift: (%6s %6s)' % (davStr, dsdStr))

        atom.rogScore.createHtmlForComments(atomMain)
        atomMain('ul', openTag=False)
    #end for

    # Do Project HTML page
    htmlMain = project.html.main

    htmlMain('table', closeTag=False)
    htmlMain('tr', closeTag=False)
    htmlMain('td', closeTag=False)

    htmlMain('h1', 'Summary')
    htmlMain('ul', closeTag=False)
    htmlMain('li', closeTag=False)
#    NTdebug("os.path.abspath(os.curdir): " + os.path.abspath(os.curdir))
    refItem = os.path.join( project.moleculePath('analysis'),'summary.txt')
#    NTdebug("refItem: " + refItem)
    if os.path.exists(refItem):
        htmlMain('a',  OpenText, href = os.path.join( "..", refItem))
    else:
        htmlMain('a',  NotAvailableText)
    htmlMain('li', openTag=False)
    htmlMain('ul', openTag=False)

    for key in project.mainPageObjects.keys():
        htmlMain('h1', key)
        for item in project.mainPageObjects[key]:
#            NTdebug('item: %s' % item)
            htmlMain('ul', closeTag=False)
            project.html.insertHtmlLinkInTag( 'li', htmlMain, project, item, text=item.name )
            htmlMain('ul', openTag=False)

    htmlMain('h1', 'Credits')
    htmlMain('ul', closeTag=False)
    htmlMain('li', closeTag=False)
    refItem = 'credits.html'
    htmlMain('a',  OpenText, href = refItem )
    htmlMain('li', openTag=False)
    htmlMain('ul', openTag=False)

    htmlMain('td', openTag=False)
    htmlMain('td', closeTag=False)
    htmlMain('img', src = 'mol.gif')
    htmlMain('td', openTag=False)
    htmlMain('tr', openTag=False)
    htmlMain('table', openTag=False)
#end def

def renderHtml(project):
    '''Description: render HTML content for a Cing.Molecule or for just a
               Cing.Chain, Cing.Residue or Cing.Atom.
       Inputs: a Cing.Molecule, Cing.Chain, Cing.Residue or Cing.Atom.
       Output: return None for success is standard.
    '''
    for htmlObj in htmlObjects:
#        NTdebug("rendering htmlObj: " + `htmlObj`)
        if htmlObj.render():
            NTerror( "Failed to render an html object." )
            return True


def populateHtmlMolecules( project, htmlOnly=False,
            doProcheck = True, doWhatif = True, ranges=None ):
    '''Description: generate the Html content for Molecules and Residues pages.
       Inputs: a Cing.Project.
       Output: return None for success is standard.
       If htmlOnly is set then the html will be created without imagery.
    '''

    if htmlOnly:
        NTmessage('Skipping export of molecular imagery to gif because htmlOnly is True')
    else:
        molGifFileName = "mol.gif"
        pathMolGif = project.path(molGifFileName)
        NTdebug("Trying to create : " + pathMolGif)
        if project.molecule.export2gif(pathMolGif, project=project):
            NTerror("Failed to generated a Molmol picture; continuelng.")

#    for molecule in [project[mol] for mol in project.moleculeNames]:
    for molecule in project.molecules:
        for chain in molecule.allChains():
            chainId = chain.name
            NTmessage("Generating residue html pages for chain: " + chainId)
            printedDots = 0
            #NB: it's falling with malloc for AWSS if >~ 140 residues
            resRange = chain.allResidues()#[:60]
            for res in resRange:
#                write without extra space
                if not printedDots % 10:
                    digit = printedDots / 10
                    NTmessageNoEOL(`digit`)
                else:
                    NTmessageNoEOL('.')
                printedDots += 1
                resNum = res.resNum
                if not printedDots % CHARS_PER_LINE_OF_PROGRESS:
                    NTmessage("")
                    printedDots = 0
                resdir = os.path.dirname(res.htmlLocation[0])

                fp = open( os.path.join( resdir, 'summary.txt' ), 'w' )
                msg = sprintf('----- %5s -----', res)
                fprintf(fp, msg+'\n')

                if res.rogScore.isCritiqued():
                    res.html.left( 'h2', 'Critiques', id='Critiques')
                    res.rogScore.createHtmlForComments(res.html.left)

                if htmlOnly:
                    pass
#                    NTmessage('Skipping export of molecular imagery to gif because htmlOnly is True')
                else:
    #                    NTdebug(msg)
                    # 0: angle 1 name
                    # 1: angle 2 name
                    # 2: Angle combination name
                    # 3: Tuple of arbitrary number of keys to value to show
                    # 4: Name of value to show (eg QUACHK)
                    plotList = [['PHI',  'PSI',  'Ramachandran', (WHATIF_STR, RAMCHK_STR, VALUE_LIST_STR), RAMCHK_STR ],
                                ['CHI1', 'CHI2', 'Janin',        (WHATIF_STR, C12CHK_STR, VALUE_LIST_STR), C12CHK_STR]]
                    for plotItem in plotList:
                        plotDihedralName1 = plotItem[0]
                        plotDihedralName2 = plotItem[1]
                        plotDihedralComboName = plotItem[2]
                        ps = makeDihedralPlot( project, [res], plotDihedralName1, plotDihedralName2)
                        if ps:
                            ps.hardcopy( fileName = os.path.join(resdir, plotDihedralComboName))
                            res.html.left( 'h2', plotDihedralComboName, id=plotDihedralComboName)
                            graphicsFormatExtension = 'png'
                            plotFileNameDihedral2D = plotDihedralComboName + '.' + graphicsFormatExtension
    #                            NTdebug('plotFileNameDihedral2D: ' + plotFileNameDihedral2D)
                            res.html.left( 'img', src = plotFileNameDihedral2D )
                            # Try to show a What If average Z-score like: 'whatif.QUACHK.valueList 0.054 (+/- 0.012'
                            keys = plotItem[3]
                            strToShow = '.'.join( keys )
                            av = getDeepByKeys(res,*keys)
                            if av != None:
                                sd = None
                                if isinstance(av, NTlist):
                                    ( av, sd, _n ) = av.average()
        #                            strToShow += '.'+'average'
                                pointNTvalueStr = "%s"  % NTvalue(value=av, error=sd, fmt='%.2f (+- %.2f)')
                                strToShow += ': %s' % pointNTvalueStr
                                res.html.left( 'p', strToShow ) # The a tag is not filled yet. Might link to NTmoleculePlot?
                        else:
                            pass
    #                            NTdebug("No 2D dihedral angle plot for plotItem: %s %s %s", res, plotItem[0], plotItem[1])


                    for dihed in res.db.dihedrals.zap('name'):
                        if dihed in res and res[dihed]:
    #                            NTdebug( '------>>>>> ' + dihed + `res` + `res[dihed]` )
                            d = res[dihed] # List of values with outliers etc attached.

                            # summarize the results
                            lenOutliers = '.' # JFD adds: Indicating None
                            outlierList = '.'
                            if d.__dict__.has_key('outliers'):
    #                            NTwarning("Found no outliers; code wasn't prepared to deal with that or is JFD wrong?")
                                lenOutliers = `len(d.outliers)`
                                outlierList = d.outliers.zap(0)
    #                            -180.1 is longest: 6.1f
                            summary = '%-2s %3d %-6s: average: %6.1f   cv: %6.3f  ||  outliers: %3s (models %s)' % (
                                chainId, resNum, dihed,
                                d.cav, d.cv, lenOutliers, outlierList
                                             )
                            fprintf( fp, '%s\n', summary )
    #                        print summary
                            graphicsFormatExtension = 'png'
                            #generate a dihedral histogram plot
                            if htmlOnly:
                                ps = None
                            else:
                                ps = makeDihedralHistogramPlot( project, res, dihed )
                            tmpPath = os.path.join(resdir,dihed + '.' + graphicsFormatExtension)
    #                        NTdebug("Will write to: "+tmpPath)
                            if not os.path.isdir(resdir):
                                NTerror("Failed to find an existing location in: " + resdir)
                                return None
                            if ps:
                                ps.hardcopy( fileName = tmpPath )
        #                        del( plot )

                                #generate HTML code for plot and text
                                res.html.left( 'h2', dihed, id=dihed),
                                res.html.left( 'img', src = dihed + '.' + graphicsFormatExtension, alt=""  )
                                res.html.left( 'p', summary )
                        #end if
                    #end for
                # end of skip test.
                # Right side
                # Distance Restraints
                _generateHtmlResidueRestraints(project, res, type = 'Distance')
                # Dihedral Restraints
                _generateHtmlResidueRestraints(project, res, type = 'Dihedral')
            #end for residue
            NTmessage("") # Done printing progress.
        #end for chain
        main = molecule.html.main

        if doWhatif and not htmlOnly:
            NTmessage("Creating Whatif plots")
            anyWIPlotsGenerated = False
            if project.createHtmlWhatif(ranges=ranges):
                NTerror('Failed to createHtmlWhatif')
                return True

            main('h1','What If')
#            anyWhatifPlotsGenerated = False
            ncols = 6
            main('table',  closeTag=False)
            plotCount = -1
            printedDots = 0 # = plotCount+1
            for p,d in wiPlotList:
                if not printedDots % 10:
                    digit = printedDots / 10
                    NTmessageNoEOL(`digit`)
                else:
                    NTmessageNoEOL('.')
                printedDots += 1
                plotCount += 1
                wiLink = os.path.join('..',
                            project.moleculeDirectories.whatif, molecule.name + p + ".pdf")
                wiLinkReal = os.path.join( project.rootPath( project.name )[0], molecule.name,
                            project.moleculeDirectories.whatif, molecule.name + p + ".pdf")
                NTdebug('wiLinkReal: ' + wiLinkReal)
                if not os.path.exists( wiLinkReal ):
                    NTerror('Failed to find expected wiLinkReal: ' + wiLinkReal)
                    continue # Skip their inclusion.

                pinupLink = os.path.join('..',
                            project.moleculeDirectories.whatif, molecule.name + p + "_pin.gif" )
                fullLink = os.path.join('..',
                            project.moleculeDirectories.whatif, molecule.name + p + ".png" )
                anyWIPlotsGenerated = True
                if plotCount % ncols == 0:
                    if plotCount:
                        main('tr',  openTag=False)
                    main('tr',  closeTag=False)
                main('td',  closeTag=False)
                main('a',   "",         href = fullLink, closeTag=False )
                main(    'img', "",     src=pinupLink ) # enclosed by _A_ tag.
                main('a',   "",         openTag=False )
                main('br')
                main('a',   d,          href = wiLink )
                main('td',  openTag=False)
            #end for plot
            NTmessage('' ) # for the eol char.

            if plotCount: # close any started rows.
                main('tr',  openTag=False)
            main('table',  openTag=False) # close table
            if not anyWIPlotsGenerated:
                main('h2', "No what if plots found at all")
        #end for doWhatif check.

        if doProcheck:
            NTmessage("Formating Procheck plots")
            main('h1','Procheck_NMR')
            anyProcheckPlotsGenerated = False
            pcPlotList = [
                 ('_01_ramachand','Ramachandran (all)'),
                 ('_02_allramach','Ramachandran (type)'),
                 ('_03_chi1_chi2','chi1-chi2'),
                 ('_04_ch1distrb','chi1'),
                 ('_05_ch2distrb','chi2'),
                 ('_06_ensramach','Ramachandran (sequence)'),
                 ('_07_ensch1ch2','Ensemble chi1-chi2'),
                 ('_08_residprop','Residue properties'),
                 ('_09_equivresl','Equivalent resolution'),
                 ('_10_modelsecs','By-model sec. structures'),
                 ('_11_rstraints','Distance restraints'),
                 ('_12_restdiffs','Restraint differences'),
                 ('_13_restrnsum','Numbers of restraints'),
                 ('_14_resdifsum','Difference summary'),
                 ('_15_resvifreq','Violation frequency'),
                 ('_16_restatist','Restraint statistics'),
                 ('_17_restrviol','By-residue violations'),
                 ('_18_modelcomp','By-model violations')
                ]
            ncols = 6
            main('table',  closeTag=False)
            plotCount = -1
            printedDots = 0 # = plotCount+1
            for p,d in pcPlotList:
                if not printedDots % 10:
                    digit = printedDots / 10
                    NTmessageNoEOL(`digit`)
                else:
                    NTmessageNoEOL('.')
                printedDots += 1
                plotCount += 1
                procheckLink = os.path.join('..',
                            project.moleculeDirectories.procheck, molecule.name + p + ".ps")
                procheckLinkReal = os.path.join( project.rootPath( project.name )[0], molecule.name,
                            project.moleculeDirectories.procheck, molecule.name + p + ".ps")
    #            NTdebug('procheck real path: ' + procheckLinkReal)
                if not os.path.exists( procheckLinkReal ):
                    continue # Skip their inclusion.

                if not htmlOnly:
#                    fileList = False
#                else:
                    fileList = convert2Web( procheckLinkReal, doMontage=True )
                fileList = False
    #            NTdebug( "Got back from convert2Web output file names: " + `fileList`)
                if fileList == True:
                    NTerror( "Failed to convert2Web input file: " + procheckLinkReal)
                    continue

    #            _pinupPath, _fullPath, _printPath = fileList
                pinupLink = os.path.join('..',
                            project.moleculeDirectories.procheck, molecule.name + p + "_pin.gif" )
                fullLink = os.path.join('..',
                            project.moleculeDirectories.procheck, molecule.name + p + ".png" )
                printLink = os.path.join('..',
                            project.moleculeDirectories.procheck, molecule.name + p + ".pdf" )
                anyProcheckPlotsGenerated = True
                # plotCount is numbered starting at zero.
                if plotCount % ncols == 0:
                    if plotCount: # Only close rows that were started
                        main('tr',  openTag=False)
                    main('tr',  closeTag=False)
                main('td',  closeTag=False)
                main('a',   "",         href = fullLink, closeTag=False )
                main(    'img', "",     src=pinupLink ) # enclosed by _A_ tag.
                main('a',   "",         openTag=False )
                main('br')
                main('a',   d,          href = procheckLink )
                main('br')
                main('a',   "pdf",      href = printLink )
                main('td',  openTag=False)
            #end for
            NTmessage('' ) # for the eol char.

            if plotCount: # close any started rows.
                main('tr',  openTag=False)
            main('table',  openTag=False) # close table
            if not anyProcheckPlotsGenerated:
                main('h2', "No procheck plots found at all")



    #end for molecule
    # return None for success is standard.
#end def

def _generateHtmlResidueRestraints( project, residue, type = None ):
    '''Description: internal routine to generate the Html content for restraints
               linked to a particular residue.
       Inputs: Cing.Residue, string type of restraint: 'Distance', 'Dihedral',
               'RDC' (?).
       Output:
    '''

    if type == 'Distance':
        restraintList = residue.distanceRestraints
    elif type == 'Dihedral':
        restraintList = residue.dihedralRestraints
    else:
        return
    #end if

    if len(restraintList) == 0: return

    resRight = residue.html.right
    resRight('h2','%s Restraints' % type)

    tmpDict = NTdict()
    for restraint in restraintList:
        RLname = os.path.basename(restraint.htmlLocation[0]).split('.')[0]
        if tmpDict.has_key(RLname):
            tmpDict[RLname].append(restraint)
        else:
            tmpDict[RLname] = NTlist(restraint)
        #end if
    #end for
    RLists = tmpDict.keys()
    # display Restraint list
    for k in RLists:
        RLobj = project[k]
        resRight('h3', closeTag=False)
        residue.html.insertHtmlLink(resRight, residue, RLobj, text=k)
        resRight('h3', openTag=False)
        resRight('p', closeTag=False)
        #resRight('br')
        resRL = tmpDict[k]
        # sort list by 'violCount3' reverse order (higher to lower values)
        NTsort(resRL, 'violCount3', inplace=True)
        resRL.reverse()
        # sort by color: 1st red, 2nd orange, then green and by violCount3 reverse order
        listRed, listOrange, listGreen = [], [], []
        for dr in resRL:
            if dr.rogScore.isRed():
                listRed.append(dr)
            elif dr.rogScore.isOrange():
                listOrange.append(dr)
            else:
                listGreen.append(dr)
        resRL = listRed + listOrange + listGreen
        # display restraint by number, in line, sorted by violCount3 reverse
        #for dr in resRL:
        #    residue.html.insertHtmlLink(resRight, residue, dr, text=str(dr.id))
        #end for
        # display restraint by line
        toShow = 5 # number of restraints to show on the right side of Residue page
        for dr in resRL:
            text = '%s:' % (str(dr.id))
            residue.html.insertHtmlLink(resRight, residue, dr, text=text)
            #resRight('ul', closeTag=False)
            if type == 'Distance':
                av = dr.av
                for atomPair in dr.atomPairs:
                    res1 = atomPair[0]._parent
                    res2 = atomPair[1]._parent
                    atomName1 = "(" + atomPair[0].toString() +','
                    atomName2 =       atomPair[1].toString() +')'
#                    atomName1 = "(%s.%s," % ( res1.name, atomPair[0].name )
#                    atomName2 = "%s.%s)" % ( res2.name, atomPair[1].name )
                    residue.html.insertHtmlLink( resRight, residue, res1,
                                                 text = atomName1 )
                    residue.html.insertHtmlLink( resRight, residue, res2,
                                                 text = atomName2 )
                #end for
            #end if
            if type == 'Dihedral':
                av = dr.cav
                #resRight( 'a', '%s' % dr.angle)
                angleName = dr.angle.split('_')[0]
                residue.html.insertHtmlLink( resRight, residue, residue,
                                             text=angleName, id=angleName )
            #end if
            resRight('br')
            resRight( 'a', type + ': Lower/Av/Upper: %.2f/ %.2f / %.2f' %
                      (dr.lower, av, dr.upper) )
            resRight('br')
            #resRight('li', 'Average (Min/Max):  %.3e (%.3e / %.3e)'
            #                 % (restraint.av, restraint.min, restraint.max))
            resRight( 'a', 'Violations: violCount3 / Average / SD / Max: %d / %s / %s / %s' %
                        (       dr.violCount3,
                                val2Str(dr.violAv,  "%.2f"),
                                val2Str(dr.violSd,  "%.2f"),
                                val2Str(dr.violMax, "%.2f") ))
            resRight('br')
            dr.rogScore.createHtmlForComments(resRight)

            #resRight('ul', openTag=False)
            resRight('br')
            if resRL.index(dr) + 1 == toShow:
                if len(resRL) > toShow :
                    resRight('a','More: ')
                    for dr in resRL[toShow:]:
                        residue.html.insertHtmlLink( resRight, residue, dr,
                                                 text=str(dr.id) )
                        #end for
                    resRight('br')
                break
            #end if
        #end for
        resRight('p', openTag=False)
        #if RLists.index(k) != RLists.index(RLists[-1]): resRight('br')
    #end for
    #resRight('p', openTag=False)
#end def

def populateHtmlModels(project):
    "Output: return None for success is standard."
#    NTdebug("Starting: populateHtmlModels")
    # Models page
#    for molecule in [project[mol] for mol in project.moleculeNames]:
    for molecule in project.molecules:
#        NTdebug("Starting: populateHtmlModels for molecule: " + molecule.name)
        # should go to setupHtml
        molecule.modelPage = HTMLfile( project.htmlPath( 'models.html' ),title = 'Outliers' )
        molecule.modelPage.header('h1', molecule.name + ' models' )
        molecule.modelPage.header('a', 'Home', href='../../index.html' )

        #molecule.modelPage.insertHtmlLink( molecule.modelPage.header,
        #                                   restraintList, project,
        #                                   text = 'Home' )
        ps = NTplotSet() # closes any previous plots
        ps.hardcopySize = (600,369)
        plot = NTplot( xLabel = 'Model', yLabel = 'Outliers',
                       xRange = (0, project.molecule.modelCount+1))
        ps.addPlot(plot)
#        project.models[i] holds the number of outliers for model i.
#        models is a NTdict containing per model a list of outliers.
        outliers = [project.models[i] for i in range(molecule.modelCount)]
        NTdebug( '>> Number of outliers per model: ' + `outliers`)
        plot.barChart( project.models.items(), 0.05, 0.95,
                       attributes = boxAttributes( fillColor='green' ) )

        plot.autoScaleYByValueList(outliers,
                    startAtZero=True,
                    useIntegerTickLabels=True )

        ps.hardcopy( project.htmlPath('outliers') )
        graphicsOutputFormat = 'png'
        molecule.modelPage.main('img', src = 'outliers.'+graphicsOutputFormat)
    #end for
#end def

def validate( project, ranges=None, htmlOnly = False, doProcheck = True, doWhatif = True ):
    """Validatation tests returns None on success or True on failure.
    """

    if setupValidation( project, ranges=ranges, doProcheck=doProcheck, doWhatif=doWhatif ):
        NTerror("Failed to setupValidation")
        return True

    if setupHtml(project):
        NTerror("Failed to setupHtml")
        return True

    # populate Molecule (Procheck) and Residues
    if populateHtmlMolecules(project,
            htmlOnly=htmlOnly,
            doProcheck=doProcheck,
            doWhatif=doWhatif,
            ranges=ranges
            ):
        NTerror("Failed to populateHtmlMolecules")

    if htmlOnly:
        NTmessage('Skipping populateHtmlModels')
    else:
        if populateHtmlModels(project):
            NTerror("Failed to populateHtmlModels")
            return True
    if renderHtml(project):
        NTerror("Failed to renderHtml")
        return True

    NTmessage("Done with overall validation")
#end def

# register the functions
methods  = [(validateDihedrals, None),
            (validateModels,None),
            (validateAssignments, None),
            (validate, None),
            (criticizeByAll, None),
            (checkForSaltbridges, None),
            (setupValidation, None),
            (populateHtmlMolecules, None), # for debugging.
            (populateHtmlModels, None), # for debugging.
            (renderHtml, None), # for debugging.
            (calculateRmsd, None),
            (summary, None),
            (makeDihedralHistogramPlot, None),
            (makeDihedralPlot, None)
           ]
#saves    = []
restores = [(validateRestraints, None),
           ]
#exports  = []