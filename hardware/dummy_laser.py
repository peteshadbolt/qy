import time

class dummy_laser:
	def __init__(self):
		self.last_command=''
				
	def close(self):
		pass
		
	def write(self, x):
		self.last_command=x.lower().strip()
			
	def readline(self, n=0):
		if self.last_command=='?s': return self.last_command+('\n%d' % -1)
		return self.last_command