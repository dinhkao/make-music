from engine import *

NAME="05-neon-noir"
BAR=4.0
SECS=[('INTRO',4),('V1',8),('CH1',8),('V2',8),('CH2',8),('OUT',4)]
S={}; _b=0.0
for _n,_c in SECS: S[_n]=_b; _b+=_c*BAR
END=_b
TOTAL = configure(160, 162, END+2)
MAP=[(n,S[n],S[n]+c*BAR) for n,c in SECS]
def bar_at(sec,i): return S[sec]+i*BAR
hseed(5)

lg=buf(); cr=buf(); vx=buf(); bs=buf(); fx=buf()

# Chords: Am, F, Dm, E
VCH=[('A1',['A3','C4','E4']), ('F1',['F3','A3','C4']), ('D2',['D4','F4','A4']), ('E1',['E3','G#3','B3'])]
CCH=VCH

def prog_bar(b0,seq,i,g=0.075,lead=False):
    bass,tops=seq[i%len(seq)]
    bm=nn(bass)
    
    # Fuzz bass (8ths)
    for off in [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]:
        fzbass(bs,ht(b0+off,0.005),bm+12,hd(SPB(b0)*0.4),hg(0.24),gl=0,bite=1.5)
    
    # Distorted rhythm
    for off,acc in [(0.0,1.0), (1.5,0.8), (2.5,0.9)]:
        for j,x in enumerate(tops):
            crunch(cr,ht(b0+off,0.008)+j*0.01,nn(x),hd(SPB(b0)*0.8),hg(g*acc),drive=8.0,seed=(i+j)%7)
            
    if lead:
        for off,acc in [(0.0,1.0), (1.0,0.8), (2.0,0.9), (3.0,0.8)]:
            leadgtr(lg,ht(b0+off,0.01),nn(tops[-1])+12,hd(SPB(b0)*0.8),hg(0.15*acc),bend=1.0,seed=i+int(off))

K=Kit(seed=105); P=Performer(K,T,SPB,TOTAL,seed=25,style='indie'); P.hum=0.8

def vgroove(b0,lvl=1.0,a=1.0):
    P.K(b0,0,1.0*lvl,a,tune=55); P.K(b0+2.0,8,0.9*lvl,a,tune=55)
    P.S(b0+1,4,1.2*lvl,'center',a); P.S(b0+3,12,1.2*lvl,'center',a)
    for gp in (1.5, 2.5, 3.5): P.S(b0+gp,int(gp*4)%16,0.6*lvl,'ghost',a)
    for s in range(16):
        P.H(b0+s*0.25,s%16,(0.9 if s%4==0 else 0.6)*lvl,o=0.0,art='tip',arc=a)

for sec,nb,lvl in [('INTRO',4,0.9), ('V1',8,0.95),('CH1',8,1.1),('V2',8,1.0),('CH2',8,1.15),('OUT',4,1.1)]:
    for i in range(nb):
        b=bar_at(sec,i); a=[1.0,0.98,1.02,1.05][i%4]
        vgroove(b,lvl,a)
        if sec.startswith('CH') or sec=='OUT':
            P.CR(b,0,0.9*lvl,size=1.2)
            P.CR(b+2,8,0.8*lvl,size=1.2)
        if i==nb-1:
            P.fill(b+2.0,2.0,'burst32',1.0)

noise_sw(fx,0,T(END),0.015,True,400,5000)

for sec,nb,seq,g,ld in [('INTRO',4,VCH,0.08,False),
                         ('V1',8,VCH,0.09,False),
                         ('CH1',8,CCH,0.11,True),
                         ('V2',8,VCH,0.09,False),
                         ('CH2',8,CCH,0.12,True),
                         ('OUT',4,CCH,0.11,True)]:
    for i in range(nb):
        prog_bar(bar_at(sec,i),seq,i,g=g,lead=ld)

# Vocals (Aggressive)
V1=[(0,.5,'A3','e','sh'),(.5,.5,'B3','a','w'),(1,.5,'C4','a','t'),(1.5,.5,'B3','e','d'),
    (2,.5,'A3','o','g'),(2.5,.5,'F3','a','r'),(3,1.0,'A3','e','n')]
CH=[(0,1.0,'E4','a','k'),(1,1.0,'D4','o','w'),(2,1.0,'C4','a','r'),(3,1.0,'B3','e','n')]

for i in range(8):
    line(vx,bar_at('V1',i),V1,g=0.22,style='shout',breath=0.4,seedbase=i*25)
    line(vx,bar_at('V2',i),V1,g=0.24,style='shout',breath=0.4,seedbase=i*25+100)
for i in range(8):
    b=bar_at('CH1',i)
    line(vx,b,CH,g=0.26,style='shout',oct8=0.5,breath=0.3,seedbase=200+i*25)
    chant(vx,b,CH,g=0.18,n=4,spread=20,style='shout',seedbase=300+i)
    b=bar_at('CH2',i)
    line(vx,b,CH,g=0.28,style='shout',oct8=0.6,breath=0.3,seedbase=400+i*25)
    chant(vx,b,CH,g=0.20,n=5,spread=22,style='shout',seedbase=500+i)
for i in range(4):
    shriek(vx,T(bar_at('OUT',i))+0.5,nn('E4'),1.5,g=0.20,seed=600+i)

P.apply_chokes()
DRUMS=mix_kit(P.bus,room_amount=0.2,oh_amount=0.9,lofi=0.0,lpf=12000)

STEMS=[(cr,-0.5,0.7,0.4),(lg,0.5,0.65,0.5),(fx,0.0,1.0,0.0)]
MAPT=[(n,a,b_,4.0) for n,a,b_ in MAP]

run(NAME, lambda voc: mixdown(NAME,vx,STEMS,DRUMS,bs,MAPT,vocals=voc,
    wet=0.15,decay=1.2,wide=1.5,drum_gain=0.85,bass_gain=0.95,crush_amt=0.4,
    rms_target=0.18), MAPT)
