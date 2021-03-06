import argparse
import os
import ref

class opts():
	def __init__(self):
		self.parser = argparse.ArgumentParser()

	def init(self):
		self.parser.add_argument('-expID', default = 'default', help = 'Experiment ID')
		self.parser.add_argument('-test', action = 'store_true', help = 'test')
		self.parser.add_argument('-DEBUG', type = int, default = 0, help = 'DEBUG level')
		self.parser.add_argument('-demo', default = '', help = 'path/to/demo/image')
		self.parser.add_argument('-mode', default = 'pose', help = 'either pose or action')

		self.parser.add_argument('-loadModel', default = 'none', help = 'Provide full path to a previously trained model')
		self.parser.add_argument('-Model2D', default = 'models/hgreg-3d.pth', help = 'Provide full path to a model to inflate')

		self.parser.add_argument('-nChannels', type = int, default = 128, help = '# features in the hourglass')
		self.parser.add_argument('-nStack', type = int, default = 2, help = '# hourglasses to stack')
		self.parser.add_argument('-nModules', type = int, default = 2, help = '# residual modules at each hourglass')
		self.parser.add_argument('-numReductions', type = int, default = 4, help = '# recursions in hourglass')
		self.parser.add_argument('-nRegModules', type = int, default = 2, help = '# depth regression modules')
		self.parser.add_argument('-nRegFrames', type = int, default = 8, help = '# number of frames temporally for regressor module')

		self.parser.add_argument('-nEpochs', type = int, default = 120, help = '#training epochs')
		self.parser.add_argument('-valIntervals', type = int, default = 2, help = '#valid intervel')
		self.parser.add_argument('-trainBatch', type = int, default = 2, help = '#Mini-batch size')
		self.parser.add_argument('-dataloaderSize', type = int, default = 2, help = '#Mini-batch size')

		self.parser.add_argument('-nFramesLoad', type = int, default = 16, help = '#Frames per video to consider')
		self.parser.add_argument('-loadConsecutive', default=1, type = int, help = '#Load frames consecutively or sampling')

		self.parser.add_argument('-LRhg', type = float, default = 2.5e-5, help = 'Learning Rate')
		self.parser.add_argument('-LRdr', type = float, default = 2.5e-5, help = 'Learning Rate')
		self.parser.add_argument('-patience', type = int, default = 13, help = 'patience for LR scheduler')
		self.parser.add_argument('-threshold', type = float, default = 0.0005, help = 'threshold for LR scheduler')
		self.parser.add_argument('-dropMag', type = float, default = 0.15, help = 'factor for LR scheduler')
		self.parser.add_argument('-scheduler', type = int, default = 1, help = 'drop LR')

		self.parser.add_argument('-ratioHM', type = float, default = 1, help = 'H36M to MPII data ratio')
		self.parser.add_argument('-ratioHP', type = float, default = 1, help = 'H36M to Posetrack data ratio')
		self.parser.add_argument('-regWeight', type = float, default = 0.2, help = 'depth regression loss weight')
		self.parser.add_argument('-varWeight', type = float, default = 0, help = 'variance loss weight')


	def parse(self):
		self.init()
		self.opt = self.parser.parse_args()
		self.opt.saveDir = os.path.join(ref.expDir, self.opt.expID)
		if self.opt.DEBUG > 0:
			ref.nThreads = 1

		args = dict((name, getattr(self.opt, name)) for name in dir(self.opt) if not name.startswith('_'))
		refs = dict((name, getattr(ref, name)) for name in dir(ref) if not name.startswith('_'))

		if not os.path.exists(self.opt.saveDir):
			os.makedirs(self.opt.saveDir)

		file_name = os.path.join(self.opt.saveDir, 'opt.txt')

		with open(file_name, 'wt') as opt_file:
			opt_file.write('==> Args:\n')
			for k, v in sorted(args.items()):
				opt_file.write('  %s: %s\n' % (str(k), str(v)))
			opt_file.write('==> Args:\n')
			for k, v in sorted(refs.items()):
				opt_file.write('  %s: %s\n' % (str(k), str(v)))
		return self.opt
