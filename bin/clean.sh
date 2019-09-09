#script used for testing
#purpose is to remove all files that are not the raw images and markes.csv
echo 'Remove Job files'
rm *.o
rm *.e
rm *.sh
echo 'Remove folder structure except raw images'
rm -r */cell_states  
rm -r */clustering  
rm -r */dearray  
rm -r feature_extraction  
rm -r illumination_profiles  
rm -r prob_maps  
rm -r registration
rm -r segmentation
echo 'Cleaning Completed'
