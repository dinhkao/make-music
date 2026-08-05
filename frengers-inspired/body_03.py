# ============================================================ BAI 3: SNOWFLAKES IN JULY
# Model: Mew - "Snow Brigade" (Frengers 2003) - A minor, 123 BPM
#   verse Am-F-G-Dm (bass root + chromatic F#2-G2-G#2 pass), chorus
#   F-Am-G-Em-F-C-G-Em-F-G (per CifraClub)
#   DIEM NHAN: chant "I will find you in the snow" lap 8 lan lien tuc (nhu
#   "I'll find you somewhere" cua Mew) - lap lam cao trao
#   drums: stomping backbeat + tambourine, toms vao chorus (Nick Villa)
BAR=4.0
NAME="03-snowflakes-in-july"
SECS=[('IN',8),('V1',8),('V2',8),('CH',8),('V3',8),('CH2',8),('BR',8),('CH3',8),('CHANT',16),('OUT',8)]
S={}; _b=0.0
for _n,_c in SECS: S[_n]=_b; _b+=_c*BAR
END=_b
configure(123,123,END+3)
MAP=[(n,S[n],S[n]+c*BAR) for n,c in SECS]
def bar_at(sec,i): return S[sec]+i*BAR
print(NAME,int(END/BAR),"bars ->",round(TOTAL,1),"s")

VERSE=[[nn('A2'),nn('C4'),nn('E4')],[nn('F2'),nn('A3'),nn('C4')],[nn('G2'),nn('B3'),nn('D4')],[nn('D3'),nn('F4'),nn('A4')]]
CHORUS=[[nn('F2'),nn('A3'),nn('C4')],[nn('A2'),nn('C4'),nn('E4')],[nn('G2'),nn('B3'),nn('D4')],[nn('E3'),nn('G4'),nn('B4')],
        [nn('F2'),nn('A3'),nn('C4')],[nn('C3'),nn('E4'),nn('G4')],[nn('G2'),nn('B3'),nn('D4')],[nn('E3'),nn('G4'),nn('B4')],
        [nn('F2'),nn('A3'),nn('C4')],[nn('G2'),nn('B3'),nn('D4')]]
def vch(i): return VERSE[i%4]
def cch(i): return CHORUS[i%8]

K=Kit(seed=1213); P=Performer(K,T,SPB,TOTAL,seed=11,style='indie'); P.hum=0.72
def villa(b,lvl=0.8,arc=1.0,mode='stomp'):
    a=arc
    if mode=='stomp':   # verse: backbeat + tambourine + kick offbeat
        for s in range(16):
            P.H(b+s*0.25,s,0.5*lvl if s%2==1 else 0.35*lvl,o=0.0,art='tip',arc=a)
        P.K(b,0,0.9*lvl,a); P.K(b+1.5,6,0.5*lvl,a); P.K(b+2.5,10,0.55*lvl,a)
        P.S(b+1,4,0.75*lvl,'center',a); P.S(b+3,12,0.8*lvl,'center',a)
        if int(b*123/60)%4==3: P.TB(b+0.5,2,0.5*lvl,a)
    else:               # chorus: stomping, toms, tamb o nhung phach lech
        for s in range(16):
            P.H(b+s*0.25,s,0.62*lvl if s%4==0 else 0.44*lvl,o=0.0,art=('edge' if s%4==0 else 'tip'),arc=a)
        P.K(b,0,1.0*lvl,a); P.K(b+1.25,5,0.5*lvl,a); P.K(b+2,8,0.75*lvl,a); P.K(b+3.25,13,0.6*lvl,a)
        P.S(b+1,4,0.95*lvl,'center',a); P.S(b+3,12,1.0*lvl,'center',a)
        P.S(b+0.5,2,0.3*lvl,'ghost',a); P.S(b+2.5,10,0.28*lvl,'ghost',a)
        P.TB(b+1.75,7,0.55*lvl,a); P.TB(b+2.75,11,0.5*lvl,a)
        if int(b*123/60)%4==3:
            P.TM(b+2.5,10,0.7*lvl,140); P.TM(b+3.25,13,0.8*lvl,112)

vn=buf(); gtL=buf(); gtR=buf(); st=buf(); bs=buf(); vx=buf(); dr_extra=buf()

# ---- INTRO: glock melody tren Am pad ----
GL=[nn('C5'),nn('A4'),nn('G4'),nn('E4')]
for i in range(8):
    b=bar_at('IN',i)
    glock(st,T(b),GL[i%4],SPB(b)*2.2,hg(0.07),seed=i)
    strings(st,T(b),vch(i),SPB(b)*3.4,hg(0.045),atk=0.8,seed=i)
    bassn(bs,T(b+2),nn('A2'),SPB(b)*1.5,hg(0.14))
    villa(b,hg(0.4),arc=0.65,mode='stomp')
# ---- V1 ----
for i in range(8):
    b=bar_at('V1',i); c=vch(i)
    arp8(jangle,gtL,b,c,SPB(b)*0.8,hg(0.085),i)
    arp8(jangle,gtR,b+0.009,c,SPB(b)*0.8,hg(0.085),i+50)
    bassn(bs,T(b+0.25),c[0],SPB(b)*0.9,hg(0.18))
    strings(st,T(b),[c[0],c[2]],SPB(b)*3.4,hg(0.035),atk=0.7,seed=i+20)
    villa(b,hg(0.55),arc=0.85,mode='stomp')
    if i%4==0:
        line(vx,b,[(0,.75,'E4','a',''),(.75,.5,'C4','o',''),(1.25,1.0,'D4','a',''),(2.5,.75,'E4','e',''),(3.25,.75,'G4','a','')],
             g=0.145,style='falsetto',breath=0.3,seedbase=10+i)
# ---- V2 ----
for i in range(8):
    b=bar_at('V2',i); c=vch(i)
    arp8(jangle,gtL,b,c,SPB(b)*0.8,hg(0.09),i)
    arp8(jangle,gtR,b+0.009,c,SPB(b)*0.8,hg(0.09),i+50)
    glassarp(st,T(b+0.5),c[2]+12,SPB(b)*1.5,hg(0.05),seed=i)
    bassn(bs,T(b+0.25),c[0],SPB(b)*0.9,hg(0.19))
    strings(st,T(b),[c[0],c[2]],SPB(b)*3.4,hg(0.04),atk=0.6,seed=i+40)
    villa(b,hg(0.6),arc=0.9,mode='stomp')
    line(vx,b,[(0,.5,'E4','o',''),(.5,.75,'G4','a',''),(1.25,.5,'F4','e',''),(2.0,.5,'C4','a',''),(2.75,1.25,'D4','i','')],
         g=0.15,style='falsetto',breath=0.3,seedbase=100+i)
# ---- CH ----
for i in range(8):
    b=bar_at('CH',i); c=cch(i)
    strum8(crunch,gtL,b,c,SPB(b)*0.7,hg(0.11),i)
    strum8(crunch,gtR,b+0.011,c,SPB(b)*0.7,hg(0.11),i+50)
    strings(st,T(b),c,SPB(b)*3.4,hg(0.05),atk=0.35,seed=i+60)
    bassn(bs,T(b+0.25),c[0],SPB(b)*0.9,hg(0.24))
    villa(b,hg(0.75),arc=1.0,mode='chorus')
    if i%4==0:
        line(vx,b,[(0,.5,'A4','a',''),(.5,.5,'C5','o',''),(1.0,.75,'A4','a',''),(1.75,.5,'G4','i',''),(2.5,1.5,'E4','a','')],
             g=0.15,style='falsetto',breath=0.32,seedbase=200+i)
# ---- V3 ----
for i in range(8):
    b=bar_at('V3',i); c=vch(i)
    arp8(jangle,gtL,b,c,SPB(b)*0.8,hg(0.09),i)
    arp8(jangle,gtR,b+0.009,c,SPB(b)*0.8,hg(0.09),i+50)
    strings(st,T(b),[c[0],c[2]],SPB(b)*3.4,hg(0.045),atk=0.6,seed=i+80)
    bassn(bs,T(b+0.25),c[0],SPB(b)*0.9,hg(0.2))
    villa(b,hg(0.62),arc=0.92,mode='stomp')
    line(vx,b,[(0,.5,'E4','a',''),(.5,.75,'G4','e',''),(1.25,.5,'A4','o',''),(2.0,.75,'G4','a',''),(2.75,1.25,'E4','i','n')],
         g=0.155,style='falsetto',breath=0.3,seedbase=300+i)
# ---- CH2 ----
for i in range(8):
    b=bar_at('CH2',i); c=cch(i)
    strum8(crunch,gtL,b,c,SPB(b)*0.7,hg(0.12),i)
    strum8(crunch,gtR,b+0.011,c,SPB(b)*0.7,hg(0.12),i+50)
    strings(st,T(b),c,SPB(b)*3.4,hg(0.055),atk=0.3,seed=i+100)
    bassn(bs,T(b+0.25),c[0],SPB(b)*0.9,hg(0.26))
    villa(b,hg(0.82),arc=1.0,mode='chorus')
    if i==3: P.fill(b+2.0,1.5,'tom',1.0,next_crash_beat=b+4)
    line(vx,b,[(0,.5,'A4','a',''),(.5,.5,'C5','a',''),(1.0,.75,'A4','i',''),(1.75,.5,'G4','a',''),(2.5,1.5,'E4','a','')],
         g=0.155,style='falsetto',breath=0.34,seedbase=400+i)
# ---- BR: C-G-Am-Em (nang len) ----
BRC=[[nn('C3'),nn('E4'),nn('G4')],[nn('G2'),nn('B3'),nn('D4')],[nn('A2'),nn('C4'),nn('E4')],[nn('E3'),nn('G4'),nn('B4')]]
for i in range(8):
    b=bar_at('BR',i); c=BRC[i%4]
    organ(gtL,ht(b,j=0.005),c,SPB(b)*1.8,hg(0.05))
    organ(gtR,ht(b+0.01,j=0.005),c,SPB(b)*1.8,hg(0.05))
    strings(st,T(b),c,SPB(b)*3.4,hg(0.05),atk=0.5,seed=i+120)
    bassn(bs,T(b+0.25),c[0],SPB(b)*0.9,hg(0.22))
    villa(b,hg(0.7),arc=0.95,mode='chorus')
    if i%4==2:
        line(vx,b,[(0,1.0,'G4','o',''),(1.0,1.0,'A4','a',''),(2.0,2.0,'C5','e','v')],
             g=0.15,style='falsetto',breath=0.32,seedbase=500+i)
# ---- CH3 ----
for i in range(8):
    b=bar_at('CH3',i); c=cch(i)
    strum8(crunch,gtL,b,c,SPB(b)*0.7,hg(0.13),i)
    strum8(crunch,gtR,b+0.011,c,SPB(b)*0.7,hg(0.13),i+50)
    strings(st,T(b),c+[x+12 for x in c[:2]],SPB(b)*3.4,hg(0.065),atk=0.25,seed=i+140)
    bassn(bs,T(b+0.25),c[0],SPB(b)*0.9,hg(0.28))
    villa(b,hg(0.9),arc=1.0,mode='chorus')
    if i==2: P.fill(b+2.0,2.0,'burst32',1.0,next_crash_beat=b+4)
    line(vx,b,[(0,.5,'A4','a',''),(.5,.5,'C5','o',''),(1.0,.75,'D5','a',''),(1.75,.5,'C5','i',''),(2.5,1.5,'A4','a','')],
         g=0.16,style='falsetto',breath=0.36,seedbase=600+i)
# ---- CHANT: "I will find you in the snow" x8 (high trao, nhu Mew) ----
for i in range(16):
    b=bar_at('CHANT',i); c=vch(i if i%2==0 else 1)
    strum8(crunch,gtL,b,c,SPB(b)*0.7,hg(0.13),i)
    strum8(crunch,gtR,b+0.011,c,SPB(b)*0.7,hg(0.13),i+50)
    strings(st,T(b),c,SPB(b)*3.4,hg(0.06),atk=0.3,seed=i+160)
    bassn(bs,T(b+0.25),c[0],SPB(b)*0.9,hg(0.26))
    glock(st,T(b+1),c[2]+12,SPB(b)*1.2,hg(0.055),seed=i+5)
    villa(b,hg(0.9),arc=1.0,mode='chorus')
    if i%2==0:
        line(vx,b,[(0,.5,'A4','a',''),(.5,.5,'A4','a',''),(1.0,.5,'G4','o',''),(1.5,.5,'E4','e',''),(2.0,.75,'G4','a',''),(2.75,1.25,'A4','o','')],
             g=0.15,style='falsetto',breath=0.3,seedbase=700+i//2)
    if i%4==3: P.fill(b+3.0,1.0,'snare',0.7)
# ---- OUT: glock quay lai, fade ----
for i in range(8):
    b=bar_at('OUT',i)
    glock(st,T(b),GL[i%4],SPB(b)*2.5,hg(0.075),seed=i+50)
    strings(st,T(b),vch(i%2),SPB(b)*3.4,hg(0.05),atk=0.6,seed=i+180)
    bassn(bs,T(b+2),nn('A2'),SPB(b)*1.5,hg(0.16))
    villa(b,hg(0.5),arc=0.7,mode='stomp')

P.apply_chokes()
P.bus['hat']=P.bus['hat']*2.6
DRUMS=mix_kit(P.bus,room_amount=0.25,oh_amount=1.0,lpf=15500)
DRUMS=DRUMS+hp(_fit(P.bus['hat'],len(DRUMS)),8000,2)*0.90
DRUMS=DRUMS*(0.052/max(rms_(DRUMS),1e-9))
bs=bs*(0.075/max(rms_(bs),1e-9))
noise_sw(dr_extra,0,T(END),0.004,True,90,1600)

STEMS=[(vn,-0.35,0.78,0.38,0.0),(gtL,-0.92,2.30,0.30,0.0),(gtR,0.92,2.30,0.30,0.0),
       (st,0.35,1.25,0.12,9.0),(dr_extra,0.0,0.8,0.0,0.0)]
MAPT=[(n,a,b,(5.0 if n in('CHANT','OUT') else 2.6)) for n,a,b in MAP]
run(NAME, lambda voc: mixdown(NAME,vx,STEMS,DRUMS,bs,MAPT,vocals=voc,
    wet=0.26,decay=1.8,wide=3.0,drum_gain=0.95,bass_gain=0.95,crush_amt=0.16,
    rms_target=0.205), MAPT)
