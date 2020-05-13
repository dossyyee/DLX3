
class node:
    def __init__(self, up, down, item, colour):
        self.up = up
        self.down = down
        self.itm = item
        self.colour = colour

class item:
    def __init__(self, name, prev, next, bound, slack):
        self.name = name
        self.prev = prev
        self.next = next
        self.bound = bound
        self.slack = slack


class DLX:

    PRIMARY = 0
    SECONDARY = 1



    def __init__(self, columns, rows=None, rowNames=None):

        self.updates = 0
        self.cleansings = 0

        self.itemcount = len(columns) + 1

        self.nodes
        self.itms

        self.last_itm

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
                    t = self.nodes[cc].len - 1
                    self.nodes[cc].len = t
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

                    if cc <=0
                        nn = uu
                        continue

                    self.nodes[uu].down = nn
                    self.nodes[dd].up = nn
                    t = self.nodes[cc].len + 1
                    self.nodes[cc].len = t
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
                        t = self.nodes[cc].len - 1
                        self.nodes[cc].len = t
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
                        t = self.nodes[cc].len + 1
                        self.nodes[cc].len = t
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
                t = self.nodes[cc].len - 1
                self.nodes[cc].len = t
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
                        t = self.nodes[cc].len + 1
                        self.nodes[cc].len = t
                    n += 1
            qq = rr
            rr = self.nodes[rr].down
        self.nodes[rr].up = qq
        self.nodes[c].len += k

        if not unblock:
            uncover(c,0)

    def solve(self):
        
