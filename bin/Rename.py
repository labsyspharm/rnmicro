#Created: Nathan T. Johnson
#Purpose: rename files so that order stamp is based on date for ashlar input and correct stitching
#call program on project folder parent
#input: project path
#output: raw image file renamed to remove what the user modified

#libraries
import os
import glob
import sys

master_dir = os.path.normpath(sys.argv[1])
#master_dir = os.path.normpath('/home/bionerd/Dana_Farber/CyCif/git/mcmicro/example_data/')

#rename all files using order
files = next(os.walk(master_dir))[1]

#rename files to ensure correct order
for i in iter(files):
	print('Processing File:'+i)
	to_process = glob.glob(''.join([master_dir + '/' + i + '/raw_files/*']))
	for n in to_process:        
		rename = n.split('/')[-1].split('Scan_')[-1]
		rename = master_dir + '/' + i + '/raw_files/' + rename
		output = ''.join(['mv ' + n + ' ' + rename]) #execution
		os.system(output)
