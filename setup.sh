#!/bin/bash
#--------------------------------------------------------------------------
# This is a setup file that is requiered by Dockerfile in order to install
# pre-compiled weights for Mask-RCNN model.
# Created by SkymeFactor, 2020.12.09.
#--------------------------------------------------------------------------

# Set the file_id for google.drive file
fileid=1Y2YSaUfsKISgbVzDlibVWYbj4bTfUN_1
# Set the filename of where to download it into
filename=MaskRCNN/weights.zip

# Download cookie file in order to get authorization token
wget --save-cookies cookies.txt 'https://docs.google.com/uc?export=download&id='$fileid -O- \
     | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1/p' > confirm.txt
# Download the actual file, containing weights
wget --load-cookies cookies.txt -O $filename \
     'https://docs.google.com/uc?export=download&id='$fileid'&confirm='$(<confirm.txt)

# Remove all temporary files
rm -f confirm.txt cookies.txt
# Move to MaskRCNN folder
cd MaskRCNN
# Extract the weights
unzip weights.zip