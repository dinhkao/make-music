# ============================================================ BAI 7: SEVEN FLEW OVER THE ROOFTOPS
# Model: Mew - "Eight Flew Over, One Was Destroyed" (Frengers 2003) - B minor, 129 BPM
#   pedal drone B1 8ths (do tu stem: bass B1 lap lien tuc) - TỐI, khac het cac bai khac
#   verse: giong thap tren pedal; chorus mo ra G-A-F#-E-D (modal)
#   climax: 16th barrage full-kit (Nick Villa Tunnel Vision style) roi cat dung
#   nhac cu: fuzzbass + subbass pedal, ebow, bowed, airlead, shriek; KHONG jangle/crunch
BAR=4.0
NAME="07-seven-flew-over-the-rooftops"
SECS=[('IN',8),('V1',8),('V2',8),('CH',8),('V3',8),('CH2',8),('V4',8),('CH3',8),('CLX',18),('OUT',8)]
S={}; _b=0.0
for _n,_c in SECS: S[_n]=_b; _b+=_c*BAR
END=_b
configure(129,129,END+3)
MAP=[(n,S[n],S[n]+c*BAR) for n,c in SECS]
def bar_at(sec,i): return S[sec]+i*BAR
print(NAME,int(END/BAR),"bars ->",round(TOTAL,1),"s")

PEDAL=nn('B1')
CHC=[[nn('G2'),nn('B3'),nn('D4')],[nn('A2'),nn('C#4'),nn('E4')],[nn('F#2'),nn('A3'),nn('C#4')],[nn('E3'),nn('G4'),nn('B4')],
    [nn('D3'),nn('F#4'),nn('A4')]]
def cch(i): return CHC[i%5]

def pedal(b,b0,g=0.3,octv=0):
    for s in range(4):   # pedal B1 8ths nhe
        fuzzbass(bs,T(b0+s*0.5),PEDAL+12*octv,SPB(b)*0.8,hg(g),seed=s)

K=Kit(seed=1217); P=Performer(K,T,SPB,TOTAL,seed=11,style='indie'); P.hum=0.75
def villa(b,lvl=0.8,arc=1.0,mode='half'):
    a=arc
    if mode=='half':    # half-time: kick 1&3, snare 3, sparse
        for s in range(8):
            P.H(b+s*0.5,s*2,0.4*lvl,o=0.0,art='tip',arc=a)
        P.K(b,0,0.9*lvl,a); P.K(b+2,8,0.7*lvl,a)
        P.S(b+2,8,0.75*lvl,'center',a)
        P.RD(b,0,0.4*lvl,bell=True,arc=a)
    elif mode=='build': # busier: kick 8ths, snare 2&4
        for s in range(16):
            P.H(b+s*0.25,s,0.5*lvl if s%2==1 else 0.36*lvl,o=0.0,art='tip',arc=a)
        P.K(b,0,1.0*lvl,a); P.K(b+0.75,3,0.6*lvl,a); P.K(b+1.5,6,0.6*lvl,a); P.K(b+2.25,9,0.6*lvl,a); P.K(b+3,12,0.7*lvl,a)
        P.S(b+1,4,0.85*lvl,'center',a); P.S(b+3,12,0.9*lvl,'center',a)
        P.S(b+0.5,2,0.3*lvl,'ghost',a); P.S(b+2.5,10,0.3*lvl,'ghost',a)
    else:               # climax: 16th barrage (Tunnel Vision)
        for s in range(16):
            P.H(b+s*0.25,s,0.7*lvl,o=0.1,art='edge',arc=a)
        for s in range(16):
            if s%2==0: P.K(b+s*0.25,s,0.8*lvl,a)
            else:      P.S(b+s*0.25,s,0.55*lvl,'ghost' if s%4!=3 else 'center',a)
        P.S(b+1,4,0.95*lvl,'center',a); P.S(b+3,12,1.0*lvl,'center',a)
        P.TM(b+0.75,3,0.6*lvl,150); P.TM(b+1.25,5,0.65*lvl,128); P.TM(b+1.75,7,0.7*lvl,110)
        P.TM(b+2.25,9,0.75*lvl,96); P.TM(b+2.75,11,0.8*lvl,84); P.TM(b+3.25,13,0.85*lvl,74)
        P.CR(b+3.75,15,0.9*lvl)

vn=buf(); gtL=buf(); gtR=buf(); st=buf(); bs=buf(); vx=buf(); dr_extra=buf()

# ---- INTRO: pedal + ebow melody + bowed (toi) ----
EM=[nn('B3'),nn('C#4'),nn('D4'),nn('E4')]
for i in range(8):
    b=bar_at('IN',i)
    pedal(b,b,0.16)
    subbass(bs,T(b),PEDAL,SPB(b)*3.6,hg(0.2))
    ebow(gtL,T(b+0.5),EM[i%4],SPB(b)*2.5,hg(0.07),seed=i,atk=0.8)
    ebow(gtR,T(b+0.52),EM[i%4]+7,SPB(b)*2.5,hg(0.045),seed=i+30,atk=0.8)
    bowed(st,T(b+1),nn('F#4'),SPB(b)*2.2,hg(0.05),seed=i)
    villa(b,hg(0.35),arc=0.6,mode='half')
# ---- V1 ----
for i in range(8):
    b=bar_at('V1',i)
    pedal(b,b,0.2)
    subbass(bs,T(b),PEDAL,SPB(b)*3.6,hg(0.22))
    ebow(gtL,T(b+0.5),EM[i%4],SPB(b)*2.5,hg(0.08),seed=i+10,atk=0.7)
    strings(st,T(b),[nn('B2'),nn('D4')],SPB(b)*3.4,hg(0.035),atk=0.8,seed=i+20)
    villa(b,hg(0.5),arc=0.8,mode='half')
    if i%4==0:
        line(vx,b,[(0,.75,'B3','a',''),(.75,.5,'C#4','o',''),(1.25,1.0,'D4','a',''),(2.5,.75,'C#4','e',''),(3.25,.75,'B3','a','')],
             g=0.15,style='falsetto',breath=0.3,seedbase=10+i)
# ---- V2 ----
for i in range(8):
    b=bar_at('V2',i)
    pedal(b,b,0.22)
    subbass(bs,T(b),PEDAL,SPB(b)*3.6,hg(0.24))
    ebow(gtL,T(b+0.5),EM[i%4],SPB(b)*2.5,hg(0.09),seed=i+20,atk=0.6)
    bowed(st,T(b+1),nn('F#4'),SPB(b)*2.2,hg(0.06),seed=i)
    strings(st,T(b),[nn('B2'),nn('D4')],SPB(b)*3.4,hg(0.04),atk=0.7,seed=i+40)
    villa(b,hg(0.55),arc=0.85,mode='half')
    line(vx,b,[(0,.5,'B3','o',''),(.5,.75,'D4','a',''),(1.25,.5,'E4','e',''),(2.0,.5,'D4','a',''),(2.75,1.25,'C#4','i','')],
         g=0.155,style='falsetto',breath=0.3,seedbase=100+i)
# ---- CH: G-A-F#-E-D ----
for i in range(8):
    b=bar_at('CH',i); c=cch(i)
    pedal(b,b,0.26)
    stchord(gtL,b,c,SPB(b)*3.0,hg(0.05),atk=0.5,seed=i)
    stchord(gtR,b+0.01,c,SPB(b)*3.0,hg(0.05),atk=0.5,seed=i+50)
    airlead(vn,T(b+0.5),c[2],SPB(b)*1.8,hg(0.07),seed=i)
    fuzzbass(bs,T(b+0.25),c[0],SPB(b)*0.85,hg(0.22),seed=i)
    villa(b,hg(0.65),arc=0.95,mode='build')
    if i%4==0:
        line(vx,b,[(0,.5,'F#4','a',''),(.5,.5,'G4','o',''),(1.0,.75,'A4','a',''),(1.75,.5,'G4','i',''),(2.5,1.5,'F#4','a','')],
             g=0.16,style='falsetto',breath=0.32,seedbase=200+i)
# ---- V3 ----
for i in range(8):
    b=bar_at('V3',i)
    pedal(b,b,0.22)
    subbass(bs,T(b),PEDAL,SPB(b)*3.6,hg(0.24))
    ebow(gtL,T(b+0.5),EM[i%4],SPB(b)*2.5,hg(0.09),seed=i+30,atk=0.6)
    strings(st,T(b),[nn('B2'),nn('D4')],SPB(b)*3.4,hg(0.045),atk=0.6,seed=i+80)
    villa(b,hg(0.58),arc=0.9,mode='half')
    line(vx,b,[(0,.5,'B3','a',''),(.5,.75,'D4','e',''),(1.25,.5,'E4','o',''),(2.0,.75,'D4','a',''),(2.75,1.25,'B3','i','n')],
         g=0.16,style='falsetto',breath=0.3,seedbase=300+i)
# ---- CH2 ----
for i in range(8):
    b=bar_at('CH2',i); c=cch(i)
    pedal(b,b,0.28)
    stchord(gtL,b,c,SPB(b)*3.0,hg(0.06),atk=0.4,seed=i)
    stchord(gtR,b+0.01,c,SPB(b)*3.0,hg(0.06),atk=0.4,seed=i+50)
    airlead(vn,T(b+0.5),c[2],SPB(b)*1.8,hg(0.08),seed=i+40)
    fuzzbass(bs,T(b+0.25),c[0],SPB(b)*0.85,hg(0.24),seed=i)
    villa(b,hg(0.72),arc=1.0,mode='build')
    if i==3: P.fill(b+2.0,1.5,'tom',1.0,next_crash_beat=b+4)
    line(vx,b,[(0,.5,'F#4','a',''),(.5,.5,'G4','a',''),(1.0,.75,'A4','i',''),(1.75,.5,'B4','a',''),(2.5,1.5,'A4','a','')],
         g=0.165,style='falsetto',breath=0.34,seedbase=400+i)
# ---- V4 ----
for i in range(8):
    b=bar_at('V4',i)
    pedal(b,b,0.22)
    subbass(bs,T(b),PEDAL,SPB(b)*3.6,hg(0.24))
    ebow(gtL,T(b+0.5),EM[i%4],SPB(b)*2.5,hg(0.09),seed=i+30,atk=0.6)
    strings(st,T(b),[nn('B2'),nn('D4')],SPB(b)*3.4,hg(0.045),atk=0.6,seed=i+80)
    villa(b,hg(0.58),arc=0.9,mode='half')
    line(vx,b,[(0,.5,'B3','a',''),(.5,.75,'D4','e',''),(1.25,.5,'E4','o',''),(2.0,.75,'D4','a',''),(2.75,1.25,'B3','i','n')],
         g=0.16,style='falsetto',breath=0.3,seedbase=330+i)
# ---- CH3 ----
for i in range(8):
    b=bar_at('CH3',i); c=cch(i)
    pedal(b,b,0.28)
    stchord(gtL,b,c,SPB(b)*3.0,hg(0.06),atk=0.4,seed=i)
    stchord(gtR,b+0.01,c,SPB(b)*3.0,hg(0.06),atk=0.4,seed=i+50)
    airlead(vn,T(b+0.5),c[2],SPB(b)*1.8,hg(0.08),seed=i+40)
    fuzzbass(bs,T(b+0.25),c[0],SPB(b)*0.85,hg(0.24),seed=i)
    villa(b,hg(0.72),arc=1.0,mode='build')
    if i==3: P.fill(b+2.0,1.5,'tom',1.0,next_crash_beat=b+4)
    line(vx,b,[(0,.5,'F#4','a',''),(.5,.5,'G4','a',''),(1.0,.75,'A4','i',''),(1.75,.5,'B4','a',''),(2.5,1.5,'A4','a','')],
         g=0.165,style='falsetto',breath=0.34,seedbase=440+i)
# ---- V4 ----
for i in range(8):
    b=bar_at('V4',i)
    pedal(b,b,0.22)
    subbass(bs,T(b),PEDAL,SPB(b)*3.6,hg(0.24))
    ebow(gtL,T(b+0.5),EM[i%4],SPB(b)*2.5,hg(0.09),seed=i+30,atk=0.6)
    strings(st,T(b),[nn('B2'),nn('D4')],SPB(b)*3.4,hg(0.045),atk=0.6,seed=i+80)
    villa(b,hg(0.58),arc=0.9,mode='half')
    line(vx,b,[(0,.5,'B3','a',''),(.5,.75,'D4','e',''),(1.25,.5,'E4','o',''),(2.0,.75,'D4','a',''),(2.75,1.25,'B3','i','n')],
         g=0.16,style='falsetto',breath=0.3,seedbase=330+i)
# ---- CLX: 16th barrage + shriek ----
for i in range(12):
    b=bar_at('CLX',i); c=cch(i)
    f=min(1.3,0.9+0.04*i)
    pedal(b,b,0.3*f,octv=1)
    stchord(gtL,b,c,SPB(b)*3.0,hg(0.07*f),atk=0.3,seed=i)
    stchord(gtR,b+0.01,c,SPB(b)*3.0,hg(0.07*f),atk=0.3,seed=i+50)
    airlead(vn,T(b+0.5),c[2]+12,SPB(b)*1.8,hg(0.09*f),seed=i+60)
    fuzzbass(bs,T(b+0.25),c[0],SPB(b)*0.85,hg(0.26*f),seed=i)
    villa(b,hg(0.85*f),arc=1.0,mode='climax')
    if i>=4:
        line(vx,b,[(0,.5,'B4','a',''),(.5,.5,'B4','a',''),(1.0,.75,'A4','o',''),(1.75,.5,'G4','e',''),(2.5,1.25,'F#4','a','')],
             g=0.15,style='shout',breath=0.32,seedbase=500+i)
# ---- OUT: cat dung ----
b=bar_at('OUT',0)
P.K(b,0,1.2); P.S(b,0,1.0,'center'); P.CR(b,0,0.85,size=1.3); P.TM(b,0,0.9,90)
fuzzbass(bs,T(b),nn('B1'),SPB(b)*3.5,0.3)
strings(st,T(b),[nn('B2'),nn('D4'),nn('F#4'),nn('B4')],SPB(b)*3.4,0.06,atk=0.2,seed=7)
shriek(vx,T(b+0.4),nn('B5'),1.2,0.10)
for i in range(1,6):
    bb=bar_at('OUT',i)
    pedal(bb,bb,0.14)
    ebow(gtL,T(bb+0.5),EM[i%4],SPB(bb)*2.5,hg(0.06),seed=i,atk=1.0)
    villa(bb,hg(0.3),arc=0.5,mode='half')

P.apply_chokes()
P.bus['hat']=P.bus['hat']*2.6
DRUMS=mix_kit(P.bus,room_amount=0.26,oh_amount=1.0,lpf=15500)
DRUMS=DRUMS+hp(_fit(P.bus['hat'],len(DRUMS)),8000,2)*0.90
DRUMS=DRUMS*(0.052/max(rms_(DRUMS),1e-9))
bs=bs*(0.075/max(rms_(bs),1e-9))
noise_sw(dr_extra,0,T(END),0.005,True,70,1200)

STEMS=[(vn,-0.35,0.80,0.36,0.0),(gtL,-0.92,1.60,0.30,0.0),(gtR,0.92,1.60,0.30,0.0),
       (st,0.35,1.25,0.12,9.0),(dr_extra,0.0,0.8,0.0,0.0)]
MAPT=[(n,a,b,(2.6 if n!='CLX' else 3.2)) for n,a,b in MAP]
run(NAME, lambda voc: mixdown(NAME,vx,STEMS,DRUMS,bs,MAPT,vocals=voc,
    wet=0.28,decay=2.0,wide=2.8,drum_gain=0.95,bass_gain=0.95,crush_amt=0.18,
    rms_target=0.20), MAPT)
