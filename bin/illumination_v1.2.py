#Purpose: generate illumination files using imageJ
#to run:  python illumination.py ['path to sample folder']
#example: python illumination ./example_data/image_1

#library
from __future__ import print_function
from subprocess import call
try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib
import sys
import os
import datetime
import glob

#functions
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

#define all inputs
#sys.argv=['tmp'] #local testing
#sys.argv.append(os.path.normpath('/home/bionerd/Dropbox/@Dana Farber/CyCif/git/mcmicro/example_data/image_1')) #local testing
path_exp = pathlib.Path('/'.join([str(sys.argv[1])]))
#dictionary of parameters
#sys.argv.append({'lambda_flat': 0.1, 'lambda_dark': 0.01, 'estimate_flat_field_only': False, 'max_number_of_fields_used': 'None'}) #local testing
parameters = dict(sys.argv[2])

#lambda_flat = '0.1'
#lambda_dark = '0.01'
#placeholder variables, not used at the moment
#estimate_flat_field_only = 'False'
#max_number_of_fields_used = 'None'

#define raw file variable
raw_file   =  ''.join(['*'  + microscope_check(path_exp)])
file_type = microscope_check(path_exp)
raw_dir = path_exp / 'raw_files'
files_exp = sorted(raw_dir.glob(raw_file))

#if len(files_exp) == 0:
#    files_exp = sorted(raw_dir.glob('*xdce'))
#    file_type = 'xdce'
if len(files_exp) == 0:
    print('No rcpnl files found in', str(raw_dir))

print('Processing files in', str(raw_dir))
print(datetime.datetime.now())
print()
ffp_list = []
dfp_list = []
for j in files_exp:
    print('\r    ' + 'Generating ffp and dfp for ' + j.name)
    ffp_file_name = j.name.replace(file_type, '-ffp.tif')
    dfp_file_name = j.name.replace(file_type, '-dfp.tif')
    illumination_dir = path_exp / 'illumination_profiles'
    if (path_exp / 'illumination_profiles' / ffp_file_name).exists() and (
            path_exp / 'illumination_profiles' / dfp_file_name).exists():
        print('\r        ' + ffp_file_name + ' already exists')
        print('\r        ' + dfp_file_name + ' already exists')
    else:
        if not illumination_dir.exists():
            illumination_dir.mkdir()
        call(
            "/home/ajn16/softwares/Fiji.app/ImageJ-linux64 --ij2 --headless --run /home/ajn16/softwares/Fiji.app/plugins/imagej_basic_ashlar.py \"filename='%s', output_dir='%s', experiment_name='%s', lambda_flat=%s, lambda_dark=%s\"" % (
            str(j), str(illumination_dir), j.name.replace(file_type, ''), parameters.get('lambda_flat'), parameters.get('lambda_dark')),
            shell=True)
        print('\r        ' + ffp_file_name + ' generated')
        print('\r        ' + dfp_file_name + ' generated')
    ffp_list.append(str(illumination_dir / ffp_file_name))
    dfp_list.append(str(illumination_dir / dfp_file_name))