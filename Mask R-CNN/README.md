## Ease-Of-Use
First of all, let's download the checkpoints of pre-trained mask-rcnn and unpack them into this folder. You must make sure that the folder ./mask-rcnn/1555659850/ is available from here by exact same path.

Tensorflow checkpoints are publicly available by link:

https://drive.google.com/file/d/17lry_2h-Pr3PsasJHtmGz922mjt3CAWc/view?usp=sharing

Next, let's execute the following command in order to install all necessarry python libraries:

`pip3 install -r requirements.txt`

And lastly, run the program with test image 'my_test.jpg'

`python3 main.py my_test.jpg`

As a result I expect you will have a file './result/my_test.jpg' containing the segmentation.

For additional help you can type

`pyhton3 main.py --help`