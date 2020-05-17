from dlx3 import DLX

names = ["0", "1", "2", "3", "4", "5"]
primary = [0,0,0,0,1,1]
low_bound = [1,1,1,1,1,1]
up_bound = [1,1,1,1,1,1]
cols = [(names[i], primary[i], low_bound[i], up_bound[i]) for i in range(6)]
rows = [([(1,0),(3,0)], "option 1"), ([(0,0),(3,0),(4,0)], "option 2"), ([(1,0),(2,0),(5,0)], "option 3"), ([(0,0)], "option 4"), ([(1,0)], "option 5"), ([(2,0)], "option 6"), ([(3,0)], "option 7"), ([(4,0)], "option 8"), ([(5,0)], "option 9")]

thing = DLX(cols,rows)
"""
i =0
for item in thing.itms:
    print("I:",i,", N:", item.next,", P:",item.prev, ", B:",item.bound,", S:",item.slack, sep='')
    i += 1

print('\n')
i=0
for node in thing.nodes:
    print("N:",i,", U:",node.up,", D:",node.down,", I:",node.itm,", C:",node.colour, sep='')
    i+=1
"""

for solution in thing.dance():
    print(solution)
