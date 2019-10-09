#Purpose: Generate summary log file for CyCif_Pipeline_run
#Secondary Purpose: Clean up any directories shouldn't be present
#Input: Base folder
#Output:

#Libraries
import os

#remove folder from HistoCat run
os.system('echo Cleaning Up Leftover Folders')
os.system('rm -r output')

#move files into folder
#[TODO] The pipeline must ignore this folder
#[TODO] What happens if pipeline is run multiple times?
#potential solution: CyCif_Pipeline_Log_Files_Run_1 ...
os.system('mkdir CyCif_Pipeline_Log_Files')
os.system('mv *.sh CyCif_Pipeline_Log_Files')
os.system('mv *.e CyCif_Pipeline_Log_Files')
os.system('mv *.o CyCif_Pipeline_Log_Files')

#[TODO] based on folder structure, summarize what successfully completed
cell_states  clustering  dearray  feature_extraction  illumination_profiles  prob_maps  raw_files  registration  segmentation

#[TODO] summarize the resource usage
for each *.o parse the bottom portion then summarize the resource usage

#[TODO] plot the resource usage

#[TODO] analyze data based on certain markers

