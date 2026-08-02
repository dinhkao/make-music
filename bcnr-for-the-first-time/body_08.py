# ============================================================ BAI 8: TIDE & TIRED
# Model: BCNR general DNA - "the quietest & most considered" extreme (Track X
#   taken further into pure stillness), PLUS a cathedral/post-rock horizontal
#   swell. 12/8 ballad, Eb major, with sustained tones that SUSPEND and never
#   cadence. Quietest: slow, brushed-only, choir+mellotron+saw_drone
#   wash, tackpiano. Build only by warmth+register, NOT loudness. Ends held.
# 12/8 = 4 dotted-quarters per bar. configure bpm 72 (dotted-quarter = 72).
# Palette only from 20-frantic-choir.py.
import numpy as _np
BAR=4.0
NAME="08-tide-and-tired"
SECS=[('IN',5),('A',9),('B',9),('C',9),('D',7),('OUT',5),('TG',2)]
S={}; _b=0.0
for _n,_c in SECS: S[_n]=_b; _b+=_c*BAR
END=_b
configure(72,72,END+4)
MAP=[(n,S[n],S[n]+c*BAR) for n,c in SECS]
def bar_at(sec,i): return S[sec]+i*BAR
e8=lambda b: SPB(b)/3.0          # one eighth in 12/8 (3 eighths/beat)
print(NAME,int(END/BAR),"bars ->",round(TOTAL,1),"s")
K=Kit(seed=8210); P=Performer(K,T,SPB,TOTAL,seed=18,style='indie'); P.hum=0.78
sl=buf(); vx=buf(); bs=buf(); fx=buf(); ch=buf(); gt=buf(); kp=buf()
# supended Eb chords: Ebsus2 -> Bbsus4 -> Abmaj7 -> Cm7 (i->V sus->VI->iv) never to plain Eb
Ebsus2=[nn('Eb3'),nn('F3'),nn('Bb3')]
Bbsus4=[nn('Bb2'),nn('Eb3'),nn('F3')]
Abmaj7=[nn('Ab2'),nn('C3'),nn('Eb3'),nn('G3')]
Cm7   =[nn('C2'),nn('Eb3'),nn('G3'),nn('Bb3')]
PROG=[Ebsus2,Bbsus4,Abmaj7,Cm7]
def vswirl(b,lvl=0.36,arc=1.0):
    # 12/8 brushes: ride bell 1 & 3, cross-stick 2 & 4, brushy eighths on hats, soft kick 1 & 3
    P.RD(b,0,0.34*lvl,bell=False,arc=arc); P.RD(b+2.0,8,0.32*lvl,bell=False,arc=arc)
    P.S(b+1.0,4,0.34*lvl,'cross',arc); P.S(b+3.0,12,0.34*lvl,'cross',arc)
    for k_ in range(12):
        P.H(b+k_*e8(b),k_*2%16,0.22*lvl,o=0.0,art='tip',arc=arc)
    P.K(b,0,0.42*lvl,arc); P.K(b+2.0,8,0.38*lvl,arc)
def strum12(b,i,c,g):
    R=_np.random.default_rng(i*9+5)
    for o in range(12):
        n_=c[o%len(c)]+(12 if o>=8 else 0)
        nylon(gt,T(b)+o*e8(b)+float(R.normal(0,0.014)),n_,hd(SPB(b)*0.5),hg(0.05*g),seed=int(o*7)+i)
# IN held Ebsus2, choir wash, very soft
for i in range(5):
    b=bar_at('IN',i); c=PROG[0]; f=0.5+0.06*i
    mellotron(ch,T(b),c[2]+12,SPB(b)*3.8,hg(0.05*f),'choir',seed=i)
    saw_drone(ch,T(b),c[0],SPB(b)*3.8,hg(0.03*f),seed=i+3)
    subbass(bs,T(b),c[0]-12,SPB(b)*3.8,0.14*f)
    bowed(sl,T(b),c[2]+12,SPB(b)*3.8,hg(0.07*f),det=float(_np.random.default_rng(i).normal(0,7)),seed=i)
    tackpiano(kp,T(b)+0.5*BAR,c[1],SPB(b)*2.6,hg(0.05*f),seed=i)
    vswirl(b,hg(0.30*f),arc=0.5+0.02*i)
# A 12 sup progressions slowly moving each 3 bars, nylon plucks in 12/8 feel
for i in range(9):
    b=bar_at('A',i); c=PROG[(i%4)]; f=1+0.02*i
    mellotron(ch,T(b),c[-1],SPB(b)*3.8,hg(0.06*f),'choir',seed=i+6)
    saw_drone(ch,T(b),c[0],SPB(b)*3.8,hg(0.035*f),seed=i+9)
    subbass(bs,T(b),c[0]-12,SPB(b)*3.6,0.16*f)
    strum12(b,i,c,f)
    tackpiano(kp,T(b),c[1],SPB(b)*3.8,hg(0.06*f),seed=i)
    bowed(sl,T(b)+0.6*BAR,c[-1]+12,SPB(b)*2.4,hg(0.085*f),det=float(_np.random.default_rng(i+1).normal(0,8)),seed=i+1)
    vswirl(b,hg(0.40*f),arc=0.7+0.012*i)
    line(vx,b,[(0,1.5,c[2],'a','h'),(1.5,1.5,c[-1],'o',''),(3.0,1.0,c[2],'a','y')],
         g=0.10*f,style='croon',breath=0.28,seedbase=i*67)
# B add rising counter (a fourth higher), warm
for i in range(9):
    b=bar_at('B',i); c=PROG[i%4]; f=1+0.03*i
    mellotron(ch,T(b),c[-1],SPB(b)*3.8,hg(0.07*f),'choir',seed=i+18)
    mellotron(ch,T(b)+0.5*BAR,c[-1]+7,SPB(b)*2.4,hg(0.05*f),'flute',seed=i+118)
    saw_drone(ch,T(b),c[0],SPB(b)*3.4,hg(0.04*f),seed=i+22)
    subbass(bs,T(b),c[0]-12,SPB(b)*3.6,0.18*f)
    strum12(b,i,c,f)
    tackpiano(kp,T(b),c[1],SPB(b)*3.8,hg(0.07*f),seed=i)
    bowed(sl,T(b),c[-1]+12,SPB(b)*3.0,hg(0.11*f),det=float(_np.random.default_rng(i+2).normal(0,8)),seed=i+2)
    bowed(sl,T(b)+0.5*BAR,c[-1]+19,SPB(b)*2.0,hg(0.08*f),det=0,seed=i+22)   # counter a 6th up
    vswirl(b,hg(0.48*f),arc=0.8+0.01*i)
    if i%4==3: P.TM(b+3.0,12,0.28*f,98,arc=0.9)
    line(vx,b,[(0,1.5,c[2],'a','o'),(1.5,1.5,c[-1],'o','v'),(3.0,1.0,c[2],'a','e')],
         g=0.118*f,style='croon',breath=0.27,seedbase=200+i)
# C warm swell - granosed horizontal build (choir+saw_drone stack), never explodes
for i in range(9):
    b=bar_at('C',i); c=PROG[i%4]; f=1+0.045*i
    mellotron(ch,T(b),c[-1],SPB(b)*3.8,hg(0.09*f),'choir',seed=i+30)
    mellotron(ch,T(b)+0.4*BAR,c[-1]+12,SPB(b)*2.6,hg(0.05*f),'choir',seed=i+130)
    saw_drone(ch,T(b),c[0],SPB(b)*3.0,hg(0.06*f),seed=i+33)
    saw_drone(ch,T(b)+0.5*BAR,c[2],SPB(b)*2.6,hg(0.04*f),seed=i+39)
    subbass(bs,T(b),c[0]-12,SPB(b)*3.6,0.20*f)
    strum12(b,i,c,f)
    crunch(gt,T(b),c[1],SPB(b)*3.8,hg(0.05*f),drive=1.4,seed=i)
    bowed(sl,T(b),c[-1]+12,SPB(b)*3.2,hg(0.125*f),det=float(_np.random.default_rng(i+3).normal(0,8)),seed=i+3)
    vswirl(b,hg(0.56*f),arc=0.9+0.008*i)
    ganglike=_np.random.default_rng(i*4)
    for v in range(3):
        say(vx,T(b)+float(ganglike.normal(0,0.02)),c[-1]+(12 if v==2 else 0),SPB(b)*2.6,'a','',0.055*f/2.5,'croon',0.30,seed=v+i,det=float(ganglike.normal(0,20)))
# D return to sparse nylon + deadpan last verse, suspend never resolve
for i in range(7):
    b=bar_at('D',i); c=PROG[i%4]; f=1-0.02*i+0.05
    mellotron(ch,T(b),c[-1],SPB(b)*3.8,hg(0.06*f),'choir',seed=i+42)
    subbass(bs,T(b),c[0]-12,SPB(b)*3.8,0.16*f)
    strum12(b,i,c,f)
    bowed(sl,T(b)+0.4*BAR,c[-1]+12,SPB(b)*2.4,hg(0.08*f),det=float(_np.random.default_rng(i+5).normal(0,8)),seed=i+5)
    vswirl(b,hg(0.42*f),arc=0.7)
    line(vx,b,[(0,1.5,c[2],'a','h'),(1.5,1.5,c[-1],'o','n'),(3.0,1.0,c[2],'a','')],
         g=0.11*f,style='croon',breath=0.29,seedbase=400+i)
# OUT fade on held Ebsus2 (never resolves)
for i in range(5):
    b=bar_at('OUT',i); c=PROG[0]; f=0.8-0.08*i
    mellotron(ch,T(b),c[2]+12,SPB(b)*3.6,hg(0.05*f),'choir',seed=i+50)
    saw_drone(ch,T(b),c[0],SPB(b)*3.6,hg(0.03*f),seed=i+53)
    subbass(bs,T(b),c[0]-12,SPB(b)*3.6,0.14*f)
    strum12(b,i,c,f)
    vswirl(b,hg(0.30*f),arc=0.6)
# TG a single held Ebsus2, violin fade - no resolution
b=bar_at('TG',0); c=PROG[0]
mellotron(ch,T(b),c[2]+12,SPB(b)*3.8,0.08,'choir',seed=99)
saw_drone(ch,T(b),c[0],SPB(b)*3.8,0.04,seed=199)
subbass(bs,T(b),c[0]-12,SPB(b)*3.8,0.16)
bowed(sl,T(b),c[2]+12,SPB(b)*3.8,hg(0.10),seed=99)
P.RD(b,0,0.32,bell=False); P.S(b+2,8,0.26,'cross')
P.apply_chokes()
DRUMS=mix_kit(P.bus,room_amount=0.32,oh_amount=0.62,lpf=7000)
noise_sw(fx,0,T(END),0.004,True,70,1200)
STEMS=[(sl,-0.40,0.66,0.30,0.0),(gt,0.42,0.54,0.30,9.0),(kp,0.0,0.56,0.28,0.0),(ch,0.14,0.72,0.0,0.0),(fx,0.0,0.7,0.0,0.0)]
MAPT=[(n,a,b_,(7.5 if n in('IN','OUT','TG') else 3.5)) for n,a,b_ in MAP]
run(NAME, lambda voc: mixdown(NAME,vx,STEMS,DRUMS,bs,MAPT,vocals=voc,
    wet=0.28,decay=2.2,wide=1.5,drum_gain=0.58,bass_gain=0.80,crush_amt=0.08,
    rms_target=0.148), MAPT)