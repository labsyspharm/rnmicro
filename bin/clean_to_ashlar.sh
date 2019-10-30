#script used for testing
#purpose is to remove all files that are not the raw images and markes.csv
echo 'Remove folder structure up to ashlar'
rm -fr */cell_states  
rm -fr */clustering  
rm -fr */dearray  
rm -fr */feature_extraction  
rm -fr */prob_maps  
rm -fr */segmentation
rm -fr output
echo 'Cleaning Completed'
