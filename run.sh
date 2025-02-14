#!/bin/bash

root=$(pwd)

echo "Running ycalc with varying azimuth angle.."
python $root/simulations/zeeman_ycalc_azi.py $root
echo "Running ycalc for synthetic retrieval.." 
python $root/simulations/ycalc.py $root

