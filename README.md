# Phenobox Project
Phenobox project at Parisod's research group University of Fribourg (CH)

## import packages on Blender
command on terminal:
```bash
<path/to/python/bin/in/blender> ./python -m pip install <package_name> --target="path/to/blender/site-packages"
```
if it doesn't work, run the terminal as the admin


## Introduction
This projects aims at creating  3D-models of plants of Biscutella laevigata to be able to extract features (e.g., volume).  

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

#### Softwares:
- **RevoScan5** (_v_)  
    Software used to control the scanning, strictly related to the scanner and turntable.  
    It is also used for the first post-processing steps of the models.
- **Revopoint MINI Calibrator**  
    Software downloaded from a sketchy [drive](https://drive.google.com/file/d/1SiG12cl_BQr5D1KG6iokxiNpssmt3VMq/view?usp=sharing) shared by a [forum](https://forum.revopoint3d.com/t/how-to-calibrate-mini/22819) moderator of Revopoint.  
    Works very well for calibrating the camera, but it is very difficult to carry out a successfull calibration.
- **Blender** (_v_)  
    