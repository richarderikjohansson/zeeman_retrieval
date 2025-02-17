#!/bin/bash

root=$(pwd)

echo "Running ycalc with varying azimuth angle.."
python $root/pyarts/zeeman_ycalc_azi.py $root
echo "Running ycalc for synthetic retrieval.." 
python $root/pyarts/ycalc.py $root
echo "Running retrievals.."
python $root/pyarts/ret.py $root 
