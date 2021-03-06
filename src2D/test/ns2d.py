import ref
import cv2
import torch
import numpy as np

from utils.img import Crop, DrawGaussian, Transform3D

c = np.ones(2) * ref.h36mImgSize / 2
s = ref.h36mImgSize * 1.0

img = cv2.imread('../data/h36m/s_01_act_02_subact_01_ca_03/s_01_act_02_subact_01_ca_03_000111.jpg')

img = Crop(img, c, s, 0, ref.inputRes) / 256.
img.shape


img = torch.from_numpy(img).unsqueeze(0).cuda()



out3d = img[:,:,None,:,:].expand(1,3,32,256,256).cuda()
model3d = torch.load('inflatedModel.pth').cuda()


out2d = img.expand(32,3,256,256).cuda()
import pickle
from functools import partial
pickle.Unpickler = partial(pickle.Unpickler, encoding="latin1")
pickle.load = partial(pickle.load, encoding="latin1")
model = torch.load('models/hgreg-3d.pth').cuda()

out2d = model.conv1_(out2d)
out2d = model.bn1(out2d)
out2d = model.relu(out2d)
out2d = model.r1(out2d)
out2d = model.maxpool(out2d)
out2d = model.r4(out2d)
out2d = model.r5(out2d)

out2d = model.hourglass[0](out2d)
out = out2d




out1 = model.Residual[0](out)
out1 = model.Residual[1](out1)
print(out1[0,:,:,:])
print("Residual model3d")

out1 = model.lin_[0](out1)
print(out1[0,:,:,:])
print("lin1 model3d")

out2 = model.tmpOut[0](out1)
print(out2[0,:,:,:])
print("lin1 model3d")

out1 = model.ll_[0](out1)
print(out1[0,:,:,:])
print("lin2 model3d")

out = out + out1 + model.tmpOut_[0](out2)
print(out[0,:,:,:])
print("lin1 model3d")
