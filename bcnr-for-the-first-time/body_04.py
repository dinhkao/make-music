# ============================================================ BAI 4: STATIC BLOOM
# Model: Black Country, New Road - "Sunglasses" (For the first time, 2021).
# Sunglasses technique (from research + tab):
#   - DROP-D low D pedal riff. Transposed here to a low C pedal.
#   - verse riff = chromatic lower-neighbour melody over the pedal + M7 colour.
#   - sax/violin minor-2nd clash (F / F#) => here  F / Gb  on top of C pedal.
#   - builds by register, density, articulation, vocal intensity NOT chord motion.
#   - the climax is a TWO-CHORD AD-INFINITUM blowout with a tritone colour
#     (the album version piles the same 2 chords forever). Here: C  <->  Gb
#     (tritone, the "two chords forever" power of the original).
#   - album version added a distorted intro solo.
# Palette: crunch/leadgtr (gtr), fuzz=fzbass, sax=hbone, violin=bowed, Kit Villa.
BAR=4.0
NAME="04-static-bloom"
SECS=[('SL',8),('VS',14),('SX',14),('BL',22),('ST',2),('FN',8),('TG',2)]
S={}; _b=0.0
for _n,_c in SECS: S[_n]=_b; _b+=_c*BAR
END=_b
configure(117,117,END+3)
MAP=[(n,S[n],S[n]+c*BAR) for n,c in SECS]
def bar_at(sec,i): return S[sec]+i*BAR
print(NAME,int(END/BAR),"bars ->",round(TOTAL,1),"s")
K=Kit(seed=4210); P=Performer(K,T,SPB,TOTAL,seed=14,style='indie'); P.hum=0.58
sl=buf(); vx=buf(); bs=buf(); fx=buf(); ch=buf(); gt=buf()
PC=nn('C2')              # low pedal (drop-C feel)
def villa(b,lvl=0.8,arc=1.0,busy=False,climax=False,ride=False):
    for s in range(16):
        acc=0.70 if s%4==0 else 0.40
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
        P.S(b+1,4,0.66*lvl,'center',arc); P.S(b+3,12,0.70*lvl,'center',arc)
        if busy:
            for gp in (0.75,2.5): P.S(b+gp,int(gp*4)%16,0.26*lvl,'ghost',arc)
def pedalriff(b,i,g,drive=3.5):
    # low C pedal drone + chromatic upper-neighbour: C.. Gb F E .. C  with M7 B colour
    R=np.random.default_rng(i*7+4)
    crunch(sl,T(b),PC,SPB(b)*3.7,hg(0.10*g),drive=2.8,seed=i)
    mel=[(nn('C4'),0.0),(nn('Eb4'),1.0),(nn('E4'),1.5),(nn('F4'),2.0),(nn('Gb4'),2.5),(nn('B4'),3.0)]
    for n_,o in mel:
        crunch(sl,T(b)+o*SPB(b)+float(R.normal(0,0.010)),n_,hd(SPB(b)*(0.4 if o in(1.5,2.5) else 0.7)),hg(g*0.06),drive=drive,seed=int(o*7)+i)
# SL intro solo (distorted) over pedal - the album-version addition
for i in range(8):
    b=bar_at('SL',i); f=0.5+0.07*i
    fzbass(bs,T(b),PC,SPB(b)*3.6,hg(0.16*f),seed=i)
    pedalriff(b,i,f*0.8,drive=4.5)
    fuzz_improv_note=nn('G4')
    leadgtr(gt,T(b)+0.5*BAR,fuzz_improv_note+i*3%12,SPB(b)*2.2,hg(0.05*f),bend=0.5 if i%3==0 else 0.0,seed=i)
    villa(b,hg(0.42*f),arc=0.5+0.03*i,busy=(i>=5))
# VS verse riff + m2 sax/violin clash (F/Gb)
for i in range(14):
    b=bar_at('VS',i); f=1+0.025*i
    fzbass(bs,T(b),PC,SPB(b)*3.5,hg(0.24*f),seed=i)
    pedalriff(b,i,f,drive=3.6)
    # m2 clash: F4 + Gb4 sustained (sax vs violin) over C pedal
    bowed(ch,T(b),nn('F4'),SPB(b)*2.4,hg(0.09*f),det=float(np.random.default_rng(i).normal(0,8)),seed=i)
    hbone(ch,T(b)+0.05,nn('Gb4'),SPB(b)*2.4,hg(0.085*f),growl=0.4,seed=i)
    villa(b,hg(0.62*f),arc=0.55+0.02*i,busy=(i>=7))
    line(vx,b,[(0,.5,'C4','a','h'),(.5,.5,'Eb4','o',''),(1,.5,'E4','a','r'),(1.5,1.0,'Gb4','o',''),
               (2,.5,'F4','a',''),(2.5,0.5,'E4','o','t'),(3,1.0,'C4','a','')],
         g=0.12*f,style='deadpan',breath=0.28,seedbase=i*73)
# SX build: dist gtr reinforces pedal riff, sax turns, density up
for i in range(14):
    b=bar_at('SX',i); f=1+0.04*i
    fzbass(bs,T(b),PC,SPB(b)*3.4,hg(0.28*f),seed=i)
    pedalriff(b,i,f,drive=5.0)
    crunch(gt,T(b)+0.5*BAR,nn('C4')+12,hd(SPB(b)*0.6),hg(0.07*f),drive=7.2,seed=i)
    bowed(ch,T(b),nn('Gb4'),SPB(b)*1.8,hg(0.10*f),det=float(np.random.default_rng(i+9).normal(0,9)),seed=i+9)
    hbone(ch,T(b)+0.6*BAR,nn('B4'),SPB(b)*1.8,hg(0.11*f),growl=0.6,seed=i)
    villa(b,hg(0.78*f),arc=0.82+0.018*i,busy=True,ride=(i%2==1))
    if i==13:
        P.fill(b+1.5,2.5,'tom',1.1,next_crash_beat=S['BL'])
# BL 2-chord ad-infinitum blowout: C <-> Gb (tritone), relentless, maximal, false stop
for i in range(22):
    b=bar_at('BL',i); f=min(1.55,1+0.05*i)
    # 2-chord: C / Gb (the tritone pair)
    c=PC if i%2==0 else nn('Gb2')
    fzbass(bs,T(b),c,SPB(b)*3.4,hg(0.26*f),seed=i,bite=1.2)
    crunch(gt,T(b),(nn('C3') if i%2==0 else nn('Gb3')),SPB(b)*3.3,hg(0.10*f),drive=8.6,seed=i)
    crunch(gt,T(b)+0.5*BAR,(nn('B3') if i%2==0 else nn('Db4')),hd(SPB(b)*0.4),hg(0.075*f),drive=9.2,seed=i+1)
    pedalriff(b,i,f*0.7,drive=6.0)
    bowed(ch,T(b),nn('F4') if i%2==0 else nn('Gb4'),SPB(b)*3.0,hg(0.10*f),seed=i)
    hbone(ch,T(b)+0.2*BAR,nn('B4') if i%2==0 else nn('Db5'),SPB(b)*2.6,hg(0.12*f),growl=0.7,seed=i)
    villa(b,hg(0.96*f),arc=1.0,busy=True,climax=True,ride=True)
    chant(vx,b,[(0,.5,'C4','a','h'),(.5,.5,'Gb4','o','y'),(1,1.0,'C4','a','')],g=0.10*f,n=5,style='shout',seedbase=700+i)
    if i==21: P.fill(b+2.5,1.5,'burst32',1.1,next_crash_beat=S['ST'])
b=bar_at('ST',0)
P.K(b,0,1.1); P.S(b,0,1.0,'rim'); P.CR(b,0,0.85,size=1.3)
bowed(ch,T(b),nn('C5'),5.0,0.05,seed=1); fzbass(bs,T(b),PC,5.0,0.10)
# FN final reprise: pedal riff, deadpan -> shout, dead stop
for i in range(8):
    b=bar_at('FN',i); f=1+0.04*i
    fzbass(bs,T(b),PC,SPB(b)*3.4,hg(0.22*f),seed=i)
    pedalriff(b,i,f,drive=4.0)
    villa(b,hg(0.7+0.05*i*f),arc=0.9,busy=True,climax=(i>=5),ride=(i>=5))
    line(vx,b,[(0,.5,'C4','a','h'),(.5,.5,'Gb4','o',''),(1,1.0,'C4','a',''),(2,.5,'Eb4','o','w')],
         g=(0.10+0.01*i)*f,style=('deadpan' if i<4 else 'shout'),oct8=(0 if i<4 else 0.3),breath=0.28,seedbase=900+i)
# TG: hit + held C pedal, never resolves (Sunglasses ends on the riff)
b=bar_at('TG',0)
P.K(b,0,1.2); P.S(b,0,1.0,'center'); P.CR(b,0,0.9,size=1.4); P.TM(b,0,1.0,80)
fzbass(bs,T(b),PC,SPB(b)*3.6,0.30)
for m in (nn('C3'),nn('C4'),nn('Gb4'),nn('B4')): crunch(gt,T(b),m,SPB(b)*3.5,hg(0.08),drive=8.5,seed=int(m))
shriek(vx,T(b+0.3),nn('C5'),1.0,0.10)
P.apply_chokes()
DRUMS=mix_kit(P.bus,room_amount=0.22,oh_amount=0.92,lpf=9800)
noise_sw(fx,0,T(END),0.008,True,70,1500)
STEMS=[(sl,-0.40,0.62,0.40,0.0),(gt,0.50,0.60,0.40,7.0),(ch,0.10,0.60,0.40,0.0),(fx,0.0,0.9,0.0,0.0)]
MAPT=[(n,a,b_,(6.5 if n in('SL','ST','TG') else 2.6)) for n,a,b_ in MAP]
run(NAME, lambda voc: mixdown(NAME,vx,STEMS,DRUMS,bs,MAPT,vocals=voc,
    wet=0.18,decay=1.5,wide=1.5,drum_gain=0.80,bass_gain=0.92,crush_amt=0.28,
    rms_target=0.182), MAPT)