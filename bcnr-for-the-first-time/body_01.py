# ============================================================ BAI 1: FIFTH HOUR
# Model: Black Country, New Road - "Instrumental" (For the first time, 2021).
#   - original E minor ~104 BPM slow-burn -> transposed to F# minor
#   - "slow-burn ensemble escalation": the climax is in ORCHESTRATION/LAYERING,
#     not chord changes. ONE motif reinforced by violin, sax, dist-guitar,
#     mellotron-choir, massed drums.
#   - slow colour chords (A maj7 / B borrowed / C major) move while F# pedal holds
#   - FALSE STOP -> near silence -> HARDER RE-ENTRY on the same motif.
# Instruments: only the palette of 20-frantic-choir.py
#   bowed=violin, bone=sax/brass, crunch=dist guitar, mellotron=choir swell,
#   bassn/subbass=bass, say/line/chant/gang=vocals (Isaac Wood style), Kit+Performer=drums (Nick Villa)
BAR=4.0
NAME="01-fifth-hour"
SECS=[('IN',10),('L1',10),('L2',10),('L3',12),('CLX',14),('ST',2),('RE',10),('TAG',2)]
S={}; _b=0.0
for _n,_c in SECS: S[_n]=_b; _b+=_c*BAR
END=_b
configure(104,105,END+3)             # 104->105 BPM (a touch of drift, BCNR live feel)
MAP=[(n,S[n],S[n]+c*BAR) for n,c in SECS]
def bar_at(sec,i): return S[sec]+i*BAR
print(NAME,int(END/BAR),"bars ->",round(TOTAL,1),"s")

# motif F#m: F#-A-C#-B-A-F# (stepwise rising-falling, the BCNR "one idea revived")
MNOT=[nn('F#4'),nn('A4'),nn('C#5'),nn('B4'),nn('A4'),nn('F#4')]
def motif(b,b0,octv,kind,g,seed=0):
    R=np.random.default_rng(int(b0*727+octv)%9999)
    for i,n_ in enumerate(MNOT):
        m=n_+12*octv
        jt=float(R.normal(0,0.011)); d=SPB(b0)*0.90+float(R.normal(0,0.02))
        tt=T(b0+i*SPB(b0)*0.90)+jt
        if   kind=='violin': bowed(b,tt,m,d,hg(g),det=float(R.normal(0,6)),seed=i+seed)
        elif kind=='sax':    hbone(b,tt,m,d,hg(g),det=float(R.normal(0,5)),growl=0.5,seed=i+seed)
        elif kind=='gtr':    crunch(b,tt,m,hd(d),hg(g),drive=6.5,seed=i+seed)
def padch(b,b0,notes,g=0.07,seed=0):
    # slow moving colour chord = faint mellotron choir (note list)
    for m in notes:
        mellotron(b,T(b0),m,SPB(b0)*3.6,hg(g),kind='choir',seed=seed+int(m))

# Kit + Performer (Nick Villa humanised)
K=Kit(seed=1220); P=Performer(K,T,SPB,TOTAL,seed=11,style='indie'); P.hum=0.62
def villa(b,lvl=0.8,arc=1.0,busy=False,climax=False):
    """Nick Villa: even quiet 16th hats locked to grid (accent off-16ths),
       kick = melodic counter-rhythm on off-16ths (empty downbeats),
       snare backbeat + ghosts, ride-bell + tom rolls at climax."""
    a=arc
    # hats even 16ths, accents on e/&
    for s in range(16):
        acc=0.70 if s%4==0 else 0.40
        P.H(b+s*0.25,s,acc*lvl,o=0.0,art=('edge' if s%4==0 else 'tip'),arc=a)
    # kick melody vs grid: lands on off-16ths, drops some downbeats
    kicks=[(0.0,1.0),(0.75,0.6),(2.0,0.5),(2.75,0.7)] if not busy else \
          [(0.0,1.0),(0.75,0.7),(1.5,0.6),(2.5,0.7),(3.0,0.6),(3.75,0.5)]
    for bb,vv in kicks: P.K(b+bb,int(bb*4)%16,vv*lvl,a)
    P.S(b+1,4,0.9*lvl,'center',a); P.S(b+3,12,0.95*lvl,'center',a)
    if busy:
        for gp in (0.75,1.75,2.5,3.5): P.S(b+gp,int(gp*4)%16,0.30*lvl,'ghost',a)
    if climax:
        P.RD(b,0,0.55*lvl,bell=True,arc=a); P.RD(b+2,8,0.45*lvl,bell=True,arc=a)
        P.CL(b+1+0.004,4,0.6*lvl,a); P.CL(b+3+0.004,12,0.62*lvl,a)

# stems (mono buffers, engine convention)
sl=buf(); vx=buf(); bs=buf(); fx=buf(); cho=buf()  # bowed/sax/gtr share 'sl'? -> separate bufs
vn=buf(); sx=buf(); gt=buf()

# colour chords over F# pedal (2-bar each feel), slow
COL=[[nn('F#2'),nn('F#3'),nn('A3'),nn('C#4')],
     [nn('F#2'),nn('F#3'),nn('A3'),nn('C#4')],
     [nn('A2'),nn('A3'),nn('C#4'),nn('E4')],     # III borrowed major colour
     [nn('B2'),nn('B3'),nn('D#4'),nn('F#4')],     # IV major-ish
     [nn('C3'),nn('C4'),nn('E4'),nn('G4')],       # bV borrowed
     [nn('F#2'),nn('A3'),nn('C#4'),nn('E4')]]    # home
def col(i): return COL[i%len(COL)]

# ---- INTRO (~0:00-0:30, 8 bars): low F# pedal + sub + sparse ----
for i in range(10):
    b=bar_at('IN',i)
    c=col(i)
    padch(cho,b,[c[0],c[1],c[2]],0.04+(0.003*i))
    subbass(bs,T(b),nn('F#1'),SPB(b)*3.6,0.22+0.005*i)
    bassn(bs,T(b),nn('F#2'),SPB(b)*1.9,hg(0.20))
    villa(b,hg(0.55),arc=0.6+0.03*i)
    if i>=4: motif(sl,b,1,'violin',0.07,seed=i)   # very faint violin hint
# ---- L1 (~0:30-1:00, 8 bars): violin motif + wurli ----
for i in range(10):
    b=bar_at('L1',i); c=col(i); f=1+0.02*i
    padch(cho,b,[c[0],c[2],c[3]],0.05*f+0.013*i)
    subbass(bs,T(b),nn('F#1'),SPB(b)*3.6,0.24*f)
    bassn(bs,T(b+0.5),c[0],SPB(b)*1.5,hg(0.18*f))
    wurli(cho,T(b),c[3],SPB(b)*3.6,hg(0.05*f))
    motif(vn,b,1,'violin',0.09*f,seed=i)
    villa(b,hg(0.65*f),arc=0.7+0.03*i)
# ---- L2 (~1:00-1:30, 8 bars): + sax counter ----
for i in range(10):
    b=bar_at('L2',i); c=col(i); f=1+0.03*i
    padch(cho,b,[c[0],c[1],c[2],c[3]],0.06*f)
    subbass(bs,T(b),nn('F#1'),SPB(b)*3.6,0.26*f)
    bassn(bs,T(b),c[0],SPB(b)*1.9,hg(0.22*f))
    motif(vn,b,2 if i<4 else 2,'violin',0.11*f,seed=i)
    hbone(sx,T(b+0.5*BAR),c[-1]+7,SPB(b)*2.6,hg(0.09*f),growl=0.4,seed=i)
    villa(b,hg(0.72*f),arc=0.82+0.02*i,busy=(i>=4))
    if i>=4: line(vx,b,[(0,.5,'F#4','a','h'),(.5,.5,'A4','a',''),(1,.5,'C#5','o','w'),(1.5,1.5,'B4','a','n')],
                  g=0.10*f,style='deadpan',breath=0.28,seedbase=50+i)
# ---- L3 (~1:30-2:09, 10 bars): dist guitar reinforces + tom ----
for i in range(12):
    b=bar_at('L3',i); c=col(i); f=1+0.03*i
    padch(cho,b,c,0.07*f)
    subbass(bs,T(b),nn('F#1'),SPB(b)*3.6,0.30*f)
    bassn(bs,T(b),c[0],SPB(b)*1.9,hg(0.26*f))
    motif(vn,b,1,'violin',0.12*f,seed=i); motif(sx,b,1,'sax',0.115*f,seed=i)
    motif(gt,b,0,'gtr',0.085*f,seed=i)
    if i%2==0: P.TM(b+2.5,10,0.5*f,tune=98,arc=0.9)
    villa(b,hg(0.82*f),arc=0.92,busy=True)
    if i%3==1: P.RD(b+3.5,14,0.4*f,bell=True)
    line(vx,b,[(0,.5,'F#4','o',''),(.75,0.4,'A4','a','k'),(1.25,.75,'C#5','a',''),(2.0,.5,'B4','o','l'),(2.75,.75,'A4','a','')],
         g=0.12*f,style='deadpan',oct8=0.0,breath=0.28,seedbase=150+i)
# ---- CLIMAX (~2:09-2:48, 10 bars): full wall ----
for i in range(14):
    b=bar_at('CLX',i); c=col(i); f=min(1.5,1+0.045*i)
    padch(cho,b,[x+12 for x in c]+c,0.10*f)
    subbass(bs,T(b),nn('F#1'),SPB(b)*3.4,0.36*f)
    bassn(bs,T(b),c[0],SPB(b)*1.8,hg(0.30*f))
    motif(vn,b,2,'violin',0.14*f,seed=i); motif(sx,b,1,'sax',0.145*f,seed=i); motif(gt,b,0,'gtr',0.11*f,seed=i)
    horn(cho,T(b),c[2]+12,SPB(b)*1.8,hg(0.06*f)); horn(cho,T(b+2),c[1]+12,SPB(b)*1.4,hg(0.05*f))
    villa(b,hg(0.95*f),arc=0.98,busy=True,climax=True)
    if i==12: P.fill(b+2.5,1.5,'burst32',1.0,next_crash_beat=S['ST'])
    chant(vx,b,[(0,.4,'F#4','a','h'),(.4,.4,'A4','o','y'),(1.2,1.2,'C#5','a','')],g=0.08*f,n=4,style='shout',seedbase=300+i)
# ---- FALSE STOP (~2:48-2:55, 2 bars near-silence) ----
b=bar_at('ST',0)
padch(cho,b,[nn('F#3'),nn('C#5'),nn('F#5')],0.018)
bowed(vn,T(b),nn('F#5'),6.2,0.05)
subbass(bs,T(b),nn('F#1'),6.0,0.05)
P.RD(b,0,0.3,bell=True)
# ---- RE-ENTRY (~2:55-3:25, 8 bars): harder, short, hard stop ---- -> trim to fit 180s
for i in range(10):
    b=bar_at('RE',i); c=col(i); f=1.3+0.06*i
    padch(cho,b,[x+12 for x in c]+c,0.12*f)
    subbass(bs,T(b),nn('F#1'),SPB(b)*1.6,0.40*f)
    bassn(bs,T(b),c[0],SPB(b)*1.5,hg(0.32*f))
    motif(vn,b,2,'violin',0.16*f,seed=i); motif(sx,b,1,'sax',0.16*f,seed=i); motif(gt,b,0,'gtr',0.13*f,seed=i)
    horn(cho,T(b),c[2]+12,SPB(b)*1.4,hg(0.07*f))
    villa(b,hg(1.0*f),arc=1.0,busy=True,climax=True)
    chant(vx,b,[(0,.5,'F#4','a','h'),(.5,.5,'C#5','o','y'),(1.0,1.0,'F#5','a','')],g=0.09*f,n=4,style='shout',seedbase=600+i)
# TAG: one hard hit + held chord
b=bar_at('TAG',0)
P.K(b,0,1.2); P.S(b,0,1.0,'center'); P.CR(b,0,0.85,size=1.3); P.TM(b,0,0.9,80); P.TM(b+0.25,2,0.9,98)
fuzzbass(bs,T(b),nn('F#1'),SPB(b)*3.5,0.30)
for m in [nn('F#3'),nn('A3'),nn('C#4'),nn('F#4')]: mellotron(cho,T(b),m,SPB(b)*3.4,0.10,'choir',seed=int(m))
shriek(vx,T(b+0.3),nn('F#5'),1.2,0.10)

P.apply_chokes()
DRUMS=mix_kit(P.bus,room_amount=0.24,oh_amount=0.9,lpf=9800)

# noise bed faint
noise_sw(fx,0,T(END),0.006,True,70,1400)

STEMS=[(vn,-0.40,0.66,0.40,0.0),(sx,0.30,0.58,0.40,8.0),(gt,0.55,0.50,0.45,0.0),
       (cho,0.10,0.70,0.22,0.0),(fx,0.0,0.9,0.0,0.0)]
MAPT=[(n,a,b_,(6.0 if n in('ST','TAG') else 2.6)) for n,a,b_ in MAP]
run(NAME, lambda voc: mixdown(NAME,vx,STEMS,DRUMS,bs,MAPT,vocals=voc,
    wet=0.20,decay=1.7,wide=1.4,drum_gain=0.78,bass_gain=0.88,crush_amt=0.20,
    rms_target=0.172), MAPT)