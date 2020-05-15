from dlx3 import DLX

names = ["0", "1", "2", "3", "4", "5"]
primary = [0,0,0,0,1,1]
bound = [1,1,1,1,1,1]
cols = [(names[i], primary[i], bound[i], bound[i]) for i in range(6)]
rows = [[(1,0),(3,0),(4,0)], [(0,0),(3,0),(4,0)], [(2,0),(5,0)]]

thing = DLX(cols,rows)

print("items")
print("names: ", end='')
print([item.name for item in thing.itms])
print("prev:  ", end='')
print([item.prev for item in thing.itms])
print("next:  ", end='')
print([item.next for item in thing.itms])

print()
print("nodes")
print("item: ", end='')
print([node.itm for node in thing.nodes])
print("up:   ", end='')
print([node.up for node in thing.nodes])
print("down: ", end='')
print([node.down for node in thing.nodes])
