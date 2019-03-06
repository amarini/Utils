#!/bin/bash

BASE=Hplus
DIR=v11

mkdir ~/www/cms-private/$BASE/
rsync -avP $DIR/ ~/www/cms-private/$BASE/$DIR/

for i in ~/www/cms-private/$BASE/$DIR/*/*pdf; 
do 
	convert -density 300 -trim +repage -gravity center $i -quality 90 -background white -flatten ${i%%.pdf}.png ;
done
