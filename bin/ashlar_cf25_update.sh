#create environment
conda create -n ashlar_cf25 python==3.7
#activate environment and install
conda install -q -y -c conda-forge pyfftw
#initial install git repo
git clone --single-branch --branch dev-handle-cf25-exp https://github.com/Yu-AnChen/ashlar.git
#install ashlar version cf25 from Yuan
pip install -e /n/groups/lsp/cycif/cycif_pipeline_testing_space/mcmicro/dev_module_git/ashlar_cf25

#if you want to update the repo
module load conda2/4.2.13
source activate  /n/groups/lsp/cycif/mcmicro/environments/ashlar
cd /n/groups/lsp/cycif/cycif_pipeline_testing_space/mcmicro/dev_module_git/ashlar
git pull
#pip install --user -e /n/groups/lsp/cycif/cycif_pipeline_testing_space/mcmicro/dev_module_git/ashlar
#current environment has: scikit-image == >0.15 
#if new environment built (10.04.2019), ensure this library version or higher to gain ashlar speed/memory use improvements
conda deactivate


#installing ashlar environment: 
#1) conda environment create python=3.7 
#2) download github repo and install using pip install -e [path to github repo]  (don't install with --user as will be installed not in conda environment)
#3) install local copy of JAVA and setup conda environment variables 
