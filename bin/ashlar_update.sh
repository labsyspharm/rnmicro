module load conda2/4.2.13
source activate  /n/groups/lsp/cycif/mcmicro/environments/ashlar
cd /n/groups/lsp/cycif/cycif_pipeline_testing_space/mcmicro/dev_module_git/ashlar
git pull
#conda install -q -y -c conda-forge pyfftw
#set environment location: 
#python -m pip install -t /n/groups/lsp/cycif/cycif_pipeline_testing_space/mcmicro/environments/ashlar/lib/python3.7/site-packages -e /n/groups/lsp/cycif/cycif_pipeline_testing_space/mcmicro/dev_module_git/ashlar
#current environment has: scikit-image == >0.15 
#if new environment built (10.04.2019), ensure this library version or higher to gain ashlar speed/memory use improvements
conda deactivate
