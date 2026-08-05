# ============================================================ BAI 8: SHE CAME HOME IN WINTER
# Model: Mew - "She Came Home for Christmas" (Frengers 2003) - F# major, 136 BPM
#   loop B-F#-E-F# (IV-I-bVII-I) + doan C#m; bass 8ths pedal C#2 (do tu stem)
#   gentle floating: glock + strings + mellotron, rim shots/cross-stick, shaker
#   tuyet doi khong crunch; giong nhe nang, repetitiv
BAR=4.0
NAME="08-she-came-home-in-winter"
SECS=[('IN',8),('V1',8),('V2',8),('CH',8),('V3',8),('CH2',8),('BR',8),('CH3',8),('V4',8),('CH4',8),('OUT',12)]
S={}; _b=0.0
for _n,_c in SECS: S[_n]=_b; _b+=_c*BAR
END=_b
configure(136,136,END+3)
MAP=[(n,S[n],S[n]+c*BAR) for n,c in SECS]
def bar_at(sec,i): return S[sec]+i*BAR
print(NAME,int(END/BAR),"bars ->",round(TOTAL,1),"s")

LOOP=[[nn('B2'),nn('D#4'),nn('F#4')],[nn('F#2'),nn('A3'),nn('C#4')],[nn('E2'),nn('G#3'),nn('B3')],[nn('F#2'),nn('A3'),nn('C#4')]]
CM=[[nn('C#3'),nn('E4'),nn('G#4')],[nn('F#2'),nn('A3'),nn('C#4')]]
BRC=[[nn('G#2'),nn('B3'),nn('D#4')],[nn('E2'),nn('G#3'),nn('B3')],[nn('B2'),nn('D#4'),nn('F#4')],[nn('F#2'),nn('A3'),nn('C#4')]]
def lpch(i): return LOOP[i%4]
def cm(i): return CM[i%2]
def brc(i): return BRC[i%4]

def basspedal(b,b0,g=0.2,root=nn('C#2')):   # 8ths pedal C#2 gentle
    for s in range(8):
        fingerbass(bs,T(b0+s*0.25),root,SPB(b)*0.75,hg(g),dead=True,seed=s)

K=Kit(seed=1218); P=Performer(K,T,SPB,TOTAL,seed=11,style='indie'); P.hum=0.68
def villa(b,lvl=0.7,arc=1.0,mode='gentle'):
    a=arc
    if mode=='gentle':   # rim/cross-stick + shaker, kick 1&3 nhe
        for s in range(8):
            P.H(b+s*0.5,s*2,0.28*lvl,o=0.0,art='tip',arc=a)
        P.K(b,0,0.6*lvl,a); P.K(b+2,8,0.5*lvl,a)
        P.S(b+1,4,0.5*lvl,'rim',a); P.S(b+3,12,0.55*lvl,'rim',a)
        P.SH(b+0.25,1,0.35*lvl,a); P.SH(b+2.25,9,0.35*lvl,a)
    else:                # chorus: snare that nhung nhe, kick 8ths
        for s in range(16):
            P.H(b+s*0.25,s,0.4*lvl if s%4==0 else 0.28*lvl,o=0.0,art='tip',arc=a)
        P.K(b,0,0.8*lvl,a); P.K(b+1.5,6,0.4*lvl,a); P.K(b+2.5,10,0.45*lvl,a); P.K(b+3.5,14,0.4*lvl,a)
        P.S(b+1,4,0.7*lvl,'center',a); P.S(b+3,12,0.75*lvl,'center',a)
        P.TB(b+1.75,7,0.4*lvl,a); P.TB(b+2.75,11,0.35*lvl,a)

vn=buf(); gtL=buf(); gtR=buf(); st=buf(); bs=buf(); vx=buf(); dr_extra=buf()

# ---- INTRO: glock + strings, A5 giu ----
GL=[nn('F#5'),nn('E5'),nn('C#5'),nn('A4')]
for i in range(8):
    b=bar_at('IN',i); c=lpch(i)
    glock(st,T(b),GL[i%4],SPB(b)*2.5,hg(0.07),seed=i)
    chord0(wurli,gtL,b+0.3,c,SPB(b)*3.0,hg(0.05),det=-8)
    for _k,_m in enumerate([c[0],c[2],c[1],c[2]]):
        wurli(gtR,ht(b+0.32,j=0.006)+_k*0.06,_m,SPB(b)*0.8,hg(0.055),det=8)
    strings(st,T(b),c,SPB(b)*3.6,hg(0.045),atk=0.9,seed=i+20)
    basspedal(b,b,0.14)
    villa(b,hg(0.4),arc=0.65,mode='gentle')
# ---- V1 ----
for i in range(8):
    b=bar_at('V1',i); c=lpch(i)
    chord0(wurli,gtL,b+0.3,c,SPB(b)*3.0,hg(0.055),det=-8)
    for _k,_m in enumerate([c[0],c[2],c[1],c[2]]):
        wurli(gtR,ht(b+0.32,j=0.006)+_k*0.06,_m,SPB(b)*0.8,hg(0.06),det=8)
    strings(st,T(b),c,SPB(b)*3.6,hg(0.05),atk=0.8,seed=i+40)
    basspedal(b,b)
    villa(b,hg(0.5),arc=0.8,mode='gentle')
    if i%4==0:
        line(vx,b,[(0,.75,'C#4','a',''),(.75,.5,'D#4','o',''),(1.25,1.0,'A#3','a',''),(2.5,.75,'C#4','e',''),(3.25,.75,'B3','a','')],
             g=0.145,style='falsetto',breath=0.3,seedbase=10+i)
# ---- V2 ----
for i in range(8):
    b=bar_at('V2',i); c=cm(i)
    chord0(wurli,gtL,b+0.3,c,SPB(b)*3.0,hg(0.06),det=-8)
    for _k,_m in enumerate([c[0],c[2],c[1],c[2]]):
        wurli(gtR,ht(b+0.32,j=0.006)+_k*0.06,_m,SPB(b)*0.8,hg(0.065),det=8)
    mellotron(st,T(b),c[2],SPB(b)*3.4,hg(0.045),kind='choir',seed=i+60)
    strings(st,T(b),c,SPB(b)*3.6,hg(0.055),atk=0.7,seed=i+60)
    basspedal(b,b)
    villa(b,hg(0.55),arc=0.85,mode='gentle')
    line(vx,b,[(0,.5,'C#4','o',''),(.5,.75,'E4','a',''),(1.25,.5,'D#4','e',''),(2.0,.5,'B3','a',''),(2.75,1.25,'C#4','i','')],
         g=0.15,style='falsetto',breath=0.3,seedbase=100+i)
# ---- CH ----
for i in range(8):
    b=bar_at('CH',i); c=lpch(i)
    chord0(wurli,gtL,b+0.3,c,SPB(b)*3.0,hg(0.065),det=-8)
    for _k,_m in enumerate([c[0],c[2],c[1],c[2]]):
        wurli(gtR,ht(b+0.32,j=0.006)+_k*0.06,_m,SPB(b)*0.8,hg(0.07),det=8)
    strings(st,T(b),c,SPB(b)*3.6,hg(0.06),atk=0.6,seed=i+80)
    glassarp(st,T(b+1),c[2]+12,SPB(b)*1.8,hg(0.05),seed=i)
    basspedal(b,b,0.22)
    villa(b,hg(0.6),arc=0.95,mode='chorus')
    if i%4==0:
        line(vx,b,[(0,.5,'F#4','a',''),(.5,.5,'F#4','o',''),(1.0,.75,'E4','a',''),(1.75,.5,'C#4','i',''),(2.5,1.5,'B3','a','')],
             g=0.155,style='falsetto',breath=0.32,seedbase=200+i)
# ---- V3 ----
for i in range(8):
    b=bar_at('V3',i); c=lpch(i)
    chord0(wurli,gtL,b+0.3,c,SPB(b)*3.0,hg(0.06),det=-8)
    for _k,_m in enumerate([c[0],c[2],c[1],c[2]]):
        wurli(gtR,ht(b+0.32,j=0.006)+_k*0.06,_m,SPB(b)*0.8,hg(0.065),det=8)
    strings(st,T(b),c,SPB(b)*3.6,hg(0.055),atk=0.7,seed=i+100)
    basspedal(b,b)
    villa(b,hg(0.55),arc=0.85,mode='gentle')
    line(vx,b,[(0,.5,'C#4','a',''),(.5,.75,'E4','e',''),(1.25,.5,'F#4','o',''),(2.0,.75,'E4','a',''),(2.75,1.25,'C#4','i','n')],
         g=0.155,style='falsetto',breath=0.3,seedbase=300+i)
# ---- CH2 ----
for i in range(8):
    b=bar_at('CH2',i); c=lpch(i)
    chord0(wurli,gtL,b+0.3,c,SPB(b)*3.0,hg(0.07),det=-8)
    for _k,_m in enumerate([c[0],c[2],c[1],c[2]]):
        wurli(gtR,ht(b+0.32,j=0.006)+_k*0.06,_m,SPB(b)*0.8,hg(0.075),det=8)
    mellotron(st,T(b),c[2],SPB(b)*3.4,hg(0.05),kind='choir',seed=i+120)
    strings(st,T(b),c,SPB(b)*3.6,hg(0.065),atk=0.5,seed=i+120)
    glassarp(st,T(b+1),c[2]+12,SPB(b)*1.8,hg(0.055),seed=i+40)
    basspedal(b,b,0.24)
    villa(b,hg(0.65),arc=1.0,mode='chorus')
    if i==3: P.fill(b+2.0,1.5,'tom',0.9,next_crash_beat=b+4)
    line(vx,b,[(0,.5,'F#4','a',''),(.5,.5,'G#4','a',''),(1.0,.75,'F#4','i',''),(1.75,.5,'E4','a',''),(2.5,1.5,'C#4','a','')],
         g=0.16,style='falsetto',breath=0.34,seedbase=400+i)
# ---- BR: G#m-E-B-F# (nang len) ----
for i in range(8):
    b=bar_at('BR',i); c=brc(i)
    chord0(wurli,gtL,b+0.3,c,SPB(b)*3.0,hg(0.07),det=-8)
    for _k,_m in enumerate([c[0],c[2],c[1],c[2]]):
        wurli(gtR,ht(b+0.32,j=0.006)+_k*0.06,_m,SPB(b)*0.8,hg(0.075),det=8)
    strings(st,T(b),c,SPB(b)*3.6,hg(0.065),atk=0.6,seed=i+140)
    basspedal(b,b,0.22,root=c[0])
    villa(b,hg(0.62),arc=0.95,mode='chorus')
    if i%4==2:
        line(vx,b,[(0,1.0,'A4','o',''),(1.0,1.0,'B4','a',''),(2.0,2.0,'C#5','e','v')],
             g=0.16,style='falsetto',breath=0.32,seedbase=500+i)
# ---- CH3 ----
for i in range(8):
    b=bar_at('CH3',i); c=lpch(i)
    chord0(wurli,gtL,b+0.3,c,SPB(b)*3.0,hg(0.075),det=-8)
    for _k,_m in enumerate([c[0],c[2],c[1],c[2]]):
        wurli(gtR,ht(b+0.32,j=0.006)+_k*0.06,_m,SPB(b)*0.8,hg(0.08),det=8)
    strings(st,T(b),c+[x+12 for x in c[:2]],SPB(b)*3.6,hg(0.07),atk=0.4,seed=i+160)
    glassarp(st,T(b+1),c[2]+12,SPB(b)*1.8,hg(0.06),seed=i+60)
    basspedal(b,b,0.26)
    villa(b,hg(0.7),arc=1.0,mode='chorus')
    if i==2: P.fill(b+2.0,2.0,'burst32',0.9,next_crash_beat=b+4)
    line(vx,b,[(0,.5,'F#4','a',''),(.5,.5,'A4','o',''),(1.0,.75,'G#4','a',''),(1.75,.5,'F#4','i',''),(2.5,1.5,'E4','a','')],
         g=0.165,style='falsetto',breath=0.36,seedbase=600+i)
# ---- V4 ----
for i in range(8):
    b=bar_at('V4',i); c=lpch(i)
    chord0(wurli,gtL,b+0.3,c,SPB(b)*3.0,hg(0.06),det=-8)
    for _k,_m in enumerate([c[0],c[2],c[1],c[2]]):
        wurli(gtR,ht(b+0.32,j=0.006)+_k*0.06,_m,SPB(b)*0.8,hg(0.065),det=8)
    strings(st,T(b),c,SPB(b)*3.6,hg(0.055),atk=0.7,seed=i+100)
    basspedal(b,b)
    villa(b,hg(0.55),arc=0.85,mode='gentle')
    line(vx,b,[(0,.5,'C#4','a',''),(.5,.75,'E4','e',''),(1.25,.5,'F#4','o',''),(2.0,.75,'E4','a',''),(2.75,1.25,'C#4','i','n')],
         g=0.155,style='falsetto',breath=0.3,seedbase=330+i)
# ---- CH4 ----
for i in range(8):
    b=bar_at('CH4',i); c=lpch(i)
    chord0(wurli,gtL,b+0.3,c,SPB(b)*3.0,hg(0.075),det=-8)
    for _k,_m in enumerate([c[0],c[2],c[1],c[2]]):
        wurli(gtR,ht(b+0.32,j=0.006)+_k*0.06,_m,SPB(b)*0.8,hg(0.08),det=8)
    strings(st,T(b),c+[x+12 for x in c[:2]],SPB(b)*3.6,hg(0.07),atk=0.4,seed=i+160)
    glassarp(st,T(b+1),c[2]+12,SPB(b)*1.8,hg(0.06),seed=i+60)
    basspedal(b,b,0.26)
    villa(b,hg(0.7),arc=1.0,mode='chorus')
    if i==2: P.fill(b+2.0,2.0,'burst32',0.9,next_crash_beat=b+4)
    line(vx,b,[(0,.5,'F#4','a',''),(.5,.5,'A4','o',''),(1.0,.75,'G#4','a',''),(1.75,.5,'F#4','i',''),(2.5,1.5,'E4','a','')],
         g=0.165,style='falsetto',breath=0.36,seedbase=660+i)
# ---- V4 ----
for i in range(8):
    b=bar_at('V4',i); c=lpch(i)
    chord0(wurli,gtL,b+0.3,c,SPB(b)*3.0,hg(0.06),det=-8)
    for _k,_m in enumerate([c[0],c[2],c[1],c[2]]):
        wurli(gtR,ht(b+0.32,j=0.006)+_k*0.06,_m,SPB(b)*0.8,hg(0.065),det=8)
    strings(st,T(b),c,SPB(b)*3.6,hg(0.055),atk=0.7,seed=i+100)
    basspedal(b,b)
    villa(b,hg(0.55),arc=0.85,mode='gentle')
    line(vx,b,[(0,.5,'C#4','a',''),(.5,.75,'E4','e',''),(1.25,.5,'F#4','o',''),(2.0,.75,'E4','a',''),(2.75,1.25,'C#4','i','n')],
         g=0.155,style='falsetto',breath=0.3,seedbase=330+i)
# ---- OUT: glock + fade ----
for i in range(8):
    b=bar_at('OUT',i); c=lpch(i%4)
    glock(st,T(b),GL[i%4],SPB(b)*2.5,hg(0.075),seed=i+50)
    strings(st,T(b),c,SPB(b)*3.6,hg(0.05),atk=0.8,seed=i+180)
    basspedal(b,b,0.15)
    villa(b,hg(0.45),arc=0.7,mode='gentle')

P.apply_chokes()
P.bus['hat']=P.bus['hat']*2.6
DRUMS=mix_kit(P.bus,room_amount=0.28,oh_amount=1.0,lpf=15500)
DRUMS=DRUMS+hp(_fit(P.bus['hat'],len(DRUMS)),8000,2)*0.90
DRUMS=DRUMS*(0.042/max(rms_(DRUMS),1e-9))
bs=bs*(0.060/max(rms_(bs),1e-9))
noise_sw(dr_extra,0,T(END),0.003,True,90,1600)

STEMS=[(vn,-0.35,0.85,0.30,0.0),(gtL,-0.92,1.80,0.30,0.0),(gtR,0.92,1.80,0.30,0.0),
       (st,0.35,1.25,0.12,9.0),(dr_extra,0.0,0.8,0.0,0.0)]
MAPT=[(n,a,b,(4.5 if n=='OUT' else 2.6)) for n,a,b in MAP]
run(NAME, lambda voc: mixdown(NAME,vx,STEMS,DRUMS,bs,MAPT,vocals=voc,
    wet=0.28,decay=1.9,wide=2.8,drum_gain=0.95,bass_gain=0.95,crush_amt=0.10,
    rms_target=0.185), MAPT)
