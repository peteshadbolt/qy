import itertools as it

def generate_code(d):
    ''' generate code for dxd permanent'''
    s=''
    indeces = range(d)
    permutations = list(it.permutations(indeces, d))
    for index, permutation in enumerate(permutations):
        s+=' + ' if index>0 else '   '
        for term_index, term in enumerate(zip(permutation, indeces)):
            s+='a[%d,%d]' % term
            if term_index < d-1: s+='*'

        if index<len(permutations)-1: s+=' \\\n'
    return s+'\n\n\n'

f=open('generated_permanent_code.txt', 'w')
f.write(generate_code(2))
f.write(generate_code(3))
f.write(generate_code(4))
f.write(generate_code(5))
f.close
