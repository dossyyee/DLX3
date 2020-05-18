from dlx3 import DLX
from dlx3_open_txt import openDlxTxt

fname = '/Users/HG/Desktop/DancingLinks/DLX3/test2.dlx.txt'

rows, cols = openDlxTxt(fname)


thing = DLX(cols,rows)

i =0
for item in thing.itms:
    print("I:",i,", N:", item.next,", P:",item.prev, ", B:",item.bound,", S:",item.slack, sep='')
    i += 1

print('\n')
i=0
for node in thing.nodes:
    print("N:",i,", U:",node.up,", D:",node.down,", I:",node.itm,", C:",node.colour, sep='')
    i+=1


for solution in thing.dance():
    print(solution)
