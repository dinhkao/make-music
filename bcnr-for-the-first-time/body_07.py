# ============================================================ BAI 7: NORTH LIGHT
# Model: BCNR general compositional DNA - "irregular or changing meter"
#   (Wikipedia on For the first time: form, tonal displacement, riffs/pedals,
#    irregular or changing meter, dynamic escalation).
# This song is built on a true 7/8 violin ostinato (3+2+2 grouping) that CYCLES
# against a 4/4 supporting band - the polymeter is the point, the metre never
# settles. A minor, ~104 BPM. bowed=violin (Georgian Ellery feel), bone=sax counter
# Palette only from 20-frantic-choir.py.
import numpy as _np
BAR=4.0
NAME="07-north-light"
SECS=[('IN',8),('A',14),('B',14),('C',16),('ST',2),('D',10),('TG',2)]
S={}; _b=0.0
for _n,_c in SECS: S[_n]=_b; _b+=_c*BAR
END=_b
configure(104,104,END+3)
MAP=[(n,S[n],S[n]+c*BAR) for n,c in SECS]
def bar_at(sec,i): return S[sec]+i*BAR
print(NAME,int(END/BAR),"bars ->",round(TOTAL,1),"s")
K=Kit(seed=7210); P=Performer(K,T,SPB,TOTAL,seed=17,style='indie'); P.hum=0.6
sl=buf(); vx=buf(); bs=buf(); fx=buf(); ch=buf(); gt=buf()
# A natural minor; 7-note ostinato cell (3+2+2). A C E  G A  E C, persistent.
OST=[nn('A4'),nn('C5'),nn('E5'), nn('G5'),nn('A5'), nn('E5'),nn('C5')]
# we lay the 7 notes evenly across a bar = each note SPB(b)*4/7 = "7/8-ish" feel
def ostinato(b,buf_,g,octv=0,seed=0):
    R=_np.random.default_rng(int(b*727)+octv)
    step=SPB(b)*4.0/7.0
    for j,n_ in enumerate(OST):
        tt=T(b)+j*step+float(R.normal(0,0.010))
        bowed(buf_,tt,n_+12*octv,step*0.95,hg(g),det=float(R.normal(0,6)),seed=seed+j)
def villa(b,lvl=0.7,arc=1.0,busy=False,climax=False,ride=False):
    for s in range(16):
        acc=0.68 if s%4==0 else 0.40
        P.H(b+s*0.25,s,acc*lvl,o=0.0,art=('edge' if s%4==0 else 'tip'),arc=arc)
    kicks=[(0.0,1.0),(0.75,0.6),(2.0,0.55),(2.75,0.7)] if not busy else \
          [(0.0,1.0),(0.75,0.7),(1.5,0.6),(2.5,0.72),(3.0,0.6),(3.75,0.5)]
    for bb,vv in kicks: P.K(b+bb,int(bb*4)%16,vv*lvl,arc)
    if climax:
        P.S(b+1,4,0.95*lvl,'center',arc); P.S(b+3,12,1.0*lvl,'center',arc)
        for gp in (0.75,1.5,2.25,2.5,3.5): P.S(b+gp,int(gp*4)%16,0.30*lvl,'ghost',arc)
        P.CL(b+1+0.004,4,0.6*lvl,arc); P.CL(b+3+0.004,12,0.62*lvl,arc)
        if ride: P.RD(b,0,0.50*lvl,bell=True,arc=arc); P.RD(b+2,8,0.42*lvl,bell=True,arc=arc)
    else:
        P.S(b+1,4,0.6*lvl,'center',arc); P.S(b+3,12,0.62*lvl,'center',arc)
        if busy:
            for gp in (0.75,2.5): P.S(b+gp,int(gp*4)%16,0.26*lvl,'ghost',arc)
def basspulse(b,i,g):
    # bass also states the 7/8 pulse: A pedal dotted into 3+2+2 so we hear the meter
    R=_np.random.default_rng(i*5+2)
    fingerbass(bs,T(b)+0.0,nn('A1'),SPB(b)*1.4,hg(g),seed=R.integers(0,1e6))
    fingerbass(bs,T(b)+SPB(b)*4/7*3,nn('A1'),SPB(b)*(4/7*2),hg(g*0.85),seed=R.integers(0,1e6))
    fingerbass(bs,T(b)+SPB(b)*4/7*5,nn('A1'),SPB(b)*(4/7*2),hg(g*0.85),seed=R.integers(0,1e6))
# IN 0:00-0:18 solo ostinato + ghost drums
for i in range(8):
    b=bar_at('IN',i); f=0.5+0.06*i
    ostinato(b,sl,hg(0.07*f),seed=i)
    villa(b,hg(0.40*f),arc=0.5+0.03*i)
    if i%2==0: basspulse(b,i,hg(0.10*f))
# A 0:18-0:51 ostinato loop + bass pulse + faint sax counter
for i in range(14):
    b=bar_at('A',i); f=1+0.025*i
    ostinato(b,sl,hg(0.10*f),seed=i+10)
    basspulse(b,i,hg(0.20*f))
    hbone(ch,T(b)+0.5*BAR,nn('E4'),SPB(b)*1.8,hg(0.07*f),growl=0.4,seed=i)
    villa(b,hg(0.62*f),arc=0.55+0.02*i,busy=(i>=7))
    line(vx,b,[(0,.5,'A4','a','h'),(.5,.5,'C5','o',''),(1,.5,'E5','a','n'),(1.5,1.0,'A5','o','')],
         g=0.11*f,style='deadpan',breath=0.28,seedbase=i*73)
# B 0:51-1:24 ostinato in higher octave + sax state the same 7/8 in eighths, density up
for i in range(14):
    b=bar_at('B',i); f=1+0.035*i
    ostinato(b,sl,hg(0.10*f),octv=1,seed=i+20)
    Basspulse=basspulse(b,i,hg(0.22*f))
    crunch(gt,T(b),nn('A2'),SPB(b)*3.6,hg(0.06*f),drive=4.5,seed=i)
    hbone(ch,T(b),nn('E4'),SPB(b)*0.7,hg(0.09*f),growl=0.5,seed=i)  # sax doubling each note
    villa(b,hg(0.74*f),arc=0.78+0.016*i,busy=True,ride=(i%2==1))
    gang_like=_np.random.default_rng(i*3)
    for v in range(3):
        say(vx,T(b+1.5)+float(gang_like.normal(0,0.02)),nn('A4')+(12 if v==2 else 0),SPB(b)*1.4,'a','',0.06*f/2.5,'deadpan',0.30,seed=v+i,det=float(gang_like.normal(0,14)))
# C 1:24-2:01 climax: whole band states the 7/8 - violin high + bass + sax + dist gtr + drums
for i in range(16):
    b=bar_at('C',i); f=min(1.5,1+0.045*i)
    ostinato(b,sl,hg(0.13*f),octv=(0 if i<8 else 2),seed=i+30)
    basspulse(b,i,hg(0.26*f))
    crunch(gt,T(b),nn('A2'),SPB(b)*3.4,hg(0.08*f),drive=7.0,seed=i)
    mellotron(ch,T(b),nn('C5'),SPB(b)*3.6,hg(0.07*f),'choir',seed=i+5)
    hbone(ch,T(b),nn('E4')+(12 if i%2 else 0),SPB(b)*0.6,hg(0.11*f),growl=0.65,seed=i)
    villa(b,hg(0.92*f),arc=0.96+0.002*i,busy=True,climax=True,ride=True)
    chant(vx,b,[(0,.5,'A4','a','h'),(.5,.5,'C5','o','y'),(1,1.0,'A4','a','')],g=0.10*f,n=4,style='shout',seedbase=700+i)
    if i==15: P.fill(b+2.5,1.5,'burst32',1.1,next_crash_beat=S['ST'])
b=bar_at('ST',0)
P.K(b,0,1.1); P.S(b,0,1.0,'rim'); P.CR(b,0,0.85,size=1.3)
ostinato(b,sl,hg(0.06),seed=777); fingerbass(bs,T(b),nn('A1'),5.0,hg(0.10))
# D 2:01-2:25 return: ostinato (deadpan) -> shout stop dead
for i in range(10):
    b=bar_at('D',i); f=1+0.04*i
    ostinato(b,sl,hg(0.10*f),octv=1,seed=i+40)
    basspulse(b,i,hg(0.20*f))
    villa(b,hg(0.68+0.04*i*f),arc=0.86,busy=(i>=5),climax=(i>=7),ride=(i>=7))
    line(vx,b,[(0,.5,'A4','a','h'),(.5,.5,'C5','o',''),(1,1.0,'E5','a',''),(2,.5,'A4','o','w')],
         g=(0.10+0.01*i)*f,style=('deadpan' if i<5 else 'shout'),oct8=(0 if i<5 else 0.3),breath=0.28,seedbase=900+i)
# TG: ostinato one bar + hit + held
b=bar_at('TG',0)
ostinato(b,sl,hg(0.10),octv=1,seed=999)
P.K(b,0,1.2); P.S(b,0,1.0,'center'); P.CR(b,0,0.9,size=1.4); P.TM(b,0,1.0,80)
fzbass(bs,T(b),nn('A1'),SPB(b)*3.6,0.30)
for m in (nn('A3'),nn('C4'),nn('E4'),nn('A4')): mellotron(ch,T(b),m,SPB(b)*3.6,0.08,'choir',seed=int(m))
shriek(vx,T(b+0.3),nn('A5'),1.0,0.10)
P.apply_chokes()
DRUMS=mix_kit(P.bus,room_amount=0.22,oh_amount=0.92,lpf=9700)
noise_sw(fx,0,T(END),0.007,True,70,1500)
STEMS=[(sl,-0.42,0.66,0.42,0.0),(gt,0.5,0.56,0.40,7.0),(ch,0.12,0.60,0.36,0.0),(fx,0.0,0.9,0.0,0.0)]
MAPT=[(n,a,b_,(6.5 if n in('IN','ST','TG') else 2.6)) for n,a,b_ in MAP]
run(NAME, lambda voc: mixdown(NAME,vx,STEMS,DRUMS,bs,MAPT,vocals=voc,
    wet=0.20,decay=1.7,wide=1.55,drum_gain=0.80,bass_gain=0.90,crush_amt=0.24,
    rms_target=0.178), MAPT)