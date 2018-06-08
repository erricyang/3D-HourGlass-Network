from  __future__ import print_function
import cv2
import ref
import torch
import numpy as np
from progress.bar import Bar
import matplotlib.pyplot as plt


from my import *
from Losses import *
from utils.eval import *
from visualise import *
from utils.utils import *

from model.SoftArgMax import *
SoftArgMaxLayer = SoftArgMax()


def step(split, epoch, opt, dataLoader, model, optimizer = None):
	if split == 'train':
		model.train()
	else:
		model.eval()
	Loss2D, Loss3D, Mpjpe, Acc = AverageMeter(), AverageMeter(), AverageMeter(), AverageMeter()

	nIters = len(dataLoader)
	bar = Bar('==>', max=nIters)

	for i, (input, targetMaps, target2D, target3D, meta) in enumerate(dataLoader):
		if split == 'train':
			input_var = torch.autograd.Variable(input).float().cuda()
			targetMaps = torch.autograd.Variable(targetMaps).float().cuda()
			target2D_var = torch.autograd.Variable(target2D).float().cuda()
			target3D_var = torch.autograd.Variable(target3D).float().cuda()
		else:
			input_var = torch.autograd.Variable(input,volatile=True).float().cuda()
			targetMaps = torch.autograd.Variable(targetMaps,volatile=True).float().cuda()
			target2D_var = torch.autograd.Variable(target2D,volatile=True).float().cuda()
			target3D_var = torch.autograd.Variable(target3D,volatile=True).float().cuda()

		model = model.float().cuda()
		output = model(input_var)
		reg = output[opt.nStack]
		#print(reg.data.type())
		#print([i.data.type() for i in output])
		if opt.DEBUG == 2:
			for j in range(input_var.shape[2]):
				#plt.imshow(input_var.data[0,:,j,:,:].transpose(0,1).transpose(1,2).cpu().numpy())
				test_heatmaps(targetMaps[0,:,j,:,:].cpu(),input_var[0,:,j,:,:].cpu(),6)
				a = np.zeros((16,3))
				b = np.zeros((16,3))
				a[:,:2] = getPreds(targetMaps[:1,:,j,:,:].cpu().numpy())
				b[:,:2] = getPreds(output[opt.nStack - 1][:1,:,j,:,:].data.cpu().numpy())
				a[:,2] = target3D[0,:,j,0]
				b[:,2] = reg[0,:,j,0].data.cpu().numpy()
				print(a)
				visualise3d(b,a,"3D",i,j,input_var.data[0,:,j,:,:].transpose(0,1).transpose(1,2).cpu())


		if ((meta == 0).all()):
			loss = torch.autograd.Variable(torch.Tensor([0])).cuda()
			oldloss = 0
		else:
			loss = opt.regWeight * JointsDepthSquaredError(reg,target3D_var)
			oldloss = float((loss).detach())
			Loss3D.update(oldloss, input.size(0))
		#print(loss.data.type())
		for k in range(opt.nStack):
			loss = loss + Joints2DHeatMapsSquaredError(output[k], targetMaps)
		Loss2D.update(float(loss.detach()) - oldloss, input.size(0))
		#print(loss.data.type())
		tempAcc = Accuracy((output[opt.nStack - 1].data).transpose(1,2).contiguous().view(-1,ref.nJoints,ref.outputRes,ref.outputRes).contiguous().cpu().numpy(), (targetMaps.data).transpose(1,2).contiguous().view(-1,ref.nJoints,ref.outputRes,ref.outputRes).contiguous().cpu().numpy())
		Acc.update(tempAcc)


		mplist = myMPJPE((output[opt.nStack - 1].data).cpu().numpy(), (reg.data).cpu().numpy(), meta)

		for l in mplist:
			mpjpe, num3D = l
			if num3D > 0:
				Mpjpe.update(mpjpe, num3D)
		tempMPJPE = (sum([(x*y if y>0 else 0) for x,y in mplist]))/(1.0*sum([(y if y>0 else 0) for x,y in mplist])) if (1.0*sum([(y if y>0 else 0) for x,y in mplist])) > 0 else 0

		if opt.DEBUG == 3 and (float(tempMPJPE) > 80):
			for j in range(input_var.shape[2]):
				a = np.zeros((16,3))
				b = np.zeros((16,3))
				a[:,:2] = getPreds(targetMaps[:,:,j,:,:].cpu().numpy())
				b[:,:2] = getPreds(output[opt.nStack - 1][:,:,j,:,:].data.cpu().numpy())
				b[:,2] = reg[0,:,j,0]
				a[:,2] = target3D_var[0,:,j,0]
				visualise3d(b,a,'val-errors-great',i,j,input_var.data[0,:,j,:,:].transpose(0,1).transpose(1,2).cpu().numpy())



		if split == 'train':
			loss = loss/opt.trainBatch
			loss.backward()
			if ((i+1)%(opt.trainBatch/opt.dataloaderSize) == 0):
				optimizer.step()
				optimizer.zero_grad()


		Bar.suffix = '{split} Epoch: [{0}][{1}/{2}]| Total: {total:} | ETA: {eta:} | Loss2D {loss.avg:.6f} | Loss3D {loss3d.avg:.6f} | PCKh {PCKh.avg:.6f} | Mpjpe {Mpjpe.avg:.6f} ({Mpjpe.val:.6f})'.format(epoch, i, nIters, total=bar.elapsed_td, eta=bar.eta_td, loss=Loss2D, split = split, loss3d = Loss3D, Mpjpe=Mpjpe, PCKh = Acc)
		bar.next()
	bar.finish()
	if (opt.completeTest):
		print("Num Frames : %d"%(input_var.shape[0]*input_var.shape[3]))
	return Loss2D.avg, Loss3D.avg, Mpjpe.avg, Acc.avg


def train(epoch, opt, train_loader, model, optimizer):
	return step('train', epoch, opt, train_loader, model, optimizer)

def val(epoch, opt, val_loader, model):
	#with torch.no_grad():
	return step('val', epoch, opt, val_loader, model)
