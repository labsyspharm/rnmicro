# CyCIF Manager

Purpose: Provide pipeline platform infrastructure to streamline CyCIF Analysis
both on a local machine and on the O2 cluster at HMS

# Pipeline Workflow
![CyCIF Pipeline Plan](/images/CyCif_Pipeline_Plan.png)

For more details, please refer to the [mcmicro
manual](https://labsyspharm.github.io/mcmicro/).

# Versions
V1.2.0 - TMA
	- Added checking if user correctly formatted folder structure for running and warning if not
	- Added pipeline will not re-run if parts of pipeline already run (ie if ashlar stitched present, start from there) 
	- Added TMA functionality and executed as passing argument
	- Add more code comments
	- Updated user documentation to include TMA inclusion and 

V1.1.0 - Parallelization

	- Added O2 pipeline parallelization for each processed image
	- Fix several bugs related to pipeline handling 
	- Change log file naming convention for easier reading
