#Created: Nathan T. Johnson
#Purpose: rename files so that order stamp is based on date for ashlar input and correct stitching
#call program on project folder parent


#libraries
import os
import glob

#not needed if run on command line
#os.chdir('/home/bionerd/test_dir')

#rename all files using order
files = os.listdir('.')
#only needed if certain files should not be processed
files.remove('Rename.py')

#rename files to ensure correct order
for i in iter(files):
	print('Processing File:'+i)
	to_process = glob.glob(''.join([i + '/raw_files/*']))
	for n in to_process:        
		rename = n.split('/')[-1].split('Scan_')[-1]
		tmp = n.split('/')[:-1]
		tmp.append(rename)
		rename = '/'.join(tmp)
		output = ''.join(['mv ' + n + ' ' + rename]) #execution 
		#print(output)       
		os.system(output)
