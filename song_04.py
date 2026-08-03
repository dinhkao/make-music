from engine import *

NAME="04-velvet-rust"
BAR=4.0
SECS=[('INTRO',4),('V1',8),('CH1',8),('V2',8),('CH2',8),('OUT',4)]
S={}; _b=0.0
for _n,_c in SECS: S[_n]=_b; _b+=_c*BAR
END=_b
TOTAL = configure(125, 126, END+2)
MAP=[(n,S[n],S[n]+c*BAR) for n,c in SECS]
def bar_at(sec,i): return S[sec]+i*BAR
hseed(4)

org=buf(); tp=buf(); hn=buf(); bn=buf(); vx=buf(); bs=buf(); fx=buf()

# Chords: Am, Dm, G, C, F, Bdim, E
VCH=[('A1',['C4','E4','A4']), ('D2',['D4','F4','A4']), ('G1',['D4','G4','B4']), ('C2',['E4','G4','C5']), 
     ('F1',['C4','F4','A4']), ('B1',['D4','F4','B4']), ('E1',['E4','G#4','B4']), ('E1',['E4','G#4','B4'])]
CCH=VCH

def prog_bar(b0,seq,i,g=0.075,horn_stab=False):
    bass,tops=seq[i%len(seq)]
    bm=nn(bass)
    
    # Bass (galloping rhythm)
    bassn(bs,ht(b0,0.005),bm+12,hd(SPB(b0)*0.8),hg(0.28),gl=1)
    bassn(bs,ht(b0+1.5,0.005),bm+12,hd(SPB(b0)*0.4),hg(0.20))
    bassn(bs,ht(b0+2.5,0.005),bm+12,hd(SPB(b0)*0.8),hg(0.25))
    bassn(bs,ht(b0+3.5,0.005),bm+12,hd(SPB(b0)*0.4),hg(0.20))
    
    # Organ (held chords)
    organ(org,ht(b0,0.01),[nn(x) for x in tops],hd(BAR*SPB(b0)*0.95),g=g*0.8)
    
    # Tack Piano (stabs)
    for off,acc in [(0.0,1.0), (1.5,0.7), (2.5,0.8)]:
        for j,x in enumerate(tops):
            tackpiano(tp,ht(b0+off,0.008)+j*0.015,nn(x),hd(SPB(b0)*0.5),hg(0.1*acc),tack=0.8,seed=(i+j)%7)
            
    if horn_stab:
        for j,x in enumerate(tops):
            hbone(bn,ht(b0+0.5,0.01)+j*0.02,nn(x)-12,hd(SPB(b0)*1.2),hg(0.12),growl=0.6,seed=i+j)
            horn(hn,ht(b0+2.5,0.01)+j*0.02,nn(x),hd(SPB(b0)*1.2),hg(0.10),rough=1.2)

K=Kit(seed=104); P=Performer(K,T,SPB,TOTAL,seed=24,style='indie'); P.hum=0.85

def vgroove(b0,lvl=1.0,a=1.0):
    P.K(b0,0,1.0*lvl,a,tune=48); P.K(b0+1.5,6,0.6*lvl,a,tune=48)
    P.K(b0+2.5,10,0.8*lvl,a,tune=48); P.K(b0+3.5,14,0.6*lvl,a,tune=48)
    P.S(b0+1,4,0.9*lvl,'rim',a); P.S(b0+3,12,0.9*lvl,'rim',a)
    for s in range(16):
        P.H(b0+s*0.25,s%16,(0.8 if s%4==0 else 0.5)*lvl,o=0.0,art='tip',arc=a)

for sec,nb,lvl in [('INTRO',4,0.85), ('V1',8,0.9),('CH1',8,1.0),('V2',8,0.95),('CH2',8,1.05),('OUT',4,0.9)]:
    for i in range(nb):
        b=bar_at(sec,i); a=[1.0,0.97,1.02,1.05][i%4]
        vgroove(b,lvl,a)
        if sec.startswith('CH'):
            P.CR(b,0,0.8*lvl,size=1.0)
            P.CL(b+1,4,0.8*lvl,a); P.CL(b+3,12,0.8*lvl,a)
        if i==nb-1:
            P.fill(b+2.0,2.0,'tom',1.0)

noise_sw(fx,0,T(END),0.01,True,200,3000)

for sec,nb,seq,g,hrn in [('INTRO',4,VCH,0.08,False),
                         ('V1',8,VCH,0.09,False),
                         ('CH1',8,CCH,0.11,True),
                         ('V2',8,VCH,0.09,False),
                         ('CH2',8,CCH,0.12,True),
                         ('OUT',4,CCH,0.10,True)]:
    for i in range(nb):
        prog_bar(bar_at(sec,i),seq,i,g=g,horn_stab=hrn)

# Vocals
V1=[(0,.5,'A3','a','d'),(.5,.5,'B3','o','n'),(1,.5,'C4','a','m'),(1.5,.5,'B3','o','t'),
    (2,.5,'A3','a','l'),(2.5,.5,'G3','e','w'),(3,1.0,'A3','a','b')]
CH=[(0,1.0,'E4','a','sh'),(1,1.0,'C4','o','w'),(2,1.0,'D4','a','r'),(3,1.0,'B3','e','n')]

for i in range(8):
    line(vx,bar_at('V1',i),V1,g=0.20,style='deadpan',breath=0.2,seedbase=i*23)
    line(vx,bar_at('V2',i),V1,g=0.22,style='deadpan',breath=0.2,seedbase=i*23+100)
for i in range(8):
    b=bar_at('CH1',i)
    line(vx,b,CH,g=0.24,style='shout',oct8=0.0,breath=0.3,seedbase=200+i*23)
    chant(vx,b,CH,g=0.15,n=4,spread=18,style='shout',seedbase=300+i)
    b=bar_at('CH2',i)
    line(vx,b,CH,g=0.26,style='shout',oct8=0.0,breath=0.3,seedbase=400+i*23)
    chant(vx,b,CH,g=0.18,n=5,spread=20,style='shout',seedbase=500+i)

P.apply_chokes()
DRUMS=mix_kit(P.bus,room_amount=0.22,oh_amount=0.85,lofi=0.0,lpf=10000)

STEMS=[(org,-0.5,0.5,0.4),(tp,0.5,0.6,0.4),(hn,0.3,0.5,0.5),(bn,-0.3,0.5,0.5),(fx,0.0,1.0,0.0)]
MAPT=[(n,a,b_,4.0) for n,a,b_ in MAP]

run(NAME, lambda voc: mixdown(NAME,vx,STEMS,DRUMS,bs,MAPT,vocals=voc,
    wet=0.2,decay=1.4,wide=1.3,drum_gain=0.75,bass_gain=0.85,crush_amt=0.15,
    rms_target=0.17), MAPT)
