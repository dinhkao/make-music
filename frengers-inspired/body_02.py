# ============================================================ BAI 2: FROM THE BEDROOM WINDOW
# Model: Mew - "156" (Frengers 2003) - E major, 130 BPM
#   vong C#m-A-E-B (vi-IV-I-V) - bat dau bang vi nen "home" bi tri hoan
#   bass 8ths octave-jump (C#2-C#3, A2-A3, E2-E3, B2-B3) - do tu stem that
#   verse: giong thap, drums offbeat pulse; chorus: backbeat, kick 8ths drive
BAR=4.0
NAME="02-from-the-bedroom-window"
SECS=[('IN',4),('V1',8),('V2',8),('CH',8),('IN2',4),('V3',8),('CH2',8),('BR',8),('CH3',8),('OUT',40)]
S={}; _b=0.0
for _n,_c in SECS: S[_n]=_b; _b+=_c*BAR
END=_b
configure(130,130,END+3)
MAP=[(n,S[n],S[n]+c*BAR) for n,c in SECS]
def bar_at(sec,i): return S[sec]+i*BAR
print(NAME,int(END/BAR),"bars ->",round(TOTAL,1),"s")

VCH=[[nn('C#3'),nn('E4'),nn('G#4')],[nn('A2'),nn('C#4'),nn('E4')],[nn('E3'),nn('G#4'),nn('B4')],[nn('B2'),nn('D#4'),nn('F#4')]]
def vch(i): return VCH[i%4]
def broot(i): return VCH[i%4][0]

def bass8(b,b0,root,g=0.26):
    for s in range(8):  # 8ths octave-jump nhu 156
        m=root+(12 if s%2==0 else 0)
        bassn(bs,T(b0+s*0.25),m,SPB(b)*0.85,hg(g))

K=Kit(seed=1212); P=Performer(K,T,SPB,TOTAL,seed=11,style='indie'); P.hum=0.72
def villa(b,lvl=0.8,arc=1.0,mode='drive'):
    a=arc
    if mode=='drive':   # verse: hat 8ths + kick offbeat, snare ghost
        for s in range(16):
            P.H(b+s*0.25,s,0.72*lvl if s%2==1 else 0.5*lvl,o=0.0,art='tip',arc=a)
        P.K(b+0.5,2,0.8*lvl,a); P.K(b+2.5,10,0.8*lvl,a); P.K(b+3.0,12,0.5*lvl,a)
        P.S(b+1,4,0.5*lvl,'ghost',a); P.S(b+3,12,0.6*lvl,'ghost',a)
    else:               # chorus: kick 8ths song song bass, backbeat that
        for s in range(16):
            P.H(b+s*0.25,s,0.75*lvl if s%4==0 else 0.5*lvl,o=0.0,art=('edge' if s%4==0 else 'tip'),arc=a)
            if s%2==0: P.K(b+s*0.25,s,0.75*lvl,a)
        P.S(b+1,4,0.9*lvl,'center',a); P.S(b+3,12,0.95*lvl,'center',a)
        P.S(b+0.5,2,0.3*lvl,'ghost',a); P.S(b+2.5,10,0.28*lvl,'ghost',a)
        P.RD(b,0,0.45*lvl,bell=True,arc=a)
        if int(b*130/60)%4==3:
            P.TM(b+2.75,11,0.65*lvl,130); P.TM(b+3.25,13,0.75*lvl,104); P.TM(b+3.75,15,0.85*lvl,86)

vn=buf(); gtL=buf(); gtR=buf(); st=buf(); bs=buf(); vx=buf(); dr_extra=buf()

# ---- INTRO: bass 8ths C#m + jangle + giong vang ----
for i in range(4):
    b=bar_at('IN',i)
    bass8(b,b,vch(i)[0],0.16)
    arp8(jangle,gtL,b,vch(i),SPB(b)*0.8,hg(0.055),i)
    arp8(jangle,gtR,b+0.009,vch(i),SPB(b)*0.8,hg(0.055),i+50)
    villa(b,hg(0.35),arc=0.6,mode='drive')
# ---- V1 ----
for i in range(8):
    b=bar_at('V1',i)
    bass8(b,b,vch(i)[0])
    arp8(jangle,gtL,b,vch(i),SPB(b)*0.8,hg(0.085),i)
    arp8(jangle,gtR,b+0.009,vch(i),SPB(b)*0.8,hg(0.085),i+50)
    strings(st,T(b),[vch(i)[0],vch(i)[2]],SPB(b)*3.4,hg(0.035),atk=0.8,seed=i+20)
    villa(b,hg(0.45),arc=0.8,mode='drive')
    if i%4==0:
        line(vx,b,[(0,.75,'C#4','a','f'),(.75,.5,'B3','o',''),(1.25,1.0,'A3','a',''),(2.5,.75,'B3','e',''),(3.25,.75,'C#4','a','')],
             g=0.145,style='falsetto',breath=0.3,seedbase=10+i)
# ---- V2 ----
for i in range(8):
    b=bar_at('V2',i)
    bass8(b,b,vch(i)[0])
    arp8(jangle,gtL,b,vch(i),SPB(b)*0.8,hg(0.09),i)
    arp8(jangle,gtR,b+0.009,vch(i),SPB(b)*0.8,hg(0.09),i+50)
    glassarp(st,T(b+0.5),vch(i)[2]+12,SPB(b)*1.4,hg(0.05),seed=i)
    glock(st,T(b+1),vch(i)[2]+12,SPB(b)*1.2,hg(0.05),seed=i+3)
    strings(st,T(b),[vch(i)[0],vch(i)[2]],SPB(b)*3.4,hg(0.04),atk=0.7,seed=i+40)
    villa(b,hg(0.5),arc=0.85,mode='drive')
    line(vx,b,[(0,.5,'C#4','o',''),(.5,.75,'E4','a','n'),(1.25,.5,'B3','e',''),(2.0,.75,'A3','a',''),(2.75,1.25,'C#4','i','')],
         g=0.15,style='falsetto',breath=0.3,seedbase=100+i)
# ---- CH: kick 8ths ----
for i in range(8):
    b=bar_at('CH',i)
    bass8(b,b,vch(i)[0],0.3)
    strum8(crunch,gtL,b,vch(i),SPB(b)*0.65,hg(0.10),i)
    strum8(crunch,gtR,b+0.011,vch(i),SPB(b)*0.65,hg(0.10),i+50)
    strings(st,T(b),vch(i),SPB(b)*3.4,hg(0.05),atk=0.35,seed=i+60)
    villa(b,hg(0.75),arc=1.0,mode='chorus')
    if i%4==0:
        line(vx,b,[(0,.5,'F#4','a',''),(.5,.5,'G#4','o',''),(1.0,.75,'A4','a',''),(1.75,.5,'B4','i',''),(2.5,1.5,'A4','a','')],
             g=0.13,style='falsetto',breath=0.32,seedbase=200+i)
# ---- IN2 ----
for i in range(4):
    b=bar_at('IN2',i)
    bass8(b,b,vch(i)[0],0.12)
    glassarp(gtR,T(b+1),vch(i)[2]+12,SPB(b)*1.5,hg(0.04),seed=i)
    villa(b,hg(0.3),arc=0.5,mode='drive')
# ---- V3 ----
for i in range(8):
    b=bar_at('V3',i)
    bass8(b,b,vch(i)[0])
    arp8(jangle,gtL,b,vch(i),SPB(b)*0.8,hg(0.09),i)
    arp8(jangle,gtR,b+0.009,vch(i),SPB(b)*0.8,hg(0.09),i+50)
    strings(st,T(b),[vch(i)[0],vch(i)[2]],SPB(b)*3.4,hg(0.042),atk=0.6,seed=i+80)
    villa(b,hg(0.52),arc=0.88,mode='drive')
    line(vx,b,[(0,.5,'C#4','a',''),(.5,.75,'E4','e',''),(1.25,.5,'G#4','o',''),(2.0,.75,'B3','a',''),(2.75,1.25,'C#4','i','n')],
         g=0.155,style='falsetto',breath=0.3,seedbase=300+i)
# ---- CH2 ----
for i in range(8):
    b=bar_at('CH2',i)
    bass8(b,b,vch(i)[0],0.32)
    strum8(crunch,gtL,b,vch(i),SPB(b)*0.65,hg(0.11),i)
    strum8(crunch,gtR,b+0.011,vch(i),SPB(b)*0.65,hg(0.11),i+50)
    strings(st,T(b),vch(i),SPB(b)*3.4,hg(0.055),atk=0.3,seed=i+100)
    villa(b,hg(0.82),arc=1.0,mode='chorus')
    if i==3: P.fill(b+2.0,1.5,'tom',1.0,next_crash_beat=b+4)
    line(vx,b,[(0,.5,'F#4','a',''),(.5,.5,'G#4','a',''),(1.0,.75,'A4','i',''),(1.75,.5,'B4','a',''),(2.5,1.5,'A4','a','')],
         g=0.135,style='falsetto',breath=0.34,seedbase=400+i)
# ---- BR: A-E-F#m-D (di len) ----
BRC=[[nn('A2'),nn('C#4'),nn('E4')],[nn('E3'),nn('G#4'),nn('B4')],[nn('F#2'),nn('A3'),nn('C#4')],[nn('D3'),nn('F#4'),nn('A4')]]
for i in range(8):
    b=bar_at('BR',i); c=BRC[i%4]
    bass8(b,b,c[0],0.26)
    organ(gtL,ht(b,j=0.005),c,SPB(b)*1.6,hg(0.045))
    organ(gtR,ht(b+0.01,j=0.005),c,SPB(b)*1.6,hg(0.045))
    strings(st,T(b),c,SPB(b)*3.4,hg(0.05),atk=0.5,seed=i+120)
    villa(b,hg(0.7),arc=0.95,mode='chorus')
    if i%4==2:
        line(vx,b,[(0,1.0,'A4','o',''),(1.0,1.0,'B4','a',''),(2.0,2.0,'C#5','e','v')],
             g=0.125,style='falsetto',breath=0.32,seedbase=500+i)
# ---- CH3 ----
for i in range(8):
    b=bar_at('CH3',i)
    bass8(b,b,vch(i)[0],0.34)
    strum8(crunch,gtL,b,vch(i),SPB(b)*0.65,hg(0.12),i)
    strum8(crunch,gtR,b+0.011,vch(i),SPB(b)*0.65,hg(0.12),i+50)
    strings(st,T(b),vch(i)+[x+12 for x in vch(i)[:2]],SPB(b)*3.4,hg(0.065),atk=0.25,seed=i+140)
    glock(st,T(b+2),vch(i)[2]+12,SPB(b)*1.2,hg(0.055),seed=i+7)
    villa(b,hg(0.9),arc=1.0,mode='chorus')
    if i==2: P.fill(b+2.0,2.0,'burst32',1.0,next_crash_beat=b+4)
    line(vx,b,[(0,.5,'F#4','a',''),(.5,.5,'G#4','o',''),(1.0,.75,'A4','a',''),(1.75,.5,'C#5','i',''),(2.5,1.5,'B4','a','')],
         g=0.14,style='falsetto',breath=0.36,seedbase=600+i)
# ---- OUT: false-stop 2 bar dau roi build to fade ----
for i in range(40):
    b=bar_at('OUT',i)
    f=0.45+0.018*i if i<28 else 0.95
    if i<2: f=0.30
    bass8(b,b,vch(i)[0],0.24*f)
    strum8(crunch,gtL,b,vch(i),SPB(b)*0.65,hg(0.10*f),i)
    strum8(crunch,gtR,b+0.011,vch(i),SPB(b)*0.65,hg(0.10*f),i+50)
    strings(st,T(b),vch(i),SPB(b)*3.4,hg(0.05*f),atk=0.4,seed=i+160)
    villa(b,hg(0.85*f),arc=0.7+0.3*min(f,1.0),mode='chorus')
    if i%4==0 and i>=2:
        line(vx,b,[(0,.5,'A4','a','f'),(.5,.5,'A4','a',''),(1.0,.5,'G#4','o',''),(1.5,.5,'F#4','e',''),(2.0,.5,'A4','a',''),(2.5,1.5,'G#4','o','')],
             g=0.12,style='falsetto',breath=0.3,seedbase=700+i//4)
    if i%8==7:
        P.fill(b+3.0,1.0,'snare',0.7)

P.apply_chokes()
P.bus['hat']=P.bus['hat']*2.6
DRUMS=mix_kit(P.bus,room_amount=0.25,oh_amount=1.0,lpf=15500)
DRUMS=DRUMS+hp(_fit(P.bus['hat'],len(DRUMS)),8000,2)*0.90
DRUMS=DRUMS*(0.052/max(rms_(DRUMS),1e-9))
bs=bs*(0.075/max(rms_(bs),1e-9))
noise_sw(dr_extra,0,T(END),0.004,True,90,1600)

STEMS=[(vn,-0.35,0.78,0.38,0.0),(gtL,-0.92,2.30,0.30,0.0),(gtR,0.92,2.30,0.30,0.0),
       (st,0.35,1.25,0.12,9.0),(dr_extra,0.0,0.8,0.0,0.0)]
MAPT=[(n,a,b,(5.5 if n=='OUT' else 2.6)) for n,a,b in MAP]
run(NAME, lambda voc: mixdown(NAME,vx,STEMS,DRUMS,bs,MAPT,vocals=voc,
    wet=0.26,decay=1.8,wide=3.0,drum_gain=0.95,bass_gain=0.95,crush_amt=0.16,
    rms_target=0.205), MAPT)
