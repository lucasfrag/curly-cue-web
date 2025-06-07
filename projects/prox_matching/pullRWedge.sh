scalpName=sideSwatchScalp.obj
guideName=sideSwatchGuides.obj
outF=../../data/matching_csvs/

python3 prox_matcher.py ../../data/scalp_clouds/${scalpName} ../../data/scalp_clouds/${guideName} --fout ${outF} --nameSuffix r30 --pullR 30
python3 prox_matcher.py ../../data/scalp_clouds/${scalpName} ../../data/scalp_clouds/${guideName} --fout ${outF} --nameSuffix r20 --pullR 20
python3 prox_matcher.py ../../data/scalp_clouds/${scalpName} ../../data/scalp_clouds/${guideName} --fout ${outF} --nameSuffix r10 --pullR 10
python3 prox_matcher.py ../../data/scalp_clouds/${scalpName} ../../data/scalp_clouds/${guideName} --fout ${outF}  --nameSuffix r5 --pullR 5
python3 prox_matcher.py ../../data/scalp_clouds/${scalpName} ../../data/scalp_clouds/${guideName} --fout ${outF} --nameSuffix r2 --pullR 2
python3 prox_matcher.py ../../data/scalp_clouds/${scalpName} ../../data/scalp_clouds/${guideName} --fout ${outF} --nameSuffix r1 --pullR 1
