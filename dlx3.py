"""
Python implementation of Donald Knuths DLX3 algorithm
By Hayden Goodwin 2020

The following program is an implementation of Donald Knuths DLX3 algorithm.
DLX3 is an extension of DLX1 and DLX 2 where the min an max amount of times
an item is covered can be specified. It also includes the 'colour' of a node
which allows only nodes with like colours to cover the same item.

DLX3 by Knuth:
https://www-cs-faculty.stanford.edu/~knuth/programs/dlx3.w

It is recommended to have a look at the original source as it is very
well documented. Do note that the original is written in cweb and for those
unfamiliar with the language, it is a recommended to read up on it first.

"""
import functools

class Node:
    def __init__(self, up, down, item, colour):
        self.up = up
        self.down = down
        self.itm = item
        self.colour = colour

class Item:
    def __init__(self, name, prev, next, bound, slack, order):
        self.name = name
        self.prev = prev
        self.next = next
        self.bound = bound
        self.slack = slack
        self.order = order

class DLX:

    PRIMARY = 0
    SECONDARY = 1
    INFTY = 100000000
    MAX_LEVEL = 500     # Maximum depth that DLX can search
    MAX_COUNT = 10**10  # Maximum amount of solutions allowed


    def __init__(self, cols, rows):
        """
        Column Formatting:
        cols is a list of item initialising values. Each item is in the form
        of a list and should be formatted:  [name,
                                             order,
                                             lower bound,
                                             upper bound
                                             ]
        name - is a unique object (usually a string)
        order - is a 0 or 1. 0 denotes Primary, 1 denotes Secondary
        lower bound and upper bound are integers which specify the range of
        nodes allowed to cover an item.

        IMPORTANT POINTS
        - All secondary items must be at the end of the cols list
        - Only primary items have bounds
        - Only secondary items have colours
        - Minimum lower bound of 1
        - upper bound can be the same as lowerbound
        - upper bound can never be lower than lower bound


        Row Formatting:
        rows is a list of options/nodes which cover a specific item. Each
        row should be formatted: ["rowname",
                                   [(item, colour), ... ,(item,colour)]
                                   ]

        rowname - a distinct identifiable object (e.g. a string)
        item - an integer corresponding to the index of the item it covers
        colour - any positive integer value (including 0) that isnt 100.

        IMPORTANT POINTS
        - If no colour is being used, it should be specified as None.
        - The 'colour' 100 has been reserved for colourless nodes
        """

        self.updates = 0
        self.cleansings = 0

        self.itms = [Item(None, 0, 0, 0, 0, 0)]
        self.nodes = [Node(0, 0, 0, 0)]
        self.rownames = []
        self.rowid = [None] * (len(cols) + 1)
        self.second = 0 # Location of first secondary item

        # Creating the linked list of items
        cur = 1
        prev = 0
        self.root = 0
        for (name, type, low_bound, up_bound) in cols:
            slack = up_bound - low_bound
            if type == DLX.PRIMARY:   # Only primary items are linked
                self.itms.append(Item(name,
                                      prev,
                                      self.root,
                                      up_bound,
                                      slack, type))
                self.itms[prev].next = cur
                self.itms[self.root].prev = cur
                prev = cur
                self.second = cur + 1
            else:
                self.itms.append(Item(name, cur, cur, up_bound, slack, type))
            self.nodes.append(Node(cur, cur, 0, 0)) # Creating the header nodes
            cur += 1


        # Creating the linked node list
        nnindex = len(self.nodes) # Index where the new nodes will be placed
        i = 0
        j = 0
        prev = 0
        for rowname, row in rows:
            self.rownames.append(rowname)
            if not self.onlySec(row):
                self.rowid.append(j)
                self.nodes.append(Node(prev, nnindex + len(row), -i, 0))
                nnindex += 1
                prev = nnindex
                for (item, colour) in row:
                    item += 1
                    self.rowid.append(j)
                    if self.itms[item].order == DLX.SECONDARY and colour == 0:
                        colour = 100
                    elif colour == None:
                        colour = 0
                    self.nodes[item].itm += 1
                    r = self.nodes[item].up
                    self.nodes.append(Node(r, item, item, colour))
                    self.nodes[item].colour = len(self.nodes) - 1
                    self.nodes[r].down = nnindex
                    self.nodes[item].up = nnindex
                    nnindex += 1
                i+=1
            j+=1
        self.nodes.append(Node(prev, 0,-i,0))

        self.last_itm = len(self.itms)
        self.last_node = len(self.nodes) - 1

        # Other variables used while dancing
        self.partialsolution = []
        self.solutions = []
        self.level = 0
        self.nodect = 0
        self.score = 0
        self.scor = []
        self.first_tweak = []
        self.choice = []
        self.best_s = 0
        self.best_l = 0
        self.best_itm = 0
        self.count = 0
        self.maxl = 0

    def onlySec(self,row):
        for (itm , _) in row:
            if not self.itms[itm + 1].order:
                return False
        return True

    def cover(self, c, deact):
        if deact:
            L = self.itms[c].prev
            r = self.itms[c].next
            self.itms[L].next = r
            self.itms[r].prev = L

        self.updates += 1

        rr = self.nodes[c].down
        while rr >= self.last_itm:

            nn = rr + 1
            while nn != rr:
                if self.nodes[nn].colour >= 0:
                    uu = self.nodes[nn].up
                    dd = self.nodes[nn].down
                    cc = self.nodes[nn].itm

                    if cc <= 0:
                        nn = uu
                        continue

                    self.nodes[uu].down = dd
                    self.nodes[dd].up = uu
                    self.updates += 1
                    self.nodes[cc].itm -= 1
                nn += 1
            rr = self.nodes[rr].down

    def uncover(self, c, react):
        rr = self.nodes[c].down
        while rr >= self.last_itm:
            nn = rr + 1
            while nn != rr:
                if self.nodes[nn].colour >= 0:
                    uu = self.nodes[nn].up
                    dd = self.nodes[nn].down
                    cc = self.nodes[nn].itm

                    if cc <= 0:
                        nn = uu
                        continue

                    self.nodes[uu].down = nn
                    self.nodes[dd].up = nn
                    self.nodes[cc].itm += 1
                nn += 1

            rr = self.nodes[rr].down

        if react:
            L = self.itms[c].prev
            r = self.itms[c].next
            self.itms[L].next = c
            self.itms[r].prev = c

    def purify(self, p):
        cc = self.nodes[p].itm
        x = self.nodes[p].colour
        self.nodes[cc].colour = x
        self.cleansings += 1

        rr = self.nodes[cc].down
        while rr >= self.last_itm:
            if self.nodes[rr].colour != x:
                nn = rr + 1
                while nn != rr:
                    uu = self.nodes[nn].up
                    dd = self.nodes[nn].down
                    cc = self.nodes[nn].itm

                    if cc <= 0:
                        nn = uu
                        continue

                    if self.nodes[nn].colour >= 0:
                        self.nodes[uu].down = dd
                        self.nodes[dd].up = uu
                        self.updates += 1
                        self.nodes[cc].itm -= 1
                    nn += 1
            elif rr != p:
                self.cleansings += 1
                self.nodes[rr].colour = -1

            rr = self.nodes[rr].down

    def unpurify(self, p):
        cc = self.nodes[p].itm
        x = self.nodes[p].colour

        rr= self.nodes[cc].up
        while rr >= self.last_itm:
            if self.nodes[rr].colour < 0:
                self.nodes[rr].colour = x
            elif rr != p:
                nn = rr - 1
                while nn != rr:
                    uu = self.nodes[nn].up
                    dd = self.nodes[nn].down
                    cc = self.nodes[nn].itm

                    if cc <= 0:
                        nn = dd
                        continue

                    if self.nodes[nn].colour >= 0:
                        self.nodes[uu].down = nn
                        self.nodes[dd].up = nn
                        self.nodes[cc].itm += 1
                    nn -= 1
            rr = self.nodes[rr].up

    def tweak(self, n, block):
        if block:
            nn = n + 1
        else:
            nn = n

        while 1:
            if self.nodes[nn].colour >= 0:
                uu = self.nodes[nn].up
                dd = self.nodes[nn].down
                cc = self.nodes[nn].itm

                if cc <= 0:
                    nn = uu
                    continue

                self.nodes[uu].down = dd
                self.nodes[dd].up = uu
                self.updates += 1
                self.nodes[cc].itm -= 1
            if nn == n:
                break
            nn += 1

    def untweak(self, c, x, unblock):
        z = self.nodes[c].down
        self.nodes[c].down = x

        rr = x
        k = 0
        qq = c
        while rr != z:
            self.nodes[rr].up = qq
            k += 1
            if unblock:
                nn = rr + 1
                while nn != rr:
                    if self.nodes[nn].colour >= 0:
                        uu = self.nodes[nn].up
                        dd = self.nodes[nn].down
                        cc = self.nodes[nn].itm

                        if cc <= 0:
                            nn = uu
                            continue

                        self.nodes[uu].down = nn
                        self.nodes[dd].up = nn
                        self.nodes[cc].itm += 1
                    nn += 1
            qq = rr
            rr = self.nodes[rr].down
        self.nodes[rr].up = qq
        self.nodes[c].itm += k

        if not unblock:
            self.uncover(c,0)

    def forward(self):
        self.score = DLX.INFTY

        k = self.itms[self.root].next
        while k != self.root:

            s = self.itms[k].slack
            if s > self.itms[k].bound:
                s = self.itms[k].bound

            t= self.nodes[k].itm + s - self.itms[k].bound + 1
            if t <= self.score:
                if ((t < self.score)
                    or (s < self.best_s)
                    or (s == self.best_s and self.nodes[k].itm > self.best_l)):
                    self.score = t
                    self.best_itm = k
                    self.best_s = s
                    self.best_l = self.nodes[k].itm
            k = self.itms[k].next

        if self.score < DLX.INFTY:
            a =1

        if self.score <= 0:
            return self.backdown

        if self.score == DLX.INFTY:
            # New solution has been found
            self.count += 1
            self.partialsolution = []
            for i in range(self.level):
                pp = self.choice[i]
                cc = pp if pp < self.last_itm else self.nodes[pp].itm

                # Record the partial solution
                if not(pp < self.last_itm
                       or pp >= self.last_node
                       or self.nodes[pp].itm <= 0):
                    self.partialsolution.append(self.rownames[self.rowid[pp]])

            self.solutions.append(self.partialsolution)

            if self.count > DLX.MAX_COUNT:
                # Maximum amount of allowed solutions has been reached
                return None
            return self.backdown

        try:
            self.scor[self.level] = self.score
        except:
            self.scor.append(self.score)

        try:
            self.first_tweak[self.level] = 0
        except:
            self.first_tweak.append(0)

        try:
            self.choice[self.level] = self.nodes[self.best_itm].down
        except:
            self.choice.append(self.nodes[self.best_itm].down)

        self.cur_node = self.nodes[self.best_itm].down

        self.itms[self.best_itm].bound -= 1
        if (self.itms[self.best_itm].bound == 0
            and self.itms[self.best_itm].slack == 0):
            self.cover(self.best_itm,1)
        else:
            self.first_tweak[self.level] = self.cur_node
            if self.itms[self.best_itm].bound == 0:
                self.cover(self.best_itm,1)

        return self.advance

    def advance(self):
        if (self.itms[self.best_itm].bound == 0
            and self.itms[self.best_itm].slack==0):
            if self.cur_node == self.best_itm:
                return self.backup

        elif (self.nodes[self.best_itm].itm
              <= (self.itms[self.best_itm].bound
                  - self.itms[self.best_itm].slack)):
            return self.backup

        elif self.cur_node != self.best_itm:
            self.tweak(self.cur_node, self.itms[self.best_itm].bound)
        elif self.itms[self.best_itm].bound != 0:
            # deactivate best item
            p = self.itms[self.best_itm].prev
            q = self.itms[self.best_itm].next
            self.itms[p].next = q
            self.itms[q].prev = p

        if self.cur_node > self.last_itm:
            pp = self.cur_node + 1
            while pp != self.cur_node:
                cc = self.nodes[pp].itm
                if cc <= 0:
                    pp = self.nodes[pp].up
                else:
                    if cc < self.second:
                        self.itms[cc].bound -= 1
                        if self.itms[cc].bound == 0:
                            self.cover(cc,1)
                    else:
                        if not self.nodes[pp].colour:
                            self.cover(cc,1)
                        elif self.nodes[pp].colour > 0:
                            self.purify(pp)
                    pp += 1

        self.level += 1
        if self.level > self.maxl:
            if self.level >= DLX.MAX_LEVEL:
                # Maximum level has been reached
                return None
            self.maxl = self.level
        return self.forward

    def backup(self):
        if (self.itms[self.best_itm].bound == 0
            and self.itms[self.best_itm].slack == 0):
            self.uncover(self.best_itm,1)
        else:
            self.untweak(
                self.best_itm,
                self.first_tweak[self.level],
                self.itms[self.best_itm].bound
                )
        self.itms[self.best_itm].bound += 1
        return self.backdown

    def backdown(self):

        if self.level == 0:
            # All possible solutions have been found
            return None
        self.level -= 1
        self.cur_node = self.choice[self.level]
        self.best_itm = self.nodes[self.cur_node].itm
        self.score = self.scor[self.level]

        if self.cur_node < self.last_itm:
            self.best_itm = self.cur_node
            p = self.itms[self.best_itm].prev
            q = self.itms[self.best_itm].next
            self.itms[p].next= self.best_itm
            self.itms[q].prev= self.best_itm
            return self.backup

        pp = self.cur_node - 1
        while pp != self.cur_node:
            cc= self.nodes[pp].itm
            if cc <= 0:
                pp = self.nodes[pp].down
            else:
                if cc < self.second:
                    if self.itms[cc].bound == 0:
                        self.uncover(cc,1)
                    self.itms[cc].bound += 1
                else:
                    if not self.nodes[pp].colour:
                        self.uncover(cc,1)
                    elif self.nodes[pp].colour > 0:
                        self.unpurify(pp)
                pp -= 1
        self.choice[self.level] = self.nodes[self.cur_node].down;
        self.cur_node = self.nodes[self.cur_node].down

        return self.advance

    def dance(self):
        """
        Starts the dancing links program and returns a list of solutions.
        The solutions are in the form of a list of 'rownames' so it is best
        to ensure that rownames are unique so solutions are distinguishable.
        """
        def tramampoline(func):
            @functools.wraps(func)
            def g(*args):
                h = func
                while h is not None:
                    h = h(*args)
                return args
            return g()

        tramampoline(self.forward)

        return self.solutions



if __name__ == '__main__':

    items = [[str(i), 0, 1, 2] for i in range(8)]
    options = [['row1', [(0,None),(0,None),(0,None),(0,None)]],
               ['row2', [(1,None),(7,None)]],
               ['row3', [(2,None),(6,None),(1,None),(4,None),(5,None)]],
               ['row4', [(0,None)]],
               ['row5', [(3,None),(4,None),(0,None),(5,None)]],
               ['row6', [(4,None),(2,None),(0,None)]],
               ['row7', [(0,None),(1,None),(7,None),(2,None)]]
               ]

    matrix = DLX(items, options)
    solutions = matrix.dance()
    for solution in solutions:
        print(solution)
