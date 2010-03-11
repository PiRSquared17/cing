"""
Execute as:
python -u $CINGROOT/python/cing/Scripts/d1d2plot.py

make sure the projects to run are already in the tmpdir.
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing import verbosityDebug
from cing import verbosityError
from cing.Libs.NTplot import NTplot
from cing.Libs.NTplot import NTplotSet
from cing.Libs.NTplot import plusPoint
from cing.Libs.NTplot import solidLine
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import fprintf
from cing.Libs.NTutils import getDeepByKeys
from cing.Libs.html import hPlot
from cing.Libs.html import makeDihedralPlot
from cing.Libs.matplotlibExt import blue_inv
from cing.Libs.matplotlibExt import green_inv
from cing.Libs.matplotlibExt import yellow_inv
from cing.PluginCode.required.reqWhatif import BBCCHK_STR
from cing.PluginCode.required.reqWhatif import VALUE_LIST_STR
from cing.PluginCode.required.reqWhatif import WHATIF_STR
from cing.Scripts.d1d2plotConstants import BBCCHK_CUTOFF
from cing.Scripts.d1d2plotConstants import CV_CUTOFF
from cing.core.classes import Project
from cing.core.constants import DIHEDRAL_NAME_Cb4C
from cing.core.constants import DIHEDRAL_NAME_Cb4N
from cing.core.constants import IUPAC
from cing.core.constants import MAX_PERCENTAGE_D1D2
from cing.core.constants import MIN_PERCENTAGE_D1D2
from cing.core.constants import SCALE_BY_SUM
from cing.core.database import NTdb
from cing.core.molecule import Dihedral
from cing.core.molecule import common20AAList
from cing.core.parameters import plotParameters
from matplotlib.pylab import * #@UnusedWildImport for most imports
from numpy.ma.core import masked_where
import cing
import os


hPlot.initHist()
set_printoptions(linewidth=100000)

# important to switch to temp space before starting to generate files for the project.
os.chdir(cingDirTmp)


def plotForEntry(entryId):
    "Arbitrary 20 bb occurrences as cuttoff for now"
    dihedralName1 = 'Cb4N'
    dihedralName2 = 'Cb4C'
    graphicsFormat = "png"

    os.chdir(cingDirTmp)
    project = Project.open(entryId, status='old')
#    titleStr = 'd1d2 all resType'

    fpGood = open(project.name + '_all_testCb2Good.out', 'w')
    fpBad = open(project.name + '_all_testCb2Bad.out', 'w')

    mCount = project.molecule.modelCount

    residueList = project.molecule.A.allResidues()
#    residueList = project.molecule.A.allResidues()[-2:-1]

    for res in residueList:
        triplet = NTlist()
        for i in [-1, 0, 1]:
            triplet.append(res.sibling(i))
        if None in triplet:
            NTmessage('Skipping because not all in triplet for %s' % res)
            continue

#        bb = getDeepByKeys(res, WHATIF_STR, BBCCHK_STR, VALUE_LIST_STR, 0) # check first one.
#        if bb == None:
#            NTmessage('Skipping without BBCCHK values (please run What If): %s' % res)
#            continue

        d1 = getDeepByKeys( res, DIHEDRAL_NAME_Cb4N)
        d2 = getDeepByKeys( res, DIHEDRAL_NAME_Cb4C)

        if d1 == None or d2 == None:
            NTmessage("Skipping residue without both dihedrals expected")
            continue

        if d1.cv == None or d2.cv == None:
            NTmessage("Skipping unstructured residue: %s" % res)
            continue
        if not ( d1.cv < CV_CUTOFF and d2.cv < CV_CUTOFF):
            NTmessage("Skipping unstructured residue (cvs %f %f): %s" % (d1.cv, d2.cv, res))
            continue

        for i in range(mCount): # Consider each model individually
            bb = getDeepByKeys(res, WHATIF_STR, BBCCHK_STR, VALUE_LIST_STR, i)
            if bb == None:
                NTmessage('Skipping without BB: %s' % res)
                continue
            angles = NTlist() # store phi, psi, chi1, chi2
            for angle in ['PHI', 'PSI', 'CHI1', 'CHI2']:
                if res.has_key(angle):
                    angles.append(res[angle][i])
                else:
                    angles.append(0.0)
            if bb < BBCCHK_CUTOFF:
                fprintf(fpBad, '%4d   %7.2f  %7.2f  %7.2f  %s  %s %s\n', res.resNum, d1[i], d2[i], bb, angles.format("%7.2f  "), res, res.dssp.consensus)
            else:
                fprintf(fpGood, '%4d   %7.2f  %7.2f  %7.2f  %s  %s %s\n', res.resNum, d1[i], d2[i], bb, angles.format("%7.2f  "), res, res.dssp.consensus)
            #end if
        #end for models
        fn = "d1d2_%03d_%s." % ( res.resNum, res.resName) + graphicsFormat
#        residueHTMLfile = ResidueHTMLfile(project, res)
        ps = makeDihedralPlot( project, [res], dihedralName1, dihedralName2,
#                          plotTitle = titleStr,
                          plotCav=False,htmlOnly=False )
        if ps:
            ps.hardcopy(fn, graphicsFormat)
    #        plot.show()
    #end for residues
    fpBad.close()
    fpGood.close()

    project.close(save=False)


def plotDihedral2DRama():
    showRestraints = False
    showDataPoints = False
    dihedralName1 = "PHI"
    dihedralName2 = "PSI"
    graphicsFormat = "png"

#        ssType = 'E'
#        resType = 'GLY'
#        for ssType in histRamaBySsAndResType.keys():
#            ssTypeForFileName = ssType.replace(' ', '_')
    ssTypeFixed = 'H'
    for resType in hPlot.histRamaBySsAndResType[ssTypeFixed].keys():
        if resType != 'HIS': # for testing enable filtering.
            continue

#                titleStr = ssType + ' ' + resType
        titleStr = resType
#            NTmessage("plotting: %s" % titleStr)
#            hist = histRamaBySsAndResType[ssType][resType]

        ps = NTplotSet() # closes any previous plots
        ps.hardcopySize = (500, 500)

#                residueName = resType + ""
        x = NTlist(-45, -80, 125) # outside the range.
        y = NTlist(-65, -63, -125)
        # 1 SMALL boxe
        lower1, upper1 = -120.00, -125.05 # if within 0.1 they're considered the same and order shouldn't matter.
        lower2, upper2 = 0, 100
        # 4 boxes:
#            lower1, upper1 = 120,   0
#            lower2, upper2 = 130,  20
        # left/right boxes:
#        lower1, upper1 =  90, 270
#        lower2, upper2 =   0,  70
        # upper/lower boxes:
#        lower1, upper1 =   0,  70
#        lower2, upper2 =  80, 270
        # borring one box
#        lower1, upper1 =   0,  70
#        lower2, upper2 =  10,  60

        # important to switch to temp space before starting to generate files for the project.
        project = Project('testPlotHistoDihedral2D')
        plotparams1 = project.plotParameters.getdefault(dihedralName1, 'dihedralDefault')
        plotparams2 = project.plotParameters.getdefault(dihedralName2, 'dihedralDefault')

        x.limit(plotparams1.min, plotparams1.max)
        y.limit(plotparams2.min, plotparams2.max)

        plot = NTplot(title=titleStr,
          xRange=(plotparams1.min, plotparams1.max),
          xTicks=range(int(plotparams1.min), int(plotparams1.max + 1), plotparams1.ticksize),
          xLabel=dihedralName1,
          yRange=(plotparams2.min, plotparams2.max),
          yTicks=range(int(plotparams2.min), int(plotparams2.max + 1), plotparams2.ticksize),
          yLabel=dihedralName2)
        ps.addPlot(plot)

        if showRestraints:
            if plot.plotDihedralRestraintRanges2D(lower1, upper1, lower2, upper2):
                NTerror("Failed plot.plotDihedralRestraintRanges2D")
                sys.exit(1)

        # Plot a Ramachandran density background
        histList = []
        ssTypeList = hPlot.histRamaBySsAndResType.keys() #@UndefinedVariable
        ssTypeList.sort() # in place sort to: space, H, S
        for ssType in ssTypeList:
#                NTdebug('appending [%s]' % ssType )
            hist = hPlot.histRamaBySsAndResType[ssType][resType]
            histList.append(hist)
        if plot.dihedralComboPlot(histList):
                NTerror("Failed plot.plotDihedralRestraintRanges2D -b-")
                sys.exit(1)
        if showDataPoints:
            myPoint = plusPoint.copy()
            myPoint.pointColor = 'green'
            myPoint.pointSize = 6.0
            myPoint.pointEdgeWidth = 1.0
            myPoint.fill = False
            if resType == 'GLY':
                myPoint.pointType = 'triangle'
            if resType == 'PRO':
                myPoint.pointType = 'square'
            plot.points(zip(x, y), attributes=myPoint)
#            fn = os.path.join('bySsAndResType', ( ssTypeForFileName+"_"+resType+"."+graphicsFormat))
#            fn = os.path.join('byResType', ( resType+"."+graphicsFormat))
        fn = resType + "_rama." + graphicsFormat
        ps.hardcopy(fn, graphicsFormat)
#        plot.show()


def plotDihedral2DJanin():
    showRestraints = True
    showDataPoints = True
    dihedralName1 = "CHI1"
    dihedralName2 = "CHI2"
    graphicsFormat = "png"

    outputDir = os.path.join(cingDirTmp, 'janin')
    if not os.path.exists(outputDir):
        os.mkdir(outputDir)
#        outputDir = cingDirTmp
    os.chdir(outputDir)

#        ssType = 'E'
#        resType = 'GLY'
#        for ssType in histRamaBySsAndResType.keys():
#            ssTypeForFileName = ssType.replace(' ', '_')
    ssTypeFixed = 'H'
    for resType in hPlot.histRamaBySsAndResType[ssTypeFixed].keys():
        if resType != 'ARG': # for testing enable filtering.
            continue

#                titleStr = ssType + ' ' + resType
        titleStr = resType
        NTmessage("plotting: %s" % titleStr)
#            hist = histRamaBySsAndResType[ssType][resType]

        ps = NTplotSet() # closes any previous plots
        ps.hardcopySize = (500, 500)

#                residueName = resType + ""
        x = NTlist(-45, -80, 125) # outside the range.
        y = NTlist(-65, -63, -125)
        # 4 boxes:
        lower1, upper1 = 120, 0
        lower2, upper2 = 130, 20
        # left/right boxes:
#        lower1, upper1 =  90, 270
#        lower2, upper2 =   0,  70
        # upper/lower boxes:
#        lower1, upper1 =   0,  70
#        lower2, upper2 =  80, 270
        # borring one box
#        lower1, upper1 =   0,  70
#        lower2, upper2 =  10,  60

        # important to switch to temp space before starting to generate files for the project.
        project = Project('testPlotHistoDihedralJanin')
        plotparams1 = project.plotParameters.getdefault(dihedralName1, 'dihedralDefault')
        plotparams2 = project.plotParameters.getdefault(dihedralName2, 'dihedralDefault')

        x.limit(plotparams1.min, plotparams1.max)
        y.limit(plotparams2.min, plotparams2.max)

        plot = NTplot(title=titleStr,
          xRange=(plotparams1.min, plotparams1.max),
          xTicks=range(int(plotparams1.min), int(plotparams1.max + 1), plotparams1.ticksize),
          xLabel=dihedralName1,
          yRange=(plotparams2.min, plotparams2.max),
          yTicks=range(int(plotparams2.min), int(plotparams2.max + 1), plotparams2.ticksize),
          yLabel=dihedralName2)
        ps.addPlot(plot)

        if showRestraints:
            plot.plotDihedralRestraintRanges2D(lower1, upper1, lower2, upper2)

        # Plot a Ramachandran density background
        histList = []
        ssTypeList = histJaninBySsAndResType.keys() #@UndefinedVariable
        ssTypeList.sort() # in place sort to: space, H, S
        for ssType in ssTypeList:
            hist = getDeepByKeys(hPlot.histJaninBySsAndResType, ssType, resType)
            if hist != None:
                NTdebug('appending [%s]' % ssType)
                histList.append(hist)
        if histList:
            if plot.dihedralComboPlot(histList):
                NTerror("Failed plot.plotDihedralRestraintRanges2D -b-")
                sys.exit(1)

        if showDataPoints:
            myPoint = plusPoint.copy()
            myPoint.pointColor = 'green'
            myPoint.pointSize = 6.0
            myPoint.pointEdgeWidth = 1.0
            myPoint.fill = False
            if resType == 'GLY':
                myPoint.pointType = 'triangle'
            if resType == 'PRO':
                myPoint.pointType = 'square'
            plot.points(zip(x, y), attributes=myPoint)
#            fn = os.path.join('bySsAndResType', ( ssTypeForFileName+"_"+resType+"."+graphicsFormat))
#            fn = os.path.join('byResType', ( resType+"."+graphicsFormat))
        fn = resType + "_janin." + graphicsFormat
        ps.hardcopy(fn, graphicsFormat)
#        plot.show()

#        plot.show()

def plotDihedralD1_1d():
    dihedralName = 'Cb4N'
    graphicsFormat = "png"

    subDir = 'doublets'
    os.chdir(os.path.join(cingDirTmp,subDir))

#    interestingResTypeList = [ 'GLY' ]
    interestingResTypeList = common20AAList
#    interestingResTypeList = [ 'GLY', 'ALA' ]
#    interestingResTypeList = [ 'CYS', 'PRO' ]
    for resType in common20AAList:
        for resTypePrev in common20AAList:
            if resType not in interestingResTypeList:
                continue
            if resTypePrev not in interestingResTypeList:
                continue
#            if resType != 'GLY':
#                continue
#            if resTypePrev != 'ALA':
#                continue

            titleStr = 'd1 %s(i-1) %s(i)' % (resTypePrev, resType)
            NTmessage("plotting: %s" % titleStr)

            plotparams = plotParameters.getdefault(dihedralName, 'dihedralDefault')

            ps = NTplotSet() # closes any previous plots
            ps.hardcopySize = (600, 369)
            plot = NTplot(title=titleStr,
              xRange=(plotparams.min, plotparams.max),
              yRange=(0, 50),
              xTicks=range(int(plotparams.min), int(plotparams.max + 1), plotparams.ticksize),
              xLabel=dihedralName,
              yLabel='Occurrence (%)')
            ps.addPlot(plot)

            h = getDeepByKeys(hPlot.histd1ByResTypes, resType, resTypePrev)
            if h == None:
                continue
            sumh = sum(h)
            plot.title += ' tot: %d' % sumh

            x = range(5, 360, 10)
            y = 100.0 * h / sumh # mod inplace
            points = zip(x, y)
            lAttr = solidLine(color='black' )
            plot.lines(points, attributes=lAttr)
            ssTypeList = hPlot.histd1BySs.keys() #@UndefinedVariable
            ssTypeList.sort() # in place sort to: space, H, S
            colorList = [ 'green', 'blue', 'yellow']

            for i, ssType in enumerate(ssTypeList):
                h = getDeepByKeys(hPlot.histd1BySsAndResTypes, ssType, resType, resTypePrev)
                sumh = sum(h)
                plot.title += ' %s: %d' % (ssType,sumh)
                if h == None:
                    continue
#                NTdebug('appending [%s]' % ssType)
                y = 100.0 * h / sumh
                points = zip(x, y)
                lAttr = solidLine(color=colorList[i])
                plot.lines(points, attributes=lAttr)

            fn = "d1 %s %s_d1d2." % (resTypePrev, resType)
            fn += graphicsFormat
            ps.hardcopy(fn, graphicsFormat)
#        plot.show()

def plotDihedralD1_2d(doOnlyOverall = True):
    dihedralName1 = 'Cb4N'
    dihedralName2 = 'Cb4C'
    graphicsFormat = "png"

    if doOnlyOverall:
        subDir = 'triplets_ov'
    else:
        subDir = 'triplets'
    os.chdir(os.path.join(cingDirTmp,subDir))

#                minPercentage =  0.08
#                maxPercentage = .2
    minPercentage =  MIN_PERCENTAGE_D1D2
    maxPercentage = MAX_PERCENTAGE_D1D2

    for resType in common20AAList:
        for resTypePrev in common20AAList:
            for resTypeNext in common20AAList:
#                if resType != 'GLY':
#                    continue
                if resTypePrev != 'ALA':
                    continue
                if resTypeNext != 'ARG':
                    continue


                # Plot a density background
                histList = []

                titleStr = 'd1d2 %s-%s-%s' % (resTypePrev, resType, resTypeNext)
                NTmessage("plotting: %s" % titleStr)

#                ps = NTplotSet() # closes any previous plots
#                ps.hardcopySize = (500, 500)

#        #                residueName = resType + ""
#                x = NTlist(-45, -80,  125) # outside the range.
#                y = NTlist(-65, -63, -125)

                # important to switch to temp space before starting to generate files for the project.
        #        project     = Project('testPlotHistoDihedrald1d2')
                plotparams1 = plotParameters.getdefault(dihedralName1, 'dihedralDefault')
                plotparams2 = plotParameters.getdefault(dihedralName2, 'dihedralDefault')

#                x.limit(plotparams1.min, plotparams1.max)
#                y.limit(plotparams2.min, plotparams2.max)

#                plot = NTplot(title=titleStr,
#                  xRange=(plotparams1.min, plotparams1.max),
#                  xTicks=range(int(plotparams1.min), int(plotparams1.max + 1), plotparams1.ticksize),
#                  xLabel=dihedralName1,
#                  yRange=(plotparams2.min, plotparams2.max),
#                  yTicks=range(int(plotparams2.min), int(plotparams2.max + 1), plotparams2.ticksize),
#                  yLabel=dihedralName2)
#                ps.addPlot(plot)
                # e.g. ALA-VAL-THR
                hist1 = getDeepByKeys(hPlot.histd1ByResTypes, resType, resTypePrev) # VAL,ALA
                hist2 = getDeepByKeys(hPlot.histd1ByResTypes, resTypeNext, resType) # THR VAL
                if hist1 == None:
                    NTdebug('skipping for hist1 is empty for [%s] [%s]' % (resType, resTypePrev))
                    continue
                if hist2 == None:
                    NTdebug('skipping for hist2 is empty for [%s] [%s]' % (resType, resTypeNext))
                    continue
                sumh1 = sum(hist1)
                sumh2 = sum(hist2)
                titleStr += ' %d-%d' % (sumh1,sumh2)
                if doOnlyOverall:
                    m1 = mat(hist1, dtype=float)
                    m2 = mat(hist2, dtype=float)
                    m2 = m2.transpose()
                    hist = multiply(m1,m2)
                    histList.append(hist)
                else:
                    titleStr += '\n'
                    ssTypeList = hPlot.histd1BySsAndResTypes.keys() #@UndefinedVariable
                    ssTypeList.sort() # in place sort to: space, H, S
                    for ssType in ssTypeList:
                        hist1 = getDeepByKeys(hPlot.histd1BySsAndResTypes, ssType, resType, resTypePrev)
                        hist2 = getDeepByKeys(hPlot.histd1BySsAndResTypes, ssType, resType, resTypeNext)
                        if hist1 == None:
                            NTdebug('skipping for hist1 is empty for [%s] [%s] [%s]' % (ssType, resType, resTypePrev))
                            continue
                        if hist2 == None:
                            NTdebug('skipping for hist2 is empty for [%s] [%s] [%s]' % (ssType, resType, resTypeNext))
                            continue

                        sumh1 = sum(hist1)
                        sumh2 = sum(hist2)
                        titleStr += " '%s' %d-%d" % (ssType, sumh1,sumh2)

#                        hist1 = 100.0 * hist1 / sumh1
#                        hist2 = 100.0 * hist2 / sumh2
                        m1 = mat(hist1, dtype=float)
                        m2 = mat(hist2, dtype=float)
                        m2 = m2.transpose()
                        hist = multiply(m1,m2)
                        histList.append(hist)

                ps = NTplotSet() # closes any previous plots
                ps.hardcopySize = (500, 500)

                myplot = NTplot(title=titleStr,
                  xRange=(plotparams1.min, plotparams1.max),
                  xTicks=range(int(plotparams1.min), int(plotparams1.max + 1), plotparams1.ticksize),
                  xLabel=dihedralName1,
                  yRange=(plotparams2.min, plotparams2.max),
                  yTicks=range(int(plotparams2.min), int(plotparams2.max + 1), plotparams2.ticksize),
                  yLabel=dihedralName2)
                ps.addPlot(myplot)

                if True:
                    myplot.dihedralComboPlot(histList, minPercentage =  minPercentage, maxPercentage = maxPercentage, scaleBy = SCALE_BY_SUM )


                fn = 'd1d2_%s-%s-%s' % (resTypePrev, resType, resTypeNext)
                if doOnlyOverall:
                    fn += '_ov_'
                fn += "." + graphicsFormat
#                savefig(fn)

                ps.hardcopy(fn, graphicsFormat)

def plotHistogramOverall():
    graphicsFormat = "png"
    alpha = 0.8 # was 0.8; looks awful with alpha = 1
    n = 20
#    d = 3 # number of ss types.
    extent = ( 0, n ) + ( 0, n )
    cmapList= [   green_inv, blue_inv, yellow_inv ]
    colorList= [ 'green',   'blue',   'yellow']
    i = 1 # decides on color picked.

    # If set it will do a single ssType otherwise the overall.
    for doOverall in [ False, True ]:
#    for doOverall in [ True ]:
        if doOverall:
            ssTypeList = [ None ]
        else:
            ssTypeList = [' ', 'S', 'H']

        for ssType in ssTypeList:
            m = zeros((n*n), dtype=int).reshape(n,n)
        #    mBySs = zeros((n,n,d), dtype=int).reshape(n,n,d)
            tickList = [ NTdb.getResidueDefByName( resType ).shortName for resType in common20AAList]
    #        tickListRev = tickList[:]
    #        tickListRev.reverse()
            for r,resTypePrev in enumerate(common20AAList):
                for c,resType in enumerate(common20AAList):
                    if doOverall:
                        hist1 = getDeepByKeys(hPlot.histd1ByResTypes, resType, resTypePrev)
                    else:
                        hist1 = getDeepByKeys(hPlot.histd1BySsAndResTypes, ssType, resType, resTypePrev)
                    if hist1 == None:
                        NTdebug('skipping for hist1 is empty for [%s] [%s]' % (resType, resTypePrev))
                        continue
                    m[r,c] = sum(hist1)

            clf()

#            axes([.1, .1, .8, .8 ] )
            xlabel('resType')
            ylabel('resTypePrev')
            xlim( (0, n) )
            ylim( (0, n) )
            offset = 0.5
            xticks( arange(offset, n), tickList )
            yticks( arange(offset, n), tickList )
#            print 'just before call to set_ticks_position'
    #        axis.xaxis.set_ticks_position('top')
    #        axis.xaxis.set_label_position('top')
        #    axis.yaxis.set_ticks_position('both')
        #    axis.yaxis.set_label_position('left')
            grid(True)
            strTitle = "ssType: [%s]" % ssType
            title(strTitle)
            plot([0,n], [0,n], 'b-', linewidth=1)
            minCount =  300.
            maxCount = 1000.
            if False:
                minCount =  0.
                maxCount =  1.
            if ssType:
                minCount /= 3.
                maxCount /= 3.
            maxHist = amax( m )
            minHist = amin( m )
            sumHist = sum( m )
            NTmessage('ssType: %s' % ssType)
            NTmessage('maxHist: %s' % maxHist) # 9165 of total of ~ 1 M.
            NTmessage('minHist: %s' % minHist) # 210
            NTmessage('sumHist: %s' % sumHist) # 210
#            NTmessage('tickList: %s' % tickList) # 210
        #    his *= 100./maxHist
            his = masked_where(m <= minCount, m, copy=1)

            palette = cmapList[i]
            palette.set_under(color = 'red', alpha = 1.0 ) # alpha is 0.0
            palette.set_over( color = colorList[i], alpha = 1.0) # alpha is 1.0 Important to make it a hard alpha; last plotted will rule.
            palette.set_bad(color = 'red', alpha = 1.0 )


            norm = Normalize(vmin = minCount, vmax = maxCount, clip = True) # clip is False
            imshow( his,
                    interpolation='nearest',
        #            interpolation='bicubic',
    #                origin='lower',
                    extent=extent,
                    alpha=alpha,
                    cmap=palette,
                    norm = norm )
#            mr = m[::-1] # reverses the rows, nice!
#            NTmessage('mr: %s' % mr)

            fn = "plotHistogram_%s_d1d2.%s" % ( ssType, graphicsFormat )
            savefig(fn)

            clf()
            l = m.reshape(n*n)
            hist(l,20)
            xlabel('pair count')
            ylabel('number of occurances')
            title(strTitle)
            fn = "plotHistOfHist_%s_d1d2.%s" % ( ssType, graphicsFormat )
            savefig(fn)

        # end loop over ssType
    # end over ssType overall
    return m

def plotDihedralD1D2():
    dihedralName1 = 'Cb4N'
    dihedralName2 = 'Cb4C'
    graphicsFormat = "png"


    entryId = "1brv" # Small much studied PDB NMR entry
#        entryId = "1hy8" # small, single model, very low scoring entry

    pdbDirectory = os.path.join(cingDirTestsData, "pdb", entryId)
    pdbFileName = "pdb" + entryId + ".ent"
    pdbFilePath = os.path.join(pdbDirectory, pdbFileName)

    # does it matter to import it just now?
    project = Project(entryId)
    project.removeFromDisk()
    project = Project.open(entryId, status='new')
    project.initPDB(pdbFile=pdbFilePath, convention=IUPAC)

#        ssType = 'E'
#        resType = 'GLY'
#        for ssType in histRamaBySsAndResType.keys():
#            ssTypeForFileName = ssType.replace(' ', '_')
    titleStr = 'd1d2 all resType'
    NTmessage("plotting: %s" % titleStr)
#            hist = histd1d2BySsAndResType[ssType][resType]

    ps = NTplotSet() # closes any previous plots
    ps.hardcopySize = (500, 500)

#                residueName = resType + ""
    x = NTlist(-45, -80, 125) # outside the range.
    y = NTlist(-65, -63, -125)

    # important to switch to temp space before starting to generate files for the project.
#        project     = Project('testPlotHistoDihedrald1d2')
    plotparams1 = project.plotParameters.getdefault(dihedralName1, 'dihedralDefault')
    plotparams2 = project.plotParameters.getdefault(dihedralName2, 'dihedralDefault')

    x.limit(plotparams1.min, plotparams1.max)
    y.limit(plotparams2.min, plotparams2.max)

    plot = NTplot(title=titleStr,
      xRange=(plotparams1.min, plotparams1.max),
      xTicks=range(int(plotparams1.min), int(plotparams1.max + 1), plotparams1.ticksize),
      xLabel=dihedralName1,
      yRange=(plotparams2.min, plotparams2.max),
      yTicks=range(int(plotparams2.min), int(plotparams2.max + 1), plotparams2.ticksize),
      yLabel=dihedralName2)
    ps.addPlot(plot)

    # Plot a density background
    histList = []
    ssTypeList = hPlot.histd1d2BySsAndCombinedResType.keys() #@UndefinedVariable
    ssTypeList.sort() # in place sort to: space, H, S
    for ssType in ssTypeList:
        hist = getDeepByKeys(hPlot.histd1d2BySsAndCombinedResType, ssType) #@UndefinedVariable
        if hist != None:
            NTdebug('appending [%s]' % ssType)
            histList.append(hist)
    if histList:
        plot.dihedralComboPlot(histList)
#            fn = os.path.join('bySsAndResType', ( ssTypeForFileName+"_"+resType+"."+graphicsFormat))
#            fn = os.path.join('byResType', ( resType+"."+graphicsFormat))


    fpGood = open(project.name + '.testCb2Good.out', 'w')
    fpBad = open(project.name + '.testCb2Bad.out', 'w')

    mCount = project.molecule.modelCount

    for res in project.molecule.A.allResidues():
        triplet = NTlist()
        for i in [-1, 0, 1]:
            triplet.append(res.sibling(i))
        if None in triplet:
            NTdebug('Skipping ' % res)

        else:
            CA_atms = triplet.zap('CA')
            CB_atms = triplet.zap('CB')

            NTdebug("%s %s %s %s" % (res, triplet, CA_atms, CB_atms))

            if None in CB_atms: # skip Gly for now
                NTdebug('Skipping %s' % res)
            else:
                d1 = Dihedral(res, 'Cb4N', range=[0.0, 360.0])
                d1.atoms = [CB_atms[0], CA_atms[0], CA_atms[1], CB_atms[1]]
                d1.calculateValues()
                res['Cb4N'] = d1 # append dihedral to residue

                d2 = Dihedral(res, 'Cb4C', range=[0.0, 360.0])
                d2.atoms = [CB_atms[1], CA_atms[1], CA_atms[2], CB_atms[2]]
                d2.calculateValues()
                res['Cb4C'] = d2 # append dihedral to residue

                bb = getDeepByKeys(res, WHATIF_STR, BBCCHK_STR, VALUE_LIST_STR, 0) # check first one.
                if bb == None:
                    NTdebug('Skipping without BB %s' % res)
                    continue

                if d1.cv < 0.03 and d2.cv < 0.03: # Only include structured residues
                    for i in range(mCount): # Consider each model individually
    #                    bb = res.Whatif.bbNormality.valueList[i]
                        bb = getDeepByKeys(res, WHATIF_STR, BBCCHK_STR, VALUE_LIST_STR, i)
                        if bb == None:
                            NTdebug('Skipping without BB %s' % res)
                            continue
                        angles = NTlist() # store phi, psi, chi1, chi2
                        for angle in ['PHI', 'PSI', 'CHI1', 'CHI2']:
                            if res.has_key(angle):
                                angles.append(res[angle][i])
                            else:
                                angles.append(0.0)
                        #end for
                        if bb < 20.0: # Arbitrary 20 bb occurences as cuttoff for now
                            fprintf(fpBad, '%4d   %7.2f  %7.2f  %7.2f  %s  %s %s\n', res.resNum, d1[i], d2[i], bb, angles.format("%7.2f  "), res, res.dssp.consensus)
                        else:
                            fprintf(fpGood, '%4d   %7.2f  %7.2f  %7.2f  %s  %s %s\n', res.resNum, d1[i], d2[i], bb, angles.format("%7.2f  "), res, res.dssp.consensus)
                #end if
            #end if
        #end if
    #end for
    fpBad.close()
    fpGood.close()

    fn = "allRestype_d1d2." + graphicsFormat
    ps.hardcopy(fn, graphicsFormat)
#        plot.show()

def plotDihedralD1D2byResType():
    showDataPoints = False
    dihedralName1 = 'Cb4N'
    dihedralName2 = 'Cb4C'
#    graphicsFormat = "png"

    outputDir = os.path.join(cingDirTmp, 'd1d2')
    if not os.path.exists(outputDir):
        os.mkdir(outputDir)
#        outputDir = cingDirTmp
    os.chdir(outputDir)

#        ssType = 'E'
#        resType = 'GLY'
#        for ssType in histRamaBySsAndResType.keys():
#            ssTypeForFileName = ssType.replace(' ', '_')
    ssTypeFixed = 'H'
    resTypeListSkip = ['CSB', 'GLUH', 'HISE', 'HISH', 'MSE', '', '', '', '', '']
    for resType in hPlot.histd1d2BySsAndResType[ssTypeFixed].keys():
#            if resType != 'ARG': # for testing enable filtering.
#                continue
        if resType in resTypeListSkip:
            continue
        titleStr = 'd1d2 ' + resType
        NTmessage("plotting: %s" % titleStr)
#            hist = histd1d2BySsAndResType[ssType][resType]

        ps = NTplotSet() # closes any previous plots
        ps.hardcopySize = (500, 500)

#                residueName = resType + ""
        x = NTlist(-45, -80, 125) # outside the range.
        y = NTlist(-65, -63, -125)

        # important to switch to temp space before starting to generate files for the project.
        project = Project('testPlotHistoDihedrald1d2')
        plotparams1 = project.plotParameters.getdefault(dihedralName1, 'dihedralDefault')
        plotparams2 = project.plotParameters.getdefault(dihedralName2, 'dihedralDefault')

        x.limit(plotparams1.min, plotparams1.max)
        y.limit(plotparams2.min, plotparams2.max)

        plot = NTplot(title=titleStr,
          xRange=(plotparams1.min, plotparams1.max),
          xTicks=range(int(plotparams1.min), int(plotparams1.max + 1), plotparams1.ticksize),
          xLabel=dihedralName1,
          yRange=(plotparams2.min, plotparams2.max),
          yTicks=range(int(plotparams2.min), int(plotparams2.max + 1), plotparams2.ticksize),
          yLabel=dihedralName2)
        ps.addPlot(plot)

        # Plot a density background
        histList = []
        ssTypeList = hPlot.histd1d2BySsAndResType.keys() #@UndefinedVariable
        ssTypeList.sort() # in place sort to: space, H, S
        for ssType in ssTypeList:
            hist = getDeepByKeys(hPlot.histd1d2BySsAndResType, ssType, resType) #@UndefinedVariable
            if hist != None:
                NTdebug('appending [%s]' % ssType)
                histList.append(hist)
        if histList:
            plot.dihedralComboPlot(histList)
        if showDataPoints:
            myPoint = plusPoint.copy()
            myPoint.pointColor = 'green'
            myPoint.pointSize = 6.0
            myPoint.pointEdgeWidth = 1.0
            myPoint.fill = False
            if resType == 'GLY':
                myPoint.pointType = 'triangle'
            if resType == 'PRO':
                myPoint.pointType = 'square'
            plot.points(zip(x, y), attributes=myPoint)
#            fn = os.path.join('bySsAndResType', ( ssTypeForFileName+"_"+resType+"."+graphicsFormat))
#            fn = os.path.join('byResType', ( resType+"."+graphicsFormat))
#        fn = resType + "_d1d2." + graphicsFormat
#        ps.hardcopy(fn, graphicsFormat)
        plot.show()


if __name__ == "__main__":
    cing.verbosity = verbosityError
    cing.verbosity = verbosityDebug
    if True:
#        entryList = "1y4o".split()
    #    entryList = "1tgq 1y4o".split()
        entryList = "1brv".split()
        for entryId in entryList:
            plotForEntry(entryId)
    if False:
        plotDihedralD1_1d()
    if False:
#        doOnlyOverall = False
        plotDihedralD1_2d(True)
#        plotDihedralD1_2d(False)
    if False:
        m = plotHistogramOverall()
    if False:
        plotDihedral2DRama()
