inputOBJ=../../data/guide_strands/sideSwatchDroopSequence/70.obj
scalpOBJ=../../data/scalp_clouds/sideSwatchScalp.obj
groupingCSV=../../data/matching_csvs/sideSwatchGuides-sideSwatchScalp-groupingsr30.csv
outputOBJ=../../data/full_strands/${1}.obj

python3 wispify.py ${inputOBJ} ${scalpOBJ} ${groupingCSV} ${outputOBJ}