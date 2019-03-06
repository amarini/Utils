#!/bin/bash

FNAME=$1
WDIR=/tmp/$USER/
TMPFILE=$WDIR/myfile.pdf
TMPFILE2=$WDIR/myfile2.pdf
echo "-> Removing preliminary from $FNAME"
[ -f $FNAME ] || { echo "No such file or directory."; exit 0; }

for ((i=0;;i++));
do
    BKNAME="${FNAME}.$i"
    [ -f $BKNAME ] || { cp -v $FNAME $BKNAME; break; }
done

MYSERVER="k2.sns.it"

[ "$MYSERVER" == "" ] && {
    #uncompress
    pdftk $FNAME output $TMPFILE uncompress 

    #sed
    sed -i'' 's:Preliminary::g' $TMPFILE
    #compress
    pdftk $TMPFILE output $TMPFILE2 compress 

    # move back
    mv -v $TMPFILE2 $FNAME
}

[ "$MYSERVER" == "" ] || {
    ssh $MYSERVER mkdir $WDIR
    scp $FNAME $MYSERVER:$TMPFILE
    ssh $MYSERVER "pdftk $TMPFILE output $TMPFILE2 uncompress; sed -i'' 's:Preliminary::g' $TMPFILE2 ; rm $TMPFILE ; pdftk $TMPFILE2 output $TMPFILE compress"
    scp $MYSERVER:$TMPFILE $FNAME
}


