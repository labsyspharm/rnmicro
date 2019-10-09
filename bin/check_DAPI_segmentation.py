#received from Hung-Yi Wu 

from skimage.external import tifffile
import numpy as np
​
with tifffile.TiffFile('./project_folder/TON7/prob_maps/TON7_NucleiPM_1.tif') as tif:
        proba_mask = tif.series[0].pages[0].asarray()
        ​
        with tifffile.TiffFile('./project_folder/TON7/segmentation/nucleiMask.tif') as tif:
                seg_mask = tif.series[0].pages[0].asarray()
                ​
                with tifffile.TiffFile('./project_folder/TON7/registration/TON7.ome.tif') as tif:
                        nuclei_stain = tif.series[0].pages[0].asarray()
                        ​
                        np.save('TON7_seg_mask.npy', seg_mask)
                        np.save('TON7_proba_mask.npy', proba_mask)
                        np.save('TON7_nuclei_stain.npy', nuclei_stain)
                        print('Done.')
