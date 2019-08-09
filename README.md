# fMRI motion estimation on FPGAs

One of the most common preprocessing steps applied to fMRI images for their analysis is motion estimation. Correcting it ensures that each voxel of the subsequent 3D images maps to the same point on the brain. A transformation matrix is calculated between a target image and the rest, such as in [niak](https://github.com/SIMEXP/niak/blob/master/bricks/fmri_preprocess/niak_brick_motion_parameters.m), which uses minctracc function for it. This method uses a distance measure among the images to  minimize a cost function on an optimization problem. One common distance measure between 2 images is the sum of squared differences (ssd). 

To explore the feasibility of implementing fMRI motion estimation on FPGAs, a simple approach was to create a script that calculates the ssd among all 3D images of a Nifti file. One was done in python (nifti.py), to take advantage of nibabel library to extract information from the header of the file and easily obtain a list of ssd values for future validation. The other one was done in C, without the use of any external library, since this programming language closely translates to OpenCL, the language needed to leverage Intel FPGAs.

## Steps for downloading the data file

Install [git-annex](http://git-annex.branchable.com/install/) and datalad (pip install datalad)
    
    datalad install ///corr/RawDataBIDS/BMB_1
    datalad get sub-0003001/ses-1/func/sub-0003001_ses-1_task-rest_run-1_bold.nii.gz
    gunzip sub-0003001/ses-1/func/sub-0003001_ses-1_task-rest_run-1_bold.nii.gz

## nifti.py

This script reads a 4D Nifti file using the python library nibabel. The loaded nii file has dimensions (64, 64, 34, 200) which means there are 200 3D images of 139264 voxels each. The head of the image is 352 bytes, and there is an offset (extensions) of 5376 bytes before the image data (although the vox_offset field of the header is wrongly marked as 0).

There are 2 functions, `ssd(img1, img2)` to get the sum of squared differences between 2 3D images and `get_ssd_list(data)`that uses the previous function to get a list of ssds between a target flattened 3D image and the other 3D images of a 4D Nifti file.

These functions (and its old slower version) are timed over 10 runs for performance comparison among them and the equivalent C code. The `get_ssd_list` function takes an average of 14.31 seconds per run on a single intel CORE i7.

## nifti.c

This code performs the same operations as the python one but without using a library for reading the Nifti file, so a function `read_img` is defined for this task. It uses the information obtained from the header of the nii file on the python script, such as the data type of the voxels, the size of the header or the 4 dimensions of the image. The size of the offset (or extensions) was calculated by sustracting from the total size of the file (55711328 bytes), the size of the header (352 bytes) and the size of the actual image data (139264 voxels per image * 200 3D images * 2 bytes per voxel = 55705600 bytes).

The C function `get_ssd_array` is equivalent to the python `get_ssd_list` function but it reads the whole 4D image data as an uni-dimensional array of short ints, and it performs much better under the same hardware conditions, taking an average of 0.047 seconds per run, which is roughly 300 times faster than the python version. 
