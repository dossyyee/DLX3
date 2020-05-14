"""
    attempting to simplify the creation of the header items
"""

#self.itms = [item(None,None,None,None,None) for i in range(self.itemcount + 1)]
prev = self.itemcount
cur = 0
for (name, type, low_bound, up_bound) in cols:
    slack = up_bound - low_bound
    if type == DLX.PRIMARY:
        self.itms.append(item(name, prev, None ,up_bound, slack)) # only primary items are linked
        prev = cur
    else:
        self.itms.append(item(name, cur, cur, up_bound, slack)) # secondary items point to thier own location
    self.nodes.append(cur, cur, None, 0) # creating the header nodes
    cur += 1
self.itms.append(item(None, prev, None, None, None)) # creating header item unsure what the bound and slack should be
self.nodes.append(node(cur, cur, None, 0)) # adding a dummy node for the item header
