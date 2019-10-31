# End-to-end pipeline execution {#pipeline}

Here we will walk you through running the default end-to-end processing pipeline
comprising [stitching and registration](#stitch), [segmentation](#segment), and
[single-cell feature extration](#features).

## Installation

Run the following command to install the pipeline execution tools:

```bash
bash /n/groups/lsp/cycif/mcmicro/O2_install.sh
source ~/.bash_profile
```

Run this command to check for success:

```bash
which cycif_pipeline_activate.sh
```
* If you see `/n/groups/lsp/cycif/mcmicro/bin/cycif_pipeline_activate.sh`, the
  installation succeeded.
* If you see no cycif_pipeline_activate.sh in ...` then the installation
  failed.
* If failed, contact someone from computational forum

## Usage

The commands below use the username `abc123`, so in the typed commands you must
substitute your own username (or the username of whomever you’re working on
behalf of).

### Data transfer

First you will need to setup an ssh Key so O2 can connect to the transfer server in order to transfer your data

*See Instructions in FAQ*

Next you will need to transfer your data to the scratch space (temporary high data volume storage):

```bash
sbatch transfer.sbatch FROM /n/scratch2/abc123/PROJECT
```

Replace `FROM` with the path to your data, and `PROJECT` with a short name for
this project or experiment. We will refer to `/n/scratch2/abc123/PROJECT` as the
"working directory".

*See Folder Setup in Folder Organization Example*

### Go to the working directory

```bash
cd /n/scratch2/abc123/PROJECT
```

### Generate the pipeline execution script

```bash
cycif_pipeline_activate.sh /n/scratch2/abc123/PROJECT
```

### Launch the pipeline

```bash
bash Run_CyCif_pipeline.sh
```

## Worked example using a sample dataset

```bash
sbatch --wait transfer.sbatch /n/groups/lsp/cycif/mcmicro/example_data/ /n/scratch2/abc123/example_data
cd /n/scratch2/abc123/example_data
cycif_pipeline_activate.sh /n/scratch2/abc123/example_data
bash Run_CyCif_pipeline.sh
```

Note that we have added the `--wait` option to the `sbatch` command which will
pause until the data has finished transferring before continuing with the
remaining steps. This is only practical if the dataset is small (less than about
50 GB). If your data is larger, see the Tips and Tricks section below.

## Results

Upon completion of the pipeline, the following folders will appear within your
project directory containing the processed information from each part of the
pipeline. The folders are:

* `cell_states`: Placeholder for future analysis
* `clustering`: Placeholder for future analysis
* `dearray`: Contains masks
* `feature_extraction`: The counts matrix of marker expression at a single cell
  level for all images (Output of HistoCAT software)
* `illumination_profiles`: Preprocessing files required for stitching the
  acquired raw tiles into a single image (Ashlar)
* `prob_maps`: Probability maps predicted by the UMAP deep learning algorithm
  for identifying nucleus, cell borders and background
* `raw_files`: Your original folder containing the raw images
* `registration`: Image that has been stitched and aligned over multiple cycles
  (needs to be uploaded to Omero for viewing or can be viewed using Image J)
* `segmentation`: Provides the location for the nuclei and a cell within an
  image

## Visualize Images on Omero

1. Transfer data to ImStor
1. Import data to Omero

## Tips and Tricks

### Processing your own data

#### Folder Organization Example
Project folder must be at a location findable by O2.

```bash
(base) bionerd@MTS-LSP-L06275:~/Dana_Farber/CyCif/git/CyCif_O2_Manager/example_data$ pwd
/home/bionerd/Dana_Farber/CyCif/git/CyCif_O2_Manager/example_data
```

Within your data folder there are separate folders for each imaged slide.
Can be whole tissue slide or TMA (eventually).

```bash
(base) bionerd@MTS-LSP-L06275:~/Dana_Farber/CyCif/git/CyCif_O2_Manager/example_data$ ll
drwxrwxrwx 1 bionerd bionerd 4096 Aug  9 08:03 image_1/
drwxrwxrwx 1 bionerd bionerd 4096 Aug  9 08:04 image_2/
```

Each folder should contain a subfolder: 'raw_files' with
where for each CyCIF cycle there should the raw images from the microscope
for example from Rare Cycte: '.rcpnl' and '.metadata '

```bash
(base) bionerd@MTS-LSP-L06275:~/Dana_Farber/CyCif/git/CyCif_O2_Manager/example_data$ ll image_1/
total 0
drwxrwxrwx 1 bionerd bionerd 4096 Aug  9 10:44 ./
drwxrwxrwx 1 bionerd bionerd 4096 Aug  7 12:19 ../
drwxrwxrwx 1 bionerd bionerd 4096 Aug  9 08:04 raw_files/
[ntj8@login01 image_1]$ cd raw_files/
[ntj8@login01 raw_files]$ ll
total 3326644
-rwxrwx--- 1 ntj8 ntj8      11516 Jul  9 17:30 Scan_20190612_164155_01x4x00154.metadata
-rwxrwx--- 1 ntj8 ntj8 1703221248 Jul  9 17:31 Scan_20190612_164155_01x4x00154.rcpnl
-rwxrwx--- 1 ntj8 ntj8      11524 Jul  9 17:31 Scan_20190613_125815_01x4x00154.metadata
-rwxrwx--- 1 ntj8 ntj8 1703221248 Jul  9 17:32 Scan_20190613_125815_01x4x00154.rcpnl
```

After the CyCIF Pipeline is run there will be additional folders created for
each slide (explained in [Results]).

#### Requirements
* Can be run either locally or on O2.
* For O2, user must have an O2 account and be a member of the `ImStor_sorger` groups. Run `groups` on O2 to check.
  * Request O2 account and group access at https://rc.hms.harvard.edu/.
* For the moment, you are responsible for transferring the data to the scratch space
* Data follows Folder Organization (shown above).
* File 'markers.csv' containing one marker per row, in the order imaged. Example:
```
DNA1
AF488
AF555
AF647
DNA2
mLY6C
mCD8A
mCD68
```
* File 'data.yaml' listing what parameters to use for pipeline execution (If you are unsure, just use the current ones) Example:

```
---
Run:
  Name: 'CyCif Example'
  TMA: False
  cf25: False
  file_extension: .rcpnl
QC:
Illumination:
  lambda_flat: 0.1
  lambda_dark: 0.01
  estimate_flat_field_only: False
  max_number_of_fields_used: None
Stitcher:
  -m: 30
  --filter-sigma: 0
Probability_Mapper:
  dapi_channel: 0
  hs_scaling: 1
  vs_scaling: 1
Segmenter:
  HPC: true
  fileNum: 1
  TissueMaskChan: [2]
  logSigma: [3 30]
  mask: tissue
  segmentCytoplasm: ignoreCytoplasm
Feature_Extractor:
```

## Frequently Asked Questions (FAQ)

### Help my O2 environment changed!
O2 loads in `.bash_profile` then `.bashrc` by default unless `.bash_profile`
does not exist. If your O2 environment has changed, it is likely that the
installation instructions created `.bash_profile`. Solution is to replace the
installation instructions from `.bash_profile` to `.bashrc`

### How To Setup O2 SSH Key


The following instructions take you through setting up a SSH Key on O2. ([Official instructions for generating SSH key](https://wiki.rc.hms.harvard.edu/display/O2/How+to+Generate+SSH+Keys))

The senario behind this is that in CyCIF pipeline, it is designed to first submit a job to transfer files from /n/files, get the job ID, and the following steps in the pipeline are dependent on the transfer job. 

And the SSH Key allows you to transfer files from /n/files using the transfer server with `ssh rsync`, without being prompted for password. So that you can put `ssh rsync` from n/files to /n/scratch2 into an sbatch script. And the job could hang until the transfer is complete, then it will run the rest of the script. 

##### Note: Replace your_ecommons with your ecommons while you type in the commands.

---

#### Generate SSH Key
*On O2 login node*
```bash
$ ssh-keygen -t rsa
Generating public/private rsa key pair.
Enter file in which to save the key (/home/your_ecommons/.ssh/id_rsa):
```
Hit Enter ⏎
```bash
Enter passphrase (empty for no passphrase):
```
Hit Enter ⏎
```bash
Enter same passphrase again:
```
Hit Enter ⏎
```bash
Your identification has been saved in /home/your_ecommons/.ssh/id_rsa.
Your public key has been saved in /home/your_ecommons/.ssh/id_rsa.pub.
The key fingerprint is:
a5:b5:38:73:b7:3c:a6:8a:1d:a8:bd:87:4e:be:33:21 your_ecommons@login01
The key's randomart image is:
```

The following command copies the public key to your authorized_keys file:
```bash
$ cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
```

#### Change file and directory permissions
*On O2 login node*
```bash
$ chmod 0600 ~/.ssh/authorized_keys
$ chmod 0700 ~/.ssh
$ chmod 0711 /home/$USER
```

#### Testing
*On O2 login node*
```
$ srun -p interactive --pty -t 1:00:00 -n 2 bash
srun: job 50830472 queued and waiting for resources
srun: job 50830472 has been allocated resources
$ rsync -Pav transfer:/n/files/ImStor/sorger/data/RareCyte/yc296/YC-20180711-bleached-for-15-min/ /n/scratch2/yc296/transfer_test/
created directory /n/scratch2/your_ecommons/transfer_test
./
CSS08_A-bleach-light-new-S100-MCM6-p57-LSP2-Scan_20180711_144802_01x4x00090.rcpnl
   995391488 100%   95.99MB/s    0:00:09 (xfer#1, to-check=5/7)
CSS08_B-bleach-light-new-S100-MCM6-p57-LSP2-Scan_20180711_144203_01x4x00110.rcpnl
  1216587776 100%   90.51MB/s    0:00:12 (xfer#2, to-check=4/7)
CSS08_C-bleach-light-old-S100-MCM6-p57-LSP1-Scan_20180711_143205_01x4x00100.rcpnl
  1105989632 100%   90.95MB/s    0:00:11 (xfer#3, to-check=3/7)
Scan_20180711_143205_01x4x00100.metadata
        8344 100%   13.34kB/s    0:00:00 (xfer#4, to-check=2/7)
Scan_20180711_144203_01x4x00110.metadata
        9024 100%   14.35kB/s    0:00:00 (xfer#5, to-check=1/7)
Scan_20180711_144802_01x4x00090.metadata
        7636 100%   12.11kB/s    0:00:00 (xfer#6, to-check=0/7)

sent 128 bytes  received 3318399628 bytes  99056709.13 bytes/sec
total size is 3317993900  speedup is 1.00
```


## Instructions for pipeline module developers

Updated your code? Wish to add your method to pipeline? Contact Nathan.

### Install & Run
Assumption: Matlab Installed, Linux Environment (can use linux subsystem for
windows)

```
git clone https://github.com/labsyspharm/mcmicro.git
```

Install conda environments, example data, and github repository dependencies by running within github directory

```
install_environments.sh
install_example_dataset.sh
```

### Local Install
Talk to Nathan.
