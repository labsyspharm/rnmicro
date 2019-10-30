#Purpose: check and create folder directory system for CyCif Pipeline if not available
#to run: python check_folder.py ['Base folder']
#example:  python check_folder.py ./example_data/

#libraries
from __future__ import print_function
try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib
import os
import sys
#sys.argv[1]='./example_data'

#grab all folders within systems argument
samples = next(os.walk(sys.argv[1]))[1]
# log folder is where run logs are stored, exclude from folder to execute
samples = [n for n in samples if not ('log' in n)]

# Create/check the desired folder structure for future pipeline steps
folders_to_make = ['dearray/masks','prob_maps','segmentation','feature_extraction',
                   'clustering/consensus', 'clustering/drclust', 'clustering/pamsig','cell_states',
                   'illumination_profiles','registration']
for d in samples:
    print('Making folder structure for sample:', d)
    for f in folders_to_make:
        print('Making folder structure:',f)
        try:
            os.makedirs(str(sys.argv[1])+'/'+d+'/'+f)
        except:
            print('Folder '+f+' already exists for '+d)