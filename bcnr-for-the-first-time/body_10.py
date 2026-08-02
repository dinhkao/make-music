# ============================================================ BAI 10: SALT CATHEDRAL
# Model: BCNR general DNA - "post-rock crescendos, jazz improv, and abrupt changes"
#   + "Ants from Up There"-style cathedral swell + final Opus klezmer run.
# Through-composed cathedral/post-rock: a slow Em pedal grows into a MASS wall
# of mellotron-choir + saw_drone + brass; FALSE STOP; then a faster Opus-style
# klezmer run finale. Tempo ACCELERATES 96 -> 130 (the finale runs faster - like
# the band pushing). E minor. Build by ORCHESTRATION, never a 4-chord pop loop.
# Palette only from 20-frantic-choir.py.
import numpy as _np
BAR=4.0
NAME="10-salt-cathedral"
SECS=[('IN',8),('SW',12),('CRX',14),('ST',2),('KLR',12),('OUT',5),('TG',2)]
S={}; _b=0.0
for _n,_c in SECS: S[_n]=_b; _b+=_c*BAR
END=_b
configure(96,130,END+3)               # ACCELERANDO 96->130 (finale faster)
MAP=[(n,S[n],S[n]+c*BAR) for n,c in SECS]
def bar_at(sec,i): return S[sec]+i*BAR
print(NAME,int(END/BAR),"bars ->",round(TOTAL,1),"s")
K=Kit(seed=10210); P=Performer(K,T,SPB,TOTAL,seed=20,style='indie'); P.hum=0.6
sl=buf(); vx=buf(); bs=buf(); fx=buf(); ch=buf(); gt=buf()
# slow colour chords over Em pedal (the massed chord rises)
COL=[[nn('E2'),nn('E3'),nn('G3'),nn('B3')],
     [nn('E2'),nn('E3'),nn('G3'),nn('B3')],
     [nn('G2'),nn('B3'),nn('D4'),nn('G4')],     # III
     [nn('C2'),nn('C3'),nn('E3'),nn('G3')],     # bVI borrowed (the big move)
     [nn('D2'),nn('D3'),nn('F#3'),nn('A3')],    # VII major-ish pull
     [nn('E2'),nn('G3'),nn('B3'),nn('D4')]]     # Em7 home
def col(i): return COL[i%len(COL)]
# klezmer run (Opus finale, on E): F-natural? keep E Phryg-dom-ish: F E Eb D C B  descending chromatic-ish
RUN=[nn('F4'),nn('E4'),nn('Eb4'),nn('D4'),nn('C4'),nn('B3')]
def cathedral_pad(b,i,g):
    c=col(i)
    for m in c:
        mellotron(ch,T(b),m,SPB(b)*3.7,hg(g),'choir',seed=int(m)+i*3)
        saw_drone(ch,T(b),m-12,SPB(b)*3.4,hg(g*0.5),seed=int(m)+i*7)
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
        if ride: P.RD(b,0,0.52*lvl,bell=True,arc=arc); P.RD(b+2,8,0.44*lvl,bell=True,arc=arc)
    else:
        P.S(b+1,4,0.62*lvl,'center',arc); P.S(b+3,12,0.66*lvl,'center',arc)
        if busy:
            for gp in (0.75,2.5): P.S(b+gp,int(gp*4)%16,0.26*lvl,'ghost',arc)
# IN slow Em pedal, sub, faint violin
for i in range(8):
    b=bar_at('IN',i); c=col(i); f=0.5+0.06*i
    cathedral_pad(b,i,0.03*f)
    subbass(bs,T(b),nn('E1'),SPB(b)*3.7,0.18*f)
    bassn(bs,T(b+0.5),c[0],SPB(b)*1.6,hg(0.16*f))
    bowed(sl,T(b),nn('B4'),SPB(b)*3.6,hg(0.06*f),det=float(_np.random.default_rng(i).normal(0,7)),seed=i)
    villa(b,hg(0.42*f),arc=0.5+0.03*i)
# SW slow warmth: layer violin, then bone, faint dist gtr, density up
for i in range(12):
    b=bar_at('SW',i); c=col(i); f=1+0.035*i
    cathedral_pad(b,i,0.04*f)
    subbass(bs,T(b),nn('E1'),SPB(b)*3.7,0.20*f)
    bassn(bs,T(b),c[0],SPB(b)*1.8,hg(0.22*f))
    bowed(sl,T(b),c[-1]+12,SPB(b)*2.6,hg(0.10*f),det=float(_np.random.default_rng(i+2).normal(0,8)),seed=i+2)
    if i>=5: hbone(ch,T(b)+0.4*BAR,c[-1],SPB(b)*1.8,hg(0.09*f),growl=0.5,seed=i)
    if i>=9: crunch(gt,T(b),c[0],SPB(b)*3.6,hg(0.06*f),drive=6.0,seed=i)
    villa(b,hg(0.62*f),arc=0.6+0.025*i,busy=(i>=8),ride=(i%2==1 and i>=8))
    line(vx,b,[(0,1.0,c[-1],'a','h'),(1,1.0,c[2],'o',''),(2,1.5,c[-1],'a','y'),(3.5,0.5,c[1],'o','')],
         g=0.10*f,style='deadpan',breath=0.28,seedbase=i*73)
# CRX cathedral crescendo wall: massed mellotron+saw_drone+brass+dist, climax
for i in range(14):
    b=bar_at('CRX',i); c=col(i); f=min(1.55,1+0.05*i)
    cathedral_pad(b,i,0.09*f)
    subbass(bs,T(b),nn('E1'),SPB(b)*3.5,0.32*f)
    bassn(bs,T(b),c[0],SPB(b)*1.8,hg(0.30*f))
    bowed(sl,T(b),c[-1]+12,SPB(b)*2.6,hg(0.14*f),det=float(_np.random.default_rng(i+9).normal(0,8)),seed=i+9)
    hbone(ch,T(b),c[-1],SPB(b)*2.4,hg(0.12*f),growl=0.6,seed=i)
    horn(ch,T(b),c[2]+12,SPB(b)*2.0,hg(0.07*f))
    crunch(gt,T(b),c[0],SPB(b)*3.4,hg(0.09*f),drive=7.5,seed=i)
    villa(b,hg(0.95*f),arc=0.96+0.002*i,busy=True,climax=True,ride=True)
    chant(vx,b,[(0,.5,c[-1],'a','h'),(.5,.5,c[2],'o','y'),(1,1.0,c[-1],'a','')],g=0.10*f,n=5,style='shout',seedbase=600+i)
    if i==13: P.fill(b+2.5,1.5,'burst32',1.1,next_crash_beat=S['ST'])
# ST false stop: one held Em violin + sub, near silence
b=bar_at('ST',0)
cathedral_pad(b,0,0.02)
bowed(sl,T(b),nn('E5'),6.0,0.05,seed=1); subbass(bs,T(b),nn('E1'),6.0,0.05)
P.RD(b,0,0.3,bell=True)
# KLR klezmer run finale (tempo now faster): whole band runs RUN descending over Em
for i in range(12):
    b=bar_at('KLR',i); c=col(i); f=1.2+0.06*i
    subbass(bs,T(b),nn('E1'),SPB(b)*3.4,0.36*f)
    bassn(bs,T(b),c[0],SPB(b)*1.6,hg(0.30*f))
    # run climbs across the band
    R=_np.random.default_rng(i*2+5)
    r=RUN[(i+int(i/2))%len(RUN)]
    for o,gg in [(0,0.09*f),(12,0.11*f),(-12,0.06*f)]:
        bone(ch,T(b)+float(R.normal(0,0.01)),r+o,SPB(b)*0.5,hg(gg),growl=0.6,seed=i+o)
    crunch(sl,T(b),r,SPB(b)*0.6,hg(0.08*f),drive=7.0,seed=i)
    crunch(gt,T(b),nn('E2'),SPB(b)*3.4,hg(0.09*f),drive=8.5,seed=i)
    cathedral_pad(b,i,0.08*f)
    villa(b,hg(1.0*f),arc=1.0,busy=True,climax=True,ride=True)
    chant(vx,b,[(0,.5,r+12,'a','h'),(.5,.5,'E4','o','y'),(1,1.0,'E4','a','')],g=0.10*f,n=5,style='shout',seedbase=900+i)
    if i==11: P.fill(b+2.5,1.5,'burst32',1.2,next_crash_beat=S['OUT'])
# OUT resolve-ish pulled back to Em colour, fade
for i in range(5):
    b=bar_at('OUT',i); c=col(i); f=0.8-0.10*i
    cathedral_pad(b,i,0.06*f)
    subbass(bs,T(b),nn('E1'),SPB(b)*3.4,0.22*f)
    bowed(sl,T(b),c[-1]+12,SPB(b)*3.0,hg(0.10*f),det=float(_np.random.default_rng(i+7).normal(0,8)),seed=i+7)
    villa(b,hg(0.55*f),arc=0.7,ride=True,busy=False,climax=False)
# TG: hit + held Em mass, brass, no plain resolve
b=bar_at('TG',0)
P.K(b,0,1.2); P.S(b,0,1.0,'center'); P.CR(b,0,0.9,size=1.4); P.TM(b,0,1.0,80)
subbass(bs,T(b),nn('E1'),SPB(b)*3.6,0.30)
cathedral_pad(b,0,0.12)
for m in (nn('E3'),nn('G3'),nn('B3'),nn('E4')): mellotron(ch,T(b),m,SPB(b)*3.6,0.09,'choir',seed=int(m))
bone(ch,T(b),nn('B4'),SPB(b)*3.5,0.13,growl=0.8,seed=999)
shriek(vx,T(b+0.3),nn('B5'),1.0,0.10)
P.apply_chokes()
DRUMS=mix_kit(P.bus,room_amount=0.24,oh_amount=0.92,lpf=9700)
noise_sw(fx,0,T(END),0.006,True,70,1400)
STEMS=[(sl,-0.42,0.66,0.40,0.0),(gt,0.5,0.58,0.40,7.0),(ch,0.12,0.66,0.0,0.0),(fx,0.0,0.9,0.0,0.0)]
MAPT=[(n,a,b_,(6.5 if n in('IN','OUT','TG') else 2.6)) for n,a,b_ in MAP]
run(NAME, lambda voc: mixdown(NAME,vx,STEMS,DRUMS,bs,MAPT,vocals=voc,
    wet=0.22,decay=1.8,wide=1.5,drum_gain=0.80,bass_gain=0.90,crush_amt=0.22,
    rms_target=0.178), MAPT)