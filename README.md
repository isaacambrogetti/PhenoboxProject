# Phenobox Project
Phenobox project at Parisod's research group University of Fribourg (CH)

## import packages on Blender
command on terminal:
```bash
<path/to/python/bin/in/blender> ./python -m pip install <package_name> --target="path/to/blender/site-packages"
```
if it doesn't work, run the terminal as the admin


## Introduction
This projects aims to create 3D-models of plants of Biscutella laevigata to be able to extract features (e.g., volume).  
It will carried out throughout 5 years, every two weeks each plant is scanned and the raw 3d-models are stored. The post-processing of the models is carried out in a second moment, and the models are kept also in their raw state to be able to peform secondary processes to extract more features from the model in the future.

## Materials
#### Hardware for scanning the plant:
- **Box** (aka phenobox)  
    About 1mx1mx1m frame having black panels on the bottom, back and top, two semitransparent plexiglass panels to the two sides, and one black rubber mat to cover the main aperture.  
    The frame also has a pole placed vertically in the middle of the main entrance to allow the placement of the scanner.
- **Light system**  
    Two wide stripes of dimmerizable LEDs placed on the cieling of the box and covered with a semitransparent film to diffuse the light evenly.
- **Turntable** (from RevoPoint)  
    Electric turntable where to place the pot that connects via bluetooth to RevoScan5 software to control the seconds/turn.
- **Structured light scanner** (*Revopoint MINI*)  
    [Structured light scanner](https://en.wikipedia.org/wiki/Structured-light_3D_scanner)  having a light projector and a camera system. Here's the [specifics](https://www.revopoint3d.com/pages/industry-3d-scanner-mini).
    - Calibration plate  
        Black plastic rectangle with different white dots.
- **PC** (Lenovo Legion)
    _""characteristics""_

#### Softwares:
- **RevoScan5** (_v_)  
    Software used to control the scanning, strictly related to the scanner and turntable.  
    It is also used for the first post-processing steps of the models.
- **Revopoint MINI Calibrator**  
    Software downloaded from a sketchy [drive](https://drive.google.com/file/d/1SiG12cl_BQr5D1KG6iokxiNpssmt3VMq/view?usp=sharing) shared by a [forum](https://forum.revopoint3d.com/t/how-to-calibrate-mini/22819) moderator of Revopoint.  
    Works very well for calibrating the camera, but it is very difficult to carry out a successfull calibration.
- **Blender** (_v_)  
    [Blender](https://www.blender.org/) is a public project hosted on blender.org, licensed as GNU GPL, owned by its contributors. For that reason Blender is Free and Open Source software, forever.  
    Use blender to import the output file from RevoScan5 to calculate its volume by using python scripts.


## Experimental setting
There are about 170 seedlings (some of them might still die before reaching maturity), ((unknown plant subspecies)), growing in the greenhouse.  
There are two main steps that are required to obtain the information required: scanning of the plant, post-processing of the model to obtain the required features (at the moment only volume).
#### Scanning
1. Open RevoScan5 on PC and enter in a new or existing project folder, connect scanner and turntable to the pc and turn on the lights in the phenobox.
2. Check that the scanning settings on the right of the screen.
3. Place the pot with the plant and the reference object on the rotor plate and set the position for best scanning, regulating accordingly the camera exposure. Set the turntable speed.
4. Start the scanning and after about 800 frames interrupt it, check quickly the quality and then save it. Repeat the process for all the plants.
#### Post-processing
1. Carry out the post-processing of the file from Fusing the pointcloud to clean and obtain the mesh. 
2. Remove the pot from the 3d-model. (working on a better solution)
2. Export the mesh and import it in Blender. 
3. In Blender use the script to open a tab on the layout page. "Separate by loose part" then select the cube and click "Calculate plant volume".
4. Save the result of the plant volume in an excell sheet.

