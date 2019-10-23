#script used for testing
#purpose is to remove all files that are not the raw images and markes.csv
echo 'Remove Job files'
rm -f *.o
rm -f *.e
rm -f *.sh
rm -f *.txt
echo 'Remove folder structure except raw images'
rm -fr */cell_states  
rm -fr */clustering  
rm -fr */dearray  
rm -fr */feature_extraction  
rm -fr */illumination_profiles  
rm -fr */prob_maps  
rm -fr */registration
rm -fr */segmentation
rm -fr output
echo 'Cleaning Completed'
