# ============================================================ BAI 10: COMFORTING NOISE
# Model: Mew - "Comforting Sounds" (Frengers 2003) - A major, 80 BPM
#   verse I-iii-IV (A-C#m-D) chi DYAD 2 not (airy, incomplete - per CifraClub tab)
#   pre-chorus I-iii-vi-IV (A-C#m-F#m-D); chorus A-E-Bm-D-E
#   OUTRO CRESCENDO: A-C#m-E-D-E-Bm-D | A-C#m-E-D-E-D | A-E-Bm-D-E (per Songsterr)
#   melody 2.33 beats/note, 100% diatomic, 58% chord tone (not lo lung)
#   bass vao MUON; drums bat dau KHONG co, vao nhe, cuoi full force
#   nhac cu: glassarp dyads + ebow + strings + crunch cuoi; melody F#4 -> F#5
BAR=4.0
NAME="10-comforting-noise"
SECS=[('IN',4),('V1',8),('PRE',4),('CH',8),('V2',8),('PRE2',4),('CH2',8),('BR',8),('OUTB',24)]
S={}; _b=0.0
for _n,_c in SECS: S[_n]=_b; _b+=_c*BAR
END=_b
configure(80,80,END+3)
MAP=[(n,S[n],S[n]+c*BAR) for n,c in SECS]
def bar_at(sec,i): return S[sec]+i*BAR
print(NAME,int(END/BAR),"bars ->",round(TOTAL,1),"s")

VCH=[[nn('A2'),nn('C#4'),nn('E4')],[nn('C#3'),nn('E4'),nn('G#4')],[nn('D3'),nn('F#4'),nn('A4')]]       # A-C#m-D
PRE=[[nn('A2'),nn('C#4'),nn('E4')],[nn('C#3'),nn('E4'),nn('G#4')],[nn('F#2'),nn('A3'),nn('C#4')],[nn('D3'),nn('F#4'),nn('A4')]]
CH=[[nn('A2'),nn('C#4'),nn('E4')],[nn('E3'),nn('G#4'),nn('B4')],[nn('B2'),nn('D4'),nn('F#4')],[nn('D3'),nn('F#4'),nn('A4')],[nn('E3'),nn('G#4'),nn('B4')]]  # A-E-Bm-D-E
OUT1=[[nn('A2'),nn('C#4'),nn('E4')],[nn('C#3'),nn('E4'),nn('G#4')],[nn('E3'),nn('G#4'),nn('B4')],[nn('D3'),nn('F#4'),nn('A4')],[nn('E3'),nn('G#4'),nn('B4')],[nn('B2'),nn('D4'),nn('F#4')],[nn('D3'),nn('F#4'),nn('A4')]]
BRC=[[nn('F#2'),nn('A3'),nn('C#4')],[nn('D3'),nn('F#4'),nn('A4')],[nn('E3'),nn('G#4'),nn('B4')],[nn('A2'),nn('C#4'),nn('E4')]]
def vch(i): return VCH[i%3]
def pre(i): return PRE[i%4]
def ch(i): return CH[i%5]
def out1(i): return OUT1[i%7]
def brc(i): return BRC[i%4]

def glassdyad(b_,t0,ch,dur,g,seed):
    for k,m in enumerate(ch):
        glassarp(b_,t0+k*0.012,m,dur,g,seed=seed+k)
# melody: not dai, lơ lửng (58% chord tone) - di qua cac passing note
K=Kit(seed=1220); P=Performer(K,T,SPB,TOTAL,seed=11,style='indie'); P.hum=0.7
def villa(b,lvl=0.8,arc=1.0,mode='soft'):
    a=arc
    if mode=='soft':    # vao nhe: hat 8ths, kick 1&3
        for s in range(8):
            P.H(b+s*0.5,s*2,0.3*lvl,o=0.0,art='tip',arc=a)
        P.K(b,0,0.7*lvl,a); P.K(b+2,8,0.6*lvl,a)
        P.S(b+2,8,0.6*lvl,'center',a)
    elif mode=='full':  # chorus: backbeat that
        for s in range(16):
            P.H(b+s*0.25,s,0.5*lvl if s%4==0 else 0.36*lvl,o=0.0,art=('edge' if s%4==0 else 'tip'),arc=a)
        P.K(b,0,0.95*lvl,a); P.K(b+1.5,6,0.5*lvl,a); P.K(b+2.5,10,0.55*lvl,a)
        P.S(b+1,4,0.85*lvl,'center',a); P.S(b+3,12,0.9*lvl,'center',a)
    else:               # outro build: kick 8ths + 16th hats
        for s in range(16):
            P.H(b+s*0.25,s,0.62*lvl if s%4==0 else 0.44*lvl,o=0.0,art=('edge' if s%4==0 else 'tip'),arc=a)
            if s%2==0: P.K(b+s*0.25,s,0.75*lvl,a)
        P.S(b+1,4,0.9*lvl,'center',a); P.S(b+3,12,0.95*lvl,'center',a)
        if int(b*80/60)%4==3:
            P.TM(b+2.75,11,0.6*lvl,150); P.TM(b+3.25,13,0.7*lvl,120); P.TM(b+3.75,15,0.8*lvl,98)

vn=buf(); gtL=buf(); gtR=buf(); st=buf(); bs=buf(); vx=buf(); dr_extra=buf()

# ---- INTRO: dyads glassarp A/C#-E/G#-D/F# (airy, khong drums) ----
for i in range(4):
    b=bar_at('IN',i); c=vch(i)
    glassdyad(gtL,T(b),[c[0],c[2]],SPB(b)*2.8,hg(0.07),seed=i)
    glassdyad(gtR,T(b+0.014),[c[0],c[2]],SPB(b)*2.8,hg(0.07),seed=i+50)
    ebow(st,T(b+0.5),c[2]+12,SPB(b)*2.5,hg(0.045),seed=i,atk=1.0)
    glock(st,T(b+2),c[2]+12,SPB(b)*1.8,hg(0.045),seed=i+2)
    strings(st,T(b),[c[0],c[2]],SPB(b)*3.6,hg(0.04),atk=1.2,seed=i)
# ---- V1: + giong, van chua co drums ----
for i in range(8):
    b=bar_at('V1',i); c=vch(i)
    glassdyad(gtL,T(b),[c[0],c[2]],SPB(b)*2.8,hg(0.075),seed=i+10)
    glassdyad(gtR,T(b+0.014),[c[0],c[2]],SPB(b)*2.8,hg(0.075),seed=i+60)
    strings(st,T(b),[c[0],c[2]],SPB(b)*3.6,hg(0.05),atk=1.0,seed=i+20)
    glock(st,T(b+2),c[2]+12,SPB(b)*1.8,hg(0.05),seed=i+6)
    ebow(st,T(b+0.5),c[2]+12,SPB(b)*2.5,hg(0.05),seed=i+30,atk=0.9)
    if i%4==0:
        line(vx,b,[(0,1.5,'F#4','a',''),(1.5,1.0,'E4','o',''),(2.5,1.5,'C#4','a',''),(4.0,1.0,'D4','e',''),(5.0,3.0,'C#4','a','')],
             g=0.16,style='falsetto',breath=0.34,seedbase=10+i)
# ---- PRE: them bass nhe ----
for i in range(4):
    b=bar_at('PRE',i); c=pre(i)
    glassdyad(gtL,T(b),[c[0],c[2]],SPB(b)*2.8,hg(0.08),seed=i+20)
    glassdyad(gtR,T(b+0.014),[c[0],c[2]],SPB(b)*2.8,hg(0.08),seed=i+70)
    strings(st,T(b),c,SPB(b)*3.6,hg(0.055),atk=0.8,seed=i+40)
    bassn(bs,T(b+0.5),c[0],SPB(b)*3.0,hg(0.14))
    if i%4==1:
        line(vx,b,[(0,2.0,'G#4','o',''),(2.0,2.0,'A4','a',''),(4.0,3.0,'E4','e','')],
             g=0.165,style='falsetto',breath=0.34,seedbase=100+i)
# ---- CH: drums vao nhe ----
for i in range(8):
    b=bar_at('CH',i); c=ch(i)
    glassdyad(gtL,T(b),[c[0],c[2]],SPB(b)*2.8,hg(0.085),seed=i+30)
    glassdyad(gtR,T(b+0.014),[c[0],c[2]],SPB(b)*2.8,hg(0.085),seed=i+80)
    strings(st,T(b),c,SPB(b)*3.6,hg(0.06),atk=0.7,seed=i+60)
    ebow(st,T(b+0.5),c[2]+12,SPB(b)*2.5,hg(0.055),seed=i+40,atk=0.8)
    bassn(bs,T(b+0.5),c[0],SPB(b)*3.0,hg(0.18))
    villa(b,hg(0.55),arc=0.9,mode='soft')
    if i%4==0:
        line(vx,b,[(0,1.5,'A4','a',''),(1.5,1.0,'B4','o',''),(2.5,1.5,'A4','a',''),(4.0,1.0,'G#4','i',''),(5.0,3.0,'E4','a','')],
             g=0.17,style='falsetto',breath=0.36,seedbase=200+i)
# ---- V2 ----
for i in range(8):
    b=bar_at('V2',i); c=vch(i)
    glassdyad(gtL,T(b),[c[0],c[2]],SPB(b)*2.8,hg(0.08),seed=i+40)
    glassdyad(gtR,T(b+0.014),[c[0],c[2]],SPB(b)*2.8,hg(0.08),seed=i+90)
    strings(st,T(b),[c[0],c[2]],SPB(b)*3.6,hg(0.055),atk=0.8,seed=i+80)
    bassn(bs,T(b+0.5),c[0],SPB(b)*3.0,hg(0.16))
    villa(b,hg(0.5),arc=0.85,mode='soft')
    if i%4==0:
        line(vx,b,[(0,1.5,'F#4','a',''),(1.5,1.0,'G#4','e',''),(2.5,1.5,'A4','o',''),(4.0,1.0,'F#4','a',''),(5.0,3.0,'E4','i','n')],
             g=0.165,style='falsetto',breath=0.34,seedbase=300+i)
# ---- PRE2 ----
for i in range(4):
    b=bar_at('PRE2',i); c=pre(i)
    glassdyad(gtL,T(b),[c[0],c[2]],SPB(b)*2.8,hg(0.09),seed=i+50)
    glassdyad(gtR,T(b+0.014),[c[0],c[2]],SPB(b)*2.8,hg(0.09),seed=i+100)
    strings(st,T(b),c,SPB(b)*3.6,hg(0.06),atk=0.7,seed=i+100)
    bassn(bs,T(b+0.5),c[0],SPB(b)*3.0,hg(0.18))
    villa(b,hg(0.6),arc=0.95,mode='soft')
    if i%4==1:
        line(vx,b,[(0,2.0,'B4','o',''),(2.0,2.0,'C#5','a',''),(4.0,3.0,'G#4','e','')],
             g=0.17,style='falsetto',breath=0.36,seedbase=400+i)
# ---- CH2 ----
for i in range(8):
    b=bar_at('CH2',i); c=ch(i)
    strum8(crunch,gtL,b,c,SPB(b)*0.7,hg(0.09),i)
    strum8(crunch,gtR,b+0.011,c,SPB(b)*0.7,hg(0.09),i+50)
    strings(st,T(b),c,SPB(b)*3.6,hg(0.065),atk=0.5,seed=i+120)
    bassn(bs,T(b+0.5),c[0],SPB(b)*3.0,hg(0.22))
    villa(b,hg(0.7),arc=1.0,mode='full')
    if i%4==0:
        line(vx,b,[(0,1.5,'A4','a',''),(1.5,1.0,'B4','a',''),(2.5,1.5,'C#5','i',''),(4.0,1.0,'B4','a',''),(5.0,3.0,'A4','a','')],
             g=0.175,style='falsetto',breath=0.36,seedbase=500+i)
# ---- BR: F#m-D-E-A ----
for i in range(8):
    b=bar_at('BR',i); c=brc(i)
    organ(gtL,ht(b,j=0.005),c,SPB(b)*1.8,hg(0.05))
    organ(gtR,ht(b+0.01,j=0.005),c,SPB(b)*1.8,hg(0.05))
    strings(st,T(b),c,SPB(b)*3.6,hg(0.06),atk=0.6,seed=i+140)
    bassn(bs,T(b+0.5),c[0],SPB(b)*3.0,hg(0.2))
    villa(b,hg(0.68),arc=1.0,mode='full')
    if i%4==2:
        line(vx,b,[(0,2.0,'D5','o',''),(2.0,2.0,'C#5','a',''),(4.0,3.0,'B4','e','v')],
             g=0.17,style='falsetto',breath=0.34,seedbase=600+i)
# ---- OUTB: CRESCENDO - A-C#m-E-D-E-Bm-D lap, bass 8ths, ngay cang day ----
for i in range(24):
    b=bar_at('OUTB',i); c=out1(i)
    f=min(1.5,0.6+0.04*i) if i<20 else 1.5
    if i==0: f=0.45
    glassdyad(gtL,T(b),[c[0],c[2]],SPB(b)*2.8,hg(0.08),seed=i+60)
    glassdyad(gtR,T(b+0.014),[c[0],c[2]],SPB(b)*2.8,hg(0.08),seed=i+110)
    if i>=2:
        strum8(crunch,gtL,b,c,SPB(b)*0.7,hg(0.07*f),i)
        strum8(crunch,gtR,b+0.011,c,SPB(b)*0.7,hg(0.07*f),i+50)
    strings(st,T(b),c+([x+12 for x in c[:2]] if i>=12 else []),SPB(b)*3.6,hg(0.06*f),atk=0.5,seed=i+160)
    for s in range(4):
        bassn(bs,T(b+s*0.5),c[0],SPB(b)*0.9,hg(0.2*f))
    if i>=3:
        villa(b,hg(0.75*f),arc=0.8+0.2*min(f,1.0),mode='build')
    if i>=4 and i%4==0:
        line(vx,b,[(0,1.5,'F#4','a',''),(1.5,1.0,'G#4','a',''),(2.5,1.5,'A4','o',''),(4.0,1.5,'B4','a',''),(5.5,2.5,'A4','a','')],
             g=0.13+0.015*min(f,1.0),style='falsetto',breath=0.34,seedbase=700+i//4)
    if i==20: P.fill(b+2.0,2.0,'burst32',1.0,next_crash_beat=b+4)
    if i==23:
        P.CR(b+3.5,14,1.0,size=1.3)
        strings(st,T(b),[nn('A3'),nn('C#4'),nn('E4'),nn('A4')],SPB(b)*4.0,0.08,atk=0.2,seed=99)

P.apply_chokes()
P.bus['hat']=P.bus['hat']*2.6
DRUMS=mix_kit(P.bus,room_amount=0.26,oh_amount=1.0,lpf=15500)
DRUMS=DRUMS+hp(_fit(P.bus['hat'],len(DRUMS)),8000,2)*0.90
DRUMS=DRUMS*(0.05/max(rms_(DRUMS),1e-9))
bs=bs*(0.07/max(rms_(bs),1e-9))
noise_sw(dr_extra,0,T(END),0.004,True,90,1600)

STEMS=[(vn,-0.35,0.85,0.34,0.0),(gtL,-0.92,1.90,0.30,0.0),(gtR,0.92,1.90,0.30,0.0),
       (st,0.35,1.30,0.12,9.0),(dr_extra,0.0,0.8,0.0,0.0)]
MAPT=[(n,a,b,(5.0 if n in('OUTB','BR') else 3.2)) for n,a,b in MAP]
run(NAME, lambda voc: mixdown(NAME,vx,STEMS,DRUMS,bs,MAPT,vocals=voc,
    wet=0.30,decay=2.1,wide=2.8,drum_gain=0.95,bass_gain=0.95,crush_amt=0.16,
    rms_target=0.20), MAPT)
