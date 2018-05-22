import sys
#sys.path.insert(0,'..')
import pickle
from functools import partial
#from twod.hg_3d import *
from model.Pose3D import *
from model.DepthRegressor3D import *
from model.HourGlassNet3D import *
from model.HourGlass3D import *
from model.Layers3D import *
from inflation.Inflate import *
import torch


model3d = Pose3D()
torch.save(model3d,open('origModel.pth','wb'))


pickle.Unpickler = partial(pickle.Unpickler, encoding="latin1")
pickle.load = partial(pickle.load, encoding="latin1")
model = torch.load('models/hgreg-3d.pth') #, map_location=lambda storage, loc: storage)

inflatePose3D(model3d, model)

torch.save(model3d,open('inflatedModel.pth','wb'))
