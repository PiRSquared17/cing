# python -u $CINGROOT/python/cing/Scripts/validateForCASD_NMR.py
from cing import cingDirScripts
from cing.NRG import CASD_NMR_BASE_NAME
from cing.NRG.PDBEntryLists import writeEntryListToFile
from cing.Scripts.doScriptOnEntryList import doScriptOnEntryList
from cing.Scripts.validateEntry import ARCHIVE_TYPE_BY_CH23_BY_ENTRY
from cing.Scripts.validateEntry import PROJECT_TYPE_CCPN
import cing
import os

cing.verbosity = cing.verbosityDebug
#cing.verbosity = cing.verbosityDefault

# parameters for doScriptOnEntryList
startDir = '/Library/WebServer/Documents/%s' % CASD_NMR_BASE_NAME
pythonScriptFileName = os.path.join(cingDirScripts, 'validateEntry.py')

if False:
    entryListFileName = os.path.join(startDir, 'list', 'entry_list_all.csv')
#    entryListFileName = os.path.join(startDir, 'list', 'entry_list_redo.csv')
else:
    entryListFileName = os.path.join(startDir, 'list', 'entry_list_single.csv')
    entryList = 'PGR122AParis2'.split()
    writeEntryListToFile(entryListFileName, entryList)

inputDirCASD_NMR = 'file:///Users/jd/%s/data' % CASD_NMR_BASE_NAME
outputDir = startDir

extraArgList = (inputDirCASD_NMR, outputDir, '.', '.', ARCHIVE_TYPE_BY_CH23_BY_ENTRY, PROJECT_TYPE_CCPN)

doScriptOnEntryList(pythonScriptFileName,
                    entryListFileName,
                    startDir,
                    processes_max = 2,
                    delay_between_submitting_jobs = 5, # why is this so long? because of time outs at tang?
                    max_time_to_wait = 3600, # 1y4o took more than 600. This is one of the optional arguments.
                    # 1ai0 took over 20 min; let's set this to 1 hour
                    START_ENTRY_ID = 0,
                    MAX_ENTRIES_TODO = 100,
                    expectPdbEntryList = False,
                    extraArgList = extraArgList)
