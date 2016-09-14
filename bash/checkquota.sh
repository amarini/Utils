#!/bin/bash

GUARD=$HOME/.quota

QUOTA=$(fs lq /afs/cern.ch/work/${USER:0:1}/$USER | grep work.amarini | tr -s ' '   | cut -d ' ' -f4 | tr -d '%')

[[ $QUOTA < 85 ]] && [ -f $GUARD ] && rm $GUARD

[ -f $GUARD ] && exit 0

echo "QUOTA is $QUOTA"
[[ $QUOTA > 90 ]] && { echo "QUOTA WARNING" ; echo "AFS Quota warning: is $QUOTA" | mail -s "AFS Quota WARNING" $USER@cern.ch ; touch $GUARD ; } || echo "everything is fine"


