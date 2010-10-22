#!/bin/tcsh
# Add to startup scripts:
# $CINGROOT/scripts/vcing/startVC.csh

# Author: Jurgen F. Doreleijers
# Thu Oct 14 23:56:36 CEST 2010

source $0:h/settings.csh

set doSvnUpdate = 1
set doTest      = 0
set doRun       = 1

##No changes required below this line
###############################################################################

# Requirements below (kept in sync manually with nrgCing.csh etc.)
#limit cputime   176000  # Maximum number of seconds the CPU can spend; needed to be upped for 2ku1 which took over 8 hrs clocktime. 24 hrs.
limit filesize   500m   # Maximum size of any one file
#limit datasize  1000m   # Maximum size of data (including stack)
limit coredumpsize 0    # Maximum size of core dump file
umask 2                 # The files created will be having special permissions.
set initialSleep = 10

set date_string = (`date "+%Y-%m-%d_%H-%M-%S"`) # gives only seconds.
set epoch_string = (`java Wattos.Utils.Programs.GetEpochTime`)
set time_string = $date_string"_"$epoch_string
set log_file = "startVC_$time_string.log"
#set tmp_dir = mktemp -d -t $0
#cd $tmp_dir
cd

echo "Startup script for VC at: $time_string on host: $HOST" >& $log_file
cat $log_file
# update log file on target of course this bits itself but it seems to be fine.
scp -q $log_file $TARGET_SDIR

if ( $isProduction ) then
    echo "Sleeping for $initialSleep seconds so system can come up with network etc." >>& $log_file
    sleep $initialSleep # give 2 minutes for getting systems up. If the machine autoshuts this might have to be longer.
endif

if ( $doSvnUpdate ) then
    # I wonder if svn updating this file will corrupt my fine little system here by biting it's own tail?
    cd $CINGROOT
    echo "Doing svn update." >>& $log_file
    svn --force update --non-interactive . >>& $log_file
    cd
endif
scp -q $log_file $TARGET_SDIR


# TEST routines
if ( $doTest ) then
    echo "First ls" >>& $log_file
    ls -al >& ls.log
    touch abcdef
    echo "Second ls" >>& $log_file
    ls -al >& ls2.log
    tar -cvzf ls2_$time_string.tgz ls2.log >>& $log_file
    scp $TARGET_PORT ls2_$time_string.tgz $TARGET_SDIR >>& $log_file
    scp -q $TARGET_PORT $log_file $TARGET_SDIR
endif

if ( $doRun ) then
    echo "Doing run." >>& $log_file
    $CINGROOT/python/cing/Scripts/vCing/vCing.py runSlave >>& $log_file
    # update log file on target
    scp -q $TARGET_PORT $log_file $TARGET_SDIR
endif

set date_string = (`date "+%Y-%m-%d_%H-%M-%S"`) # gives only seconds.
set epoch_string = (`java Wattos.Utils.Programs.GetEpochTime`)
set time_string = $date_string"_"$epoch_string
echo "DONE at:                  $time_string"  >>& $log_file
scp -q $TARGET_PORT $log_file $TARGET_SDIR
echo "DONE and this message will not show up anywhere I'm afraid."

#shutdown -h now NOT NEEDED BUT ALSO FAILS BECAUSE REQUIRES PASSWORD.