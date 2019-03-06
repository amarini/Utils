#/bin/bash
#eos='/afs/cern.ch/project/eos/installation/0.3.84-aquamarine/bin/eos.select'
eos='/afs/cern.ch/project/eos/installation/0.3.15/bin/eos.select'
$eos quota | grep -A 3 '/eos/cms/store/user/' | head -n 4 
$eos root://eosuser quota | grep -A 3 '/eos/user/' | head -n 4
