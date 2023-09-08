# Installation

## Linux

```shell
sudo apt-get install python3-pyqt5.qtopengl freeglut3-dev
pip3 install ecofaber
```

## Windows

```shell
pip3 install ecofaber
```





# Example

Example1.py

```python
import numpy as np

import ecofaber
import ecofaber.basemodel as bm


@bm.register
class Model(bm.ModelElement):
    def __init__(self, data=None):
        super().__init__(data)

        self.angle = 0

    def update(self):
        self.angle += 0.1

    def getView(self):
        view = []

        view.append({
            "name": "b_cube_1",
            "pos": [10*np.cos(self.angle),10*np.sin(self.angle),0], 
            "color": [200,100,0],
        })

        view.append({
            "name": "b_ring_3",
            "pos": [0,0,0], 
            "color": [200,100,0],
        })

        return view

    def getObj(self, pos):
        return None


ecofaber.launch(Model)
```



Execute the following code 

```shell
git clone git@github.com:flokapi/ecofaber.git
cd ecofaber/example
python3 example1.py
```



This will open the application with the model. You can now start the simulation, control the speed, the view, ...

![example_screenshot](img/example_screenshot.png)



Use the left click to move, the right click to rotate and scroll to zoom in/out.
