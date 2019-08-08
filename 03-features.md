# Extract spatial single cell features {#features}

Once the image is [segmented](#segment) label masks for nuclei, cytoplasm and cell can be used to extract spatial single cell features.

**Expected input:**

  * `.tif` (16/32 bit) label mask for nuclei, cytoplasm or cell - only one mask can be used per run 
  * `.ome.tif` [stitched](#ashlar) image
  * `.csv` including all channels - corresponding to the `ome.tif`

  **Expected output:**
  
