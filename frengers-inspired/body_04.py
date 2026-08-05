# ============================================================ BAI 4: MIRROR OF THE MIND
# Model: Mew - "Symmetry" (Frengers 2003) - Eb major ~61 BPM (half-time feel)
#   verse Cm-Eb (vi-IV), bridge Eb-F-Ab, chorus Eb-Cm-Bb-Ab-Bb-Eb (per CifraClub)
#   giong rat cham, giu not 1-6s ("Caught in the symmetry of your mind")
#   bass giu not dai; drums SPARSE: rim shots, khong kick trong verse
#   nhac cu: wurli + mellotron choir + strings; khong crunch
BAR=4.0
NAME="04-mirror-of-the-mind"
SECS=[('IN',4),('V1',6),('V2',6),('CH',8),('V3',6),('CH2',8),('BR',6),('CH3',8),('OUT',4)]
S={}; _b=0.0
for _n,_c in SECS: S[_n]=_b; _b+=_c*BAR
END=_b
configure(61,61,END+3)
MAP=[(n,S[n],S[n]+c*BAR) for n,c in SECS]
def bar_at(sec,i): return S[sec]+i*BAR
print(NAME,int(END/BAR),"bars ->",round(TOTAL,1),"s")

VCH=[[nn('C3'),nn('Eb4'),nn('G4')],[nn('Eb2'),nn('G3'),nn('Bb3')]]
CHC=[[nn('Eb2'),nn('G3'),nn('Bb3')],[nn('C3'),nn('Eb4'),nn('G4')],[nn('Bb2'),nn('D4'),nn('F4')],[nn('Ab2'),nn('C4'),nn('Eb4')],[nn('Bb2'),nn('D4'),nn('F4')],[nn('Eb2'),nn('G3'),nn('Bb3')]]
BRC=[[nn('Eb2'),nn('G3'),nn('Bb3')],[nn('F2'),nn('A3'),nn('C4')],[nn('Ab2'),nn('C4'),nn('Eb4')]]
def vch(i): return VCH[i%2]
def cch(i): return CHC[i%6]
def brc(i): return BRC[i%3]

K=Kit(seed=1214); P=Performer(K,T,SPB,TOTAL,seed=11,style='indie'); P.hum=0.65
def villa(b,lvl=0.7,arc=1.0,mode='sparse'):
    a=arc
    if mode=='sparse':   # rim shots + shimmer hats, khong kick
        for s in range(8):
            P.H(b+s*0.5,s*2,0.3*lvl,o=0.0,art='tip',arc=a)
        P.S(b+1,4,0.5*lvl,'rim',a); P.S(b+3,12,0.55*lvl,'rim',a)
    else:                # chorus: kick nhe 1&3, snare backbeat, ride
        for s in range(16):
            P.H(b+s*0.25,s,0.4*lvl if s%4==0 else 0.28*lvl,o=0.0,art='tip',arc=a)
        P.K(b,0,0.7*lvl,a); P.K(b+2,8,0.55*lvl,a)
        P.S(b+1,4,0.8*lvl,'center',a); P.S(b+3,12,0.85*lvl,'center',a)
        P.RD(b,0,0.4*lvl,bell=True,arc=a)

vn=buf(); gtL=buf(); gtR=buf(); stL=buf(); stR=buf(); bs=buf(); vx=buf(); dr_extra=buf()

# ---- INTRO: wurli + strings, khong drums ----
for i in range(4):
    b=bar_at('IN',i)
    chord0(wurli,gtL,b+0.3,VCH[0],SPB(b)*3.0,hg(0.055),det=-18)
    for _k,_m in enumerate([VCH[0][0],VCH[0][2],VCH[0][1],VCH[0][2]]):
        wurli(gtR,ht(b+0.32,j=0.006)+_k*0.06,_m,SPB(b)*0.8,hg(0.055),det=18)
    strings(stL,T(b),VCH[0],SPB(b)*3.6,hg(0.05),seed=0)
    strings(stR,T(b+0.012),VCH[0],SPB(b)*3.6,hg(0.05),seed=200)
    subbass(bs,T(b),nn('C2'),SPB(b)*3.5,hg(0.16))
# ---- V1 ----
for i in range(6):
    b=bar_at('V1',i); c=vch(i)
    chord0(wurli,gtL,b+0.3,c,SPB(b)*3.0,hg(0.06),det=-18)
    for _k,_m in enumerate([c[0],c[2],c[1],c[2]]):
        wurli(gtR,ht(b+0.32,j=0.006)+_k*0.06,_m,SPB(b)*0.8,hg(0.06),det=18)
    strings(stL,T(b),c,SPB(b)*3.6,hg(0.05),seed=0)
    strings(stR,T(b+0.012),c,SPB(b)*3.6,hg(0.05),seed=200)
    bassn(bs,T(b+0.5),c[0],SPB(b)*3.0,hg(0.17))
    villa(b,hg(0.5),arc=0.8,mode='sparse')
    if i%3==0:
        line(vx,b,[(0,2.0,'G4','a','k'),(2.0,2.0,'Eb4','o',''),(4.0,2.0,'F4','a',''),(6.0,2.0,'Eb4','e','')],
             g=0.15,style='falsetto',breath=0.32,seedbase=10+i)
# ---- V2 ----
for i in range(6):
    b=bar_at('V2',i); c=vch(i)
    chord0(wurli,gtL,b+0.3,c,SPB(b)*3.0,hg(0.065),det=-18)
    for _k,_m in enumerate([c[0],c[2],c[1],c[2]]):
        wurli(gtR,ht(b+0.32,j=0.006)+_k*0.06,_m,SPB(b)*0.8,hg(0.065),det=18)
    mellotron(stL,T(b),c[2],SPB(b)*3.4,hg(0.05),kind="choir",seed=i+40)
    mellotron(stR,T(b+0.01),c[2],SPB(b)*3.4,hg(0.05),kind="choir",seed=i+240)
    strings(stL,T(b),c,SPB(b)*3.6,hg(0.05),seed=0)
    strings(stR,T(b+0.012),c,SPB(b)*3.6,hg(0.05),seed=200)
    bassn(bs,T(b+0.5),c[0],SPB(b)*3.0,hg(0.18))
    villa(b,hg(0.55),arc=0.85,mode='sparse')
    line(vx,b,[(0,2.0,'G4','o',''),(2.0,2.0,'Ab4','a',''),(4.0,3.0,'Bb4','e','')],
         g=0.155,style='falsetto',breath=0.32,seedbase=100+i)
# ---- CH ----
for i in range(8):
    b=bar_at('CH',i); c=cch(i)
    chord0(wurli,gtL,b+0.3,c,SPB(b)*3.0,hg(0.07),det=-18)
    for _k,_m in enumerate([c[0],c[2],c[1],c[2]]):
        wurli(gtR,ht(b+0.32,j=0.006)+_k*0.06,_m,SPB(b)*0.8,hg(0.07),det=18)
    strings(stL,T(b),c,SPB(b)*3.6,hg(0.05),seed=0)
    strings(stR,T(b+0.012),c,SPB(b)*3.6,hg(0.05),seed=200)
    glassarp(stR,T(b+1),c[2]+12,SPB(b)*2.0,hg(0.05),seed=i)
    bassn(bs,T(b+0.5),c[0],SPB(b)*3.2,hg(0.2))
    villa(b,hg(0.65),arc=1.0,mode='chorus')
    if i%4==0:
        line(vx,b,[(0,1.5,'Bb4','a',''),(1.5,1.5,'Ab4','o',''),(3.0,1.5,'G4','a',''),(4.5,3.5,'Eb4','a','')],
             g=0.16,style='falsetto',breath=0.34,seedbase=200+i)
# ---- V3 ----
for i in range(6):
    b=bar_at('V3',i); c=vch(i)
    chord0(wurli,gtL,b+0.3,c,SPB(b)*3.0,hg(0.06),det=-18)
    for _k,_m in enumerate([c[0],c[2],c[1],c[2]]):
        wurli(gtR,ht(b+0.32,j=0.006)+_k*0.06,_m,SPB(b)*0.8,hg(0.06),det=18)
    strings(stL,T(b),c,SPB(b)*3.6,hg(0.05),seed=0)
    strings(stR,T(b+0.012),c,SPB(b)*3.6,hg(0.05),seed=200)
    bassn(bs,T(b+0.5),c[0],SPB(b)*3.0,hg(0.18))
    villa(b,hg(0.55),arc=0.85,mode='sparse')
    line(vx,b,[(0,2.0,'Ab4','a',''),(2.0,2.0,'G4','o',''),(4.0,3.0,'Eb4','e','n')],
         g=0.155,style='falsetto',breath=0.32,seedbase=300+i)
# ---- CH2 ----
for i in range(8):
    b=bar_at('CH2',i); c=cch(i)
    chord0(wurli,gtL,b+0.3,c,SPB(b)*3.0,hg(0.075),det=-18)
    for _k,_m in enumerate([c[0],c[2],c[1],c[2]]):
        wurli(gtR,ht(b+0.32,j=0.006)+_k*0.06,_m,SPB(b)*0.8,hg(0.075),det=18)
    mellotron(stL,T(b),c[2],SPB(b)*3.4,hg(0.055),kind='choir',seed=i+100)
    mellotron(stR,T(b+0.01),c[2],SPB(b)*3.4,hg(0.055),kind='choir',seed=i+300)
    strings(stL,T(b),c,SPB(b)*3.6,hg(0.05),seed=0)
    strings(stR,T(b+0.012),c,SPB(b)*3.6,hg(0.05),seed=200)
    glassarp(stR,T(b+1),c[2]+12,SPB(b)*2.0,hg(0.055),seed=i+40)
    bassn(bs,T(b+0.5),c[0],SPB(b)*3.2,hg(0.22))
    villa(b,hg(0.7),arc=1.0,mode='chorus')
    if i==3: P.fill(b+2.0,2.0,'tom',0.9,next_crash_beat=b+4)
    line(vx,b,[(0,1.5,'Bb4','a',''),(1.5,1.5,'C5','o',''),(3.0,1.5,'Bb4','a',''),(4.5,3.5,'Ab4','a','')],
         g=0.165,style='falsetto',breath=0.34,seedbase=400+i)
# ---- BR: Eb-F-Ab (cang len) ----
for i in range(6):
    b=bar_at('BR',i); c=brc(i)
    chord0(wurli,gtL,b+0.3,c,SPB(b)*3.0,hg(0.07),det=-18)
    for _k,_m in enumerate([c[0],c[2],c[1],c[2]]):
        wurli(gtR,ht(b+0.32,j=0.006)+_k*0.06,_m,SPB(b)*0.8,hg(0.07),det=18)
    strings(stL,T(b),c,SPB(b)*3.6,hg(0.05),seed=0)
    strings(stR,T(b+0.012),c,SPB(b)*3.6,hg(0.05),seed=200)
    bassn(bs,T(b+0.5),c[0],SPB(b)*3.2,hg(0.21))
    villa(b,hg(0.68),arc=1.0,mode='chorus')
    if i%3==1:
        line(vx,b,[(0,2.0,'C5','o',''),(2.0,2.0,'Bb4','a',''),(4.0,2.0,'Ab4','e','')],
             g=0.16,style='falsetto',breath=0.32,seedbase=500+i)
# ---- CH3 ----
for i in range(8):
    b=bar_at('CH3',i); c=cch(i)
    chord0(wurli,gtL,b+0.3,c,SPB(b)*3.0,hg(0.08),det=-18)
    for _k,_m in enumerate([c[0],c[2],c[1],c[2]]):
        wurli(gtR,ht(b+0.32,j=0.006)+_k*0.06,_m,SPB(b)*0.8,hg(0.08),det=18)
    strings(stL,T(b),c+[x+12 for x in c[:2]],SPB(b)*3.6,hg(0.05),seed=0)
    strings(stR,T(b+0.012),c+[x+12 for x in c[:2]],SPB(b)*3.6,hg(0.05),seed=200)
    glassarp(stR,T(b+1),c[2]+12,SPB(b)*2.0,hg(0.06),seed=i+60)
    bassn(bs,T(b+0.5),c[0],SPB(b)*3.2,hg(0.24))
    villa(b,hg(0.75),arc=1.0,mode='chorus')
    if i==2: P.fill(b+2.0,2.0,'burst32',1.0,next_crash_beat=b+4)
    line(vx,b,[(0,1.5,'C5','a',''),(1.5,1.5,'Bb4','o',''),(3.0,2.0,'Ab4','a',''),(5.0,3.0,'Eb4','a','')],
         g=0.17,style='falsetto',breath=0.36,seedbase=600+i)
# ---- OUT: Cm quay lai, glock ----
for i in range(4):
    b=bar_at('OUT',i)
    chord0(wurli,gtL,b+0.3,VCH[0],SPB(b)*3.0,hg(0.06),det=-18)
    for _k,_m in enumerate([VCH[0][0],VCH[0][2],VCH[0][1],VCH[0][2]]):
        wurli(gtR,ht(b+0.32,j=0.006)+_k*0.06,_m,SPB(b)*0.8,hg(0.06),det=18)
    glock(stR,T(b+1),nn("C5"),SPB(b)*2.5,hg(0.06),seed=i)
    strings(stL,T(b),VCH[0],SPB(b)*3.6,hg(0.05),seed=0)
    strings(stR,T(b+0.012),VCH[0],SPB(b)*3.6,hg(0.05),seed=200)
    subbass(bs,T(b),nn('C2'),SPB(b)*3.5,hg(0.16))
    villa(b,hg(0.45),arc=0.7,mode='sparse')

P.apply_chokes()
P.bus['hat']=P.bus['hat']*2.6
DRUMS=mix_kit(P.bus,room_amount=0.28,oh_amount=1.0,lpf=15500)
DRUMS=DRUMS+hp(_fit(P.bus['hat'],len(DRUMS)),8000,2)*0.90
DRUMS=DRUMS*(0.035/max(rms_(DRUMS),1e-9))
bs=bs*(0.045/max(rms_(bs),1e-9))
noise_sw(dr_extra,0,T(END),0.003,True,90,1600)

STEMS=[(vn,-0.35,0.85,0.30,0.0),(gtL,-0.92,2.30,0.30,0.0),(gtR,0.92,2.30,0.30,0.0),
       (stL,-0.88,1.55,0.12,0.0),(stR,0.88,1.55,0.12,0.0),(dr_extra,0.0,0.8,0.0,0.0)]
MAPT=[(n,a,b,(2.6 if n in('CH','CH2','CH3','BR') else 2.4)) for n,a,b in MAP]
run(NAME, lambda voc: mixdown(NAME,vx,STEMS,DRUMS,bs,MAPT,vocals=voc,
    wet=0.30,decay=2.0,wide=2.8,drum_gain=0.95,bass_gain=0.95,crush_amt=0.10,
    rms_target=0.185), MAPT)
