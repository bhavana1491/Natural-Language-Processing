import sys
from fst import FST
from fsmutils import composewords, trace

kFRENCH_TRANS = {0: "zero", 1: "un", 2: "deux", 3: "trois", 4:
                 "quatre", 5: "cinq", 6: "six", 7: "sept", 8: "huit",
                 9: "neuf", 10: "dix", 11: "onze", 12: "douze", 13:
                 "treize", 14: "quatorze", 15: "quinze", 16: "seize",
                 20: "vingt", 30: "trente", 40: "quarante", 50:
                 "cinquante", 60: "soixante", 100: "cent"}

kFRENCH_AND = 'et'

def prepare_input(integer):
    assert isinstance(integer, int) and integer < 1000 and integer >= 0, \
      "Integer out of bounds"
    return list("%03i" % integer)

def french_count():
    f = FST('french')

    f.add_state('start')
    f.add_state('next')
    f.add_state('sd')
    f.add_state('dd')
    f.add_state('ts')
    f.add_state('17')
    f.add_state('18')
    f.add_state('19')
    f.add_state('7t')
    f.add_state('8t')
    f.add_state('nt')
    f.add_state('cent')
    f.add_state('centsd')

    f.initial_state = 'start'

    f.set_final('next')
    f.set_final('sd')
    f.set_final('dd')
    f.set_final('17')
    f.set_final('18')
    f.set_final('19')
    f.set_final('ts')
    f.set_final('7t')
    f.set_final('8t')
    f.set_final('nt')
    f.set_final('cent')
    f.set_final('centsd')

    #one-digits
    f.add_arc('start', 'next', ['0'], [])
    f.add_arc('next', 'sd', ['0'], [])
    for ii in xrange(0,10):
        f.add_arc('sd', 'sd', [str(ii)], [kFRENCH_TRANS[ii]])
    #one-digits

    #two-digits
    f.add_arc('next','dd',['1'],[])
    for d in xrange(0,7):
        i = 10 + d
        f.add_arc('dd','dd',[str(d)],[kFRENCH_TRANS[i]])
    #two-digits

    #17-19
    f.add_arc('dd','17',['7'],['dix' + ' ' + kFRENCH_TRANS[7]])
    f.add_arc('dd', '18', ['8'], ['dix' + ' ' + kFRENCH_TRANS[8]])
    f.add_arc('dd', '19', ['9'], ['dix' + ' ' + kFRENCH_TRANS[9]])
    # 17-19

    #20-60

    for i in range(2,7):
        d = i * 10
        f.add_arc('next', 'ts', [str(i)], [kFRENCH_TRANS[d]])
        #f.add_arc('ts','ts',[str(i)],[])
    #f.add_arc('next', 'ts', ['3'], [kFRENCH_TRANS[30]])
    #f.add_arc('next', 'ts', ['4'], [kFRENCH_TRANS[40]])
    #f.add_arc('next', 'ts', ['5'], [kFRENCH_TRANS[50]])
    #f.add_arc('next', 'ts', ['6'], [kFRENCH_TRANS[60]])
    f.add_arc('ts','ts',['0'],[])
    # 20-60

    #20-69(except 21,31,....)
    for d in range(2,10):
        f.add_arc('ts','ts',[str(d)],[kFRENCH_TRANS[d]])

    # 20-69(except 21,31,....)

    #21,31....
    f.add_arc('ts', 'ts', ['1'], [kFRENCH_AND + ' ' + kFRENCH_TRANS[1]])
    # 21,31....

    #70s
    f.add_arc('next','7t',['7'],[])
    #f.add_arc('7t','7t',['0'],[kFRENCH_TRANS[60]])
    #f.add_arc('7t','7t',['1'],[kFRENCH_AND + ' ' + kFRENCH_TRANS[11]])
    for i in range(0,10):
        if i == 1:
            f.add_arc('7t', '7t', ['1'], [kFRENCH_TRANS[60]]+ [kFRENCH_AND] + [kFRENCH_TRANS[11]])
            break
        else:
            f.add_arc('7t','dd',[],[kFRENCH_TRANS[60]])
    #70s

    #80s
    f.add_arc('next','8t',['8'],[kFRENCH_TRANS[4]])
    f.add_arc('8t','8t',['0'],[kFRENCH_TRANS[20]])
    for i in range(1,10):
        f.add_arc('8t','8t',[str(i)],[kFRENCH_TRANS[20]] + [kFRENCH_TRANS[i]])
    #80s

    #90s
    f.add_arc('next','nt',['9'],[kFRENCH_TRANS[4]])
    f.add_arc('nt','dd',[],[kFRENCH_TRANS[20]])
    #90s

    #cents
    f.add_arc('start', 'cent', ['1'], [kFRENCH_TRANS[100]])
    f.add_arc('cent', 'centsd', ['0'], [])
    f.add_arc('centsd', 'centsd', ['0'], [])
    for i in xrange(1, 10):
        f.add_arc('centsd', 'centsd', [str(i)], [kFRENCH_TRANS[i]])
    for ii in xrange(2, 10):
        f.add_arc('start', 'cent', [str(ii)], [kFRENCH_TRANS[ii]] + [kFRENCH_TRANS[100]])

    f.add_arc('cent', 'dd', ['1'], [])
    for i in range(2,7):
        d = i * 10
        f.add_arc('cent', 'ts', [str(i)], [kFRENCH_TRANS[d]])
    #f.add_arc('cent', 'ts', ['2'], [kFRENCH_TRANS[20]])
    #f.add_arc('cent', 'ts', ['3'], [kFRENCH_TRANS[30]])
    #f.add_arc('cent', 'ts', ['4'], [kFRENCH_TRANS[40]])
    #f.add_arc('cent', 'ts', ['5'], [kFRENCH_TRANS[50]])
    #f.add_arc('cent', 'ts', ['6'], [kFRENCH_TRANS[60]])
    f.add_arc('cent','7t',['7'],[])
    f.add_arc('cent', '8t', ['8'], [kFRENCH_TRANS[4]])
    f.add_arc('cent','nt',['9'],[kFRENCH_TRANS[4]])
    #cents

    return f

if __name__ == '__main__':
    string_input = raw_input()
    user_input = int(string_input)
    f = french_count()
    print trace(f,['0','2','0'])
    if string_input:
        print user_input, '-->',
        print " ".join(f.transduce(prepare_input(user_input)))
    #print " ".join(f.transduce(prepare_input(0)))
    #print prepare_input(20)