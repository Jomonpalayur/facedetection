# Face Detection and Matching with OpenCV

This Python code demonstrates real-time face detection using OpenCV and matches detected faces with reference photos. It also displays the file name of the matched reference photo in the camera preview.

## Prerequisites

Before running the code, ensure you have the following installed:

- Python (version 3.x recommended)
- OpenCV (cv2)
- NumPy
- A webcam or camera device connected to your computer

## Getting Started

1. **Clone this repository** to your local machine using the following command:

   ```bash
   git clone https://github.com/yourusername/face-detection-and-matching.git
   
   
## Adding Reference photos
Add reference photos to the reference_photos directory. These photos will be used for face matching. Ensure that the reference photos have a clear face of the person you want to match.

Each reference image should ideally contain a single face.
The quality and clarity of the reference images can significantly affect matching accuracy.
Running the Code
To run the code, execute the following command in your terminal:

```bash
python face_detection_and_matching.py
```
##
This will start the webcam and display the camera preview with real-time face detection. Detected faces will be matched with reference photos, and the file name of the matching reference photo will be displayed next to each detected face.

Press the 'q' key to exit the program when you're finished.

## Configuration
You can adjust the following parameters in the code to customize the behavior:

reference_photos: The directory containing reference photos.
threshold: The threshold for face matching. Adjust this value to control the matching sensitivity.
License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments
Haar Cascade Classifier for face detection provided by OpenCV.
OpenCV - Open Source Computer Vision Library.
