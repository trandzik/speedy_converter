def onValueChange(par, prev):
	if par.name == "Refreshinterval" and parent().TimerRefreshProgress['timer_active']:
		parent().TimerRefreshProgress.par.start.pulse()
	if par.name == "Outputfolder" or par.name == "Inputfolder":
		parent().CheckFolders(par)
	return

def onPulse(par):
	if par.name == "Run":
		parent().Run()
	elif par.name == "Stop":
		parent().Halt()
	elif par.name == "Loadasset" and ipar.Converter.Totalitems > 0:
		parent().LoadAsset(1)
	elif par.name == "Resetoutputnames":
		parent().RefreshFolderTable()
	return