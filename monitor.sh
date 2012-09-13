#!/bin/bash

CDIR=${PWD}
TMPFILE=/tmp/amarini/monitor_$RANDOM.txt
TMPFILE2=/tmp/amarini/monitor2_$RANDOM.txt

DIRS=$( echo RUN2012A-06Aug/{JetHT,PhotonHad}/Run2012A_recover_06Aug2012_v1 RUN2012C/{JetHT,PhotonHad}/Run2012C_PromptReco_v{1,2} RUN2012AB/{JetHT,PhotonHad}/Run2012{A,B}_13Jul2012_v1 )

STATUS="Aborted"
EXITCODES="8021 60307 60317"

for dir in ${DIRS} ; do 

[ -f "$TMPFILE" ] && rm ${TMPFILE}

echo Entering Directory "$dir" 
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
echo -e "\033[01;36mGet ${LIST}\033[00m"
	crab -get ${LIST} -c ${dir}
echo -e "\033[01;36mResubmit ${LIST}\033[00m"
	crab -resubmit ${LIST} -c ${dir}

echo 
done
