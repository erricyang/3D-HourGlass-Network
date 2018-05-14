import os
import sys
import numpy as np
import cv2
import torch
from HourGlassNet3D import *
from Loss import *
from Softargmax import *

argumentList = sys.argv[1:]

assert len(argumentList) > 0, "Give an Image Folder with -imageFolder Flag"
assert argumentList[0] == "-imageFolder", "Give an Image Folder with -imageFolder Flag"


argumentList[1] += "/"
all_frames = os.listdir(argumentList[1])


#hg = HourglassNet3D(256,1,2,4,16)
hg = torch.load('inflatedModel.pth')
#hg = hg.contiguous()
print("Model Loaded")
#hg = hg.cuda()
#print("Model in cuda\n")       



n_frames = len(all_frames)
frames_seq = np.zeros((1, 3, n_frames, 256, 256))
for idx, frame in enumerate(all_frames):
	frames_seq[0,:,idx,:,:] = cv2.imread(argumentList[1] + frame).transpose(2,0,1)

frames_seq = torch.from_numpy(frames_seq).float() /256
print("Frames Develope")
frames_var = torch.autograd.Variable(frames_seq).float().cuda()
print("Frames in cuda")

"""
#hg = HourglassNet3D(256,1,2,4,16)
hg = torch.load('inflatedModel.pth')
hg = hg.contigous()
print("Model Loaded")
#hg = hg.cuda()
#print("Model in cuda\n")
"""


heatmaps = hg(frames_var)

heatmapsLen = len(heatmaps)

loss = 0

SoftArgMaxLayer = SoftArgMax()

for i in range(heatmapsLen):
	temp = SoftArgMaxLayer(heatmaps[i])
	#temp = SoftArgMax(heatmaps[i])
	#temp1 += (torch.randn(temp.size()) + 1)*256
	#loss  += JointSquaredError(temp, temp1)
	print(temp)

loss.backward()