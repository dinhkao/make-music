from engine import *

NAME="01-dusty-trail"
BAR=4.0
SECS=[('INTRO',4),('V1',8),('CH1',8),('V2',8),('CH2',8),('OUT',8)]
S={}; _b=0.0
for _n,_c in SECS: S[_n]=_b; _b+=_c*BAR
END=_b
TOTAL = configure(140, 142, END+2)
MAP=[(n,S[n],S[n]+c*BAR) for n,c in SECS]
def bar_at(sec,i): return S[sec]+i*BAR
hseed(1)

gt=buf(); hn=buf(); bw=buf(); vx=buf(); bs=buf(); fx=buf()

# Chords: Dm, A7, Bb, Gm
VCH=[('D2',['D4','F4','A4']), ('A1',['C#4','E4','G4']), ('Bb1',['D4','F4','Bb4']), ('G1',['D4','G4','Bb4'])]
CCH=[('D2',['D4','F4','A4']), ('F2',['C4','F4','A4']), ('Bb1',['D4','F4','Bb4']), ('A1',['C#4','E4','G4'])]

def prog_bar(b0,seq,i,g=0.075,stab=True,bow=False,horn_stab=False):
    bass,tops=seq[i%len(seq)]
    bm=nn(bass)
    # Fuzz bass
    fzbass(bs,ht(b0,0.005),bm+12,hd(SPB(b0)*1.5),hg(0.24),gl=2,bite=1.2)
    fzbass(bs,ht(b0+2.5,0.006),bm+12,hd(SPB(b0)*0.7),hg(0.18))
    
    if stab:
        for off,acc in [(0.0,1.0),(1.75,0.8),(2.5,0.9),(3.25,0.7)]:
            for j,x in enumerate(tops):
                crunch(gt,ht(b0+off,0.006)+j*0.007,nn(x),hd(SPB(b0)*0.4),hg(g*acc),drive=7.0,seed=(i+j)%6)
                
    if bow:
        for j,x in enumerate(tops):
            bowed(bw,ht(b0,0.015)+j*0.04,nn(x)+12,hd(BAR*SPB(b0)*0.95),0.05,rough=0.6,det=-4+4*j,seed=j)
            
    if horn_stab:
        for off,acc in [(2.0,1.0), (3.5,0.8)]:
            for j,x in enumerate(tops):
                horn(hn,ht(b0+off,0.01),nn(x),hd(SPB(b0)*0.6),hg(0.08*acc),det=-5+3*j,rough=1.5)

K=Kit(seed=101); P=Performer(K,T,SPB,TOTAL,seed=12,style='indie'); P.hum=0.8

def vgroove(b0,lvl=1.0,a=1.0):
    P.K(b0,0,1.0*lvl,a,tune=50); P.K(b0+2.5,10,0.7*lvl,a,tune=50)
    P.K(b0+3.25,13,0.5*lvl,a,tune=50)
    P.S(b0+1,4,1.1*lvl,'center',a); P.S(b0+3,12,1.1*lvl,'center',a)
    for gp in (1.5, 2.75, 3.5): P.S(b0+gp,int(gp*4)%16,0.5*lvl,'ghost',a)
    for s in range(16):
        P.H(b0+s*0.25,s%16,(0.8 if s%4==0 else 0.4)*lvl,o=0.0,art='tip',arc=a)

for sec,nb,lvl in [('INTRO',4,0.85), ('V1',8,0.9),('CH1',8,1.05),('V2',8,0.95),('CH2',8,1.1),('OUT',8,1.15)]:
    for i in range(nb):
        b=bar_at(sec,i); a=[1.0,0.98,1.02,1.05][i%4]
        vgroove(b,lvl,a)
        if sec.startswith('CH') or sec=='OUT':
            P.CR(b,0,0.8*lvl,size=1.1)
            P.CR(b+2,8,0.7*lvl,size=1.1)
        if i==nb-1:
            P.fill(b+2.0,2.0,'stutter',1.0)

noise_sw(fx,0,T(END),0.012,True,100,2000)

for sec,nb,seq,g,bow,hrn in [('INTRO',4,VCH,0.07,False,False),
                             ('V1',8,VCH,0.08,False,False),
                             ('CH1',8,CCH,0.09,True,True),
                             ('V2',8,VCH,0.08,False,True),
                             ('CH2',8,CCH,0.10,True,True),
                             ('OUT',8,CCH,0.11,True,True)]:
    for i in range(nb):
        prog_bar(bar_at(sec,i),seq,i,g=g,bow=bow,horn_stab=hrn)

# Vocals
V1=[(0,.5,'D3','a','d'),(.5,.5,'D3','o','n'),(1,.5,'F3','a','m'),(1.5,.5,'E3','o','t'),
    (2,.5,'D3','a','l'),(2.5,.5,'D3','e','w'),(3,1.0,'A2','a','b')]
CH=[(0,.5,'A3','a','sh'),(.5,.5,'G3','o','w'),(1,.5,'F3','a','r'),(1.5,.5,'E3','e','n'),
    (2,.5,'D3','a','m'),(2.5,.5,'D3','e','t'),(3,1.0,'A3','a','y')]

for i in range(8):
    line(vx,bar_at('V1',i),V1,g=0.20,style='deadpan',breath=0.3,seedbase=i*17)
    line(vx,bar_at('V2',i),V1,g=0.22,style='shout',breath=0.4,seedbase=i*17+100)
for i in range(8):
    b=bar_at('CH1',i)
    line(vx,b,CH,g=0.24,style='shout',oct8=0.4,breath=0.2,seedbase=200+i*17)
    chant(vx,b,CH,g=0.15,n=4,spread=18,style='shout',seedbase=300+i)
    b=bar_at('CH2',i)
    line(vx,b,CH,g=0.26,style='shout',oct8=0.5,breath=0.2,seedbase=400+i*17)
    chant(vx,b,CH,g=0.18,n=5,spread=20,style='shout',seedbase=500+i)
for i in range(8):
    shriek(vx,T(bar_at('OUT',i))+0.5,nn('D4'),1.5,g=0.18,seed=600+i)

P.apply_chokes()
DRUMS=mix_kit(P.bus,room_amount=0.25,oh_amount=0.9,lofi=0.0,lpf=12000)

STEMS=[(gt,-0.6,0.65,0.4),(hn,0.6,0.6,0.5),(bw,0.0,0.5,0.5),(fx,0.0,1.0,0.0)]
MAPT=[(n,a,b_,4.0) for n,a,b_ in MAP]

run(NAME, lambda voc: mixdown(NAME,vx,STEMS,DRUMS,bs,MAPT,vocals=voc,
    wet=0.2,decay=1.3,wide=1.4,drum_gain=0.8,bass_gain=0.9,crush_amt=0.3,
    rms_target=0.18), MAPT)
