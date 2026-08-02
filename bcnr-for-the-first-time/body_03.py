# ============================================================ BAI 3: HALF A SMILE
# Model: Black Country, New Road - "Science Fair" (For the first time, 2021).
# Science Fair technique (from research):
#   - anxious CIRCLING on a tritone dyad (C# + G = C#mib5) - a dissonant
#     unresolved shape that never lets you relax.
#   - intro = improvised FUZZ noise, abrasive & uncontrolled; accuracy matters
#     less than destructive tone.
#   - the song builds by ARTICULATION, register & density - NOT by chord changes.
#     it just circles the tritone harder and louder.
# New key => transpose the tritone dyad to  B + F  (B + its b5 = F), Bmib5 feel.
# Palette: fuzz = crunch/leadgtr (drive high) + fuzzbass; sax = hbone; drums = Kit.
BAR=4.0
NAME="03-half-a-smile"
SECS=[('FZ',6),('VS',16),('BD',16),('BL',20),('ST',2),('FN',12),('TG',2)]
S={}; _b=0.0
for _n,_c in SECS: S[_n]=_b; _b+=_c*BAR
END=_b
configure(128,128,END+3)
MAP=[(n,S[n],S[n]+c*BAR) for n,c in SECS]
def bar_at(sec,i): return S[sec]+i*BAR
print(NAME,int(END/BAR),"bars ->",round(TOTAL,1),"s")
K=Kit(seed=3210); P=Performer(K,T,SPB,TOTAL,seed=13,style='indie'); P.hum=0.6
sl=buf(); vx=buf(); bs=buf(); fx=buf(); ch=buf(); gt=buf()
# tritone dyad B+F (B is root, F is b5). we CIRCLE it; never resolve.
DB=nn('B2'); DF=nn('F2')
DN=[nn('B3'),nn('F4')]
def villa(b,lvl=0.78,arc=1.0,busy=False,climax=False,ride=False):
    for s in range(16):
        acc=0.72 if s%4==0 else 0.42
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
        P.S(b+1,4,0.66*lvl,'center',arc); P.S(b+3,12,0.70*lvl,'center',arc)
        if busy:
            for gp in (0.75,2.5): P.S(b+gp,int(gp*4)%16,0.26*lvl,'ghost',arc)
def fuzz_improv(b,i,g):
    # like Science Fair: aggressive improvised fuzz over the dyad
    R=np.random.default_rng(i*13+7)
    for k_ in range(5):
        n_=DN[R.integers(0,2)]+(0 if R.random()<0.6 else 12)
        tt=T(b)+R.uniform(0,3.6)*SPB(b)
        d_=R.uniform(0.06,0.32)
        drive=R.uniform(5,9)
        crunch(gt,tt,n_,hd(SPB(b)*d_),hg(g),drive=drive if drive<8.9 else 8.5,seed=k_+i*5)
    # also a low feedback-y fuzz swell
    if i%3==2:
        x=ks(DB,SPB(b)*3.0,0.9920,0.42,seed=i*7).astype(np.float64)
        x=np.tanh(x*9.0); bq,aq=sg.butter(2,[140/(SR/2),1600/(SR/2)],'band'); x=sg.lfilter(bq,aq,x)
        put(gt,T(b),x*hg(g*0.5),1.0)
def dyad_circle(b,i,g,glvl=0.10):
    # the iconic circling tritone: B . F . B . F  - quarter notes, relentless
    R=np.random.default_rng(i*23+3)
    js=2 if i>=0 else 1
    for k_ in range(4):
        n_=DN[k_%2]
        crunch(sl,T(b)+k_*SPB(b)+float(R.normal(0,0.008)),n_,hd(SPB(b)*0.5),hg(g),drive=6.5,seed=k_+i*4)
    fzbass(bs,T(b),DB if i%2==0 else DF,SPB(b)*3.6,hg(0.22*glvl),seed=i,bite=1.1)
# FZ 0:00-0:18 fuzz intro (improvised, abrasive) + faint drums
for i in range(6):
    b=bar_at('FZ',i); f=0.5+0.08*i
    fuzz_improv(b,i,0.06*f)
    fzbass(bs,T(b),DB,SPB(b)*3.6,hg(0.10*f),seed=i)
    villa(b,hg(0.4*f),arc=0.5+0.04*i)
# VS 0:18-1:06 verse: tritone circle + deadpan vocal, very sparse under
for i in range(16):
    b=bar_at('VS',i); f=1+0.025*i
    dyad_circle(b,i,hg(0.10*f),glvl=f)
    hbone(ch,T(b)+0.5*BAR,DN[1]+7,SPB(b)*2.0,hg(0.07*f),growl=0.4,seed=i)  # sax answering
    villa(b,hg(0.62*f),arc=0.55+0.02*i,busy=(i>=8))
    line(vx,b,[(0,.5,'B3','a','h'),(.5,.5,'F4','o',''),(1,.5,'B3','a','n'),(1.5,1.5,'F4','o','t')],
         g=0.13*f,style='deadpan',breath=0.30,seedbase=i*73)
# BD 1:06-1:44 build: + dist guitar doubling dyad, density up
for i in range(16):
    b=bar_at('BD',i); f=1+0.04*i
    dyad_circle(b,i,hg(0.11*f),glvl=f)
    # dist gtr in higher octave reinforcing
    crunch(gt,T(b),DN[1]+12,SPB(b)*3.6,hg(0.06*f),drive=7.5,seed=i)
    hbone(ch,T(b)+0.25*BAR,DN[int(i/4)%2]+12,SPB(b)*2.4,hg(0.09*f),growl=0.55,seed=i)
    villa(b,hg(0.75*f),arc=0.8+0.02*i,busy=True,ride=(i%2==1))
    _R=np.random.default_rng(i*5+1)
    for v in range(4):
        say(vx,T(b)+0.5*BAR+float(_R.normal(0,0.02)),DN[0]+12+(12 if v==3 else 0),SPB(b)*2.6,'a','',0.07*f/2,'shout',0.3,seed=v*9+i,det=float(_R.normal(0,16)))
    if i==15: villa(b,hg(0.85*f),arc=1.0,climax=True,ride=True)
# BL 1:44-2:21 blowout: 2-chord ad-infinitum on the tritone, maximal, stopped
for i in range(20):
    b=bar_at('BL',i); f=min(1.6,1+0.055*i)
    # 2-chord: B (power) <-> F (b5), relentless ad-infinitum
    c=[DB,DF][i%2]
    fzbass(bs,T(b),c,SPB(b)*3.4,hg(0.26*f),seed=i,bite=1.3)
    crunch(gt,T(b),DN[i%2],SPB(b)*3.4,hg(0.10*f),drive=8.5,seed=i)
    crunch(gt,T(b)+0.5*BAR,DN[(i+1)%2]+12,hd(SPB(b)*0.4),hg(0.08*f),drive=9.0,seed=i+1)
    hbone(ch,T(b),DN[i%2]+12,SPB(b)*3.2,hg(0.13*f),growl=0.7,seed=i)
    dyad_circle(b,i,hg(0.12*f),glvl=f)
    villa(b,hg(0.95*f),arc=1.0,busy=True,climax=True,ride=True)
    chant(vx,b,[(0,.5,'B3','a','h'),(.5,.5,'F4','o','y'),(1,1.0,'B3','a','')],g=0.10*f,n=5,style='shout',seedbase=600+i)
    if i==19: P.fill(b+2.7,1.3,'burst32',1.1,next_crash_beat=S['ST'])
# ST false stop
b=bar_at('ST',0)
P.K(b,0,1.1); P.S(b,0,1.0,'rim'); P.CR(b,0,0.85,size=1.3)
bowed(ch,T(b),nn('B4'),5.0,0.06,seed=1)
# FN 2:21-2:44 final reprise, slower feel, deadpan to shout, stop dead
for i in range(12):
    b=bar_at('FN',i); f=1.0+0.03*i
    dyad_circle(b,i,hg(0.09*f),glvl=f)
    fzbass(bs,T(b),DB if i%2==0 else DF,SPB(b)*3.4,hg(0.20*f),seed=i)
    villa(b,hg(0.7+0.04*i*f),arc=0.85,busy=(i>=6),climax=(i>=9),ride=(i>=9))
    style='deadpan' if i<6 else 'shout'
    line(vx,b,[(0,.5,'B3','a','h'),(.5,.5,'F4','o',''),(1,1.0,'B3','a',''),(2,.5,'F4','o','w')],
         g=(0.11+0.01*i)*f,style=style,oct8=(0 if i<6 else 0.3),breath=0.28,seedbase=800+i)
# TG: hit + held tritone, no resolution
b=bar_at('TG',0)
P.K(b,0,1.2); P.S(b,0,1.0,'center'); P.CR(b,0,0.9,size=1.4); P.TM(b,0,1.0,80)
fzbass(bs,T(b),DB,SPB(b)*3.5,0.30)
for m in (DB+12,DF+12): crunch(gt,T(b),m,SPB(b)*3.5,0.10,drive=9.0,seed=int(m))
hbone(ch,T(b),DN[0]+12,SPB(b)*3.5,0.13,growl=0.8,seed=99)
shriek(vx,T(b+0.3),nn('B5'),1.0,0.10)
P.apply_chokes()
DRUMS=mix_kit(P.bus,room_amount=0.22,oh_amount=0.92,lpf=9800)
noise_sw(fx,0,T(END),0.008,True,70,1500)
STEMS=[(sl,-0.40,0.62,0.42,0.0),(gt,0.5,0.60,0.42,7.0),(ch,0.10,0.60,0.40,0.0),(fx,0.0,0.9,0.0,0.0)]
MAPT=[(n,a,b_,(6.5 if n in('FZ','ST','TG') else 2.6)) for n,a,b_ in MAP]
run(NAME, lambda voc: mixdown(NAME,vx,STEMS,DRUMS,bs,MAPT,vocals=voc,
    wet=0.18,decay=1.4,wide=1.5,drum_gain=0.80,bass_gain=0.90,crush_amt=0.26,
    rms_target=0.180), MAPT)