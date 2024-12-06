# Vector Annotation Tool

This is a Python-based tool for annotating nucleus-Golgi vectors on 3D microscopy images. This tool can be used to annotate vectors for [3DCellPol](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4947066) training.
The tool supports annotation of paired centroids and zooming, with the ability to save annotations and load previously saved annotations.
![](https://github.com/HemaxiN/VectorAnnotationTool/blob/main/images/annotation_tool.png)

## How to cite

```bibtex
@article{narotamo49470663dcellpol,
  title={3dcellpol: Joint Detection and Pairing of Cell Structures to Compute Cell Polarity},
  author={Narotamo, Hemaxi and Franco, Cl{\'a}udio Areias and Silveira, Margarida},
  journal={Available at SSRN 4947066}
}
```

## Features

* Multi-Channel Image Support: Load and view RGB TIFF files (the red and green channels will be considered for annotation). Navigate through z-slices using the horizontal slider at the bottom.
* Zoom and Pan: Use the mouse wheel to zoom in and out at any position on the image. Use the left mouse button to drag and reposition the image within the display area.
* Centroid Selection: After clicking on ```Select Centroids```, you can select the nucleus centroid (first click), and then the corresponding Golgi centroid (second click). Note: You can change slices after selecting the nucleus centroid and then choose the corresponding Golgi centroid in a different slice.
* Vector Display: A white line connecting the nucleus and Golgi centroids will be drawn. This line is only displayed in the z-slices that the vector spans.
* Vector Removal: After clicking on ```Remove Vector```, you can delete a vector by clicking on it. Confirm the vector's removal by navigating through the slices.
* Annotation Management: Save and load annotations in .csv format.

## How to use

1. **Download the App**: Download the `annotation_vectors.zip` file, extract its contents, and use the ```annotation_vectors.exe``` file (available [here](https://huggingface.co/Hemaxi/VectorAnnotationTool/tree/main)). Alternatively, run the Python script [annotation_vectors.py](https://github.com/HemaxiN/VectorAnnotationTool/blob/main/annotation_vectors.py).
2. **Load an Image**: Click on `Load Image` and select a .tif file. The tool will normalize the intensity values of each slice and display one z-slice at a time.
3. **Navigate Slices**: Use the horizontal slider at the bottom of the interface to navigate through the z-slices of the image stack.
4. **Zoom and Pan**: Use the mouse wheel to zoom in and out at the cursor's position. Drag the image with the left mouse button to move around the image.
5. **Select Centroids**: Click on ```Select Centroids``` and follow these steps: Click on the image to mark a nucleus centroid (green dot). Click again to mark the corresponding Golgi centroid (red dot). A white line will automatically connect the two centroids. Note: You can change slices between marking the nucleus and Golgi centroids.
6. **Remove a Vector**: Click on ```Remove Vector``` and then click on a white vector to delete it. Confirm the removal by navigating through the z-slices.
7. **Save/Load Annotations**: Use ```Save Centroids```to save annotations as a .csv file. Use ```Load Centroids``` to load existing annotations.
   
## Output CSV files

Each output CSV file has N rows, each row contains the (XN,YN,XG,YG,ZN,ZG) coordinates of the annotated nucleus-Golgi pairs, where:
* XN, YN, ZN are the (x,y,z) coordinates of the nucleus centroid;
* XG, YG, ZG are the (x,y,z) coordinates of the corresponding Golgi centroid.
