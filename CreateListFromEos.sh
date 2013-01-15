#!/bin/bash

#for i in * ; do echo -n "$i   "; /afs/cern.ch/project/eos/installation/0.2.5/bin/eos.select ls /store/user/amarini/zjets/${i} | cut -d'_' -f2 | sort -n | uniq | wc -l  ; done

declare -a DIRS=("DoubleMu_Run2012A-13Jul2012-v1_AOD" "DoubleMu_Run2012B-13Jul2012-v4_AOD" "DoubleMu_Run2012C-PromptReco-v2_AOD" "DoubleMu_Run2012D-PromptReco-v1_AOD")
declare -a NJOBS=(162 750 1049 1143)

NDIRS=${#DIRS[@]}
echo Process $NDIRS directories
for ((i=0;i<NDIRS;i++)); do
	OUTFILES=$(/afs/cern.ch/project/eos/installation/0.2.5/bin/eos.select ls /store/user/amarini/zjets/${DIRS[i]} | cut -d'_' -f2 | sort -n | uniq | wc -l  ; )
	LIST1=$(/afs/cern.ch/project/eos/installation/0.2.5/bin/eos.select ls /store/user/amarini/zjets/${DIRS[i]} | cut -d'_' -f2 | sort -n | uniq | tr '\n' ' ' ; )
	#LIST2=$(echo $LIST1 | perl -lane '($a,$b)=@F[0,-1];$,=" ";@h{@F}=();print grep!exists$h{$_},$a..$b' )
	LIST2=$(echo $LIST1 | perl -lane '$,=" ";@h{@F}=();print grep!exists$h{$_},1..'${NJOBS[i]} )
	
	echo -e "\033[01;31m${DIRS[i]}\033[00m ${OUTFILES}/${NJOBS[i]}"
	echo -n "JOBS processed: "
		echo $LIST1 | tr ' ' ',' | sed "s/,/\n/g" | while read num; do
			    if [[ -z $first ]]; then
			        first=$num; last=$num; continue;
			    fi
			    if [[ num -ne $((last + 1)) ]]; then
			        if [[ first -eq last ]]; then echo $first; else echo $first-$last; fi
			        first=$num; last=$num
			    else
			        : $((last++))
			    fi
			done | paste -sd ","
		echo
	echo -n "JOBS missing: "
		echo $LIST2 | tr ' ' ','| sed "s/,/\n/g" | while read num; do
			    if [[ -z $first ]]; then
			        first=$num; last=$num; continue;
			    fi
			    if [[ num -ne $((last + 1)) ]]; then
			        if [[ first -eq last ]]; then echo $first; else echo $first-$last; fi
			        first=$num; last=$num
			    else
			        : $((last++))
			    fi
			done | paste -sd ","
		echo
	
done
