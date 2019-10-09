# CyCIF Manager

Purpose: Provide pipeline platform infrastructure to streamline CyCIF Analysis
both on a local machine and on the O2 cluster at HMS

# Pipeline Workflow
![CyCIF Pipeline Plan](/images/CyCif_Pipeline_Plan.png)

For more details, please refer to the [mcmicro
manual](https://labsyspharm.github.io/mcmicro/).

# Versions
V1.2.0 - TMA
	- Added TMA functionality and executed as passing argument 
	- Added pipeline will not re-run if parts of pipeline already run (ie if ashlar stitched present, start from there) 
	- Added more code comments
	- Updated user documentation to include feedback from non-computer science users 
	- Add environment and module version tracking
	- Add ability to update if new versions from developers
	- Add ability to use ashlar version cf25 for older images
	- Add varying QC checks to pipeline
		- Check if cycles are stitched correctly (number of cells identified for each DNA channel should stay the same or decrease)
		- Check if user correctly formatted folder structure 
		- Check if resource requirements for O2 need to be changed
		- Check if user modified raw cycle names and fix if they have
		- Add image summary for different stages of pipeline
	- Add summary file of pipeline progress
	- Add summary of resources used	


V1.1.0 - Parallelization

	- Added O2 pipeline parallelization for each processed image
	- Fix several bugs related to pipeline handling 
	- Change log file naming convention for easier reading
