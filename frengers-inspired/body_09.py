# ============================================================ BAI 9: SHE SPINS IN THE MOONLIGHT
# Model: Mew - "She Spider" (Frengers 2003) - D major, ~74 BPM half-time
#   intro D-G-A-F#-G-A; verse Bm-A-Em-D-F#; chorus D-G-Em-Bm-A; F#/Bb chromatic
#   (per Songsterr); bass 8ths D2-D3 octave (do tu stem)
#   spacious: tackpiano + organ + strings; drums half-time, toms TO, fill sparse
BAR=4.0
NAME="09-she-spins-in-the-moonlight"
SECS=[('IN',8),('V1',8),('V2',8),('CH',8),('V3',8),('CH2',8),('BR',8),('CH3',8),('OUT',6)]
S={}; _b=0.0
for _n,_c in SECS: S[_n]=_b; _b+=_c*BAR
END=_b
configure(74,74,END+3)
MAP=[(n,S[n],S[n]+c*BAR) for n,c in SECS]
def bar_at(sec,i): return S[sec]+i*BAR
print(NAME,int(END/BAR),"bars ->",round(TOTAL,1),"s")

INTRO=[[nn('D3'),nn('F#4'),nn('A4')],[nn('G2'),nn('B3'),nn('D4')],[nn('A2'),nn('C#4'),nn('E4')],[nn('F#2'),nn('A3'),nn('C#4')]]
VERSE=[[nn('B2'),nn('D4'),nn('F#4')],[nn('A2'),nn('C#4'),nn('E4')],[nn('E3'),nn('G4'),nn('B4')],[nn('D3'),nn('F#4'),nn('A4')],[nn('F#2'),nn('A3'),nn('C#4')]]
CHORUS=[[nn('D3'),nn('F#4'),nn('A4')],[nn('G2'),nn('B3'),nn('D4')],[nn('E3'),nn('G4'),nn('B4')],[nn('B2'),nn('D4'),nn('F#4')],[nn('A2'),nn('C#4'),nn('E4')]]
def inx(i): return INTRO[i%4]
def vch(i): return VERSE[i%5]
def cch(i): return CHORUS[i%5]

def bass8d(b,b0,root,g=0.22):
    for s in range(8):   # 8ths D2-D3 octave
        m=root+(12 if s%2==0 else 0)
        bassn(bs,T(b0+s*0.25),m,SPB(b)*0.85,hg(g))

K=Kit(seed=1219); P=Performer(K,T,SPB,TOTAL,seed=11,style='indie'); P.hum=0.72
def villa(b,lvl=0.8,arc=1.0,mode='half'):
    a=arc
    if mode=='half':    # half-time spacious: kick 1, snare 3, toms chan
        for s in range(8):
            P.H(b+s*0.5,s*2,0.6*lvl,o=0.0,art='tip',arc=a)
        P.K(b,0,0.95*lvl,a)
        P.S(b+2,8,0.7*lvl,'center',a)
        P.RD(b,0,0.4*lvl,bell=True,arc=a)
        if int(b*74/60)%4==3:
            P.TM(b+2.5,10,0.6*lvl,140); P.TM(b+3.25,13,0.7*lvl,112)
    else:               # chorus: kick 1&3, snare 3, tamb
        for s in range(16):
            P.H(b+s*0.25,s,0.5*lvl if s%2==1 else 0.35*lvl,o=0.0,art='tip',arc=a)
        P.K(b,0,1.0*lvl,a); P.K(b+2,8,0.8*lvl,a)
        P.S(b+2,8,0.85*lvl,'center',a)
        P.TB(b+3.5,14,0.5*lvl,a)
        P.RD(b,0,0.45*lvl,bell=True,arc=a)

vn=buf(); gtL=buf(); gtR=buf(); st=buf(); bs=buf(); vx=buf(); dr_extra=buf()

# ---- INTRO: tackpiano + organ, D-G-A-F# ----
for i in range(8):
    b=bar_at('IN',i); c=inx(i)
    chord0(tackpiano,gtL,b+0.3,c,SPB(b)*2.5,hg(0.06))
    for _k,_m in enumerate([c[0],c[2],c[1],c[2]]):
        tackpiano(gtR,ht(b+0.32,j=0.006)+_k*0.06,_m,SPB(b)*0.7,hg(0.065),seed=_k+9)
    organ(st,T(b+1),c,SPB(b)*2.0,hg(0.04))
    bass8d(b,b,c[0],0.16)
    strings(st,T(b),[c[0],c[2]],SPB(b)*3.6,hg(0.04),atk=0.8,seed=i+20)
    villa(b,hg(0.4),arc=0.65,mode='half')
# ---- V1 ----
for i in range(8):
    b=bar_at('V1',i); c=vch(i)
    chord0(tackpiano,gtL,b+0.3,c,SPB(b)*2.5,hg(0.065))
    for _k,_m in enumerate([c[0],c[2],c[1],c[2]]):
        tackpiano(gtR,ht(b+0.32,j=0.006)+_k*0.06,_m,SPB(b)*0.7,hg(0.07),seed=_k+9)
    bass8d(b,b,c[0])
    strings(st,T(b),[c[0],c[2]],SPB(b)*3.6,hg(0.05),atk=0.7,seed=i+40)
    villa(b,hg(0.52),arc=0.82,mode='half')
    if i%4==0:
        line(vx,b,[(0,1.5,'F#4','a',''),(1.5,1.0,'G4','o',''),(2.5,1.5,'A4','a',''),(4.0,1.0,'F#4','e',''),(5.0,3.0,'D4','a','')],
             g=0.155,style='falsetto',breath=0.3,seedbase=10+i)
# ---- V2 ----
for i in range(8):
    b=bar_at('V2',i); c=vch(i)
    chord0(tackpiano,gtL,b+0.3,c,SPB(b)*2.5,hg(0.07))
    for _k,_m in enumerate([c[0],c[2],c[1],c[2]]):
        tackpiano(gtR,ht(b+0.32,j=0.006)+_k*0.06,_m,SPB(b)*0.7,hg(0.075),seed=_k+9)
    glassarp(st,T(b+0.5),c[2]+12,SPB(b)*2.0,hg(0.05),seed=i)
    glock(st,T(b+2),c[2]+12,SPB(b)*1.5,hg(0.05),seed=i+5)
    bass8d(b,b,c[0])
    strings(st,T(b),[c[0],c[2]],SPB(b)*3.6,hg(0.055),atk=0.6,seed=i+60)
    villa(b,hg(0.56),arc=0.88,mode='half')
    line(vx,b,[(0,1.0,'F#4','o',''),(1.0,1.0,'A4','a',''),(2.0,1.5,'G4','e',''),(3.5,1.0,'E4','a',''),(4.5,3.5,'D4','i','')],
         g=0.16,style='falsetto',breath=0.3,seedbase=100+i)
# ---- CH ----
for i in range(8):
    b=bar_at('CH',i); c=cch(i)
    chord0(tackpiano,gtL,b+0.3,c,SPB(b)*2.5,hg(0.075))
    for _k,_m in enumerate([c[0],c[2],c[1],c[2]]):
        tackpiano(gtR,ht(b+0.32,j=0.006)+_k*0.06,_m,SPB(b)*0.7,hg(0.08),seed=_k+9)
    organ(st,T(b+1),c,SPB(b)*2.0,hg(0.05))
    strings(st,T(b),c,SPB(b)*3.6,hg(0.06),atk=0.5,seed=i+80)
    bass8d(b,b,c[0],0.26)
    villa(b,hg(0.65),arc=0.95,mode='chorus')
    if i%4==0:
        line(vx,b,[(0,1.0,'A4','a',''),(1.0,1.0,'B4','o',''),(2.0,1.5,'A4','a',''),(3.5,1.0,'F#4','i',''),(4.5,3.5,'D4','a','')],
             g=0.165,style='falsetto',breath=0.32,seedbase=200+i)
# ---- V3 ----
for i in range(8):
    b=bar_at('V3',i); c=vch(i)
    chord0(tackpiano,gtL,b+0.3,c,SPB(b)*2.5,hg(0.07))
    for _k,_m in enumerate([c[0],c[2],c[1],c[2]]):
        tackpiano(gtR,ht(b+0.32,j=0.006)+_k*0.06,_m,SPB(b)*0.7,hg(0.075),seed=_k+9)
    bass8d(b,b,c[0])
    strings(st,T(b),[c[0],c[2]],SPB(b)*3.6,hg(0.055),atk=0.6,seed=i+100)
    villa(b,hg(0.58),arc=0.9,mode='half')
    line(vx,b,[(0,1.0,'F#4','a',''),(1.0,1.0,'A4','e',''),(2.0,1.5,'B4','o',''),(3.5,1.0,'A4','a',''),(4.5,3.5,'F#4','i','n')],
         g=0.16,style='falsetto',breath=0.3,seedbase=300+i)
# ---- CH2 ----
for i in range(8):
    b=bar_at('CH2',i); c=cch(i)
    chord0(tackpiano,gtL,b+0.3,c,SPB(b)*2.5,hg(0.08))
    for _k,_m in enumerate([c[0],c[2],c[1],c[2]]):
        tackpiano(gtR,ht(b+0.32,j=0.006)+_k*0.06,_m,SPB(b)*0.7,hg(0.085),seed=_k+9)
    organ(st,T(b+1),c,SPB(b)*2.0,hg(0.055))
    strings(st,T(b),c,SPB(b)*3.6,hg(0.065),atk=0.4,seed=i+120)
    glassarp(st,T(b+0.5),c[2]+12,SPB(b)*2.0,hg(0.055),seed=i+40)
    glock(st,T(b+2),c[2]+12,SPB(b)*1.5,hg(0.055),seed=i+9)
    bass8d(b,b,c[0],0.28)
    villa(b,hg(0.7),arc=1.0,mode='chorus')
    if i==3: P.fill(b+2.0,2.0,'tom',1.0,next_crash_beat=b+4)
    line(vx,b,[(0,1.0,'A4','a',''),(1.0,1.0,'B4','a',''),(2.0,1.5,'C#5','i',''),(3.5,1.0,'A4','a',''),(4.5,3.5,'F#4','a','')],
         g=0.17,style='falsetto',breath=0.34,seedbase=400+i)
# ---- BR: F#-G-A (chromatic F#/Bb feel) ----
BRC=[[nn('F#2'),nn('A3'),nn('C#4')],[nn('G2'),nn('B3'),nn('D4')],[nn('A2'),nn('C#4'),nn('E4')],[nn('A#2'),nn('D4'),nn('F#4')]]
for i in range(8):
    b=bar_at('BR',i); c=BRC[i%4]
    organ(gtL,ht(b,j=0.005),c,SPB(b)*2.0,hg(0.06))
    organ(gtR,ht(b+0.01,j=0.005),c,SPB(b)*2.0,hg(0.06))
    strings(st,T(b),c,SPB(b)*3.6,hg(0.06),atk=0.5,seed=i+140)
    bass8d(b,b,c[0],0.24)
    villa(b,hg(0.68),arc=1.0,mode='chorus')
    if i%4==2:
        line(vx,b,[(0,2.0,'C#5','o',''),(2.0,2.0,'D5','a',''),(4.0,3.0,'A4','e','v')],
             g=0.165,style='falsetto',breath=0.32,seedbase=500+i)
# ---- CH3 ----
for i in range(8):
    b=bar_at('CH3',i); c=cch(i)
    chord0(tackpiano,gtL,b+0.3,c,SPB(b)*2.5,hg(0.085))
    for _k,_m in enumerate([c[0],c[2],c[1],c[2]]):
        tackpiano(gtR,ht(b+0.32,j=0.006)+_k*0.06,_m,SPB(b)*0.7,hg(0.09),seed=_k+9)
    strings(st,T(b),c+[x+12 for x in c[:2]],SPB(b)*3.6,hg(0.07),atk=0.35,seed=i+160)
    glassarp(st,T(b+0.5),c[2]+12,SPB(b)*2.0,hg(0.06),seed=i+60)
    glock(st,T(b+1),c[2]+12,SPB(b)*1.5,hg(0.06),seed=i+13)
    glock(st,T(b+3),c[2]+12,SPB(b)*1.2,hg(0.05),seed=i+17)
    bass8d(b,b,c[0],0.3)
    villa(b,hg(0.75),arc=1.0,mode='chorus')
    if i==2: P.fill(b+2.0,2.0,'burst32',1.0,next_crash_beat=b+4)
    line(vx,b,[(0,1.0,'A4','a',''),(1.0,1.0,'D5','o',''),(2.0,1.5,'C#5','a',''),(3.5,1.0,'B4','i',''),(4.5,3.5,'A4','a','')],
         g=0.17,style='falsetto',breath=0.36,seedbase=600+i)
# ---- OUT: intro quay lai, fade ----
for i in range(6):
    b=bar_at('OUT',i); c=inx(i%4)
    chord0(tackpiano,gtL,b+0.3,c,SPB(b)*2.5,hg(0.06))
    for _k,_m in enumerate([c[0],c[2],c[1],c[2]]):
        tackpiano(gtR,ht(b+0.32,j=0.006)+_k*0.06,_m,SPB(b)*0.7,hg(0.065),seed=_k+9)
    bass8d(b,b,c[0],0.16)
    strings(st,T(b),c,SPB(b)*3.6,hg(0.045),atk=0.8,seed=i+180)
    villa(b,hg(0.42),arc=0.65,mode='half')

P.apply_chokes()
P.bus['hat']=P.bus['hat']*2.6
DRUMS=mix_kit(P.bus,room_amount=0.27,oh_amount=1.0,lpf=15500)
DRUMS=DRUMS+hp(_fit(P.bus['hat'],len(DRUMS)),8000,2)*0.90
DRUMS=DRUMS*(0.052/max(rms_(DRUMS),1e-9))
bs=bs*(0.070/max(rms_(bs),1e-9))
noise_sw(dr_extra,0,T(END),0.004,True,90,1600)

STEMS=[(vn,-0.35,0.82,0.34,0.0),(gtL,-0.92,1.80,0.30,0.0),(gtR,0.92,1.80,0.30,0.0),
       (st,0.35,1.25,0.12,9.0),(dr_extra,0.0,0.8,0.0,0.0)]
MAPT=[(n,a,b,(4.5 if n=='OUT' else 2.8)) for n,a,b in MAP]
run(NAME, lambda voc: mixdown(NAME,vx,STEMS,DRUMS,bs,MAPT,vocals=voc,
    wet=0.28,decay=1.9,wide=2.8,drum_gain=0.95,bass_gain=0.95,crush_amt=0.12,
    rms_target=0.195), MAPT)
