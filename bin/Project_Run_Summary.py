#Created: Nathan T. Johnson
#Data: 10.12.2019
#Purpose: Look through project folder after run and summarize what worked
#To Run: python Project_Run_Summary.py [path to project Folder]
#Output: 'CyCif_Run_Summary.csv'

#Libraries
from contextlib import redirect_stdout
import yaml
import os
import sys
import shutil
import glob
import pandas as pd
import subprocess
import re
import time

#expand the number of raw files types searched for
#if RareCyte or Exemplar data not found, returns
def microscope_check(current_sample,master_dir):
    if len(glob.glob(master_dir + '/' + current_sample + '/raw_files/*.ome.tiff')) != 0:
        #print('Exemplar Dataset Used')
        output = 'ome.tiff'
        return(output)
    if len(glob.glob(master_dir + '/' + current_sample + '/raw_files/*.rcpnl')) != 0:
        #print('Rarecyte Microscope')
        output = '.rcpnl'
        return(output)
    else:
        output = 'notfound' #if neither found, still needs to return a string
        return(output)

#input variables
master_dir = os.path.normpath(sys.argv[1])
run_name = ''.join(sys.argv[2:])
os.chdir(master_dir)

#local testing
#master_dir = os.path.normpath('/home/bionerd/Dropbox/@Dana Farber/CyCif/git/mcmicro/example_data')

#test for markers.csv file
if os.access(''.join([master_dir + '/markers.csv']), mode=0):
    print('PASSED: markers.csv file present')
else:
    print('ERROR, must have \'markers.csv\' file present in your project folder')
    print('File should contain a name for each cycle channel')
    print('Example:')
    example = ['DNA1', 'MARKER1', 'MARKER2', 'MARKER3', 'DNA2', 'MARKER4', 'MARKER5', 'MARKER6']
    for i in example:
        print(i)

#cleanup directory system
print('Cleaning Up')
os.system('rm -fr output') #let over from HistoCat

#store log files and stored analysis run
print('Making Log Folder')
#log folder
try:
    os.makedirs('log')
except:
    print('Log Folder Exists')

#make project based folder
log_name = 'log' + '/' + str(run_name)
try:
    os.makedirs(log_name)
except:
    print('Another mcmicro run with same name already exists, making alternative folder')
    os.makedirs(''.join([log_name + '.' + str(time.time())]))
    log_name = log_name + '.' + time.time()

#store log files
command = ''.join(['mv CyCif_Pipeline_log.txt ' + log_name])
os.system(command)

command = ''.join(['mv cycif_pipeline_versions.txt ' + log_name])
os.system(command)

command = ''.join(['mv Run_CyCif_pipeline.sh ' + log_name])
os.system(command)

command = ''.join(['mv *.e ' + log_name])
os.system(command)

command = ''.join(['mv *.o ' + log_name])
os.system(command)

command = ''.join(['mv *.sh ' + log_name])
os.system(command)

command = ''.join(['cp markers.csv ' + log_name])
os.system(command)

command = ''.join(['cp data.yaml ' + log_name])
os.system(command)

#grab all samples
samples = next(os.walk(master_dir))[1]
# log folder is where run logs are stored, exclude from folder to execute
samples = [n for n in samples if not ('log' in n)]

#process summary per sample
for i in samples:
    print('Processing ' + i)

    # Project Name
    Project = master_dir.split('/')[-1]

    # Sample Name
    Sample = i

    #CyCle Number
    if os.access(''.join([master_dir + '/' + i + '/raw_files']),mode=0):
        #Find the number of Cycles
        Cycle_Number = len(glob.glob(''.join([master_dir + '/' + i + '/raw_files/*' + microscope_check(i,master_dir)])))
    else:
        Cycle_Number = 'Fail'

    # Illumination Progress (dfp.tif and ffp)
    if os.access(''.join([master_dir + '/' + i + '/illumination_profiles']),mode=0):

        #if number of cycles matches the number of expected illumination profiles then remove illumination from pipeline
        if (len(glob.glob(''.join([master_dir + '/' + i + '/illumination_profiles/*-dfp.tif']))) == Cycle_Number) & (len(glob.glob(''.join([master_dir + '/' + i + '/illumination_profiles/*-ffp.tif']))) == Cycle_Number):
            Illumination = 'Pass'
        else:
            Illumination = 'Fail'
    else:
        Illumination = 'Fail'

    # Stitcher Progress (*ome.tif)
    if os.access(''.join([master_dir + '/' + i + '/registration']), mode=0):
        if (len(glob.glob(''.join([master_dir + '/' + i + '/registration/*.ome.tif']))) == 1):
            Stitcher = 'Pass'
        else:
            Stitcher = 'Fail'
    else:
        Stitcher = 'Fail'

    # Probability Mapper (*ContoursPM_1.tif *NucleiPM_1.tif)
    if os.access(''.join([master_dir + '/' + i + '/prob_maps']), mode=0):
        if (len(glob.glob(''.join([master_dir + '/' + i + '/prob_maps/*ContoursPM_1.tif']))) == 1) & (len(glob.glob(''.join([master_dir + '/' + i + '/prob_maps/*NucleiPM_1.tif']))) == 1):
            Prob_Mapper = 'Pass'
        else:
            Prob_Mapper = 'Fail'
    else:
        Prob_Mapper = 'Fail'

    # Segmentation (cellMask.tif cellOutlines.tif nucleiMask.tif nucleiOutlines.tif segParams.mat)
    if os.access(''.join([master_dir + '/' + i + '/segmentation']), mode=0):
        if (len(glob.glob(''.join([master_dir + '/' + i + '/segmentation/*.tif']))) == 4):
            Segmentation = 'Pass'
        else:
            Segmentation = 'Fail'
    else:
        Segmentation = 'Fail'

    # Feature Extraction (if feature_extractor ran image_1 / feature_extraction = Cell_image_1*.mat == length of markers.csv & sample_name.csv)
    if os.access(''.join([master_dir + '/' + i + '/feature_extraction']), mode=0):
        if os.access(''.join([master_dir + '/markers.csv']), mode=0):
            markers = pd.read_csv(''.join([master_dir + '/markers.csv']))

            # if files exist, remove feature extracto from pipeline
            if (len(glob.glob(''.join([master_dir + '/' + i + '/feature_extraction/Cell*.mat']))) == len(markers)+1):
                print(''.join([master_dir + '/feature_extraction/' + i + '.csv']))
                if os.access(''.join([master_dir + '/feature_extraction/' + i + '.csv']), mode=0):
                    Feature_Extraction = 'Pass'
                else:
                    Feature_Extraction = 'Fail: Final csv file not found'
            else:
                Feature_Extraction = 'Fail: Not all channels extracted'
        else:
            Feature_Extraction = 'Fail: markers.csv file not found'
    else:
        Feature_Extraction = 'Fail: Folder not found'

    #saving results for per image
    if i == samples[0]:
        df = pd.DataFrame({'Project': [Project],'Sample': [Sample],'Number of Cycles': [Cycle_Number],
                           'Illumination': [Illumination],'Stitcher': [Stitcher],'Probability Maps': [Prob_Mapper],
                          'Segmentation': [Segmentation],'Feature Extraction': [Feature_Extraction]})
        output=df
        #print(i)
        #print(output)
    else:
        #print(i)
        #print(df)
        df = pd.DataFrame({'Project': [Project],'Sample': [Sample],'Number of Cycles': [Cycle_Number],
                           'Illumination': [Illumination],'Stitcher': [Stitcher],'Probability Maps': [Prob_Mapper],
                          'Segmentation': [Segmentation],'Feature Extraction': [Feature_Extraction]})
        output = pd.merge(df,output,how='outer')

#save results
output.to_csv('CyCif_Run_Summary.csv',index=False)

#move results to log folder
command = ''.join(['mv CyCif_Run_Summary.csv ' + log_name])
os.system(command)