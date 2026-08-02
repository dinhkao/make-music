# ============================================================ BAI 9: WIRE HOUSE
# Model: BCNR general DNA - free-jazz/klezmer STOP-START (Science Fair's
#   improvised fuzz + Opus' klezmer turn + Sunglasses' abrupt cut/re-entry).
# C Phrygian DOMINANT (C Db E F G Ab Bb - harmonic-minor flavour, klezmer-flamenco).
# Abrupt cuts, fuzz improv interludes, brass stabs, relentless stomp. 128 BPM.
# Palette only from 20-frantic-choir.py.
import numpy as _np
BAR=4.0
NAME="09-wire-house"
SECS=[('FZ',5),('VS',12),('CUT',1),('RFF',10),('CUT',1),('STB',10),('CUT',1),('BL',14),('OUT',5),('TG',2)]
S={}; _b=0.0
for _n,_c in SECS: S[_n]=_b; _b+=_c*BAR
END=_b
configure(128,128,END+3)
MAP=[(n,S[n],S[n]+c*BAR) for n,c in SECS]
def bar_at(sec,i): return S[sec]+i*BAR
print(NAME,int(END/BAR),"bars ->",round(TOTAL,1),"s")
K=Kit(seed=9210); P=Performer(K,T,SPB,TOTAL,seed=19,style='indie'); P.hum=0.6
sl=buf(); vx=buf(); bs=buf(); fx=buf(); ch=buf(); gt=buf()
PC=nn('C2')
TURN=[nn('C4'),nn('Db4'),nn('C4')]           # C-Db-C klezmer turn (Phrygian dom b2)
RUN =[nn('Eb4'),nn('E4'),nn('F4'),nn('Ab4'),nn('G4')]  # half-step colour run
def villa(b,lvl=0.8,arc=1.0,busy=False,climax=False,ride=False):
    for s in range(16):
        acc=0.70 if s%4==0 else 0.40
        P.H(b+s*0.25,s,acc*lvl,o=0.0,art=('edge' if s%4==0 else 'tip'),arc=arc)
    kicks=[(0.0,1.0),(0.75,0.62),(2.0,0.55),(2.75,0.7)] if not busy else \
          [(0.0,1.0),(0.75,0.72),(1.5,0.6),(2.5,0.72),(3.0,0.6),(3.75,0.5)]
    for bb,vv in kicks: P.K(b+bb,int(bb*4)%16,vv*lvl,arc)
    if climax:
        P.S(b+1,4,0.95*lvl,'center',arc); P.S(b+3,12,1.0*lvl,'center',arc)
        for gp in (0.75,1.5,2.25,2.5,3.5): P.S(b+gp,int(gp*4)%16,0.30*lvl,'ghost',arc)
        P.CL(b+1+0.004,4,0.6*lvl,arc); P.CL(b+3+0.004,12,0.62*lvl,arc)
        if ride: P.RD(b,0,0.50*lvl,bell=True,arc=arc); P.RD(b+2,8,0.42*lvl,bell=True,arc=arc)
    else:
        P.S(b+1,4,0.6*lvl,'center',arc); P.S(b+3,12,0.64*lvl,'center',arc)
        if busy:
            for gp in (0.75,2.5): P.S(b+gp,int(gp*4)%16,0.26*lvl,'ghost',arc)
def fuzz_improv(b,i,g):
    R=_np.random.default_rng(i*13+9)
    for k_ in range(5):
        n_=TURN[R.integers(0,3)]+(0 if R.random()<0.6 else 12)
        tt=T(b)+R.uniform(0,3.4)*SPB(b)
        d_=R.uniform(0.05,0.3)
        crunch(gt,tt,n_,hd(SPB(b)*d_),hg(g),drive=float(R.uniform(5.5,8.5)),seed=k_+i*5)
    x=ks(PC,SPB(b)*3.0,0.9920,0.42,seed=i*7).astype(_np.float64)
    x=_np.tanh(x*9.0); bq,aq=sg.butter(2,[140/(SR/2),1600/(SR/2)],'band'); x=sg.lfilter(bq,aq,x)
    put(gt,T(b),x*hg(g*0.5),1.0)
def droneriff(b,i,g,drive=4.0):
    R=_np.random.default_rng(i*9+2)
    fzbass(bs,T(b),PC,SPB(b)*3.6,hg(0.24),seed=i,bite=1.1)
    crunch(sl,T(b),PC,SPB(b)*3.6,hg(0.10*g),drive=2.8,seed=i)
    for k_ in range(3):
        base=k_*1.2
        for j,n_ in enumerate(TURN):
            crunch(sl,T(b)+(base+j*0.20)*SPB(b)+float(R.normal(0,0.010)),n_+(12 if k_==2 else 0),hd(SPB(b)*0.2),hg(0.07*g),drive=drive,seed=i*5+k_*3+j)
        leadgtr(gt,T(b)+(base+0.5)*SPB(b),nn('C4')+12+k_*3,hd(SPB(b)*0.3),hg(0.05*g),bend=0.4,seed=i*7+k_)
def horn_stab(b,i,note,g):
    R=_np.random.default_rng(i*4+1)
    bone(ch,T(b),note,SPB(b)*0.9,hg(g),growl=0.6,seed=i,det=float(R.normal(0,8)))
    horn(ch,T(b),note-12,SPB(b)*0.9,hg(g*0.7))
# FZ fuzz improv intro over pedal
for i in range(5):
    b=bar_at('FZ',i); f=0.5+0.08*i
    fzbass(bs,T(b),PC,SPB(b)*3.6,hg(0.14*f),seed=i)
    fuzz_improv(b,i,0.06*f)
    villa(b,hg(0.4*f),arc=0.5+0.04*i)
# VS verse: turn 3x, brass stabs, deadpan, sparse
for i in range(12):
    b=bar_at('VS',i); f=1+0.025*i
    droneriff(b,i,f)
    mellotron(ch,T(b),nn('C4'),SPB(b)*3.6,hg(0.04*f),'choir',seed=i)
    horn_stab(b,i,nn('G4'),0.06*f)
    villa(b,hg(0.62*f),arc=0.55+0.02*i,busy=(i>=7))
    line(vx,b,[(0,.5,'C4','a','h'),(.5,.5,'Db4','o','t'),(1,.5,'C4','a',''),(1.5,1.0,'G4','o','w')],
         g=0.12*f,style='deadpan',breath=0.28,seedbase=i*73)
# CUT 1 bar near-silence (only fuzz stab + sub)
for i in range(1):
    b=bar_at('CUT',0 if i==0 else 1)
    fuzzbass_dum=fzbass(bs,T(b),PC,SPB(b)*3.0,hg(0.16))
    crunch(gt,T(b),nn('C3'),SPB(b)*0.9,hg(0.10),drive=8.5,seed=7)
    P.K(b,0,0.8); P.S(b,0,0.8,'rim'); P.CR(b,0,0.7,size=1.2)
# RFF turn + brass counter, building density (busier)
for i in range(10):
    b=bar_at('RFF',i); f=1+0.04*i
    droneriff(b,i,f,drive=5.0)
    mellotron(ch,T(b),nn('C4'),SPB(b)*3.6,hg(0.05*f),'choir',seed=i+20)
    crunch(gt,T(b)+0.5*BAR,nn('C4')+12,hd(SPB(b)*0.6),hg(0.06*f),drive=7.0,seed=i)
    hbone(ch,T(b),nn('Eb4'),SPB(b)*1.6,hg(0.10*f),growl=0.6,seed=i)
    villa(b,hg(0.74*f),arc=0.82+0.018*i,busy=True,ride=(i%2==1))
    if i==9: P.fill(b+2.5,1.5,'stutter',1.1,next_crash_beat=S['CUT']+BAR)
# CUT 2 near-silence
b=bar_at('CUT',BAR)
fzbass(bs,T(b),PC,SPB(b)*3.0,hg(0.16))
crunch(gt,T(b),nn('C3'),SPB(b)*0.9,hg(0.10),drive=8.5,seed=8)
P.K(b,0,0.8); P.S(b,0,0.8,'rim'); P.CR(b,0,0.7,size=1.2)
# STB brass-stab stop-start section: stabs + gtr punches, drums pull back then SLAM
for i in range(10):
    b=bar_at('STB',i); f=1+0.05*i
    fzbass(bs,T(b),PC,SPB(b)*3.4,hg(0.22*f),seed=i,bite=1.2)
    horn_stab(b,i,[nn('G4'),nn('Eb4'),nn('C5'),nn('Bb4')][i%4],0.09*f)
    crunch(gt,T(b),nn('C3'),SPB(b)*0.6,hg(0.09*f),drive=8.5,seed=i)
    crunch(gt,T(b)+1.5*BAR,nn('Eb3'),SPB(b)*0.5,hg(0.08*f),drive=9.0,seed=i+1)
    cup=P.fill(b+2.5,1.5,'tom',1.1,next_crash_beat=S['CUT']+2*BAR) if i==9 else None
    villa(b,hg(0.78*f),arc=0.86+0.012*i,busy=True,climax=(i>=7),ride=(i>=7))
    chant(vx,b,[(0,.5,'C4','a','h'),(.5,.5,'Db4','o','y'),(1,1.0,'C4','a','')],g=0.09*f,n=4,style='shout',seedbase=400+i)
# CUT 3
b=bar_at('CUT',2*BAR)
fzbass(bs,T(b),PC,SPB(b)*3.0,hg(0.16))
crunch(gt,T(b),nn('C3'),SPB(b)*0.9,hg(0.10),drive=8.5,seed=9)
P.K(b,0,0.8); P.S(b,0,0.8,'rim'); P.CR(b,0,0.7,size=1.2)
# BL blowout: 2-chord C/Db (the klezmer tritone-ish neighbour pair ad-infinitum)
for i in range(14):
    b=bar_at('BL',i); f=min(1.55,1+0.05*i)
    c=PC if i%2==0 else nn('Db2')
    fzbass(bs,T(b),c,SPB(b)*3.4,hg(0.26*f),seed=i,bite=1.2)
    crunch(gt,T(b),(nn('C3') if i%2==0 else nn('Db3')),SPB(b)*3.3,hg(0.10*f),drive=8.8,seed=i)
    crunch(gt,T(b)+0.5*BAR,(nn('C4') if i%2==0 else nn('Eb4')),hd(SPB(b)*0.4),hg(0.075*f),drive=9.2,seed=i+1)
    droneriff(b,i,f*0.7,drive=6.0)
    hbone(ch,T(b),[nn('E4'),nn('Eb4')][i%2],SPB(b)*1.5,hg(0.12*f),growl=0.65,seed=i)
    villa(b,hg(0.96*f),arc=1.0,busy=True,climax=True,ride=True)
    chant(vx,b,[(0,.5,'C4','a','h'),(.5,.5,'Db4','o','y'),(1,1.0,'E4','a','')],g=0.10*f,n=5,style='shout',seedbase=700+i)
    if i==13: P.fill(b+2.5,1.5,'burst32',1.1,next_crash_beat=S['OUT'])
# OUT fade turn, never resolves on C
for i in range(5):
    b=bar_at('OUT',i); f=0.7-0.08*i
    droneriff(b,i,f,drive=3.2)
    villa(b,hg(0.5*f),arc=0.6)
# TG hit + held C pedal, brass, no resolution
b=bar_at('TG',0)
P.K(b,0,1.2); P.S(b,0,1.0,'center'); P.CR(b,0,0.9,size=1.4); P.TM(b,0,1.0,80)
fzbass(bs,T(b),PC,SPB(b)*3.6,0.30)
for n_ in TURN: crunch(gt,T(b),n_,SPB(b)*3.5,hg(0.08),drive=6.0,seed=int(n_))
bone(ch,T(b),nn('G4'),SPB(b)*3.5,0.12,growl=0.8,seed=99)
shriek(vx,T(b+0.3),nn('G5'),1.0,0.10)
P.apply_chokes()
DRUMS=mix_kit(P.bus,room_amount=0.22,oh_amount=0.92,lpf=9700)
noise_sw(fx,0,T(END),0.008,True,70,1500)
STEMS=[(sl,-0.42,0.62,0.42,0.0),(gt,0.5,0.60,0.40,7.0),(ch,0.10,0.60,0.36,0.0),(fx,0.0,0.9,0.0,0.0)]
MAPT=[(n,a,b_,(6.5 if n in('FZ','CUT','TG') else 2.6)) for n,a,b_ in MAP]
run(NAME, lambda voc: mixdown(NAME,vx,STEMS,DRUMS,bs,MAPT,vocals=voc,
    wet=0.18,decay=1.4,wide=1.5,drum_gain=0.82,bass_gain=0.92,crush_amt=0.28,
    rms_target=0.182), MAPT)