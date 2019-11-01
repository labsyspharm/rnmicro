#Received from Hung-Yi Wu




from google.colab import drive
drive.mount('/content/drive')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from skimage.transform import resize

folderpath = '/content/drive/My Drive/Peter_Sorger_lab/Project/Pre-Cancer Atlas'

def clip(a):
    b = np.copy(a).astype(float)
    b_min = b.min()
    b_scale = b.max()-b_min
    b -= b_min
    b /= b_scale
    return b

def crop(a):
    return a

image_ID = 'TON7'
# load
proba_mask = np.load(os.path.join(folderpath, '{}_proba_mask.npy'.format(image_ID)))
seg_mask = np.load(os.path.join(folderpath, '{}_seg_mask.npy'.format(image_ID)))
nuclei_stain = np.load(os.path.join(folderpath, '{}_nuclei_stain.npy'.format(image_ID)))
df = pd.read_csv(os.path.join(folderpath, 'TON7.csv'))
y_lim, x_lim = nuclei_stain.shape
# proba_mask was down-sampled to fit to U-net training sample resolution
# in order to compare, resize it back
proba_mask = resize(proba_mask, seg_mask.shape)
# clip & crop
proba_mask = crop(clip(proba_mask))
seg_mask = crop(clip(seg_mask))
nuclei_stain = crop(clip(nuclei_stain))

# plot
fig, ax = plt.subplots(ncols=4, nrows=1, figsize=(16,4))
ax[0].imshow(proba_mask, cmap='Reds', aspect='auto')
ax[0].set_title('U-net Mask (red)')
ax[1].imshow(seg_mask, cmap='Reds', aspect='auto')
ax[1].set_title('Segmentation Mask (red)')
ax[2].imshow(nuclei_stain, cmap='Blues', aspect='auto')
ax[2].set_title('Nuclei Stain (blue)')
ax[3].scatter(df['X_position'], 14521-df['Y_position'], s=5)
ax[3].set_title('Feature cell positions (red)')
ax[3].set_xlim([0, x_lim])
ax[3].set_ylim([0, y_lim])
for axis in ax:
    axis.set_xticks([])
    axis.set_yticks([])
fig.tight_layout()
# plt.show()
plt.savefig(os.path.join(folderpath, '{}_proba_seg_stain.png'.format(image_ID)), dpi=600)
plt.close()

seg_mask = np.load(os.path.join(folderpath, '{}_seg_mask.npy'.format(image_ID)))
plt.imshow(seg_mask, 'Reds')
plt.show()

plt.imshow(seg_mask>0, 'Reds')
plt.show()

seg_mask[seg_mask>0].flatten()[0:5]

np.unique(seg_mask[seg_mask>0])

import collections
c = collections.Counter(seg_mask[seg_mask>0].flatten())
c.most_common(5)

a = np.zeros(seg_mask.shape)
a[seg_mask>0] = 1
plt.imshow(a, 'Reds')
plt.colorbar()
plt.show()

len(c.most_common())
