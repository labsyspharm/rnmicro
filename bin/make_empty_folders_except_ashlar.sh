#make tmp folder
mkdir tmp

#make folder directories
for i in `ls -d JENNTNBC*/raw_files`; do mkdir -p ./tmp/${i}; done
for i in `ls -d JENNTNBC*/illumination_profiles`; do mkdir -p ./tmp/${i}; done
for i in `ls -d JENNTNBC*/registration`; do mkdir -p ./tmp/${i}; done

#cp the file name into folders
for n in `ls -d JENNTNBC*/raw_files`;
do
	for i in `ls ${n}/*`; do touch tmp/${i}; done;
done

for n in `ls -d JENNTNBC*/illumination_profiles`;
do 
	for i in `ls ${n}/*`; do touch tmp/${i}; done;
done
