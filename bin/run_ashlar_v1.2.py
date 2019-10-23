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

#input from path
ashlar_path = pathlib.Path(str(sys.argv[2]))
ashlar_path ='/n/groups/lsp/cycif/cycif_pipeline_testing_space/mcmicro/environments/ashlar/bin/ashlar'

#function
def text_to_bool(text):
    return False \
        if not str(text) \
        else str(text).lower() in '1,yes,y,true,t'
def path_to_date(path):
    return os.path.getmtime(str(path))
def microscope_check(current_sample):
    if len(glob.glob(current_sample + '/raw_files/*.ome.tiff')) != 0:
        print('Exemplar Dataset Used')
        output = 'ome.tiff'
        return(output)
    if len(glob.glob(current_sample + '/raw_files/*.rcpnl')) != 0:
        print('Rarecyte Microscope')
        output = '.rcpnl'
        return(output)
    else:
        output = 'notfound' #if neither found, still needs to return a string
        return(output)

#Possible Parameters to Expose #[TODO] add for Conditional parameter in yaml file
#if text_to_bool(exp['Correction']):
lambda_flat = '0.1'
lambda_dark = '0.01'

#define all directories
#ROI = next(os.walk(sys.argv[1]))[1]

#for i in ROI:
#path_exp = pathlib.Path('/'.join([str(sys.argv[1]),i]))
path_exp = pathlib.Path('/'.join([str(sys.argv[1])]))
raw_file   =  ''.join(['*'  + microscope_check(path_exp)])
file_type = microscope_check(path_exp)
raw_dir = path_exp / 'raw_files'
files_exp = sorted(raw_dir.glob(raw_file))
#file_type = 'rcpnl'
#if len(files_exp) == 0:
#    files_exp = sorted(raw_dir.glob('*xdce'))
#    file_type = 'xdce'
#files_exp.sort(key=path_to_date)

print('Processing files in', str(raw_dir))
print(datetime.datetime.now())
print()
#if text_to_bool(exp['Correction']):
#lambda_flat = '0.1'
#lambda_dark = '0.01'
ffp_list = []
dfp_list = []
for j in files_exp:
    # print('\r    ' + 'Generating ffp and dfp for ' + j.name)
    ffp_file_name = j.name.replace(file_type, '-ffp.tif')
    dfp_file_name = j.name.replace(file_type, '-dfp.tif')
    illumination_dir = path_exp / 'illumination_profiles'
    # if (path_exp / 'illumination_profiles' / ffp_file_name).exists() and (
    #         path_exp / 'illumination_profiles' / dfp_file_name).exists():
    #     print('\r        ' + ffp_file_name + ' already exists')
    #     print('\r        ' + dfp_file_name + ' already exists')
    # else:
    #     if not illumination_dir.exists():
    #         illumination_dir.mkdir()
    #     call(
    #         "/home/ajn16/softwares/Fiji.app/ImageJ-linux64 --ij2 --headless --run /home/ajn16/softwares/Fiji.app/plugins/imagej_basic_ashlar.py \"filename='%s', output_dir='%s', experiment_name='%s', lambda_flat=%s, lambda_dark=%s\"" % (
    #         str(j), str(illumination_dir), j.name.replace('.' + file_type, ''), lambda_flat, lambda_dark),
    #         shell=True)
    #     print('\r        ' + ffp_file_name + ' generated')
    #     print('\r        ' + dfp_file_name + ' generated')
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

    #[TODO] expose ashlar parameters to CyCif Pipeline program which then will be saved as a parameter log
    command = 'python ' + ashlar_path + ' ' + input_files + ' -m 30 -o ' + str(out_dir)

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
