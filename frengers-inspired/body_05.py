# ============================================================ BAI 5: BEHIND THE CURTAIN
# Model: Mew - "Behind the Drapes" (Frengers 2003) - G major, 96 BPM
#   verse Bm-D-Em7, chorus G-D-Am-C-G-D-Am-D (per CifraClub), vai cho C/G
#   mid-tempo march: ride bell + backbeat restrained (Nick Villa "programmed-feeling"),
#   ghost snare day; bass root + passing notes (G#2 luot - do tu stem)
#   nhac cu: jangle arps + wurli + glassarp; chorus them crunch
BAR=4.0
NAME="05-behind-the-curtain"
SECS=[('IN',4),('V1',8),('V2',8),('CH',12),('V3',8),('CH2',12),('BR',8),('CH3',12),('OUT',6)]
S={}; _b=0.0
for _n,_c in SECS: S[_n]=_b; _b+=_c*BAR
END=_b
configure(96,96,END+3)
MAP=[(n,S[n],S[n]+c*BAR) for n,c in SECS]
def bar_at(sec,i): return S[sec]+i*BAR
print(NAME,int(END/BAR),"bars ->",round(TOTAL,1),"s")

VCH=[[nn('B2'),nn('D4'),nn('F#4')],[nn('D3'),nn('F#4'),nn('A4')],[nn('E3'),nn('G4'),nn('B4')]]
CHC=[[nn('G2'),nn('B3'),nn('D4')],[nn('D3'),nn('F#4'),nn('A4')],[nn('A2'),nn('C4'),nn('E4')],[nn('C3'),nn('E4'),nn('G4')],
    [nn('G2'),nn('B3'),nn('D4')],[nn('D3'),nn('F#4'),nn('A4')],[nn('A2'),nn('C4'),nn('E4')],[nn('D3'),nn('F#4'),nn('A4')]]
BRC=[[nn('C3'),nn('E4'),nn('G4')],[nn('D3'),nn('F#4'),nn('A4')],[nn('B2'),nn('D4'),nn('F#4')],[nn('E3'),nn('G4'),nn('B4')]]
def vch(i): return VCH[i%3]
def cch(i): return CHC[i%8]
def brc(i): return BRC[i%4]

K=Kit(seed=1215); P=Performer(K,T,SPB,TOTAL,seed=11,style='indie'); P.hum=0.72
def villa(b,lvl=0.8,arc=1.0,mode='march'):
    a=arc
    if mode=='march':   # ride bell + backbeat + ghost snare
        for s in range(16):
            P.H(b+s*0.25,s,0.42*lvl if s%4==0 else 0.3*lvl,o=0.0,art='tip',arc=a)
        P.RD(b,0,0.5*lvl,bell=(int(b*96/60)%2==0),arc=a)
        P.K(b,0,0.8*lvl,a); P.K(b+2,8,0.6*lvl,a)
        P.S(b+1,4,0.7*lvl,'center',a); P.S(b+3,12,0.75*lvl,'center',a)
        P.S(b+0.5,2,0.3*lvl,'ghost',a); P.S(b+1.5,6,0.25*lvl,'ghost',a)
        P.S(b+2.5,10,0.28*lvl,'ghost',a); P.S(b+3.5,14,0.22*lvl,'ghost',a)
    else:               # chorus: stomp hon, toms
        for s in range(16):
            P.H(b+s*0.25,s,0.58*lvl if s%4==0 else 0.4*lvl,o=0.0,art=('edge' if s%4==0 else 'tip'),arc=a)
        P.K(b,0,1.0*lvl,a); P.K(b+1.5,6,0.5*lvl,a); P.K(b+2.75,11,0.55*lvl,a); P.K(b+3.5,14,0.5*lvl,a)
        P.S(b+1,4,0.9*lvl,'center',a); P.S(b+3,12,0.95*lvl,'center',a)
        P.S(b+0.5,2,0.32*lvl,'ghost',a); P.S(b+2.5,10,0.3*lvl,'ghost',a)
        if int(b*96/60)%4==3:
            P.TM(b+2.5,10,0.65*lvl,150); P.TM(b+3.25,13,0.75*lvl,120)

vn=buf(); gtL=buf(); gtR=buf(); st=buf(); bs=buf(); vx=buf(); dr_extra=buf()

# ---- INTRO: wurli + glassarp ----
for i in range(4):
    b=bar_at('IN',i)
    chord0(wurli,gtL,b+0.3,VCH[0],SPB(b)*3.0,hg(0.06),det=-9)
    chord0(wurli,gtR,b+0.32,VCH[0],SPB(b)*3.0,hg(0.06),det=9)
    glassarp(st,T(b+1),nn('F#4'),SPB(b)*2.0,hg(0.06),seed=i)
    bassn(bs,T(b+1.5),nn('B2'),SPB(b)*1.8,hg(0.15))
    villa(b,hg(0.4),arc=0.65,mode='march')
# ---- V1 ----
for i in range(8):
    b=bar_at('V1',i); c=vch(i)
    arp8(jangle,gtL,b,c,SPB(b)*0.8,hg(0.085),i)
    arp8(jangle,gtR,b+0.009,c,SPB(b)*0.8,hg(0.085),i+50)
    bassn(bs,T(b+0.25),c[0],SPB(b)*0.85,hg(0.19))
    strings(st,T(b),[c[0],c[2]],SPB(b)*3.4,hg(0.035),atk=0.7,seed=i+20)
    villa(b,hg(0.55),arc=0.85,mode='march')
    if i%4==0:
        line(vx,b,[(0,.75,'F#4','a',''),(.75,.5,'D4','o',''),(1.25,1.0,'E4','a',''),(2.5,.75,'F#4','e',''),(3.25,.75,'D4','a','')],
             g=0.15,style='falsetto',breath=0.3,seedbase=10+i)
# ---- V2 ----
for i in range(8):
    b=bar_at('V2',i); c=vch(i)
    arp8(jangle,gtL,b,c,SPB(b)*0.8,hg(0.09),i)
    arp8(jangle,gtR,b+0.009,c,SPB(b)*0.8,hg(0.09),i+50)
    glassarp(st,T(b+0.5),c[2]+12,SPB(b)*1.5,hg(0.05),seed=i)
    bassn(bs,T(b+0.25),c[0],SPB(b)*0.85,hg(0.2))
    strings(st,T(b),[c[0],c[2]],SPB(b)*3.4,hg(0.04),atk=0.6,seed=i+40)
    villa(b,hg(0.6),arc=0.9,mode='march')
    line(vx,b,[(0,.5,'F#4','o',''),(.5,.75,'A4','a',''),(1.25,.5,'G4','e',''),(2.0,.5,'D4','a',''),(2.75,1.25,'E4','i','')],
         g=0.155,style='falsetto',breath=0.3,seedbase=100+i)
# ---- CH ----
for i in range(12):
    b=bar_at('CH',i); c=cch(i)
    strum8(crunch,gtL,b,c,SPB(b)*0.7,hg(0.10),i)
    strum8(crunch,gtR,b+0.011,c,SPB(b)*0.7,hg(0.10),i+50)
    strings(st,T(b),c,SPB(b)*3.4,hg(0.05),atk=0.35,seed=i+60)
    bassn(bs,T(b+0.25),c[0],SPB(b)*0.85,hg(0.24))
    villa(b,hg(0.75),arc=1.0,mode='chorus')
    if i%4==0:
        line(vx,b,[(0,.5,'B4','a',''),(.5,.5,'A4','o',''),(1.0,.75,'G4','a',''),(1.75,.5,'D4','i',''),(2.5,1.5,'E4','a','')],
             g=0.155,style='falsetto',breath=0.32,seedbase=200+i)
# ---- V3 ----
for i in range(8):
    b=bar_at('V3',i); c=vch(i)
    arp8(jangle,gtL,b,c,SPB(b)*0.8,hg(0.09),i)
    arp8(jangle,gtR,b+0.009,c,SPB(b)*0.8,hg(0.09),i+50)
    strings(st,T(b),[c[0],c[2]],SPB(b)*3.4,hg(0.045),atk=0.6,seed=i+80)
    bassn(bs,T(b+0.25),c[0],SPB(b)*0.85,hg(0.21))
    villa(b,hg(0.62),arc=0.92,mode='march')
    line(vx,b,[(0,.5,'F#4','a',''),(.5,.75,'A4','e',''),(1.25,.5,'B4','o',''),(2.0,.75,'A4','a',''),(2.75,1.25,'F#4','i','n')],
         g=0.16,style='falsetto',breath=0.3,seedbase=300+i)
# ---- CH2 ----
for i in range(12):
    b=bar_at('CH2',i); c=cch(i)
    strum8(crunch,gtL,b,c,SPB(b)*0.7,hg(0.11),i)
    strum8(crunch,gtR,b+0.011,c,SPB(b)*0.7,hg(0.11),i+50)
    strings(st,T(b),c,SPB(b)*3.4,hg(0.055),atk=0.3,seed=i+100)
    bassn(bs,T(b+0.25),c[0],SPB(b)*0.85,hg(0.26))
    villa(b,hg(0.82),arc=1.0,mode='chorus')
    if i==5: P.fill(b+2.0,1.5,'tom',1.0,next_crash_beat=b+4)
    line(vx,b,[(0,.5,'B4','a',''),(.5,.5,'A4','a',''),(1.0,.75,'G4','i',''),(1.75,.5,'D4','a',''),(2.5,1.5,'E4','a','')],
         g=0.16,style='falsetto',breath=0.34,seedbase=400+i)
# ---- BR: C-D-Bm-Em ----
for i in range(8):
    b=bar_at('BR',i); c=brc(i)
    organ(gtL,ht(b,j=0.005),c,SPB(b)*1.8,hg(0.05))
    organ(gtR,ht(b+0.01,j=0.005),c,SPB(b)*1.8,hg(0.05))
    strings(st,T(b),c,SPB(b)*3.4,hg(0.05),atk=0.5,seed=i+120)
    bassn(bs,T(b+0.25),c[0],SPB(b)*0.85,hg(0.23))
    villa(b,hg(0.7),arc=0.95,mode='chorus')
    if i%4==2:
        line(vx,b,[(0,1.0,'A4','o',''),(1.0,1.0,'B4','a',''),(2.0,2.0,'D5','e','v')],
             g=0.16,style='falsetto',breath=0.32,seedbase=500+i)
# ---- CH3 ----
for i in range(12):
    b=bar_at('CH3',i); c=cch(i)
    strum8(crunch,gtL,b,c,SPB(b)*0.7,hg(0.12),i)
    strum8(crunch,gtR,b+0.011,c,SPB(b)*0.7,hg(0.12),i+50)
    strings(st,T(b),c+[x+12 for x in c[:2]],SPB(b)*3.4,hg(0.065),atk=0.25,seed=i+140)
    bassn(bs,T(b+0.25),c[0],SPB(b)*0.85,hg(0.28))
    villa(b,hg(0.9),arc=1.0,mode='chorus')
    if i==4: P.fill(b+2.0,2.0,'burst32',1.0,next_crash_beat=b+4)
    line(vx,b,[(0,.5,'B4','a',''),(.5,.5,'D5','o',''),(1.0,.75,'B4','a',''),(1.75,.5,'A4','i',''),(2.5,1.5,'G4','a','')],
         g=0.165,style='falsetto',breath=0.36,seedbase=600+i)
# ---- OUT: giong lap + fade ----
for i in range(6):
    b=bar_at('OUT',i); c=cch(i%4)
    arp8(jangle,gtL,b,c,SPB(b)*0.8,hg(0.085),i)
    arp8(jangle,gtR,b+0.009,c,SPB(b)*0.8,hg(0.085),i+50)
    strings(st,T(b),c,SPB(b)*3.4,hg(0.045),atk=0.6,seed=i+160)
    bassn(bs,T(b+0.25),c[0],SPB(b)*0.85,hg(0.19))
    villa(b,hg(0.55),arc=0.75,mode='march')
    if i%2==0:
        line(vx,b,[(0,.75,'G4','a','g'),(.75,.5,'G4','a',''),(1.25,.75,'F#4','o',''),(2.0,.75,'D4','e',''),(2.75,1.25,'E4','a','')],
             g=0.14,style='falsetto',breath=0.3,seedbase=700+i//2)

P.apply_chokes()
P.bus['hat']=P.bus['hat']*2.6
DRUMS=mix_kit(P.bus,room_amount=0.25,oh_amount=1.0,lpf=15500)
DRUMS=DRUMS+hp(_fit(P.bus['hat'],len(DRUMS)),8000,2)*0.90
DRUMS=DRUMS*(0.048/max(rms_(DRUMS),1e-9))
bs=bs*(0.070/max(rms_(bs),1e-9))
noise_sw(dr_extra,0,T(END),0.004,True,90,1600)

STEMS=[(vn,-0.35,0.78,0.38,0.0),(gtL,-0.92,2.30,0.30,0.0),(gtR,0.92,2.30,0.30,0.0),
       (st,0.35,1.25,0.12,9.0),(dr_extra,0.0,0.8,0.0,0.0)]
MAPT=[(n,a,b,(5.5 if n=='OUT' else 2.6)) for n,a,b in MAP]
run(NAME, lambda voc: mixdown(NAME,vx,STEMS,DRUMS,bs,MAPT,vocals=voc,
    wet=0.26,decay=1.8,wide=3.0,drum_gain=0.95,bass_gain=0.95,crush_amt=0.16,
    rms_target=0.205), MAPT)
