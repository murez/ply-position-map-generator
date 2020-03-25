# ply-position-map-generator
a script written in python to generate ply and position map from RGBD
To run it, `numpy`, `pillows`, `scipy.io`must be installed in your running environment.
## How to run it
Firstly, replace the `fx`, `fy`, `cx`, `cy`'s data by your camera setting.
Then run the code in the terminal.
```
python3 generator.py rgb_or_rgba.png depth.png output.ply positionmap.mat
```
