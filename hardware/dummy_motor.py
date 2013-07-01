import time

class dummy_motor:
	''' emulates an SMC100 motor controller '''
	def __init__(self):
		self.res=.001
		self.last_command=''
		self.targets=[0,0,0]
		self.positions=[0,0,0]
		
	def close(self):
		pass
		
	def write(self, x):
		self.last_command=x.lower().strip()
		
		if self.last_command[2:4]=='pa': 
			index=int(self.last_command[0:2])
			position=float(self.last_command[4:])
			self.targets[index]=position
			
	def readline(self, n=1):
		#time.sleep(0.01)
		index=int(self.last_command[0:2])
		
		for i in range(len(self.targets)):
			dir=0
			if self.targets[i]>self.positions[i]+self.res/2: dir=1
			if self.targets[i]<self.positions[i]-self.res/2: dir=-1
			self.positions[i]+=(self.targets[i]-self.positions[i])*0.1
			
			#self.positions[i]+=self.res*dir
		
		if self.last_command.endswith('tp'): return '%02dTP%.5f' % (index, self.positions[index])
		
		if self.last_command.endswith('ts'): 
			state_code='33' if abs(self.positions[index]-self.targets[index])<self.res else '28'
			return '%02dTS0000%s' % (index, state_code)
		