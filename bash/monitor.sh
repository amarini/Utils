#!/bin/bash

CDIR=${PWD}
TMPFILE=/tmp/$(whoami)/monitor_$RANDOM.txt
TMPFILE2=/tmp/$(whoami)/monitor2_$RANDOM.txt

DIRS="DiPhotonJets/DiPhotonJets GluGluToHToGG_M-125/GluGluToHToGG_M-125"
DIRS="GJet_Pt40_doubleEMEnriched/GJet_Pt40_doubleEMEnriched"

STATUS="Aborted"
EXITCODES="8021 60307 60317 50664 Cancelled"

#options

#-submit
#-check
#-exitcodes
#-dirs

CHECK=1;
SUBMIT=0;
RESUBMIT=1;
MAXJOBSUB=500

function usage
{
echo "Original author: Andrea Carlo Marini (2012)"
echo "Usage: $0"
echo "-s | --submit: SUBMIT=true CHECK = false"
echo "-c | --check: CHECK=true"
echo "-r | --resubmit: RESUBMIT=true (default)"
echo "-n | --noresubmit"
echo "-d | --dirs  DIR: directories to work on"
echo "-e | --exitcodes EXIT: exitcodes to parse"
echo "-h | --help: print this message and exit. Give the values of the previously set pars"
echo
echo -e "\033[31;03m CURRENT VALUES: \033[00m"
echo -e "\tSTATUS:\t$STATUS"
echo -e "\tEXITCODES:\t$EXITCODES"
echo -e "\tDIRS:\t$DIRS"
echo -e "\tCHECK:\t$CHECK"
echo -e "\tSUBMIT:\t$SUBMIT"
echo -e "\tRESUBMIT:\t$RESUBMIT"
echo -e "\tTMPFILE:\t$TMPFILE"
echo -e "\tTMPFILE2:\t$TMPFILE2"

echo 
}

#function get_par
#{
    set -- $(getopt -o sihd:e:rn --long submit,check,help,dirs:,exitcodes:,resubmit,nocheck,noresubmit -- "$@" )

    while true ; do
    case $1 in
        -s | --submit ) 
                                SUBMIT=1;
				CHECK=0;
                                ;;
        -c | --check )    	CHECK=1;
                                ;;
        -h | --help )           usage
                                exit
                                ;;
	-d | --dirs ) 		DIRS=$(echo $2| tr ',' ' ' | tr -d "'" ) ; shift ;;
	-e | --exitcodes ) 	EXITCODES=$(echo $2 | tr ',' ' ' | tr -d "'") ; shift ;;
	-r | --resubmit) 	RESUBMIT=1 ;;
	-n | --noresubmit) 	RESUBMIT=0 ;;
	--) 			break;;
        * )                     usage
                                exit 1
    esac
    shift
    done
#}

function resubmit
{
  LIST=$1
#convert list with no range and count
NUM=$(echo $LIST | sed 's/,/\n/g' | sed 's/-/\ /g' | while read min max; do seq $min ${max:-$min} ; done  | sort -n | uniq | wc -l )
LIST2=$(echo $LIST | sed 's/,/\n/g' | sed 's/-/\ /g' | while read min max; do seq $min ${max:-$min} ; done  | sort -n | uniq )

for count in `seq 0 ${MAXJOBSUB} $NUM` ; do 
	LIST3=$(echo "${LIST2}" | head -n $((count+ MAXJOBSUB)) | tail -n ${MAXJOBSUB} | tr '\n' ',' | tr ' ' ',' | sed 's/,$//')
#eventually we have a double count for the last 
	echo -e "Going to get \033[01;31m${NUM}\033[00m Jobs"
	echo -e "\033[01;36mGet ${LIST3}\033[00m"
		crab -get ${LIST3} -c ${dir}
	echo -e "\033[01;36mResubmit ${LIST3}\033[00m"
		crab -resubmit ${LIST3} -c ${dir}
	
	echo 
	done

}


function check
{
for dir in ${DIRS} ; do 

[ -f "$TMPFILE" ] && rm ${TMPFILE}

echo Entering Directory "$dir" 
	 crab -status -c ${dir} 2>/dev/null  > /dev/null
	 crab -get -c ${dir} 2>/dev/null  > /dev/null
	 crab -status -c ${dir} 2>/dev/null  > $TMPFILE2

	for stat in $STATUS ; do 
		echo -n -e "\033[01;31mFiles in status ${stat}: \033[00m"
		cat ${TMPFILE2}|  grep -A 2 ">>>>>>>>> .* ${stat}\ *$" | tail -n 1  |  cut -d ':' -f 2 | tee -a ${TMPFILE} | tr -d '\n'
		echo ""
	done
	for stat in ${EXITCODES} ; do 
		echo -n -e "\033[01;31mFiles in status ${stat}: \033[00m"
		cat ${TMPFILE2} |  grep -A 1 ">>>>>>>>> .* ${stat}\ *$" | tail -n 1  |  cut -d ':' -f 2 | tee -a ${TMPFILE} | tr -d '\n'
		echo ""
	done
		echo -n -e "\033[01;32mFiles in status 0: \033[00m"
		cat ${TMPFILE2} |  grep -A 1 ">>>>>>>>> .* 0\ *$" | tail -n 1  |  cut -d ':' -f 2  | tr -d '\n' 
		echo ""
		echo -n -e "\033[01;33mFiles in Running: \033[00m"
		cat ${TMPFILE2} |  grep -A 1 ">>>>>>>>> .* Running\ *$" | tail -n 1  |  cut -d ':' -f 2 | tr -d '\n'  
		echo ""
		echo -n -e "\033[01;33mFiles in Submitted: \033[00m"
		cat ${TMPFILE2} |  grep -A 1 ">>>>>>>>> .* Submitted\ *$" | tail -n 1  |  cut -d ':' -f 2 | tr -d '\n' 
		echo ""

[ -f ${TMPFILE} ] || continue;
LIST=$(cat ${TMPFILE} | tr '\n' ',' | tr -d ' ' | sed 's/,$//g')
[ "${LIST}" == "" ] && continue;

	[ $RESUBMIT -gt 0 ] && resubmit "${LIST}"

done

}

function submit
{
for dir in $DIRS; do
echo "Entering in dir $dir"
echo crab -status -c $dir > $TMPFILE2
crab -status -c $dir > $TMPFILE2
LIST=$(cat $TMPFILE2 | grep '[0-9]\+\ .*Created.*Created' | tr '\t' ' '| tr -s ' '| cut -d ' ' -f1 | tr '\n' ',' |  tr -d ' '| sed 's/,$//g' ) 
#convert list with no range and count
NUM=$(echo $LIST | sed 's/,/\n/g' | sed 's/-/\ /g' | while read min max; do seq $min ${max:-$min} ; done  | sort -n | uniq | wc -l )
LIST2=$(echo ${LIST} | sed 's/,/\n/g' | sed 's/-/\ /g' | while read min max; do seq $min ${max:-$min} ; done  | sort -n | uniq )

#echo LIST $LIST
#echo NUM $NUM
#echo "LIST2 $LIST2"

echo -e "Going to submit \033[01;31m${NUM}\033[00m Jobs"
for count in `seq 0 ${MAXJOBSUB} $NUM` ; do 
	LIST3=$(echo "${LIST2}" | head -n $((count+ MAXJOBSUB)) | tail -n ${MAXJOBSUB} | tr '\n' ',' | tr ' ' ',' | sed 's/,$//')
#eventually we have a double count for the last 
	echo -e "\033[01;36mSubmit ${LIST3}\033[00m"
		crab -submit ${LIST3} -c ${dir}
	
	echo 
	done
done
}

#main
#get_par $*
[ $CHECK -gt 0 ] && check ;
[ $SUBMIT -gt 0 ] && submit ;
