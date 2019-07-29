#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

/*** signed short int has size 2 bytes */
#define BYTES_PER_READ 2
/*** 5376 offset + 352 nii_header_size = 5728 bytes */
#define NIFTI_HEADER_SIZE 5728
/*** product of the 3 dimensions of one 3D image (64*64*34) */
#define IMG_SIZE 139264
/*** there are 200 3D images on the nifti file indicated by its 4th dimension */
#define NUM_OF_IMAGES 200

struct Nifti{
    short *buffer;
};

/*** function to read the image data from a Nifti file with the previously defined characteristics */ 
struct Nifti read_img(char* filename){

    clock_t duration = clock();

    long size;
    size_t read;
    short *buffer;

    FILE *file = fopen(filename, "rb");

    if (!file) {
        fprintf(stderr, "Unable to open/create file\n");
        exit( 1 );
    }

    /*** Size of file */
    fseek(file, 0, SEEK_END);
    size = ftell(file) - NIFTI_HEADER_SIZE;

    if(!(buffer = malloc(size))) {
        fprintf(stderr, "Failed to allocate buffer memory\n");
        exit( 1 );
    }

    fseek(file, NIFTI_HEADER_SIZE, SEEK_SET);   
    read = fread(buffer, BYTES_PER_READ, size / BYTES_PER_READ, file);
    printf("I read %zu elements of size %d bytes (total bytes read: %zu)\n",
        read, BYTES_PER_READ, read * BYTES_PER_READ);

    struct Nifti img = {buffer};   
	fclose(file);

    duration = clock() - duration;
    double time_taken = ((double)duration)/CLOCKS_PER_SEC;

    printf("Elapsed read_img time: %fs\n", time_taken);

    return img;

}

/*** function to get an array of ssds between a target image and the rest */
long long *get_ssd_array( short* buffer, int num_of_images, int img_size ){

    clock_t duration = clock();
	
    long long *ssd_array;
    if(!(ssd_array = malloc(sizeof(long long)*(num_of_images - 1)))) {
        fprintf(stderr, "Failed to allocate ssd_array memory\n");
        exit( 1 );
    }
	
    long long ssd;
    short diff = 0;

    for( int j = 1; j < num_of_images; j = j + 1 ){
        ssd = 0;
	for( int  i = 0; i < img_size; i = i + 1 ){
            diff = buffer[i] - buffer[i + j*img_size];
            ssd += (long long)(diff*diff);
        }
        ssd_array[j-1] = ssd;
    }

    duration = clock() - duration;
    double time_taken = ((double)duration)/CLOCKS_PER_SEC;

    printf("Elapsed get_ssd_array time: %fs\n", time_taken);

    return ssd_array;

} 


int main(int argc, char *argv[])
{    
	char *nii_file;
	/*** set file path accordingly*/
	nii_file = "C:\\Users\\Javier\\Desktop\\BMB_1\\sub-0003001\\ses-1\\func\\sub-0003001_ses-1_task-rest_run-1_bold.nii";

	struct Nifti img = read_img(nii_file);

	long long *ssd_array = get_ssd_array(img.buffer, NUM_OF_IMAGES, IMG_SIZE);
	printf("ssd_first: %lld\n", ssd_array[0]);
	printf("ssd_last: %lld\n", ssd_array[NUM_OF_IMAGES - 2]);

    return 0;
}

/*** Sample output:
I read 27852800 elements of size 2 bytes (total bytes read: 55705600)
Elapsed read_img time: 0.421000s
Elapsed get_ssd_array time: 0.047000s
ssd_first: 36263554
ssd_last: 198750728
Press any key to continue... */
