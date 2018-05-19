import torch
import torch.nn as nn

lossfunc = nn.MSELoss().cuda()

#@torch.set_default_tensor_type('torch.cuda.FloatTensor')

def Joints2DHeatMapsSquaredError(input, target):
	global lossfunc
	"""
	Takes input as (N,C,D,H,W) and similar target (Here C is number of channels equivalent to number of joints
	and H,W are equal to the input image dimensions (i.e. 256 each))
	"""
	#assert len(input.shape) == 5, "Joints2DHeatMapsSquaredError"
	N = input.size()[0]
	return lossfunc(input.view(N,-1), target.view(N,-1))

def Joints2DArgMaxSquaredError(input, target):
	global lossfunc
	"""
	Takes input as (N,C,D,2) and similar target (Here C is number of channels equivalent to number of joints)
	"""
	#assert len(input.shape) == 4 & input.shape[3] == 2, "Joints2DArgMaxSquaredError"
	N = input.size()[0]
	return lossfunc(input.view(N,-1), target.view(N,-1))

def JointsDepthSquaredError(input, target):
	global lossfunc
	"""
	Takes input as (N,C,D,1) and similar target (Here C is number of channels equivalent to number of joints)
	"""	
	#assert len(input.shape) == 4 & input.size()[3] == 1, "JointsDepthSquaredError"
	N = input.size()[0]
	input = input.cuda()
	return lossfunc(input.view(N,-1), target.view(N,-1))
