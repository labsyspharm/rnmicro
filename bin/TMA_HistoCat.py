#Created by: Nathan T. Johnson
#Edited: 10.09.2019
#Purpose: Supply HistoCat Processing for TMA files based on mcmicro pipeline
#Input: directory to based, image to be processed
#Output: Histocat output similiar to mcmicro pipeline except for individual TMA files

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

#Global Variables
#master_dir = os.path.normpath(sys.argv[1])
#image = os.path.normpath(sys.argv[2])
master_dir = '/home/bionerd/Dana_Farber/CyCif/git/mcmicro/example_data' #unique to local test
image = 'image_1'
O2_global_path = '/n/groups/lsp/cycif/cycif_pipeline_testing_space/mcmicro/environments'
parameters = ["5", "no"]
run = 'matlab -nodesktop -r '
environment = ''.join([O2_global_path + 'environments/histoCAT'])
program = ''.join(['"addpath(genpath(\'', environment, '\'));Headless_histoCAT_loading('])

if __name__ == '__main__':
    #define path information
    path_tif = master_dir + '/' + image + '/dearray/'
    path_mask = master_dir + '/' + image + '/dearray/masks/'

    #tif
    tif = glob.glob(path_tif + '*.tif')
    tif = [i.split(path_tif)[1] for i in tif]
    regex = re.compile(r"[0-9]") #remove any tif files do not have digits in them
    tif = [i for i in tif if regex.search(i)]

    #masks
    masks = glob.glob(path_mask + '*mask.tif')
    masks = [i.split(path_mask)[1] for i in masks]

    #basic error checking
    if not len(tif) or len(masks) == 0:
        print('ERROR: Failure to find TMAs or mask')
    if len(tif) != len(masks):
        print('ERROR: Number of TMAs do not match number of mask')

    #processing for each TMA
    for i in range(0,len(tif)):
        # make sure to grab the same mask and TMA
        print('Processing:', tif[i], masks[i])
        #warn user if not the same
        if tif[i].split('.')[0] != masks[i].split('_')[0]:
            print('ERROR: Tif and Mask names are not the same')
        # specific for histocat TODO: change to be yaml inputable
        tmp = ''
        tmp = tmp.__add__(run)
        tmp = tmp.__add__(program)
        tmp = tmp.__add__(''.join(["'", path_tif, ","]))
        tmp = tmp.__add__(''.join(["'", tif[i]]))
        tmp = tmp.__add__(''.join(["'", path_mask, "',"]))
        tmp = tmp.__add__(''.join([masks[i], ",'", master_dir, "/", "markers.csv'", ",", "'", parameters[0], "'", ",","'", parameters[1], "')\""]))

        #process to run [TODO: test if works]
        os.system(tmp)