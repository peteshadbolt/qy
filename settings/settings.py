import os


print 'loading settings...',
filename=os.path.dirname(__file__)
filename=os.path.join(filename, 'qython.txt')
f=open(filename, 'r')
lines=f.readlines()
f.close()
main_dict={}
keys=[]
for line in lines:
	p=line.find(':')
	if p!=-1:		
		key, value = line[:p].strip(), line[p+1:].strip()
		
		try:
			value=float(value)
			if int(value)==float(value): value=int(value)
		except ValueError:
			pass
		
		
		keys.append(key)
		main_dict[key]=value
		
print 'done'

def lookup(search):
	search=search.lower().strip()
	if search in main_dict: return main_dict[search]
	print '%s not found in settings file (%s)!' % (search, filename)
	return None
			
def write(search, value):
	search=search.lower().strip()
	main_dict[search]=value
	
def save():
	return
	f=open(filename, 'w')
	for key in keys:
		s='%s: %s\n' % (key, main_dict[key])
		f.write(s)
	f.close()
		
	