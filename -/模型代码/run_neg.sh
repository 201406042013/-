#!/bin/sh


for i in 60 70 80 90 100 
do
	for neg in 6 7 8 9 10 
	do
		for min_count in  2 3
		do		
			for dim in 80 100 120 140 160
			do			
				python train.py -epoch $i  -dim $dim -min_count $min_count 
				python test_for_all.py
			done		
		done
	done	
done	




