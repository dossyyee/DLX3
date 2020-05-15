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
    MAX_LEVEL = 500
    MAX_COUNT = 10**10


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
        self.root = None # the first item in the linked list of items
        for (name, type, low_bound, up_bound) in cols:
            slack = up_bound - low_bound
            if type == DLX.PRIMARY: # only primary items are linked
                if self.root == None: self.root = cur # setting the start item of the linked list
                self.itms.append(Item(name, prev, self.root ,up_bound, slack, type)) # adding an item
                self.itms[prev].next = cur # ammending the previous items next pointer
                self.itms[start].prev = cur # ammending the first items prev pointer
                prev = cur
            else:
                self.itms.append(Item(name, cur, cur, up_bound, slack, type)) # secondary items point to thier own location
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

        self.last_itm = len(cols) - 1
        self.second = self.last_itm

        # variables used within the solve function
        self.level = None
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
        #self.thresh = 0
        #self.delta = 0



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

    def dance(self):

        self.level = 0

        def forward():

            self.score = DLX.INFTY

            k = self.itms[self.root].next
            while k != self.root:

                s = self.itms[k].slack
                if s > self.itms[k].bound:
                    s = self.itms[k].bound

                t= self.nodes[k].itm + s - self.itms[k].bound + 1
                if t <= self.score:
                    if (t < self.score) or (s < self.best_s) or (s == self.best_s and self.node[k].itm > self.best_l):
                        self.score = t
                        self.best_itm = k
                        self.best_s = s
                        self.best_l = self.nodes[k].itm
                        p = 1;
                    elif s == self.best_s and self.nodes[k].itm == self.best_l:
                        p += 1 # this many items achieve the min may not be necessary
                k = self.itms[k].next

            if self.score <= 0:
                backdown()
                return

            if self.score == infty:
                self.count += 1
                for i in range(self.level):
                    pp = self.choice[i]
                    cc = pp if pp < self.last_itm else self.nodes[pp].itm
                    try:
                        if not self.first_tweak[i]:
                            print_option(pp,stdout,nd[cc].down,self.scor[i]) # find what the hell this is doing will need to adapt it
                    except:
                        print_option(pp,stdout,self.first_tweak[i],self.scor[i])
                if self.count > DLX.MAX_COUNT:
                    return

                backdown()
                return

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

            self.cur_node = self.nodes[best_itm].down

            if self.itms[best_itm].bound == 0 and self.itms[best_itm].slack == 0:
                cover(self.best_itm,1)
            else:
                self.first_tweak[self.level] = self.cur_node
                if self.itms[self.best_itm].bound == 0:
                    cover(self.best_itm,1)

            advance()
            return

        def advance():
            if (self.itms[self.best_itm].bound == 0) and (self.itms[self.best_itm].slack==0):
                if self.cur_node == best_itm:
                    backup()
                    return
            elif self.nodes[self.best_itm].itm <= (self.itms[self.best_itm].bound - self.itms[self.best_itm].slack):
                backup()
                return
            elif self.cur_node != self.best_itm:
                tweak(self.cur_node, self.itms[self.best_itm].bound)
            elif self.itms[self.best_itm].bound != 0:
                # deactivate best item
                p = cl[best_itm].prev
                q = cl[best_itm].next
                cl[p].next = q
                cl[q].prev = p

            if self.cur_node > self.last_itm:
                pp = self.cur_node + 1
                while pp != self.cur_node:
                    cc = self.nodes[pp].itm
                    if cc <= 0:
                        pp = self.nodes[pp].up
                    else:
                        if cc < self.last_itm:
                            self.itms[cc].bound -= 1
                            if self.itms[cc].bound == 0:
                                cover(cc,1)
                        else:
                            if not self.nodes[pp].color:
                                cover(cc,1)
                            elif self.nodes[pp].color > 0):
                                purify(pp)
                        pp += 1

            self.level += 1
            if self.level > self.maxl:
                if level >= DLX.MAX_LEVEL:
                    error = true #there are too many levels, create function that will quit the function and maybe return found solutions
                self.maxl = self.level
            forward()
            return

        def backup():
            if(self.itms[self.best_itm].bound == 0) and (self.itms[self.best_itm].slack == 0):
                uncover(self.best_itm,1)
            else:
                untweak(self.best_itm,self.first_tweak[self.level],self.itms[self.best_itm].bound)
            self.itms[self.best_itm].bound += 1
            backdown()
            return

        def backdown():
            if level == 0:
                return
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
                backup()
                return

            pp = self.cur_node - 1
            while pp != self.cur_node:
                cc= self.nodes[pp].itm
                if cc <= 0:
                    pp = self.nodes[pp].down
                else:
                    if cc < self.last_itm:
                        if self.itms[cc].bound == 0:
                            uncover(cc,1)
                        self.itms[cc].bound += 1
                    else:
                        if not self.nodes[pp].color:
                            uncover(cc,1)
                        elif self.nodes[pp].color > 0:
                            unpurify(pp)
                    pp -= 1
            self.cur_node = self.nodes[self.cur_node].down
            self.choice[level] = self.nodes[self.cur_node].down;
            advance()
            return

        forward()
        return
