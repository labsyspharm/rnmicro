module load conda2/4.2.13
source activate /n/groups/lsp/cycif/cycif_pipeline_testing_space/mcmicro/environments/cycif_pipeline/
#run program, echo to screen and save to output file
python /n/groups/lsp/cycif/cycif_pipeline_testing_space/mcmicro/O2/CyCif_Pipeline_O2_v1.2.py $1 $2 $3 | tee CyCif_Pipeline_log.txt
conda deactivate
