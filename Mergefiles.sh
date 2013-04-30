

DIR0=$1
DIR1=$2

echo "Going to copy each file in $DIR0 in the right position of $DIR1"
read

find $DIR0 -maxdepth 1  -type f | while read file ; do

NUM=$(find $DIR1 -name ${file##*/} | wc -l)
if [ $NUM -eq 1 ] ;then
DEST=$(find $DIR1 -name ${file##*/} )
echo cp $DEST $DEST.bk
echo cp $file $DEST
else
echo more than one/none Match for file $file:
find $DIR1 -name ${file##*/} 
fi;

done
