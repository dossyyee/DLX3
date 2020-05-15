from dlx3 import DLX

'''
class h:
    def __init__(self, num):
        self.i = num

    def outer(self):
        def a():
            self.i += 1
            return b()
        def b():
            return self.i if self.i == 7 else a()

        a()
        return self.i

H = h(2)
'''
names = ["0", "1", "2", "3", "4", "5"]
primary = [0,0,0,0,1,1]
bound = [1,1,1,1,1,1]
cols = [(names[i], primary[i], bound[i], bound[i]) for i in range(6)]
rows = [[(1,0),(3,0),(4,0)], [(0,0),(3,0),(4,0)], [(2,0),(5,0)]]

thing = DLX(cols,rows)

print([item.name for item in thing.itms])
print([(node.up, node.down) for node in thing.nodes[len(names):]])
