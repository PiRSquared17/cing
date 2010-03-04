"""
python $CINGROOT/python/cing/Scripts/getPhiPsiWrapper.py

Use below to find the entries done and todo:

"""
from cing import cingDirScripts
from cing import cingDirTmp
from cing.Scripts.doScriptOnEntryList import doScriptOnEntryList
import cing
import os

Ramachandran = 'Ramachandran'
Janin = 'Janin'
d1d2 = 'd1d2'
#dihedralTodo = Ramachandran
#dihedralTodo = Janin
dihedralComboTodo = d1d2
# Throw away the worst 10 % within the chain.
DEFAULT_BFACTOR_PERCENTAGE_FILTER = 5 # DEFAULT from Gert: 10
# Then after the above check throw away additionaly any residue above 20
DEFAULT_MAX_BFACTOR = 60 # Default from Gert 40; Sander suggested to take 2 sd instead perhaps.
BFACTOR_COLUMN = 7
IDX_COLUMN = 8

subdir = None
if dihedralComboTodo == Ramachandran:
    subdir = 'phipsi_wi_db'
elif dihedralComboTodo == Janin:
    subdir = 'chi1chi2_wi_db'
elif dihedralComboTodo == d1d2:
    subdir = 'd1d2_wi_db'

def main():
    """This is a potentially dangerous script. It took JFD an hour one time
    to realize it was called inadvertently by not having it wrappen in a function.
"""


    # parameters for doScriptOnEntryList
    startDir              = os.path.join(cingDirTmp,     subdir)
    pythonScriptFileName  = os.path.join(cingDirScripts, 'getPhiPsi.py')
#    entryListFileName     = os.path.join(cingDirScripts, 'data', 'PDB.LIS')
#    entryListFileName     = os.path.join(cingDirScripts, 'data', 'PDB_WI_SELECT_Rfactor_2.1_Res2.0_2009-02-28.LIS')
    entryListFileName     = os.path.join(cingDirScripts, 'data', 'PDB_todo.txt')

    START_ENTRY_ID                 =0 # default 0
    MAX_ENTRIES_TODO               =1 # default a ridiculously large number like 999999

    doScriptOnEntryList(pythonScriptFileName, entryListFileName, startDir,
                        max_time_to_wait = 240, # 1gkp  took over 120
                        processes_max                  = 8,   # default 3
                        START_ENTRY_ID                 = START_ENTRY_ID, # default 0
                        MAX_ENTRIES_TODO               = MAX_ENTRIES_TODO # default a ridiculously large number like 999999
                        )

if __name__ == '__main__':
    cing.verbosity = cing.verbosityDebug
    main()