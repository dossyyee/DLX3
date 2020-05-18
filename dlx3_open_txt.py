def openDlxTxt(fname):
    unsolved = open(fname, "r")

    # names, primary, low bound, up bound
    cols = []
    names = []
    # [nodes], name
    rows = []

    order = 0
    i=0
    for line in unsolved:
        if i == 0:
            for item in line.split():
                if item == "|":
                    order = 1
                    continue

                if order:
                    if not ":" in item:
                        cols.append([item, order, 0, 0])
                        names.append(item)
                    else:
                        cols.append([item[4:], order, int(item[0]), int(item[2])])
                        names.append(item[4:])
                else:
                    cols.append([item[4:], order, int(item[0]), int(item[2])])
                    names.append(item[4:])
            i+=1
            continue
        row = []
        for node in line.split():
            if node[0] == "|":
                break
            if not ":" in node:
                row.append((names.index(node), None))
            else:
                colon = node.index(":")
                row.append((names.index(node[:colon]), int(node[colon+1:])))

        rows.append([row, "row " + str(i)])
        i += 1

    return rows, cols
