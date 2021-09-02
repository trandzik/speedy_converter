class ConverterExt:
	"""
	ConverterExt description
	"""
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp
		self.VideoIn = op("moviefilein1")
		self.VideoOut = op("moviefileout1")
		self.folderData = op("null_folder")
		self.folderTable = op("table_folder")
		self.TimerRefreshProgress = op('timer_refresh_progress')
		self.Lister = op('lister')
		self.Lister.par.Filtercols = '0'
		self.SelectedRows = ''
		self.RefreshFolderTable()

	def Run(self):
		self.FreezeUI(True)
		project.realTime = False
		# start conversion
		ipar.Converter.Activeitem = 0
		self.AdvanceTask()

	def StartWarmUp(self):
		# moviefileout needs couple of frames for warmup - else it reports frame drops
		# and file will contain duplicated starting frame
		if ipar.Converter.Activeitem == 1:
			# indicate warmup at start in order to block displaying progress bar and video, later it isn't needed
			ipar.Converter.Warmup = 1
		self.VideoIn.cook(force=True)
		op('info_in').cook(force=True)
		self.VideoOut.cook(force=True)
		self.VideoIn.par.play = 1
		self.VideoOut.par.record = 1
	
	def EndWarmUp(self):
		self.VideoIn.par.play = 0
		self.VideoOut.par.record = 0
		self.VideoOut.cook(force=True) # close video file
		ipar.Converter.Warmup = 0
	
	def Halt(self):
		ipar.Converter.Activeitem = -1
		self.StopRender()

	def FreezeUI(self, state):
		if state:
			self.SelectedRows = self.Lister.par.Selectedrows.eval()
			self.Lister.par.callbacks = '' # disables mouse interaction
			self.Lister.par.enable = False # disables keyboard interaction
			op('folder_input').par.refresh = False
			op('folder_output').par.refresh = False
		else:
			self.Lister.par.callbacks = './internalCallbacks'
			self.Lister.par.enable = True
			op('folder_input').par.refresh = True
			op('folder_output').par.refresh = True
			run('parent().Lister.par.Selectedrows = parent().SelectedRows', fromOP=me, delayFrames=2)
	
	def RefreshProgress(self):
		op('cache1').par.activepulse.pulse()
		op('constant_index_fraction').par.value0 = op('select_index_fraction')[0]

	def AdvanceTask(self):
		activeItem = ipar.Converter.Activeitem
		if activeItem.val != -1:
			activeItem.val += 1
			if activeItem.val < self.folderData.numRows:
				debug(f'Processing item {activeItem.val}')
				self.LoadAsset(activeItem.val)
				self.StartWarmUp()
				run("parent().StartRender()", delayFrames=10)
			else:
				# done!
				activeItem.val = -1
				self.FreezeUI(False)
				project.realTime = True
		else:
			debug('No active item, doing nothing.')
			self.FreezeUI(False)
			project.realTime = True

	def LoadAsset(self, rowIndex):
		inputName = self.folderData[rowIndex, 'name'].val
		outputName = self.folderData[rowIndex, 'outputname'].val
		self.VideoIn.par.file = f"{parent().par.Inputfolder.eval()}/{inputName}"
		self.VideoOut.par.file = f"{parent().par.Outputfolder.eval()}/{outputName}"
		print(f'Loading input video {self.VideoIn.par.file}')
		print(f'Loading output video {self.VideoOut.par.file}')

	def StartRender(self):
		project.realTime = False
		self.EndWarmUp()
		self.VideoIn.par.cuepoint = 0
		self.VideoIn.par.cuepulse.pulse()
		self.VideoOut.par.fps = parent().VideoIn.rate
		
		self.VideoIn.cook(force=True)
		op('info_in').cook(force=True)
		self.VideoOut.cook(force=True)

		self.TimerRefreshProgress.par.start.pulse()
		self.RefreshProgress()
		self.VideoIn.par.play = 1
		self.VideoOut.par.record = 1

	def StopRender(self):
		self.TimerRefreshProgress.par.gotodone.pulse()
		self.VideoIn.par.play = 0
		self.VideoOut.par.record = 0
		self.VideoOut.cook(force=True) # close video file
		self.AdvanceTask()

	def RefreshFolderTable(self):
		self.folderTable.copy(op('null_folder_to_copy'))
		self.CheckOverwrites()

	def CheckOverwrites(self):
		for r in range(1, self.folderTable.numRows):
			name = self.folderTable[r, 'outputname'].val
			exists = False
			for i in range(1, op('folder_output').numRows):
				if name == op('folder_output')[i, 'name'].val:
					exists = True
					break
			if exists:
				self.folderTable[r, 'state'] = 'Warning'
			else:
				self.folderTable[r, 'state'] = ''

	def CheckFolders(self, lastEdited):
		inputFolder = tdu.expandPath(parent().par.Inputfolder)
		outputFolder = tdu.expandPath(parent().par.Outputfolder)
		if inputFolder == outputFolder:
			lastEdited.val = ''
			op('popDialog').par.Open.pulse()
