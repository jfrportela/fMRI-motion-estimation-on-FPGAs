# -*- coding: utf-8 -*-
"""
Simple script to read a 4D Nifti image using nibabel library and calculate the
sum of squared differences between the first 3D image and each of the other images.

@author: Javier Fernandez-Rial Portela
"""

import os
import numpy as np
import nibabel as nib
import timeit

# Setting file path and name (current directory by default)
PATH=""
file = os.path.join(PATH, 'sub-0003001_ses-1_task-rest_run-1_bold.nii')

# Loading Nifti image from nii file using nibabel library
img = nib.load(file)

# The 4 dimentions of the image, 3 spacial and one temporal
img.shape
# Output: (64, 64, 34, 200)

# The data type of each voxel is signed short int, of size 2 bytes
img.get_data_dtype()
# Output: dtype('<i2') (equivalent to numpy int16)

# Reading the header of the image
hdr = img.header
# Getting the vox_offset (extensions) of the image
hdr.get_data_offset()
# Output is 0, but that is false, the actual offset is 5376

# Getting the image data after the header and extensions
data = img.get_fdata()
# There are 200 3D images of dimensions (64,64,34)
data.shape
# Output: (64, 64, 34, 200)

# Getting the first 3D image
img1 = data[:,:,:,0]
img1.shape
# Output: (64, 64, 34)

# Converting first image to a 1 dimentional array of 139264 voxels
img1_flat = img1.flatten()
img1_flat.shape
# Output: (139264,)

# Getting the second 3D image
img2 = data[:,:,:,1]
img2_flat = img2.flatten()
img2_flat.shape
# Output: (139264,)

# Function to get the sum of squared differences between 2 3D images
# Params: two flattened 3D images
# Returns: ssd of the two images, an integer
def ssd(img1, img2):
    ssd = 0
    img_len = img1.shape[0]    
    for i in range(img_len):
        diff = img1[i] - img2[i]
        ssd += diff*diff
    return ssd

# Function to get a list of ssds between a target image and the rest 
# Params: the data from a 4D Nifti image
# Returns: a list of ssds, an integer list of size data.shape[3] - 1   
def get_ssd_list(data):
    target_img = data[:,:,:,0].flatten()
    ssd_list = []
    num_of_imgs = data.shape[3]
    for i in range(1,num_of_imgs):
        img = data[:,:,:,i].flatten()
        current_ssd = ssd(target_img,img)
        ssd_list.append(current_ssd)
    return ssd_list

# Getting a list of ssds from the data and printing the first and last ssd values
ssd_list = get_ssd_list(data)
print(ssd_list[0])
# Output: 36263554
print(ssd_list[-1])
# Output: 198750728

# Measuring the time it takes to run the ssd function (data.shape[3]-1)*10 times  
timeit.timeit('ssd(img1_flat, img2_flat)', number=1990, globals=globals())
# Output: 141.7s

# Measuring the time it takes to run the get_ssd_list function 10 times
timeit.timeit('get_ssd_list(data)', number=10, globals=globals())
# Output: 143.1s (average of 14.31s per call)


'''
For the sake of comparison, I show the initial versions of the previous functions
which were 4 times slower due to the use of numpy square or not flattening the 3D images
'''
# Slower version of the ssd function due to the use of numpy square
def ssd_slow(img1, img2):
    ssd = 0
    img_len = img1.shape[0]    
    for i in range(img_len):
        ssd += np.square(img1[i] - img2[i])
    return ssd

# Slower version of the get_ssd_list function due to not flattening the 3D images
def get_ssd_slow(data):
    ssd_list = []
    for i in range(1,data.shape[3]):
        ssd = 0
        for j in range(data.shape[2]):
            for k in range(data.shape[1]):
                for l in range(data.shape[0]):
                    diff = data[l,k,j,0] - data[l,k,j,i]
                    ssd += diff*diff
        ssd_list.append(ssd)
    return ssd_list

# Verifying that the output is the same
ssd_list_2 = get_ssd_slow(data)
print(ssd_list_2[0])
# Output: 36263554
print(ssd_list_2[-1])
# Output: 198750728

# Measuring the performance of the slower functions
timeit.timeit('ssd_slow(img1_flat, img2_flat)', number=1990, globals=globals())
# Output: 517.01s
timeit.timeit('get_ssd_slow(data)', number=10, globals=globals())
# Output: 546.52s (average of 54.65s per run, 4 times slower than get_ssd_list)
