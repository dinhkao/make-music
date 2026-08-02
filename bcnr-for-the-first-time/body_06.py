# ============================================================ BAI 6: OPAL
# Model: Black Country, New Road - "Opus" (For the first time, 2021).
# Opus technique (from research + tab, Drop D, A minor):
#   - one A PEDAL + a Phrygian/klezmer turn  A-Bb-A  (the 7h8p7 hammer-on)
#   - 4/4 verse -> 6/8 VARIATION slower (same idea, triplet feel), lots of
#     improv/glissando/vibrato.
#   - chromatic runs (Bb-A-G#-G-F#) climb during the build.
#   - HORNS / brass stabs guide the form changes.
# Transposed to D pedal (D Phrygian dominant): D-Eb-D turn, chromatic run Eb-D-C#-C-B.
# Palette: horn/bone (brass), crunch (gtr), bassn/subbass, mellotron (choir), Kit Villa.
BAR=4.0
NAME="06-opal"
SECS=[('IN',8),('VS',16),('BR',12),('S68',16),('RUN',14),('OUT',6),('TG',2)]
S={}; _b=0.0
for _n,_c in SECS: S[_n]=_b; _b+=_c*BAR
END=_b
configure(140,140,END+3)
MAP=[(n,S[n],S[n]+c*BAR) for n,c in SECS]
def bar_at(sec,i): return S[sec]+i*BAR
print(NAME,int(END/BAR),"bars ->",round(TOTAL,1),"s")
K=Kit(seed=6210); P=Performer(K,T,SPB,TOTAL,seed=16,style='indie'); P.hum=0.6
sl=buf(); vx=buf(); bs=buf(); fx=buf(); ch=buf(); gt=buf()
PD=nn('D2')                                  # D pedal
TURN=[nn('D4'),nn('Eb4'),nn('D4')]            # D-Eb-D klezmer turn (the 7h8p7 moved to D)
RUN=[nn('Eb4'),nn('D4'),nn('C#4'),nn('C4'),nn('B3')]
def villa(b,lvl=0.78,arc=1.0,busy=False,climax=False,ride=False,sixeight=False):
    if sixeight:
        # 6/8 feel: 12 eighths, ride bell on 1 & 7 (the two dotted quarters), snare on 4 & 10, hats shuffle eighths
        sp8=SPB(b)/2.0
        P.RD(b+0.0,0,0.45*lvl,bell=True,arc=arc); P.RD(b+1.5,6,0.36*lvl,bell=True,arc=arc)
        P.S(b+0.5,2,0.6*lvl,'center',arc); P.S(b+2.0,8,0.64*lvl,'center',arc)
        P.K(b+0.0,0,0.7*lvl,arc); P.K(b+1.5,6,0.55*lvl,arc)
        for k_ in range(12):
            P.H(b+k_*0.5,k_*2%16,0.26*lvl,o=0.0,art='tip',arc=arc)
        if climax:
            for gp in (0.25,1.0,1.75,2.5): P.S(b+gp,int(gp*4)%16,0.28*lvl,'ghost',arc)
            P.CL(b+0.5,2,0.5*lvl,arc); P.CL(b+2.0,8,0.55*lvl,arc)
        return
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
        P.S(b+1,4,0.62*lvl,'center',arc); P.S(b+3,12,0.66*lvl,'center',arc)
        if busy:
            for gp in (0.75,2.5): P.S(b+gp,int(gp*4)%16,0.26*lvl,'ghost',arc)
def droneriff(b,i,g,drive=3.5):
    R=np.random.default_rng(i*9+2)
    fzbass(bs,T(b),PD,SPB(b)*3.6,hg(0.24),seed=i)
    crunch(sl,T(b),PD,SPB(b)*3.6,hg(0.10*g),drive=2.6,seed=i)
    # the klezmer turn D-Eb-D placed 3 times + ornaments (the "lots of improv")
    for k_ in range(3):
        base=0.0+k_*1.2
        for j,n_ in enumerate(TURN):
            crunch(sl,T(b)+(base+j*0.18)*SPB(b)+float(R.normal(0,0.010)),n_+(12 if k_==2 else 0),hd(SPB(b)*0.18),hg(0.07*g),drive=drive,seed=i*5+k_*3+j)
        # a little gliss up at end of each turn
        leadgtr(gt,T(b)+(base+0.5)*SPB(b),nn('D4')+12+k_*3,hd(SPB(b)*0.3),hg(0.05*g),bend=0.4,seed=i*7+k_)
def horn_stab(b,i,note,g):
    R=np.random.default_rng(i*4+1)
    bone(ch,T(b),note,SPB(b)*0.9,hg(g),growl=0.5,seed=i,det=float(R.normal(0,8)))
    horn(ch,T(b),note-12,SPB(b)*0.9,hg(g*0.7))
# IN intro: D pedal + turn, horns, sparse
for i in range(8):
    b=bar_at('IN',i); f=0.5+0.06*i
    droneriff(b,i,0.7*f)
    mellotron(ch,T(b),nn('D4'),SPB(b)*3.6,hg(0.04*f),'choir',seed=i)
    villa(b,hg(0.42*f),arc=0.55+0.03*i,busy=(i>=5))
    horn_stab(b,i,nn('A4'),0.05*f)
# VS verse: turn 3x per bar, sax/bone counter, deadpan
for i in range(16):
    b=bar_at('VS',i); f=1+0.025*i
    droneriff(b,i,f)
    mellotron(ch,T(b),nn('D4'),SPB(b)*3.6,hg(0.05*f),'choir',seed=i+8)
    hbone(ch,T(b)+0.5*BAR,nn('A4'),SPB(b)*1.6,hg(0.09*f),growl=0.45,seed=i)
    villa(b,hg(0.62*f),arc=0.55+0.02*i,busy=(i>=8),ride=(i%2==1 and i>=8))
    line(vx,b,[(0,.5,'D4','a','h'),(.5,.5,'Eb4','o',''),(1,.5,'D4','a','t'),(1.5,1.0,'A4','o','')],
         g=0.12*f,style='deadpan',breath=0.28,seedbase=i*73)
    if i==15: P.fill(b+2.5,1.5,'stutter',0.9,next_crash_beat=S['BR'])
# BR bridge: big 4/4 with horns pump, dist gtr
for i in range(12):
    b=bar_at('BR',i); f=1+0.05*i
    droneriff(b,i,f,drive=5.5)
    mellotron(ch,T(b),nn('D4'),SPB(b)*3.6,hg(0.07*f),'choir',seed=i+24)
    horn_stab(b,i,nn('A4')+(12 if i%2==1 else 0),0.07*f)
    crunch(gt,T(b),nn('D3'),SPB(b)*3.6,hg(0.07*f),drive=7.0,seed=i)
    villa(b,hg(0.80*f),arc=0.82+0.015*i,busy=True,ride=True)
    if i==11: P.fill(b+2.6,1.4,'tom',1.1,next_crash_beat=S['S68'])
# S68 6/8 variation: same turn slower triplet feel, chromatic run begins
for i in range(16):
    b=bar_at('S68',i); f=1+0.04*i
    fzbass(bs,T(b),PD,SPB(b)*3.6,hg(0.24*f),seed=i)
    mellotron(ch,T(b),nn('D4'),SPB(b)*3.6,hg(0.06*f),'choir',seed=i+40)
    # turn in 6/8: D . Eb . D spread as triplets
    R=np.random.default_rng(i*3+7)
    for j,n_ in enumerate(TURN):
        crunch(sl,T(b)+j*SPB(b)*0.66+float(R.normal(0,0.012)),n_+(12 if j==2 else 0),hd(SPB(b)*0.5),hg(0.07*f),drive=4.0,seed=i*4+j)
    note=RUN[i%len(RUN)]
    hbone(ch,T(b)+0.5*BAR,note+12,SPB(b)*1.5,hg(0.09*f),growl=0.5,seed=i)
    villa(b,hg(0.66*f),arc=0.72+0.016*i,busy=True,sixeight=True,climax=(i>=12),ride=(i>=12))
    line(vx,b,[(0,1.0,'D4','a','h'),(1.0,1.0,'Eb4','o','e'),(2.0,2.0,'D4','a','y')],g=0.11*f,style='deadpan',breath=0.28,seedbase=300+i)
# RUN chromatic climb: Eb-D-C#-C-B climbing across the band, full + 6/8
for i in range(14):
    b=bar_at('RUN',i); f=min(1.5,1+0.06*i)
    fzbass(bs,T(b),PD,SPB(b)*3.4,hg(0.28*f),seed=i,bite=1.2)
    mellotron(ch,T(b),nn('D4'),SPB(b)*3.6,hg(0.08*f),'choir',seed=i+60)
    r=RUN[(i+int(i/2))%len(RUN)]
    # whole band climbs the run together across octaves
    R=np.random.default_rng(i*2+5)
    for o,gg in [(0,0.08*f),(12,0.10*f),(-12,0.06*f)]:
        bone(ch,T(b)+float(R.normal(0,0.01)),r+o,SPB(b)*0.5,hg(gg),growl=0.6,seed=i+o)
    crunch(sl,T(b),r,SPB(b)*0.6,hg(0.07*f),drive=6.5,seed=i)
    crunch(gt,T(b)+0.5*BAR,nn('D3'),SPB(b)*1.5,hg(0.08*f),drive=8.5,seed=i)
    villa(b,hg(0.92*f),arc=0.96+0.003*i,busy=True,sixeight=True,climax=True,ride=True)
    chant(vx,b,[(0,.5,r+12,'a','h'),(.5,.5,'D4','o','y'),(1,1.0,'D4','a','')],g=0.09*f,n=4,style='shout',seedbase=500+i)
    if i==13: P.fill(b+2.5,1.5,'burst32',1.1,next_crash_beat=S['OUT'])
# OUT resolve to D (the "Ends with intro again" feel), gentle, held
for i in range(6):
    b=bar_at('OUT',i); f=0.7-0.07*i
    droneriff(b,i,f,drive=3.0)
    mellotron(ch,T(b),nn('D4'),SPB(b)*3.6,hg(0.06*f),'choir',seed=i+80)
    villa(b,hg(0.5*f),arc=0.6,sixeight=True)
# TG: held D pedal + final turn
b=bar_at('TG',0)
P.K(b,0,1.1); P.S(b,0,1.0,'center'); P.CR(b,0,0.85,size=1.3)
fzbass(bs,T(b),PD,SPB(b)*3.6,0.30)
for n_ in TURN: crunch(gt,T(b),n_,SPB(b)*3.5,hg(0.08),drive=5.0,seed=int(n_))
bone(ch,T(b),nn('A4'),SPB(b)*3.5,0.12,growl=0.8,seed=99)
shriek(vx,T(b+0.3),nn('A5'),1.0,0.10)
P.apply_chokes()
DRUMS=mix_kit(P.bus,room_amount=0.22,oh_amount=0.9,lpf=9700)
noise_sw(fx,0,T(END),0.007,True,70,1500)
STEMS=[(sl,-0.42,0.62,0.40,0.0),(gt,0.5,0.58,0.40,7.0),(ch,0.12,0.62,0.26,0.0),(fx,0.0,0.9,0.0,0.0)]
MAPT=[(n,a,b_,(6.5 if n in('IN','OUT','TG') else 2.6)) for n,a,b_ in MAP]
run(NAME, lambda voc: mixdown(NAME,vx,STEMS,DRUMS,bs,MAPT,vocals=voc,
    wet=0.19,decay=1.5,wide=1.45,drum_gain=0.80,bass_gain=0.90,crush_amt=0.24,
    rms_target=0.178), MAPT)