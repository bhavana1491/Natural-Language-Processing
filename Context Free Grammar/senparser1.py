from collections import defaultdict
rDict = defaultdict(list)

def parse(tokens):
    best = defaultdict(dict)
    back = defaultdict(dict)
    print tokens
    n = len(tokens)
    for i in range(1,n+1):
        t = tokens[i-1]
        if not rDict.has_key(t):
            t = "<unk>"
        for j in rDict[t]:
            s = str(i-1)+","+str(i)
            if j[0] in best[s].keys():
                if j[1] > best[s][j[0]]:
                    best[s][j[0]] = j[1]
                    back[s][j[0]] = j[0]+"("+s+")"+"->"+t
            else:
                best[s][j[0]] = j[1]
                back[s][j[0]] = j[0] + "(" + s + ")" + "->" + t
    print "best",best
    #print "back",back

    prob = 0
    for l in range(2,n+1):
        for i in range(0,n+1-l):
            j = i+l
            for k in range(i+1,j):
                '''ik = str(i)+","+str(k)
                kj = str(k)+","+str(j)
                ij = str(i)+","+str(j)
                print "ik",ik
                print "kj",kj
                print "ij",ij
                for key in rDict.keys():
                    kl = key.split(" ")
                    if len(kl) == 2:
                        Y = kl[0]
                        Z = kl[1]
                        for v in rDict[key]:
                            X = v[0]
                            #print "Y",Y
                            print "best ik",best[ik]
                            if Y not in best[ik].keys():
                                best[ik][Y] = 0
                            #print "Z",Z
                            if Z not in best[kj].keys():
                                best[kj][Z] = 0'''
                            prob = float(v[1]) * float(best[ik][Y]) * float(best[kj][Z])
                            #print "prob: ",prob
                            if X in best[ij].keys():
                                if prob > float(best[ij][X]):
                                    print "here"
                                    best[ij][X] = prob
                                    back[ij][X] = X+ij+"->"+Y+ik+Z+kj
                                else:
                                    best[ij][X] = prob
                                    back[ij][X] = X + ij + "->" + Y + ik + Z + kj

    print "back",back










if __name__ == "__main__":
    sen = open("dev.strings","r")
    gr = open("rules.txt","r")

    line = sen.read().splitlines()
    rule = gr.read().splitlines()

    for r in rule:
        rl = []
        rl = r.split("->")
        k = rl[0]
        v = [rl[1],rl[2]]
        rDict[k].append(v)
    print rDict

    count = 0
    for k in rDict:
        count += len(rDict[k])
    print count

    '''for w in line:
        tokens = w.split(" ")'''
    parse("Which is last ?".split(" "))

    #print "bestDict", best
    #print "back", back