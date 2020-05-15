''' Note that in the original dlx3.c file, the following macro is made
#define itm itm
#define aux colour
When reading the following code and comparing to the c file you can assume all
instances of len will be itm and aux will be colour

Most instances of the mems macros have also been erased from the original file

Each item of the input matrix is represented by an item struct,
and each option is represented as a collection of node structs. There's one
node for each nonzero entry in the matrix.
'''
class Node:
    def __init__(self, up, down, item, colour):
        self.up = up
        self.down = down
        self.itm = item
        self.colour = colour

class Item:
    def __init__(self, name, prev, next, bound, slack):
        self.name = name
        self.prev = prev
        self.next = next
        self.bound = bound
        self.slack = slack


class DLX:

    PRIMARY = 0
    SECONDARY = 1


    def __init__(self, cols, rows):
        # columns is a list of item info where each item is in the form of a tuple
        # each item info should be formatted: (name, primary, upper bound, lower bound)

        # columns is a list of options where each option is a list of items covered and corresponding colour
        # each should be formatted: [(item, colour), ... ,(item,colour)]

        self.updates = 0
        self.cleansings = 0

        self.nodes = []
        self.itms = []
        self.rownames = []          # unused so far, not sure if necessary
        self.rowIdentifiers = []    # ditto ^^^

        # creating the linked list of items
        cur = 0
        prev = cur
        start = None
        for (name, type, low_bound, up_bound) in cols:
            slack = up_bound - low_bound
            if type == DLX.PRIMARY: # only primary items are linked
                if start == None: start = cur # setting the start item of the linked list
                self.itms.append(Item(name, prev, start ,up_bound, slack)) # adding an item
                self.itms[prev].next = cur # ammending the previous items next pointer
                self.itms[start].prev = cur # ammending the first items prev pointer
                prev = cur
            else:
                self.itms.append(Item(name, cur, cur, up_bound, slack)) # secondary items point to thier own location
            self.nodes.append(Node(cur, cur, 0, 0)) # creating the header nodes
            cur += 1
        
        # creating the linked node list
        nnindex = len(self.nodes) # Index where the new nodes will be placed
        for row in rows:
            for (item, colour) in row:

                t = self.nodes[item].itm + 1
                self.nodes[item].itm = t # increasing the length of the linked list that is stored to reflect the newly added node
                r = self.nodes[item].up # the bottom node in the list
                self.nodes.append(Node(r, item, item, colour)) # creating new node
                self.nodes[item].colour = nnindex # storing the new last node in the linked list
                self.nodes[r].down = nnindex # ammending the previous nodes' down pointer
                self.nodes[item].up = nnindex # ammending the header nodes' up pointer
                nnindex += 1 # increase the new node index

        self.partialsolution = [] # Solution options will be appended here  Note!!! will  need to implement a method of etraction the useful solutions


    def cover(self, c, deact):
        if deact:
            l = self.itms[c].prev
            r = self.itms[c].next
            self.itms[l].next = r
            self.itms[r].prev = l

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
                    t = self.nodes[cc].itm - 1
                    self.nodes[cc].itm = t
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
                    t = self.nodes[cc].itm + 1
                    self.nodes[cc].itm = t
                nn += 1

            if react:
                l = self.itms[c].prev
                r = self.itms[c].next
                self.itms[l].next = c
                self.itms[r].prev = c

            rr = self.nodes[rr].down

    def purify(self, p):
        cc = self.nodes[p].itm
        x = self.nodes[p].color
        self.nodes[cc].color = x
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
                        t = self.nodes[cc].itm - 1
                        self.nodes[cc].itm = t
                    nn += 1
            elif rr != p:
                self.cleansings += 1
                self.nodes[rr].colour = -1

            rr = self.nodes[rr].down

    def unpurify(self, p):
        cc = self.nodes[p].itm
        x = self.nodes[p].color

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
                        t = self.nodes[cc].itm + 1
                        self.nodes[cc].itm = t
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
                t = self.nodes[cc].itm - 1
                self.nodes[cc].itm = t
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
                    if self.nodes[nn].colours >= 0:
                        uu = self.nodes[nn].up
                        dd = self.nodes[nn].down
                        cc = self.nodes[nn].itm

                        if cc <= 0:
                            nn = uu
                            continue

                        self.nodes[uu].down = nn
                        self.nodes[dd].up = nn
                        t = self.nodes[cc].itm + 1
                        self.nodes[cc].itm = t
                    n += 1
            qq = rr
            rr = self.nodes[rr].down
        self.nodes[rr].up = qq
        self.nodes[c].itm += k

        if not unblock:
            uncover(c,0)
'''
    def solve(self):
        level = 0

        forward()

        def forward():
            yadda
            yadda
            yadda

            if score <= 0: backdown()

            if score == infty:
                visit solution
                backdown()
            cleared the rest

            advance()

        def advance():
            if current node offlimits:
                maybe tweak
                backup()

            increase level
            forward()

        def backup():
            restore original

        def backdown():
            if level == 0:
                done()

            if curnode < lastitm:
                backup()

            uncover stuff
            other shinanigans
            advance()

        def done():
            return
            the soltuions
            stoof
'''
