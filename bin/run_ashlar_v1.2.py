#library
from __future__ import print_function
import csv
from subprocess import call
try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib
import argparse
import os
import datetime
import sys
import glob

#function
def text_to_bool(text):
    return False \
        if not str(text) \
        else str(text).lower() in '1,yes,y,true,t'
def path_to_date(path):
    return os.path.getmtime(str(path))
#expand the number of microscope raw files types searched for
def microscope_check(current_sample):
    if len(glob.glob(str(current_sample) + '/raw_files/*.ome.tiff')) != 0:
        print('Exemplar Dataset Used')
        output = '.ome.tiff'
        return(output)
    if len(glob.glob(str(current_sample) + '/raw_files/*.rcpnl')) != 0:
        print('Rarecyte Microscope')
        output = '.rcpnl'
        return(output)
    else:
        output = 'notfound' #if neither found, still needs to return a string
        return(output)

#local testing
#sys.argv=['tmp'] #local testing
#sys.argv.append(os.path.normpath('/home/bionerd/Dropbox/@Dana Farber/CyCif/git/mcmicro/example_data/image_1'))
#sys.argv.append('/n/groups/lsp/cycif/cycif_pipeline_testing_space/mcmicro/environments/ashlar/bin/ashlar')
#sys.argv.append(str(['-m','30','--filter-sigma','0']))

#global variables from input
path_exp = pathlib.Path('/'.join([str(sys.argv[1])]))
ashlar_path = pathlib.Path(str(sys.argv[2]))
#parameters = eval(str(sys.argv[3])) #converting string to list (assumption is list to begin with)
parameters = ''.join(sys.argv[3:])
parameters = parameters[1:-1].split(',')



print('Data Path passed:',path_exp)
print('Ashlar Path passed:',ashlar_path)
print('Paramters passed',str(parameters))

# global variables
raw_file   =  ''.join(['*'  + microscope_check(path_exp)])
file_type = microscope_check(path_exp)
raw_dir = path_exp / 'raw_files'
files_exp = sorted(raw_dir.glob(raw_file))

print('Processing files in', str(raw_dir))
print(datetime.datetime.now())
print()

ffp_list = []
dfp_list = []
for j in files_exp:
    # print('\r    ' + 'Generating ffp and dfp for ' + j.name)
    ffp_file_name = j.name.replace(file_type, '-ffp.tif')
    dfp_file_name = j.name.replace(file_type, '-dfp.tif')
    illumination_dir = path_exp / 'illumination_profiles'
    ffp_list.append(str(illumination_dir / ffp_file_name))
    dfp_list.append(str(illumination_dir / dfp_file_name))

print('Run ashlar')
print(datetime.datetime.now())
print()
out_dir = path_exp / 'registration'
test_sample = out_dir / '.ome.tif'

# test if already run, if not run

if not test_sample.exists():

    input_files = ' '.join([str(f) for f in files_exp])

    #command for run
    command = 'python ' + str(ashlar_path) + ' ' + input_files + ' ' + ' '.join(parameters) + ' -o ' + str(out_dir)

    #if text_to_bool(exp['Pyramid']): #[TODO] add to parameter yaml
    command += ' --pyramid -f ' + path_exp.name + '.ome.tif'

    #if text_to_bool(exp['Correction']):  [TODO] add to parameter yaml
    ffps = ' '.join(ffp_list)
    dfps = ' '.join(dfp_list)
    command += ' --ffp ' + ffps + ' --dfp ' + dfps

    #save the list order for rcpnl, ffp, and dfp
    print([i for i in files_exp])
    print([i for i in ffp_list])
    print([i for i in dfp_list])

    #save the command passed to ashlar
    print(command)
    call(command, shell=True)
    print(datetime.datetime.now())
else:
    print('Sample '+test_sample+ 'exists')
