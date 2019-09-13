#libraries
from contextlib import redirect_stdout
import yaml
import os
import sys
import shutil
import glob
import pandas as pd

#handles path to data correctly
#master_dir = os.path.normpath(sys.argv[1])
#os.chdir(master_dir)

#local testing
master_dir = os.path.normpath('/home/bionerd/Dana_Farber/CyCif/git/mcmicro/example_data/')
os.chdir('/home/bionerd/Dana_Farber/CyCif/git/mcmicro/O2')

#easy global environment path and version updating on O2 (for switching between testing and stable versions)
O2_global_path = '/n/groups/lsp/cycif/cycif_pipeline_testing_space/mcmicro/'
Version = 'v1.2'

######################
#O2 Handling Function#
######################

#commonly users incorrectly structure the folders for execution or missing files
#input: list of samples and path to data
#returns: error messages to warn user prior to running (doesn't stop user, just warns)
#checking 1) markers.csv exists, 2) checking if each sample has a raw_file,
#3) checking if correct data exists in raw_files folder, 4) check if number of raw cycle number matches the marker names
def file_err_checking(samples,master_dir):
    print('Checking If Data is organized correctly')
    #does the user have markers.csv file
    try:
        os.access(''.join([master_dir + '/markers.csv']),mode=0)

        # if markers.csv exist, test if raw_file exists for each sample
        for current in samples:

            #check if raw_files folder exists
            try:
                os.makedirs(master_dir + '/' + current + '/raw_files')

                try:
                    glob.glob(master_dir + '/' + current + '/raw_files/*.rcpnl')
                except:
                    print('Uh Oh! Image' + current + 'does not have .rcpnl files')
                    print('Must add your raw images!')
                    print('If your microscope does not output .rcpnl files, pipeline may work, but bug Nathan for not adding your favorite microscope')

            except:
                print('Uh Oh! Image' + current + 'did not have the raw_files folder')
                print('Within each image folder, there must be a raw_files folder containing the raw images and metadata for each cycle')

    except:
        print('ERROR, must have \'markers.csv\' file present in your project folder')
        print('File should contain a name for each cycle channel')
        print('Example:')
        example=['DNA1','MARKER1','MARKER2','MARKER3','DNA2','MARKER4','MARKER5','MARKER6']
        for i in example:
            print(i)

#check if any module parts of pipeline have already been run
#input: path to data, list of images, list of pipeline modules to run
#[TODO]: consider markers.csv size
#[TODO]: consider customizing what is removed on an individual sample basis
def pipeline_checking(master_dir,samples,pipeline):
    for i in samples: #i know bad coding practice to use lots of if then, but lots of customization [TODO] clean up code
        # if illumination ran /image/illumination_profiles = (*dfp.tif  *ffp.tif)
        if os.access(''.join([master_dir + '/' + i + '/illumination_profiles']),mode=0):
            #if files exist, remove illumination from pipeline
            if (len(glob.glob(''.join([master_dir + '/' + i + '/illumination_profiles/*.dfp.tif']))) >= 1) & (len(glob.glob(''.join([master_dir + '/' + i + '/illumination_profiles/*.dfp.tif']))) >= 1):
                #pop off illumination check
                pipeline = [n for n in pipeline if not ('illumination' in n)]

        # if stitcher ran /image/registration = (*.ome.tif)
        if os.access(''.join([master_dir + '/' + i + '/registration']), mode=0):
            # if files exist, remove stitcher from pipeline
            if (len(glob.glob(''.join([master_dir + '/' + i + '/registration/*.ome.tif']))) == 1):
                # pop off illumination
                pipeline = [n for n in pipeline if not ('stitcher' in n)]

        #if prob_mapper ran /image/prob_maps = (*ContoursPM_1.tif *NucleiPM_1.tif)
        if os.access(''.join([master_dir + '/' + i + '/prob_maps']), mode=0):
            #if files exist, remove prob_mapper from pipeline
            if (len(glob.glob(''.join([master_dir + '/' + i + '/prob_maps/*ContoursPM_1.tif']))) >= 1) & (len(glob.glob(''.join([master_dir + '/' + i + '/prob_maps/*NucleiPM_1.tif']))) >= 1):
                #pop off illumination
                pipeline = [n for n in pipeline if not ('prob_mapper' in n)]

        #if segmenter ran image/segmentation = (cellMask.tif cellOutlines.tif nucleiMask.tif nucleiOutlines.tif segParams.mat)
        if os.access(''.join([master_dir + '/' + i + '/segmentation']), mode=0):
            #if files exist, remove segmenter from pipeline
            if (len(glob.glob(''.join([master_dir + '/' + i + '/segmentation/*.tif']))) == 4):
                #pop off segmenter
                pipeline = [n for n in pipeline if not ('segmenter' in n)]

        #if feature_extractor ran image_1 / feature_extraction = Cell_image_1*.mat == length of markers.csv & sample_name.csv
        if os.access(''.join([master_dir + '/' + i + '/feature_extraction']), mode=0):

            try:
                os.access(''.join([master_dir + '/markers.csv']), mode=0)
                markers = pd.read_csv(''.join([master_dir + '/markers.csv']))

                # if files exist, remove segmenter from pipeline
                if (len(glob.glob(''.join([master_dir + '/' + i + '/feature_extraction/Cell*.mat']))) == len(markers)) & os.access(''.join([master_dir + '/' + i + '.csv']), mode=0):
                    # pop off segmenter
                    pipeline = [n for n in pipeline if not ('feature_extractor' in n)]

            except:
                print('markers.csv file does not exist')
    return(pipeline)

#create list of lists to handle organizing job ranking and submission to slurm
#input: list of pipeline steps to run and list of samples to integrate
#[TODO] change to image dependent pipeline stack (for now assume first sample image has the same images already ran)
def populate_image_job_dependency(pipeline,samples):
    # list length of number of samples plus one to store the QC step
    res = lst = [[] for _ in range(len(samples)+1)]

    # for QC step
    res[0] = [i for i in files if pipeline[0] in i]

    #make list of lists for each sample and its processing stack to put together
    for n in range(1,len(pipeline)):

        #grab all files to be run as part of each stage
        tmp = [i for i in files if pipeline[n] in i]

        # populate the list with each file (TOFIX:list comprehension?)
        for z in range(0, len(tmp)):

            #error checking: if tripped most likely due to overlapping names so pipeline dependencies may be screwed up
            #solution: check 'Run_CyCif_pipeline.sh' to see if the images are correctly formatted
            #easy fix: change a sample name so the base name doesn't overlap
            #for example: image_1 vs image_1A = cause it to trip
            if len([i for i in tmp if samples[z] in i]) != 1:
                print('Sample length error! Check O2 submission stack')

            #rearrange order of samples is consistent ie image 1 goes with all image 1 pipeline defined by variable samples
            res[z + 1].append([i for i in tmp if samples[z] in i][0])
            #res[i+1].append(tmp[i])

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

        #each step dependent on QC run, then a stack is made separated for each individual sample ID
        for i in range(1,len(res)): #length to number of samples
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

        #tell User done submitting
        print ('echo Successfully submitted CyCif Pipeline')
    f.close()

#master function that controls error checking, submission, organizing, creating 'Run_CyCif_Pipeline.sh' for cycif pipeline
def master(samples):

    #look for all scripts to include in cycif pipeline
    files = glob.glob('*.sh')

    #Order of list is dependent on order of pipeline steps to be run
    pipeline = ['QC','illumination','stitcher','prob_mapper','segmenter','feature_extractor']

    #error checking raw files are where they should be, markers.csv exists, and cycles matches markers.csv number
    file_err_checking(samples, master_dir)

    #update pipeline list to run based on what files are found to exist (not checking QC of images, just they are present)
    #check whether any parts of pipeline already run using the first image as a reference
    #if images already generated then remove from pipeline array those parts
    print('Checking if pipeline was run previously')
    pipeline=rerun_err_checking(master_dir, samples, pipeline)

    print('Integrating pipeline')
    res=populate_image_job_dependency(pipeline, samples)

    print('Saving Run_CyCif_pipeline.sh')
    save_cycif_pipeline(res)

################################
#CyCIf Method Class Definitions#
################################

#QC (at the moment just folder infrastructure checking) [TODO]
class QC(object):
    directory = master_dir
    executable_path = '../bin/check_folder_v1.py'
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

    # what sbatch parameters to load in O2
    def sbatch_def(self):
        self.sbatch = sbatch_submission()

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

#Illumination Profiles (pre-req for ashlar) [TODO]
class Ilumination(object):
    #environment = '/n/groups/lsp/cycif/CyCif_Manager/environments/ImageJ'
    environment = ''.join([O2_global_path+'environments/ImageJ'])
    directory = master_dir
    parameters = ''.join([O2_global_path + 'bin/illumination_' + Version + '.py'])
    #parameters = '/n/groups/lsp/cycif/CyCif_Manager/bin/illumination_v1.py'
    modules = ['conda2/4.2.13']
    run = 'python '
    sbatch = ['-p short', '-t 0-12:00', '--mem=64G', '-J illumination',
              '-o Step_2_illumination.o', '-e Step_2_illumination.e']
    sample = 'NA'
    sbatchfilename = 'NA'

    # initilizing class and printing when done
    def __init__(self):
        print("Initialize Illumination Definition")

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
        print(self.run, self.parameters, self.directory+'/'+self.sample)
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

#stich the multiple images together [TODO]: fix what runs
class Stitcher(object):
    method = 'Ashlar'
    run = 'No'
    #environment = '/n/groups/lsp/cycif/CyCif_Manager/environments/ashlar'
    environment = ''.join([O2_global_path + 'environments/ashlar'])
    directory = master_dir
    #program = '/n/groups/lsp/cycif/CyCif_Manager/bin/run_ashlar_v1.py'
    program = ''.join([O2_global_path + 'bin/run_ashlar_' + Version + '.py'])
    modules = ['conda2/4.2.13']
    run = 'python'
    sbatch = ['-p short','-t 0-12:00', '--mem=64G', '-J ashlar',
              '-o Step_3_ashlar.o','-e Step_3_ashlar.e']
    sample = 'NA'

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

    # export the module parameters
    def module_exporter(self):
        for i in self.modules:
            print('module load',i)

    #print the sbatch job script
    def print_sbatch_file(self):
        print('#!/bin/bash')
        self.sbatch_exporter()
        self.module_exporter()
        print('source activate ', self.environment)
        print(self.run, self.program, self.directory+'/'+self.sample)
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
    #environment = '/n/groups/lsp/cycif/CyCif_Manager/environments/unet'
    environment = ''.join([O2_global_path + 'environments/unet'])
    directory = master_dir
    executable_path = '../bin/run_batchUNet2DtCycif_V1.py'
    #parameters = ['/n/groups/lsp/cycif/CyCif_Manager/bin/run_batchUNet2DtCycif_v1.py',0,1,1]
    parameters = [''.join([O2_global_path + 'bin/run_batchUNet2DtCycif_' + Version + '.py']), 0, 1, 1]
    modules = ['gcc/6.2.0','cuda/9.0','conda2/4.2.13']
    run = 'python'
    sbatch = ['-p gpu','-n 1','-c 12', '--gres=gpu:1','-t 0-12:00','--mem=64000',
              '-J prob_mapper','-o Step_4_probability_mapper.o','-e Step_4_probability_mapper.e']
    sample = 'NA'

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

    #print the sbatch job script
    def print_sbatch_file(self):
        print('#!/bin/bash')
        self.sbatch_exporter()
        self.module_exporter()
        print('source activate ', self.environment)
        print(self.run, self.parameters[0],self.directory+'/'+self.sample,self.parameters[1],self.parameters[2],self.parameters[3])
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
class Segementer(object):
    method = 'S3'
    run = 'No'
    directory = master_dir
    modules = ['matlab/2018b']
    run = 'matlab -nodesktop -r '
    #environment = '/n/groups/lsp/cycif/CyCif_Manager/environments/segmenter/'
    environment = ''.join([O2_global_path + 'environments/segmenter'])
    #program = ''.join(['"addpath(genpath(\'',self.environment,'\'));O2batchS3segmenterWrapperR('])
    program = 'NA'
    parameters =  ",'HPC','true','fileNum',1,'TissueMaskChan',[2],'logSigma',[3 30],'mask'," \
                  "'tissue','segmentCytoplasm','ignoreCytoplasm')\""
    sbatch = ['-p short', '-t 0-12:00', '-c 1','--mem=100G', '-J Step_5_segmenter', '-o Step_5_segmenter.o', '-e segmenter.e']
    sample = 'NA'

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

    #find all folder names from the directory path position
    def file_finder(self):
        self.files=next(os.walk(self.directory))[1]

    #print the sbatch job script
    def print_sbatch_file(self):
        print('#!/bin/bash')
        self.sbatch_exporter()
        self.module_exporter()
        print(self.run,self.program,"'",self.directory+'/'+self.sample,"'",self.parameters,sep='')
        print("mv", ''.join([self.directory+'/'+self.sample+'/segmentation/'+self.sample+'/*']),''.join([self.directory+'/'+self.sample+'/segmentation/']))
        print("rm -r ", ''.join([self.directory+'/'+self.sample+'/segmentation/'+self.sample]))
        print('sleep 5')  # wait for slurm to get the job status into its database
        print('sacct --format=JobID,Submit,Start,End,State,Partition,ReqTRES%30,CPUTime,MaxRSS,NodeList%30 --units=M -j $SLURM_JOBID')  # resource usage

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
    #environment = '/n/groups/lsp/cycif/CyCif_Manager/environments/histoCAT/'
    environment = ''.join([O2_global_path + 'environments/histoCAT'])
    program = 'NA'
    #program = '"addpath(genpath(\'/n/groups/lsp/cycif/CyCif_Manager/environments/histoCAT/\'));Headless_histoCAT_loading('
    #program = ''.join(['"addpath(genpath(\'',self.environment,'\'));O2batchS3segmenterWrapperR('])
    parameters = ["5", "no"]
    sbatch = ['-p short', '-t 0-12:00', '-c 8','--mem=100G', '-J feature_extractor', '-o Step_6_feature_extractor.o', '-e Step_6_feature_extractor.e']
    sample = 'NA'

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

    #print the sbatch job script
    def print_sbatch_file(self):
        print('#!/bin/bash')
        self.sbatch_exporter()
        self.module_exporter()
        #specific for histocat TODO: change to be yaml inputable
        tmp = ''
        tmp = tmp.__add__(''.join(["'",self.directory,"/",self.sample,"/registration'",","]))
        tmp = tmp.__add__(''.join(["'",self.sample,".ome.tif',"]))
        tmp = tmp.__add__(''.join(["'",self.directory,"/",self.sample,'/segmentation/',"',"]))
        tmp = tmp.__add__(''.join(["'cellMask.tif'",",'",self.directory,"/","markers.csv'",",","'",self.parameters[0] ,"'",",","'",self.parameters[1] ,"')\""]))
        print(self.run,self.program,tmp,sep='')
        print("mv",''.join(['./output/',self.sample,'/*']),''.join([self.directory,'/',self.sample,'/feature_extraction']))
        print("rm -r ",''.join(['./output/',self.sample]))
        print('sleep 5') # wait for slurm to get the job status into its database
        print('sacct --format=JobID,Submit,Start,End,State,Partition,ReqTRES%30,CPUTime,MaxRSS,NodeList%30 --units=M -j $SLURM_JOBID') #resource usage

    # save the sbatch job script
    def save_sbatch_file(self):
        self.sbatchfilename = self.sample + '_feature_extractor.sh'
        f = open(self.sbatchfilename, 'w')
        with redirect_stdout(f):
            self.print_sbatch_file()
        f.close()

#run it
if __name__ == '__main__':
    #output sbatch files to run for O2 for each component in pipeline

    # grab all image folders within master directory
    samples = next(os.walk(master_dir))[1]

    #QC
    part1=QC()
    part1.save_sbatch_file()

    #for each sample create a pipeline structure for that sample
    for n in samples:

        print('Initializing for Sample:'+n)

        # Illumination
        part2 = Ilumination()
        part2.sample = n
        part2.save_sbatch_file()

        # define stitcher & make sbatch file for task
        part3 = Stitcher()
        part3.sample = n
        part3.save_sbatch_file()

        # define probability mapper
        part4 = Probability_Mapper()
        part4.sample = n
        part4.save_sbatch_file()

        # define segmenter
        part5 = Segementer()
        part5.sample = n
        part5.save_sbatch_file()

        # define histocat
        part6 = feature_extractor()
        part6.sample = n
        part6.save_sbatch_file()

        #output master run file to manage running cycif pipeline

    #merge all sbatch jobs for the samples to be run into one file to be submitted to O2
    print('Integrating CyCif Pipeline')
    master(samples)

    # change permissions to make file runable on linux
    os.system('chmod 755 Run_CyCif_pipeline.sh')
