# ============================================================ BAI 5: GLASS AVENUE
# Model: Black Country, New Road - "Track X" (For the first time, 2021).
# Track X technique (from research):
#   - the album's "quietest & most considered" track - acid-folk ballad.
#   - reworked from Sunglasses but slowed & softened.
#   - held, suspended tones; the wistful feel comes from SUSPENSION that never
#     resolves (Gsus4, Dsus2) rather than happy major resolution.
#   - brushed / restrained drums.
# Key D major, very slow ~76 BPM. ny guitar + bowed violin + taeckpiano +
# mellotron-choir swell + fingerbass. Never explode. Build only from warmth.
BAR=4.0
NAME="05-glass-avenue"
SECS=[('IN',5),('V1',10),('MID',10),('SW',10),('V2',8),('OUT',4),('TG',2)]
S={}; _b=0.0
for _n,_c in SECS: S[_n]=_b; _b+=_c*BAR
END=_b
configure(76,76,END+4)
MAP=[(n,S[n],S[n]+c*BAR) for n,c in SECS]
def bar_at(sec,i): return S[sec]+i*BAR
print(NAME,int(END/BAR),"bars ->",round(TOTAL,1),"s")
K=Kit(seed=5210); P=Performer(K,T,SPB,TOTAL,seed=15,style='indie'); P.hum=0.74
sl=buf(); vx=buf(); bs=buf(); fx=buf(); ch=buf(); gt=buf(); kp=buf()
# suspended chords (D area): Dsus2 Asus4 Gmaj7/D Em7 -> never cadence to plain D
Dsus2=[nn('D3'),nn('E3'),nn('A3')]
Asus4=[nn('A2'),nn('D3'),nn('E3')]
Gmj7 =[nn('G2'),nn('B3'),nn('D4'),nn('F#4')]
Em7  =[nn('E2'),nn('G3'),nn('B3'),nn('D4')]
PROG=[Dsus2,Asus4,Gmj7,Em7]
def vbrush(b,lvl=0.42,arc=1.0,ride=True):
    # brushed kit: ride sweet 1&3, soft cross-stick 2&4, brushy 16th hats, soft kick 1&3
    if ride:
        P.RD(b,0,0.40*lvl,bell=False,arc=arc); P.RD(b+2.0,8,0.32*lvl,bell=False,arc=arc)
    P.S(b+1.0,4,0.42*lvl,'cross',arc); P.S(b+3.0,12,0.42*lvl,'cross',arc)
    for s in range(16):
        P.H(b+s*0.25,s,0.26*lvl,o=0.0,art='tip',arc=arc)
    P.K(b,0,0.46*lvl,arc); P.K(b+2.0,8,0.40*lvl,arc)
# nylon fingerpicked pattern over the sus chord (BCNR acid-folk feel)
def nylonpick(b,i,c,g):
    R=np.random.default_rng(i*11+5)
    pat=[(0,c[0]+12),(0.5,c[1]+12),(1.0,c[2]+12),(1.5,c[1]+12),(2.0,c[0]+19),(2.5,c[-1]+12),(3.0,c[1]+12),(3.5,c[2]+12)]
    for o,n_ in pat:
        nylon(gt,T(b)+o*SPB(b)+float(R.normal(0,0.012)),n_,hd(SPB(b)*0.8),hg(g),seed=int(o*9)+i)
# IN 0:00-0:19 hold Dsus2, bowed drone, very soft
for i in range(5):
    b=bar_at('IN',i); c=PROG[0]; f=0.5+0.06*i
    mellotron(ch,T(b),c[2],SPB(b)*3.7,hg(0.04*f),'choir',seed=i)
    subbass(bs,T(b),c[0]-12,SPB(b)*3.7,0.16*f)
    bowed(sl,T(b),c[2]+12,SPB(b)*3.7,hg(0.06*f),det=float(np.random.default_rng(i).normal(0,7)),seed=i)
    tackpiano(kp,T(b)+0.4*BAR,c[1],SPB(b)*2.6,hg(0.05*f),seed=i)
    vbrush(b,hg(0.32*f),arc=0.5+0.02*i)
# V1 0:19-0:57 nylon + tackpiano, sus progressions slowly moving
for i in range(10):
    b=bar_at('V1',i); c=PROG[i%4]; f=1+0.02*i
    mellotron(ch,T(b),c[-1],SPB(b)*3.6,hg(0.05*f),'choir',seed=i+6)
    fingerbass(bs,T(b),c[0],SPB(b)*3.6,hg(0.20*f),seed=i)
    nylonpick(b,i,c,0.08*f)
    tackpiano(kp,T(b),c[1],SPB(b)*3.6,hg(0.06*f),seed=i)
    bowed(sl,T(b)+0.6*BAR,c[-1]+12,SPB(b)*2.4,hg(0.085*f),det=float(np.random.default_rng(i+2).normal(0,8)),seed=i+2)
    vbrush(b,hg(0.42*f),arc=0.7+0.015*i)
    line(vx,b,[(0,1.0,c[2],'a','h'),(1.0,1.0,c[-1],'o',''),(2.0,1.0,c[2],'a','y'),(3.0,1.0,c[1],'o','')],
         g=0.10*f,style='croon',breath=0.28,seedbase=i*67)
# MID 0:57-1:35 add violin counter, warm
for i in range(10):
    b=bar_at('MID',i); c=PROG[i%4]; f=1+0.03*i
    mellotron(ch,T(b),c[-1],SPB(b)*3.6,hg(0.06*f),'choir',seed=i+18)
    fingerbass(bs,T(b),c[0],SPB(b)*3.6,hg(0.22*f),seed=i)
    nylonpick(b,i,c,0.09*f)
    tackpiano(kp,T(b),c[1],SPB(b)*3.6,hg(0.07*f),seed=i)
    bowed(sl,T(b),c[-1]+12,SPB(b)*3.0,hg(0.11*f),det=float(np.random.default_rng(i+3).normal(0,8)),seed=i+3)
    bowed(sl,T(b)+0.5*BAR,c[-1]+19,SPB(b)*2.0,hg(0.08*f),det=0,seed=i+33)  # counter line a sixth higher
    vbrush(b,hg(0.48*f),arc=0.8+0.012*i,ride=True)
    line(vx,b,[(0,1.0,c[2],'a','o'),(1.0,1.0,c[-1],'o','v'),(2.0,1.5,c[2],'a','e'),(3.0,0.5,c[1],'o','r')],
         g=0.118*f,style='croon',oct8=0.0,breath=0.27,seedbase=200+i)
# SW 1:35-2:13 warm swell (mellotron swells but never explodes) - the "considered" lift
for i in range(10):
    b=bar_at('SW',i); c=PROG[i%4]; f=1+0.04*i
    mellotron(ch,T(b),c[-1],SPB(b)*3.6,hg(0.08*f),'choir',seed=i+30)
    mellotron(ch,T(b)+0.5*BAR,c[-1]+7,SPB(b)*2.6,hg(0.06*f),'flute',seed=i+130)
    saw_drone(ch,T(b),c[0],SPB(b)*3.0,hg(0.04*f),seed=i+5)
    fingerbass(bs,T(b),c[0],SPB(b)*3.6,hg(0.24*f),seed=i)
    nylonpick(b,i,c,0.085*f)
    crunch(gt,T(b),c[1],SPB(b)*3.6,hg(0.05*f),drive=1.4,seed=i)   # faint strum under
    bowed(sl,T(b),c[-1]+12,SPB(b)*3.2,hg(0.12*f),det=float(np.random.default_rng(i+4).normal(0,8)),seed=i+4)
    vbrush(b,hg(0.54*f),arc=0.9+0.008*i,ride=True)
    P.TM(b+3.5,14,0.3*f,98,arc=0.9) if i%4==3 else None
    chant(vx,b,[(0,2.0,c[2],'a','h'),(2.0,2.0,c[-1],'o','y')],g=0.06*f,n=3,style='croon',spread=20,seedbase=300+i)
# V2 2:13-2:45 return to sparse nylon + deadpan, last verse
for i in range(8):
    b=bar_at('V2',i); c=PROG[i%4]; f=1-0.02*i+0.06
    mellotron(ch,T(b),c[-1],SPB(b)*3.6,hg(0.05*f),'choir',seed=i+42)
    fingerbass(bs,T(b),c[0],SPB(b)*3.6,hg(0.20*f),seed=i)
    nylonpick(b,i,c,0.08*f)
    bowed(sl,T(b)+0.4*BAR,c[-1]+12,SPB(b)*2.4,hg(0.08*f),det=float(np.random.default_rng(i+5).normal(0,8)),seed=i+5)
    vbrush(b,hg(0.42*f),arc=0.7)
    line(vx,b,[(0,1.0,c[2],'a','h'),(1.0,1.0,c[-1],'o','n'),(2.0,1.5,c[2],'a',''),(3.0,0.5,c[1],'o','e')],
         g=0.11*f,style='croon',breath=0.29,seedbase=400+i)
# OUT 2:45-3:04 fade on held Dsus2 (never resolves)
for i in range(4):
    b=bar_at('OUT',i); c=PROG[0]; f=0.8-0.08*i
    mellotron(ch,T(b),c[2],SPB(b)*3.6,hg(0.05*f),'choir',seed=i+50)
    subbass(bs,T(b),c[0]-12,SPB(b)*3.6,0.14*f)
    nylonpick(b,i,c,0.05*f)
    vbrush(b,hg(0.30*f),arc=0.6,ride=True)
# TG: a single soft Dsus2 hold, violin fade
b=bar_at('TG',0); c=PROG[0]
mellotron(ch,T(b),c[2],SPB(b)*3.8,0.08,'choir',seed=99)
subbass(bs,T(b),c[0]-12,SPB(b)*3.8,0.16)
bowed(sl,T(b),c[2]+12,SPB(b)*3.8,hg(0.10),seed=99)
P.RD(b,0,0.34,bell=False); P.S(b+2,8,0.28,'cross')
P.apply_chokes()
DRUMS=mix_kit(P.bus,room_amount=0.30,oh_amount=0.7,lpf=7300)
noise_sw(fx,0,T(END),0.005,True,70,1200)
STEMS=[(sl,-0.42,0.64,0.34,0.0),(gt,0.45,0.52,0.34,8.0),(kp,0.0,0.56,0.34,0.0),(ch,0.15,0.70,0.0,0.0),(fx,0.0,0.7,0.0,0.0)]
MAPT=[(n,a,b_,(7.0 if n in('IN','OUT','TG') else 3.2)) for n,a,b_ in MAP]
run(NAME, lambda voc: mixdown(NAME,vx,STEMS,DRUMS,bs,MAPT,vocals=voc,
    wet=0.26,decay=2.0,wide=1.5,drum_gain=0.62,bass_gain=0.82,crush_amt=0.10,
    rms_target=0.150), MAPT)