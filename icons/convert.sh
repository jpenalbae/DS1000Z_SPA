#!/bin/bash

for i in `ls svg/*.svg`;
do
   convert -background transparent $i `basename $i .svg`.png
done
