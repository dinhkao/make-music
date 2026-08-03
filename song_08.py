from engine import *

NAME="08-fracture"
BAR=4.0
SECS=[('INTRO',4),('V1',8),('V2',8),('BUILD',8),('CLIMAX',8),('OUT',4)]
S={}; _b=0.0
for _n,_c in SECS: S[_n]=_b; _b+=_c*BAR
END=_b
TOTAL = configure(130, 134, END+2)
MAP=[(n,S[n],S[n]+c*BAR) for n,c in SECS]
def bar_at(sec,i): return S[sec]+i*BAR
hseed(8)

tp=buf(); ml=buf(); hn=buf(); cr=buf(); vx=buf(); bs=buf(); fx=buf()

# Chords: Am, G, F, C
VCH=[('A1',['C4','E4','A4']), ('G1',['B3','D4','G4']), ('F1',['A3','C4','F4']), ('C2',['C4','E4','G4'])]
CCH=VCH

def prog_bar(b0,seq,i,g=0.075,flute=False,horns=False,drive=4.0):
    bass,tops=seq[i%len(seq)]
    bm=nn(bass)
    
    # Bass
    fzbass(bs,ht(b0,0.005),bm+12,hd(SPB(b0)*3.5),hg(0.24),gl=1,bite=drive*0.2)
    
    # Tack Piano Arps
    for off,acc in [(0.0,1.0), (0.5,0.7), (1.0,0.8), (1.5,0.7), (2.0,0.9), (2.5,0.7), (3.0,0.8), (3.5,0.7)]:
        j = int(off*2) % len(tops)
        tackpiano(tp,ht(b0+off,0.015),nn(tops[j]),hd(SPB(b0)*0.8),hg(g*acc),tack=0.6,seed=(i+j)%6)
            
    if flute:
        for j,x in enumerate(tops):
            mellotron(ml,ht(b0,0.02)+j*0.02,nn(x)+12,hd(BAR*SPB(b0)*0.95),g=0.08,kind='flute',seed=j+i)
            
    if horns:
        for j,x in enumerate(tops):
            horn(hn,ht(b0,0.015)+j*0.01,nn(x),hd(BAR*SPB(b0)*0.95),hg(0.12),rough=1.5)
        for off,acc in [(0.0,1.0), (1.5,0.8), (2.5,0.9)]:
            for j,x in enumerate(tops):
                crunch(cr,ht(b0+off,0.006)+j*0.007,nn(x),hd(SPB(b0)*0.5),hg(g*1.5*acc),drive=drive,seed=(i+j)%6)

K=Kit(seed=108); P=Performer(K,T,SPB,TOTAL,seed=28,style='indie'); P.hum=0.8

def vgroove(b0,lvl=1.0,a=1.0,build=False,climax=False):
    if not climax and not build:
        # Minimal ride bell
        P.RD(b0,0,0.7*lvl,bell=True,arc=a)
        P.RD(b0+2,8,0.7*lvl,bell=True,arc=a)
        P.K(b0,0,0.8*lvl,a,tune=46)
        P.S(b0+2,8,0.7*lvl,'rim',a)
    elif build:
        # Toms building up
        P.TM(b0,0,0.7*lvl,tune=112)
        P.TM(b0+1,4,0.7*lvl,tune=112)
        P.TM(b0+2,8,0.8*lvl,tune=112)
        P.TM(b0+3,12,0.8*lvl,tune=112)
        P.K(b0,0,0.9*lvl,a,tune=46)
        P.K(b0+2,8,0.9*lvl,a,tune=46)
    elif climax:
        # Explosive
        P.K(b0,0,1.1*lvl,a,tune=46); P.K(b0+2.5,10,0.9*lvl,a,tune=46)
        P.S(b0+1,4,1.2*lvl,'center',a); P.S(b0+3,12,1.2*lvl,'center',a)
        for s in range(8):
            P.CR(b0+s*0.5,s*2,1.0*lvl,size=1.2)

for sec,nb,lvl,bld,clm in [('INTRO',4,0.7,False,False), ('V1',8,0.8,False,False),
                           ('V2',8,0.85,False,False),('BUILD',8,0.95,True,False),
                           ('CLIMAX',8,1.2,False,True),('OUT',4,0.7,False,False)]:
    for i in range(nb):
        b=bar_at(sec,i); a=[1.0,0.98,1.02,1.05][i%4]
        vgroove(b,lvl,a,build=bld,climax=clm)
        if i==nb-1 and sec=='BUILD':
            P.fill(b+2.0,2.0,'tom',1.2)

noise_sw(fx,0,T(END),0.015,True,200,6000)

for sec,nb,seq,g,fl,hrn,drv in [('INTRO',4,VCH,0.08,False,False,4.0),
                                ('V1',8,VCH,0.09,True,False,4.0),
                                ('V2',8,VCH,0.09,True,False,5.0),
                                ('BUILD',8,VCH,0.11,True,True,6.0),
                                ('CLIMAX',8,CCH,0.13,True,True,9.0),
                                ('OUT',4,VCH,0.08,False,False,4.0)]:
    for i in range(nb):
        prog_bar(bar_at(sec,i),seq,i,g=g,flute=fl,horns=hrn,drive=drv)

# Vocals
V1=[(0,.5,'A3','a','d'),(.5,.5,'B3','o','n'),(1,.5,'C4','a','m'),(1.5,.5,'B3','o','t'),
    (2,.5,'A3','a','l'),(2.5,.5,'G3','e','w'),(3,1.0,'A3','a','b')]
CH=[(0,1.0,'E4','a','sh'),(1,1.0,'C4','o','w'),(2,1.0,'D4','a','r'),(3,1.0,'B3','e','n')]

for i in range(8):
    line(vx,bar_at('V1',i),V1,g=0.18,style='deadpan',breath=0.4,seedbase=i*31)
    line(vx,bar_at('V2',i),V1,g=0.20,style='deadpan',breath=0.4,seedbase=i*31+100)
for i in range(8):
    b=bar_at('BUILD',i)
    line(vx,b,CH,g=0.22,style='shout',oct8=0.4,breath=0.3,seedbase=200+i*31)
    b=bar_at('CLIMAX',i)
    line(vx,b,CH,g=0.28,style='shout',oct8=0.6,breath=0.2,seedbase=400+i*31)
    chant(vx,b,CH,g=0.20,n=6,spread=22,style='shout',seedbase=500+i)

P.apply_chokes()
DRUMS=mix_kit(P.bus,room_amount=0.35,oh_amount=0.9,lofi=0.0,lpf=10000)

STEMS=[(tp,-0.4,0.6,0.3),(ml,0.4,0.6,0.4),(hn,0.3,0.6,0.5),(cr,-0.3,0.6,0.5),(fx,0.0,1.0,0.0)]
MAPT=[(n,a,b_,4.0) for n,a,b_ in MAP]

run(NAME, lambda voc: mixdown(NAME,vx,STEMS,DRUMS,bs,MAPT,vocals=voc,
    wet=0.25,decay=1.8,wide=1.5,drum_gain=0.8,bass_gain=0.9,crush_amt=0.25,
    rms_target=0.18), MAPT)
