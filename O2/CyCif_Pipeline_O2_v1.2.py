#Created by: Nathan T. Johnson
#Edited: 09.24.2019
#Purpose: Supply error checking, O2 slurm job handling, and sbatch scripts for each image
#Input: Full Path to the Project directory with assumption it fits certain organization as defined by documentation
#Output: 1) sbatch scripts for each image 2) slurm submission script for job dependencies
#Example: python /n/groups/lsp/cycif/mcmicro/O2/CyCif_Pipeline_O2_v1.1.py /n/scratch2/ntj8/117-BRCA_VAD2-2019APR/test

#libraries
from contextlib import redirect_stdout
import yaml
import os
import sys
import shutil
import glob
import pandas as pd
import subprocess
import re

#handles path to data correctly
master_dir = os.path.normpath(sys.argv[1])
file = 'data.yaml'

#TODO implement debugging mode
#! for local testing
#master_dir = os.path.normpath('/home/bionerd/Dropbox/@Dana Farber/CyCif/git/mcmicro/example_data/')
os.chdir(master_dir)

#! change O2 global path and cycif environment file each update

#easy global environment path and version updating on O2 (for switching between testing and stable versions)
#O2 testing location
#O2_global_path = '/n/groups/lsp/cycif/cycif_pipeline_testing_space/mcmicro/'
#O2 stable version
O2_global_path = '/n/groups/lsp/cycif/mcmicro'
Version = 'v1.2'

################
#Pipeline Tests#
################

#expand the number of microscope raw files types searched for [TODO] add ability for user to modify extension searched for from yaml
def microscope_check(current_sample,master_dir):
    if len(glob.glob(master_dir + '/' + current_sample + '/raw_files/*.ome.tiff')) != 0:
        print('Exemplar Dataset Used')
        output = '.ome.tiff'
        return(output)
    if len(glob.glob(master_dir + '/' + current_sample + '/raw_files/*.rcpnl')) != 0:
        print('Rarecyte Microscope')
        output = '.rcpnl'
        return(output)
    else:
        output = 'notfound' #if neither found, still needs to return a string
        return(output)

#commonly users incorrectly structure the folders for execution or missing files
#input: list of samples and path to data
#returns: error messages to warn user prior to running (doesn't stop user, just warns)
#checking 1) markers.csv exists, 2) checking if each sample has a raw_file,
#3) checking if correct data exists in raw_files folder, 4) check if number of raw cycle number matches the marker names
def file_err_checking(samples,master_dir):
    print('Checking If Data is organized correctly')

    #test for marker.csv file present [TODO] update check to pull from yaml file for individual sample marker file
    if os.access(''.join([master_dir + '/markers.csv']), mode=0):
        print('PASSED: markers.csv file present')
    else:
        print('ERROR, must have \'markers.csv\' file present in your project folder')
        print('File should contain a name for each cycle channel')
        print('Example:')
        example = ['DNA1', 'MARKER1', 'MARKER2', 'MARKER3', 'DNA2', 'MARKER4', 'MARKER5', 'MARKER6']
        for i in example:
            print(i)

    # test if raw_file folder and raw files exists for each sample
    for current in samples:
        print('Checking Folders for Image:',current)

        #check if raw_files folder exists
        if os.access(master_dir + '/' + current + '/raw_files',mode=0):
            print('PASSED: ' + current + ' raw files folder present')

            # check if raw files are present
            if len(glob.glob(master_dir + '/' + current + '/raw_files/*' + microscope_check(current,master_dir))) >0:
                print('PASSED: ' + current + ' raw images present')
            else:
                print('ERROR: Uh Oh! Sample: ' + current + ' does not have raw image files')
                print('If your microscope is not a RareCyte or Exemplar Data, pipeline may work, but bug Nathan for not adding your favorite microscope')

            #check if metadata files are present: metadata is not essential (not sure why we need/want it)
            # if len(glob.glob(master_dir + '/' + current + '/raw_files/*.metadata')) > 0:
            #     print('test')
            # else:
            #     print('Sample' + current + 'does not have .metadata files')
            #     print('Customary but not necessary')
        else:
            print('ERROR: Uh Oh! Image: ' + current + ' did not have the raw_files folder')
            print('Within each image folder, there must be a raw_files folder containing the raw images for each cycle')

# check if the file name has not been modified as order of image name is how the files are stitched together
def file_name_checking(samples,master_dir):
    print('Checking if Raw File Names Have Been Modified (Assuming RareCyte)')
    #files = next(os.walk(master_dir))[1]

    #rename files to ensure correct order
    for i in iter(samples):
        print('Checking Image: ' + i)
        #find
        to_process = glob.glob(''.join([master_dir + '/' + i + '/raw_files/*' + microscope_check(i,master_dir)]))
        #remove path length
        to_process = [i.split('/')[-1] for i in to_process]

        #test if past test based on 4 tests
        test = 'Pass'
        # default is Pass
        for n in to_process:
            if len(n.split('_')) == 4:
                test = 'Pass'
                # TODO:fix
                # if n.split('_')[0] != 'Scan': #first word should be Scan
                #    test = 'Fail'
                # if n.split('_')[1].isdigit(): #second statement should be a Date
                #    test = 'Fail'
                # if n.split('_')[2].isdigit(): #third statement should be a number
                #    test = 'Fail'
                # if len(n.split('_')[3].split('x')) == 3: #fourth statement should be '01x4x00154', test is splitting by x == 3 splits
                #    test = 'Fail'
            else:
                test = 'Fail'

        #what to do if test fails or pass
        if test == 'Fail':
            print('ERROR: Assuming RareCyte, Raw File name has been modified: Order of cycles depends on cycle file name')
            #print('Suggest running \'Rename.py\'')
            #print('Will turn  HER2_BR_Cycle1_Scan_20190612_164155_01x4x00154.rcpnl into 20190612_164155_01x4x00154.rcpnl')
        else:
            print('Pass: ' + i + ' raw files not modified')

#check if any module parts of pipeline have already been run
#input: path to data, list of images, list of pipeline modules to run
#[TODO]: consider markers.csv size
#[TODO]: consider customizing what is removed on an individual sample basis
def pipeline_checking(master_dir,samples,pipeline):
    for i in samples: #i know bad coding practice to use lots of if then, but lots of customization [TODO] clean up code
        # if illumination ran /image/illumination_profiles = (*dfp.tif  *ffp.tif)
        if os.access(''.join([master_dir + '/' + i + '/illumination_profiles']),mode=0):
            #print(i + ' Illumination Profile Folder Exists')

            #calculate number of cycles to verify illumination was done on
            cycle_number = len(glob.glob(''.join([master_dir + '/' + i + '/raw_files/*' + microscope_check(i,master_dir)])))

            #Solve for false positives if raw image files are missing
            if cycle_number != 0:
                #if number of cycles matches the number of expected illumination profiles then remove illumination from pipeline
                if (len(glob.glob(''.join([master_dir + '/' + i + '/illumination_profiles/*-dfp.tif']))) == cycle_number) & (len(glob.glob(''.join([master_dir + '/' + i + '/illumination_profiles/*-ffp.tif']))) == cycle_number):
                    print(i + ' Illumination Files Found, skipping')
                    #pop off illumination check
                    pipeline = [n for n in pipeline if not ('illumination' in n)]

        # if stitcher ran /image/registration = (*.ome.tif)
        if os.access(''.join([master_dir + '/' + i + '/registration']), mode=0):
            #print(i + ' Registration Folder Found')
            # if files exist, remove stitcher from pipeline
            if (len(glob.glob(''.join([master_dir + '/' + i + '/registration/*.ome.tif']))) == 1):
                print(i + ' Stitched Image Found, skipping')
                # pop off stitcher
                pipeline = [n for n in pipeline if not ('stitcher' in n)]

        #if prob_mapper ran /image/prob_maps = (*ContoursPM_1.tif *NucleiPM_1.tif)
        if os.access(''.join([master_dir + '/' + i + '/prob_maps']), mode=0):
            #print(i + ' Probability Mapper Folder Found')

            #if files exist, remove prob_mapper from pipeline
            if (len(glob.glob(''.join([master_dir + '/' + i + '/prob_maps/*ContoursPM_1.tif']))) == 1) & (len(glob.glob(''.join([master_dir + '/' + i + '/prob_maps/*NucleiPM_1.tif']))) == 1):
                print(i + ' Probability Maps Found, skipping')
                #pop off illumination
                pipeline = [n for n in pipeline if not ('prob_mapper' in n)]

        #if segmenter ran image/segmentation = (cellMask.tif cellOutlines.tif nucleiMask.tif nucleiOutlines.tif segParams.mat)
        if os.access(''.join([master_dir + '/' + i + '/segmentation']), mode=0):
            #print(i + ' Segmentation Folder Found')
            #if files exist, remove segmenter from pipeline
            if (len(glob.glob(''.join([master_dir + '/' + i + '/segmentation/*.tif']))) == 4):
                print(i + ' Segmentation Folder Found, skipping')
                #pop off segmenter
                pipeline = [n for n in pipeline if not ('segmenter' in n)]

        #if feature_extractor ran image_1 / feature_extraction = Cell_image_1*.mat == length of markers.csv
        if os.access(''.join([master_dir + '/' + i + '/feature_extraction']), mode=0):
            #print(i + ' Feature Extraction Folder Found')

            # function file_err_checking checks for markers.csv file, otherwise it will print missing for each sample == redundant
            if os.access(''.join([master_dir + '/markers.csv']), mode=0):
                markers = pd.read_csv(''.join([master_dir + '/markers.csv']),header = None)
                #print('Marker File length:',len(markers))

                # if files exist, remove feature extractor from pipeline
                if (len(glob.glob(''.join([master_dir + '/' + i + '/feature_extraction/Cell*.mat']))) == len(markers)):
                    print(i + ' Feature Extractor run previously, skipping')
                    # pop off feature extractor
                    pipeline = [n for n in pipeline if not ('feature_extractor' in n)]

    return(pipeline)

######################
#O2 Handling Function#
######################

#create list of lists to handle organizing job ranking and submission to slurm
#input: list of pipeline steps to run and list of samples to integrate
#[TODO] change to image dependent pipeline stack (for now assume first sample image has the same images already ran)
def populate_image_job_dependency(pipeline,samples,files):
    # list length of number of samples plus one to store the QC step
    res = [[] for _ in range(len(samples)+2)]

    # for QC step
    res[0] = [i for i in files if pipeline[0] in i]

    #make list of lists for each sample and its processing stack to put together
    for n in range(1,len(pipeline)-1): #do not include QC and Summary

        #grab all files to be run as part of each stage
        tmp = [i for i in files if pipeline[n] in i]

        # populate the list with each file (TOFIX:list comprehension?)
        for z in range(0, len(tmp)):

            #error checking: if tripped most likely due to overlapping names so pipeline dependencies may be screwed up
            #for example: image_1 vs image_1A = cause it to trip
            #solution: file variable explicitly defining the pattern to be found should fix any solution
            #currently: keep warning present in case there is an edge case not being considered
            #if len([i for i in tmp if samples[z] in i]) != 1:
            #    print('Sample length error! Check Run_CyCif_pipeline.sh for correct job dependency')

            #rearrange order of samples is consistent ie image 1 goes with all image 1 pipeline defined by variable samples
            file = samples[z] + '_' + pipeline[n] + '.sh'
            res[z + 1].append([i for i in tmp if file in i][0])

    #end of pipeline processing script
    res[-1] = [i for i in files if pipeline[-1] in i]
    return(res)

#create 'Run_CyCif_pipeline.sh'
#input: list of list from populate image job dependency
def save_cycif_pipeline(res):
    #write list to file with job id dependencies [TODO] separate into function to handle O2 job dependency separately
    f = open('Run_CyCif_pipeline.sh', 'w')
    with redirect_stdout(f):
        print('#!/bin/bash')

        #User viewing
        print('echo Submitting Jobs')

        #QC step
        print('jid0=$(sbatch --parsable '+res[0][0]+')')

        #initialize variables [todo] not sure why needed, but error thrown if not
        current_jobID = 1
        previous_job_id = 0
        summary_dependency_jobids=[]

        #each step dependent on QC run, then a stack is made separated for each individual sample ID
        for i in range(1,len(res)-1): #length to number of samples
            for n in range(0,len(res[i])): #length to number of processing steps for each individual sample
                # if first image and first in processing stack, initialize jobIDs
                #print("i:"+str(i)+" n:"+str(n)+ " current_jobID:"+str(current_jobID)+ " previous_job_id:"+str(previous_job_id)+('\n'))
                if (i == 1) & (n == 0):
                    #current_jobID = 1
                    #previous_job_id = 0
                    print('jid' + str(current_jobID) + '=$(sbatch --dependency=afterok:$jid' + str(previous_job_id) + ' --parsable ' + res[i][n] + ')')
                    previous_job_id = previous_job_id + 1
                    current_jobID = current_jobID + 1

                # if not first job in pipeline stack, bump up as normal
                if n != 0:
                    print('jid' + str(current_jobID) + '=$(sbatch --dependency=afterok:$jid' + str(previous_job_id) + ' --parsable ' + res[i][n] + ')')
                    previous_job_id = previous_job_id + 1
                    current_jobID = current_jobID + 1

                # if the second image and first in processing stack, previous job id must depend on QC step
                if (i >= 2) & (n == 0):
                    previous_job_id = 0
                    print('jid' + str(current_jobID) + '=$(sbatch --dependency=afterok:$jid' + str(previous_job_id) + ' --parsable ' + res[i][n] + ')')
                    #update ids for place in stack
                    previous_job_id = current_jobID
                    current_jobID = current_jobID + 1

                #job ids for the end of the job processing stack for each image
                if n == len(res[i])-1:
                    summary_dependency_jobids.append(''.join(['$jid' + str(previous_job_id)]))

        #Pipeline Summary Step

        #Using the end of each job depenceny stack, execute summary script that is dependent on those jobs finishing
        if len(summary_dependency_jobids) != 0:
            print(''.join(['jid' + str(current_jobID) + '=$(sbatch --dependency=afterok:',':'.join(summary_dependency_jobids)]),' --parsable ' + res[i + 1][0] + ')')
        else: #no job dependencies due to pipeline successfully run
            print(''.join(['jid' + str(current_jobID) + '=$(sbatch --parsable ' + res[i + 1][0] + ')']))

        #tell User done submitting
        print ('echo Successfully submitted CyCif Pipeline')
    f.close()

#save version for each submodule in pipeline
#save git hash for each module and the last modification time stamp for environments
def save_module_versions():
    f = open('cycif_pipeline_versions.txt', 'w')
    with redirect_stdout(f):
        print('Cycif Pipeline Version:', Version)
        print('Environment Versions:')
        # go through each environment in /environments/ and capture the environment modification time stamp to get 'version'
        environments = next(os.walk(''.join([O2_global_path + '/environments'])))[1]
        for i in environments:
            print(i)
            print(os.stat(O2_global_path + 'environments' + '/' + i)[-2]) #get last modification time
        # go through each dev_module_git and spit out github hash version
        print('Module Versions:')
        modules = next(os.walk(''.join([O2_global_path + '/dev_module_git'])))[1]
        for i in modules:
            print(i)
            os.chdir(''.join([O2_global_path + '/dev_module_git/' + i]))
            result = subprocess.run(['git', 'rev-parse', 'HEAD'], stdout=subprocess.PIPE)
            print(str(result.stdout.decode("utf-8").rstrip()))
        os.chdir(master_dir)
    f.close()

#master function that controls error checking, submission, organizing, creating 'Run_CyCif_Pipeline.sh' for cycif pipeline
def master(samples,TMA_Test):
    #look for all scripts to include in cycif pipelineA
    files = sorted(glob.glob('*.sh')) #check for miserror

    if TMA_Test == 'True':
        # Order of list is dependent on order of pipeline steps to be run [segmenter vs prob_mapper]
        pipeline = ['QC', 'illumination', 'stitcher', 'segmenter', 'prob_mapper', 'feature_extractor','Summary']
    else:
        # Order of list is dependent on order of pipeline steps to be run
        pipeline = ['QC', 'illumination', 'stitcher', 'prob_mapper', 'segmenter', 'feature_extractor','Summary']

    #error checking raw files are where they should be, markers.csv exists, and cycles matches markers.csv number
    file_err_checking(samples, master_dir)

    #checking raw_files names are correctly formatted
    file_name_checking(samples, master_dir)

    #update pipeline list to run based on what files are found to exist (not checking QC of images, just they are present)
    #check whether any parts of pipeline already run using the first image as a reference
    #if images already generated then remove from pipeline array those parts
    print('Checking if pipeline was run previously')
    pipeline=pipeline_checking(master_dir, samples, pipeline)

    print('Integrating pipeline')
    res=populate_image_job_dependency(pipeline, samples, files)

    print('Saving Run_CyCif_pipeline.sh')
    save_cycif_pipeline(res)

#parse user parameters to set, otherwise use default
def yaml_parser(file):
    with open(file) as f:
        conditions = yaml.safe_load_all(f)
        for module in conditions:
            print('Parameters Parsed')
            print(module)
        return(module)

#using yaml parser, update parameters
def update_parameters(file,part3,part4,part5,part6):
    #parse yaml file and store as dictionary
    condition = yaml_parser(file)

    #Global Run Conditions

    #test for TMA run
    if str(condition.get('Run').get('TMA')) == 'True':
        part4.TMA = 'Yes'
        part5.TMA = 'Yes'
        part6.TMA = 'Yes'

    # test if cf25 run or not
    part3.cf25(str(condition.get('Run').get('cf25')))

    #microscope check
    #microscope_type = condition.get('Run').get('file_extension')

    #Update various module conditions using user supplied parameters
    #Illumination
    part2.parameters = condition.get('Illumination')

    #Stitcher
    part3.parameters = condition.get('Stitcher')

    #Probability Mapper
    part4.parameters = condition.get('Probability_Mapper')

    #Segmenter
    part5.parameters = condition.get('Segmenter')

    #Feature Extractor [TODO]
    part6.parameters = condition.get('Feature_Extractor')

    return(condition)

################################
#CyCIf Method Class Definitions#
################################

#QC (at the moment just folder infrastructure checking) [TODO]
class QC(object):
    directory = master_dir
    #environment = '/n/groups/lsp/cycif/CyCif_Manager/environments/cycif_pipeline'
    environment = ''.join([O2_global_path+'environments/cycif_pipeline'])
    parameters = master_dir
    modules = ['conda2/4.2.13']
    run = ''.join(['python ' + O2_global_path + 'bin/check_folder_' + Version + '.py'])
    #run = 'python /n/groups/lsp/cycif/CyCif_Manager/bin/check_folder_v1.py'
    sbatch = ['-p short', '-t 0-1:00', '-J QC', '-o Step_1_QC.o', '-e Step_1_QC.e']

    # initilizing class and printing when done
    def __init__(self):
        print("Initialize QC Definition")

    # export the sbatch parameters saved
    def sbatch_exporter(self):
        for i in self.sbatch:
            print('#SBATCH ', i)

    # export the module parameters
    def module_exporter(self):
        for i in self.modules:
            print('module load', i)

    # print the sbatch job script
    def print_sbatch_file(self):
        print('#!/bin/bash')
        self.sbatch_exporter()
        self.module_exporter()
        print('source activate ', self.environment)
        print(self.run, self.parameters)
        print('conda deactivate')
        print('sleep 5') # wait for slurm to get the job status into its database
        print('sacct --format=JobID,Submit,Start,End,State,Partition,ReqTRES%30,CPUTime,MaxRSS,NodeList%30 --units=M -j $SLURM_JOBID') #resource usage

    # save the sbatch job script
    def save_sbatch_file(self):
        f = open('QC.sh', 'w')
        with redirect_stdout(f):
            self.print_sbatch_file()
        f.close()

#Illumination Profiles (pre-req for ashlar)
class Illumination(object):
    environment = ''.join([O2_global_path+'environments/ImageJ'])
    directory = master_dir
    parameters = {'lambda_flat': 0.1, 'lambda_dark': 0.01, 'estimate_flat_field_only': False, 'max_number_of_fields_used': 'None'} #default parameters
    modules = ['conda2/4.2.13']
    run = ''.join(['python ' + O2_global_path + 'bin/illumination_' + Version + '.py'])
    sbatch = ['-p short', '-t 0-12:00', '--mem=64G', '-J illumination',
              '-o Step_2_illumination.o', '-e Step_2_illumination.e']
    sample = 'NA'
    sbatchfilename = 'NA'

    # initilizing class and printing when done
    def __init__(self):
        print("Initialize Illumination Definition:")

    # what sbatch parameters to load in O2
    def sbatch_def(self):
        #update Job name and output to be reflective of sample
        self.sbatch[3] = ''.join(['-J illum_'+self.sample])
        self.sbatch[4] = ''.join(['-o ' + 'Step_2_' + self.sample + '_illumination.o'])
        self.sbatch[5] = ''.join(['-e ' + 'Step_2_' + self.sample + '_illumination.e'])

    # export the sbatch parameters saved
    def sbatch_exporter(self):
        self.sbatch_def()
        for i in self.sbatch:
            print('#SBATCH ', i)

    # export the module parameters
    def module_exporter(self):
        for i in self.modules:
            print('module load', i)

    # print the sbatch job script
    def print_sbatch_file(self):
        print('#!/bin/bash')
        self.sbatch_exporter()
        self.module_exporter()
        print('source activate ', self.environment)
        print(self.run, self.directory+'/'+self.sample, self.parameters)
        print('conda deactivate')
        print('sleep 5') # wait for slurm to get the job status into its database
        print('sacct --format=JobID,Submit,Start,End,State,Partition,ReqTRES%30,CPUTime,MaxRSS,NodeList%30 --units=M -j $SLURM_JOBID') #resource usage

    # save the sbatch job script
    def save_sbatch_file(self):
        self.sbatchfilename = self.sample + '_illumination.sh'
        f = open(self.sbatchfilename, 'w')
        with redirect_stdout(f):
            self.print_sbatch_file()
        f.close()

#stitch the multiple images together
class Stitcher(object):
    method = 'Ashlar'
    TMA = 'No'
    environment = ''.join([O2_global_path + 'environments/ashlar'])
    program = ''.join([O2_global_path + 'bin/run_ashlar_' + Version + '.py'])
    directory = master_dir
    ashlar_path = ''.join([O2_global_path + 'environments/ashlar/bin/ashlar'])
    modules = ['conda2/4.2.13']
    run = 'python'
    sbatch = ['-p short','-t 0-12:00', '--mem=64G', '-J ashlar',
              '-o Step_3_ashlar.o','-e Step_3_ashlar.e']
    sample = 'NA'
    parameters = ['-m 30']

    #initilizing class and printing when done
    def __init__(self):
        print ("Initialize Stitcher Definition")

    # what sbatch parameters to load in O2
    def sbatch_def(self):
        # update Job name and output to be reflective of sample
        self.sbatch[3] = ''.join(['-J ashlar_' + self.sample])
        self.sbatch[4] = ''.join(['-o ' + 'Step_3_' + self.sample + '_ashlar.o'])
        self.sbatch[5] = ''.join(['-e ' + 'Step_3_' + self.sample + '_ashlar.e'])

    # export the sbatch parameters saved
    def sbatch_exporter(self):
        self.sbatch_def()
        for i in self.sbatch:
            print('#SBATCH ',i)

    #check for cf25 modification
    def cf25(self,cf25_test):
        if cf25_test == 'True':
            self.environment = ''.join([O2_global_path + 'environments/ashlar_cf25'])

    # export the module parameters
    def module_exporter(self):
        for i in self.modules:
            print('module load',i)

    #YAML Parser
    def segmenter_yaml_parser(self):
        #test that parameters have been parsed with yaml
        if isinstance(self.parameters, dict):
            #convert to data type desired
            self.parameters = [[k, v] for k, v in self.parameters.items()]  # dict to 2d array
            self.parameters = ','.join(str(item) for innerlist in self.parameters for item in innerlist)  # 2d array to 1d string array
            self.parameters = self.parameters.split(',')  # retain individual elements for array

            #change any 'True' to 'true' as required by S3 requirments
            self.parameters = ['true' if i == 'True' else i for i in self.parameters]

            #modify parameter list to correctly handle integars, single and multiple digit arrays to match what matlab expects
            #assumption is any element in array not a string has already been modified
            for i in range(0,len(self.parameters)):
                #print(self.parameters[i])

                #assumption is any element in array not a string has already been modified
                if isinstance(self.parameters[i],str):
                    # testing if single integer
                    if self.parameters[i].isdigit():
                        #print('Digit')
                        self.parameters[i] = int(self.parameters[i])

                # assumption is any element in array not a string has already been modified
                if isinstance(self.parameters[i],str):
                    # testing for single digit list
                    pattern = r'\[(\d+)'
                    if re.search(pattern, self.parameters[i]):
                        #print('Single Digit List')
                        # remove brackets and convert to single digit list
                        self.parameters[i] = [int(self.parameters[i][1:-1])]

                # assumption is any element in array not a string has already been modified
                if isinstance(self.parameters[i], str):
                    #test for multiple digit array
                    pattern = r'\[\'(\d+)'
                    if re.search(pattern, self.parameters[i]):
                        #print('Multiple Digit Array')
                        # remove brackets and extra quotes and convert to multiple digit list
                        self.parameters[i] = [int(i) for i in self.parameters[7][2:-2].split(' ')]

    #print the sbatch job script
    def print_sbatch_file(self):

        #update parameters for command line input
        self.segmenter_yaml_parser()

        print('#!/bin/bash')
        self.sbatch_exporter()
        self.module_exporter()
        print('source activate ', self.environment)
        print(self.run, self.program, self.directory+'/'+self.sample, self.ashlar_path, self.parameters)
        print('conda deactivate')
        print('sleep 5') # wait for slurm to get the job status into its database
        print('sacct --format=JobID,Submit,Start,End,State,Partition,ReqTRES%30,CPUTime,MaxRSS,NodeList%30 --units=M -j $SLURM_JOBID') #resource usage

    # save the sbatch job script
    def save_sbatch_file(self):
        self.sbatchfilename = self.sample + '_stitcher.sh'
        f = open(self.sbatchfilename, 'w')
        with redirect_stdout(f):
            self.print_sbatch_file()
        f.close()

#determine probability of cell boundary on image
class Probability_Mapper(object):
    method = 'Unet'
    run = 'No'
    environment = ''.join([O2_global_path + 'environments/unet'])
    directory = master_dir
    run = ''.join(['python ' + O2_global_path + 'bin/run_batchUNet2DtCycif_mcmicro.py'])
    parameters = [0,1,1]
    modules = ['gcc/6.2.0','cuda/9.0','conda2/4.2.13']
    sbatch = ['-p gpu','-n 1','-c 12', '--gres=gpu:1','-t 0-12:00','--mem=64000',
              '-J prob_mapper','-o Step_4_probability_mapper.o','-e Step_4_probability_mapper.e']
    sample = 'NA'
    TMA = 'NA'

    #initilizing class and printing when done
    def __init__(self):
        print ("Initialize Probability Mapper Definition")

    # what sbatch parameters to load in O2
    def sbatch_def(self):
        # update Job name and output to be reflective of sample
        self.sbatch[6] = ''.join(['-J prob_map_' + self.sample])
        self.sbatch[7] = ''.join(['-o ' + 'Step_4_' + self.sample + '_probability_mapper.o'])
        self.sbatch[8] = ''.join(['-e ' + 'Step_4_' + self.sample + '_probability_mapper.e'])

    # export the sbatch parameters saved
    def sbatch_exporter(self):
        self.sbatch_def()
        for i in self.sbatch:
            print('#SBATCH ',i)

    # export the module parameters
    def module_exporter(self):
        for i in self.modules:
            print('module load',i)

    #modifies environment and program if TMA_test is True
    def TMA_mode(self):
        self.parameters = [''.join([O2_global_path + 'dev_module_git/UnMicst/batchUNet2DTMACycif.py']), 0, 1, 1]

    #print the sbatch job script
    def print_sbatch_file(self):
        if self.TMA == 'True':
            TMA_mode()
        #expected parameters is an array, yaml file parsing creates dict
        if isinstance(self.parameters, dict):
            self.parameters = [v for v in self.parameters.values()]
        print('#!/bin/bash')
        self.sbatch_exporter()
        self.module_exporter()
        print('source activate ', self.environment)
        print(self.run, self.directory + '/' + self.sample, self.parameters[0], self.parameters[1],self.parameters[2])
        print('conda deactivate')
        print('sleep 5') # wait for slurm to get the job status into its database
        print('sacct --format=JobID,Submit,Start,End,State,Partition,ReqTRES%30,CPUTime,MaxRSS,NodeList%30 --units=M -j $SLURM_JOBID') #resource usage

    # save the sbatch job script
    def save_sbatch_file(self):
        self.sbatchfilename = self.sample + '_prob_mapper.sh'
        f = open(self.sbatchfilename, 'w')
        with redirect_stdout(f):
            self.print_sbatch_file()
        f.close()

#segment fluroscence probes
class Segmenter(object):
    method = 'S3'
    run = 'No'
    directory = master_dir
    modules = ['matlab/2018b']
    run = 'matlab -nodesktop -r '
    environment = ''.join([O2_global_path + 'environments/segmenter'])
    program = 'NA'
    #parameters =  "'HPC','true','fileNum',1,'TissueMaskChan',[2],'logSigma',[3 30],'mask'," \
    #              "'tissue','segmentCytoplasm','ignoreCytoplasm')\""
    parameters = []
    sbatch = ['-p short', '-t 0-12:00', '-c 1','--mem=100G', '-J Step_5_segmenter', '-o Step_5_segmenter.o', '-e segmenter.e']
    sample = 'NA'
    TMA = 'NA'

    #initilizing class and printing when done
    def __init__(self):
        print ("Initialize Segmenter Definition")
        self.program = ''.join(['"addpath(genpath(\'', self.environment, '\'));O2batchS3segmenterWrapperR('])

    # what sbatch parameters to load in O2
    def sbatch_def(self):
        # update Job name and output to be reflective of sample
        self.sbatch[4] = ''.join(['-J segmenter_' + self.sample])
        self.sbatch[5] = ''.join(['-o ' + 'Step_5_' + self.sample + '_segmenter.o'])
        self.sbatch[6] = ''.join(['-e ' + 'Step_5_' + self.sample + '_segmenter.e'])

    # export the sbatch parameters saved
    def sbatch_exporter(self):
        self.sbatch_def()
        for i in self.sbatch:
            print('#SBATCH ',i)

    # export the module parameters
    def module_exporter(self):
        for i in self.modules:
            print('module load',i)

    #clean up after run
    def post_run_cleanup(self):
        if self.TMA == 'True':
            print("mv", ''.join([self.directory + '/' + self.sample + '/' + self.sample + '/dearray/*']),
                  ''.join([self.directory + '/' + self.sample + '/dearray']))
            print("rm -r ", ''.join([self.directory + '/' + self.sample + '/' + self.sample + '/dearray/']))
            print('sleep 5')  # wait for slurm to get the job status into its database
            print('sacct --format=JobID,Submit,Start,End,State,Partition,ReqTRES%30,CPUTime,MaxRSS,NodeList%30 --units=M -j $SLURM_JOBID')  # resource usage
        else:
            print("mv", ''.join([self.directory+'/'+self.sample+'/segmentation/'+self.sample+'/*']),''.join([self.directory+'/'+self.sample+'/segmentation/']))
            print("rm -r ", ''.join([self.directory+'/'+self.sample+'/segmentation/'+self.sample]))
            print('sleep 5')  # wait for slurm to get the job status into its database
            print('sacct --format=JobID,Submit,Start,End,State,Partition,ReqTRES%30,CPUTime,MaxRSS,NodeList%30 --units=M -j $SLURM_JOBID')  # resource usage

    #modifies environment and program if TMA_test is True
    def TMA_mode(self):
        self.environment = '/n/groups/lsp/cycif/cycif_pipeline_testing_space/mcmicro/dev_module_git/batchtmaDearray/TMAsegmentation/'
        self.program = ''.join(['"addpath(genpath(\'', self.environment, '\'));batchtmaDearray('])
        self.parameters = ",'outputChan', 0')\""
        sbatch = ['-p short', '-t 0-12:00', '-c 8', '--mem=100G', '-J Step_5_segmenter', '-o Step_5_segmenter.o',
                  '-e segmenter.e']

    #find all folder names from the directory path position
    def file_finder(self):
        self.files=next(os.walk(self.directory))[1]

    #YAML Parser
    def segmenter_yaml_parser(self):
        #test that parameters have been parsed with yaml
        if isinstance(self.parameters, dict):
            #convert to data type desired
            self.parameters = [[k, v] for k, v in self.parameters.items()]  # dict to 2d array
            self.parameters = ','.join(str(item) for innerlist in self.parameters for item in innerlist)  # 2d array to 1d string array
            self.parameters = self.parameters.split(',')  # retain individual elements for array

            #change any 'True' to 'true' as required by S3 requirments
            self.parameters = ['true' if i == 'True' else i for i in self.parameters]

            #modify parameter list to correctly handle integars, single and multiple digit arrays to match what matlab expects
            #assumption is any element in array not a string has already been modified
            for i in range(0,len(self.parameters)):
                #print(self.parameters[i])

                #assumption is any element in array not a string has already been modified
                if isinstance(self.parameters[i],str):
                    # testing if single integer
                    if self.parameters[i].isdigit():
                        #print('Digit')
                        self.parameters[i] = int(self.parameters[i])

                # assumption is any element in array not a string has already been modified
                if isinstance(self.parameters[i],str):
                    # testing for single digit list
                    pattern = r'\[(\d+)'
                    if re.search(pattern, self.parameters[i]):
                        #print('Single Digit List')
                        # remove brackets and convert to single digit list
                        self.parameters[i] = [int(self.parameters[i][1:-1])]

                # assumption is any element in array not a string has already been modified
                if isinstance(self.parameters[i], str):
                    #test for multiple digit array
                    pattern = r'\[\'(\d+)'
                    if re.search(pattern, self.parameters[i]):
                        #print('Multiple Digit Array')
                        # remove brackets and extra quotes and convert to multiple digit list
                        self.parameters[i] = [int(i) for i in self.parameters[i][2:-2].split(' ')]

    #print the sbatch job script
    def print_sbatch_file(self):
        if self.TMA == 'True':
            self.TMA_mode()
        #If YAML parser has been run, modify input parameters
        if isinstance(self.parameters, dict):
            self.segmenter_yaml_parser()
            #self.parameters = [[k, v] for k, v in self.parameters.items()]  # dict to 2d array
            #self.parameters = ','.join(str(item) for innerlist in self.parameters for item in innerlist)  # 2d array to 1d string array
            #self.parameters = self.parameters.split(',')  # retain individual elements for array
        print('#!/bin/bash')
        #O2 computational requirements
        self.sbatch_exporter()
        #what O2 needs to load
        self.module_exporter()
        #S3 segmenter headless matlab run
        print(self.run, self.program, "'", self.directory + '/' + self.sample, "',", str(self.parameters)[1:-1], ")\"",
              sep='')
        #what folders and files need to be moved and cleaned up
        self.post_run_cleanup()

    # save the sbatch job script
    def save_sbatch_file(self):
        self.sbatchfilename = self.sample + '_segmenter.sh'
        f = open(self.sbatchfilename, 'w')
        with redirect_stdout(f):
            self.print_sbatch_file()
        f.close()

#extra features from image
class feature_extractor(object):
    method = 'histoCat'
    run = 'No'
    directory = master_dir
    modules = ['matlab/2018b']
    run = 'matlab -nodesktop -r '
    environment = ''.join([O2_global_path + 'environments/histoCAT'])
    program = 'NA'
    parameters = ["5", "no"]
    sbatch = ['-p short', '-t 0-12:00', '-c 8','--mem=100G', '-J feature_extractor', '-o Step_6_feature_extractor.o', '-e Step_6_feature_extractor.e']
    sample = 'NA'
    TMA = 'NA'

    #initilizing class and printing when done
    def __init__(self):
        print ("Initialize Feature Extractor Definition")
        self.program = ''.join(['"addpath(genpath(\'', self.environment, '\'));Headless_histoCAT_loading('])

    # what sbatch parameters to load in O2
    def sbatch_def(self):
        # update Job name and output to be reflective of sample
        self.sbatch[4] = ''.join(['-J fea_ext_' + self.sample])
        self.sbatch[5] = ''.join(['-o ' + 'Step_6_' + self.sample + '_feature_extractor.o'])
        self.sbatch[6] = ''.join(['-e ' + 'Step_6_' + self.sample + '_feature_extractor.e'])

    # export the sbatch parameters saved
    def sbatch_exporter(self):
        self.sbatch_def()
        for i in self.sbatch:
            print('#SBATCH ',i)

    # export the module parameters
    def module_exporter(self):
        for i in self.modules:
            print('module load',i)

    #find all folder names from the directory path position
    def file_finder(self):
        self.files=next(os.walk(self.directory))[1]

    #print the sbatch job for TMA implementation (using a separate python program to process the TMA files)
    def print_TMA_sbatch_file(self):
        print('#!/bin/bash')
        self.sbatch_exporter()
        self.module_exporter()
        print('python TMA_HistoCat.py ' + master_dir + ' ' + self.sample)
        print("mv",''.join(['./output/',self.sample,'/*']),''.join([self.directory,'/',self.sample,'/feature_extraction']))
        print("rm -r ",''.join(['./output/',self.sample]))
        print('sleep 5') # wait for slurm to get the job status into its database
        print('sacct --format=JobID,Submit,Start,End,State,Partition,ReqTRES%30,CPUTime,MaxRSS,NodeList%30 --units=M -j $SLURM_JOBID') #resource usage

    #modify parameters in particular to HistoCat exepected input
    def segmenter_yaml_parser(self):
            #python will change yes and no to True/False automatically
            if str(part6.parameters.get('neighborhood')) == 'False':
                self.parameters['neighborhood'] = 'no'
            if str(part6.parameters.get('neighborhood')) == 'True':
                self.parameters['neighborhood'] = 'yes'

    #print the sbatch job script
    def print_sbatch_file(self):
        #change parameters based on HistoCat specific conditions
        self.segmenter_yaml_parser()
        print('#!/bin/bash')
        self.sbatch_exporter()
        self.module_exporter()
        #change yaml dictionary to array
        # or just a list of the list of key value pairs
        #self.parameters = [[k, v] for k, v in self.parameters.items()]
        tmp = ''
        tmp = tmp.__add__(''.join(["'",self.directory,"/",self.sample,"/registration'",","]))
        tmp = tmp.__add__(''.join(["'",self.sample,".ome.tif',"]))
        tmp = tmp.__add__(''.join(["'",self.directory,"/",self.sample,'/segmentation/',"',"]))
        tmp = tmp.__add__(''.join(["'",str(part6.parameters.get('mask')),"','",self.directory,"/","markers.csv'",",","'",str(part6.parameters.get('expansionpixels')) ,"'",",","'",str(part6.parameters.get('neighborhood')),"')\""]))
        print(self.run,self.program,tmp,sep='')
        print("mv",''.join(['./output/',self.sample,'/*']),''.join([self.directory,'/',self.sample,'/feature_extraction']))
        print("rm -r ",''.join(['./output/',self.sample]))
        print('sleep 5') # wait for slurm to get the job status into its database
        print('sacct --format=JobID,Submit,Start,End,State,Partition,ReqTRES%30,CPUTime,MaxRSS,NodeList%30 --units=M -j $SLURM_JOBID') #resource usage

    # save the sbatch job script
    def save_sbatch_file(self):
        #save image file for histoCat extraction
        self.sbatchfilename = self.sample + '_feature_extractor.sh'
        #open file
        f = open(self.sbatchfilename, 'w')
        with redirect_stdout(f): #save sbatch file
        #test if TMA run or not
            if self.TMA == 'True':
                self.environment = ''.join([O2_global_path + 'environments/cycif_pipeline'])
                print_TMA_sbatch_file()
            else:
                self.print_sbatch_file()
        f.close()

#summary class for pipeline
class Summary(object):
    directory = master_dir
    environment = ''.join([O2_global_path+'environments/cycif_pipeline'])
    parameters = master_dir
    modules = ['conda2/4.2.13']
    run = ''.join(['python ' + O2_global_path + 'bin/Project_Run_Summary.py'])
    run_name = 'NA'
    sbatch = ['-p short', '-t 0-1:00', '-J Run_Summary', '-o Step_7_Project_Summary.o', '-e Step_7_Project_Summary.e']

    # initilizing class and printing when done
    def __init__(self):
        print("Initialize Summary Definition")

    # export the sbatch parameters saved
    def sbatch_exporter(self):
        for i in self.sbatch:
            print('#SBATCH ', i)

    # export the module parameters
    def module_exporter(self):
        for i in self.modules:
            print('module load', i)

    # print the sbatch job script
    def print_sbatch_file(self):
        print('#!/bin/bash')
        self.sbatch_exporter()
        self.module_exporter()
        print('source activate ', self.environment)
        print(self.run, self.parameters, self.run_name)
        print('conda deactivate')
        print('sleep 5') # wait for slurm to get the job status into its database
        print('sacct --format=JobID,Submit,Start,End,State,Partition,ReqTRES%30,CPUTime,MaxRSS,NodeList%30 --units=M -j $SLURM_JOBID') #resource usage

    # save the sbatch job script
    def save_sbatch_file(self):
        f = open('Summary.sh', 'w')
        with redirect_stdout(f):
            self.print_sbatch_file()
        f.close()

#run it
if __name__ == '__main__':
    #output sbatch files to run for O2 for each component in pipeline

    # grab all image folders within master directory
    samples = next(os.walk(master_dir))[1]
    # log folder is where run logs are stored, exclude from folder to execute
    samples = [n for n in samples if not ('log' in n)]

    #QC
    part1=QC()
    part1.save_sbatch_file()

    #for each sample create a pipeline sbatch script for each sample
    for n in samples:
        #log by sample
        print('Initializing for Sample:'+n)

        # Define Illumination
        part2 = Illumination()
        part2.sample = n

        # Define stitcher & update sample name
        part3 = Stitcher()
        part3.sample = n

        # Define probability mapper
        part4 = Probability_Mapper()
        part4.sample = n

        # Define segmenter
        part5 = Segmenter()
        part5.sample = n

        # Define histocat
        part6 = feature_extractor()
        part6.sample = n

        #Parse Yaml File for parameters
        condition=update_parameters(file,part3,part4,part5,part6)

        #Save sbatch files
        part2.save_sbatch_file()
        part3.save_sbatch_file()
        part4.save_sbatch_file()
        part5.save_sbatch_file()
        part6.save_sbatch_file()

    # Summary
    part7 = Summary()
    part7.run_name = condition.get('Run').get('Name') #name given for run
    part7.save_sbatch_file()

    #merge all sbatch jobs for the samples to be run into one file to be submitted to O2
    print('Integrating CyCif Pipeline')
    master(samples,str(condition.get('Run').get('TMA')))

    # change permissions to make file runable on linux
    os.system('chmod 755 Run_CyCif_pipeline.sh')

    #save module and environment versions
    save_module_versions()