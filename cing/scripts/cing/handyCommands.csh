set list = ( AR3436A AtT13 CGR26A CtR69A ET109Aox ET109Ared HR5537A NeR103A PGR122A VpR247 )
set baseDir = ~/CASD-NMR-CING

foreach x ( $list )
	echo $x
    set ch23 = ( `echo $x | cut -c2-3` )
    mkdir $baseDir/data/$x
    tar -czf $baseDir/data/$x/$x.tgz $x
end

# Sync ALL to production
cd /Users/jd/CASD-NMR-CING
tar -cvf dataTgz.tar data/*/*/*.tgz
scp -P 39676 dataTgz.tar localhost-nmr:/Users/jd/CASD-NMR-CING

cd /Users/jd/CASD-NMR-CING/data
\ls -1l */*/log_doAnn*/*.log

# Sync single entry to production: without the need to decompress on production.
cd ~/CASD-NMR-CING
set x = ET109AoxParis
set ch23 = ( `echo $x | cut -c2-3` )
set dirEntry = data/$ch23/$x
scp -P 39676 $dirEntry/$x.tgz localhost-nmr:/Users/jd/CASD-NMR-CING/$dirEntry

scp -r -P 39676 list Overview localhost-nmr:/Users/jd/CASD-NMR-CING


cd $D/CASD-NMR-CING
scp -r -P 39676 list  localhost-nmr:/Library/WebServer/Documents/CASD-NMR-CING

# Check logs
cd $D/CASD-NMR-CING
grep ERROR */*/log_validateEntry/*.log