from engine import *

NAME="06-glass-house"
BAR=4.0
SECS=[('INTRO',4),('V1',8),('CH1',8),('V2',8),('CH2',8),('OUT',4)]
S={}; _b=0.0
for _n,_c in SECS: S[_n]=_b; _b+=_c*BAR
END=_b
TOTAL = configure(80, 82, END+2)
MAP=[(n,S[n],S[n]+c*BAR) for n,c in SECS]
def bar_at(sec,i): return S[sec]+i*BAR
hseed(6)

nyl=buf(); chm=buf(); bw=buf(); vx=buf(); bs=buf(); fx=buf()

# Chords: C, Em, Am, F
VCH=[('C2',['E4','G4','C5']), ('E1',['E4','G4','B4']), ('A1',['C4','E4','A4']), ('F1',['C4','F4','A4'])]
CCH=VCH

def prog_bar(b0,seq,i,g=0.075,chimes=False):
    bass,tops=seq[i%len(seq)]
    bm=nn(bass)
    
    # Soft Bass
    bassn(bs,ht(b0,0.01),bm+12,hd(SPB(b0)*2.0),hg(0.25),gl=1)
    
    # Nylon Guitar (Arpeggiated)
    for off,acc in [(0.0,1.0), (0.5,0.7), (1.0,0.8), (1.5,0.7), (2.0,0.9), (2.5,0.7)]:
        j = int(off*2) % len(tops)
        nylon(nyl,ht(b0+off,0.02),nn(tops[j]),hd(SPB(b0)*1.2),hg(g*acc),seed=(i+j)%6)
            
    # Bowed strings drone
    bowed(bw,ht(b0,0.03),bm+24,hd(BAR*SPB(b0)*0.95),g=0.06,rough=0.3,det=2,seed=i)
            
    if chimes:
        for off,acc in [(0.0,1.0), (2.0,0.8)]:
            chime12(chm,ht(b0+off,0.01),nn(tops[0])+12,hd(SPB(b0)*3.0),hg(0.12*acc),seed=i+int(off))

K=Kit(seed=106); P=Performer(K,T,SPB,TOTAL,seed=26,style='indie'); P.hum=0.9

def vgroove(b0,lvl=1.0,a=1.0,sparse=True):
    P.K(b0,0,0.8*lvl,a,tune=42); P.K(b0+2.5,10,0.6*lvl,a,tune=42)
    P.S(b0+2,8,0.7*lvl,'cross',a)
    if not sparse:
        for gp in (1.5, 3.5): P.S(b0+gp,int(gp*4)%16,0.3*lvl,'ghost',a)
        for s in range(8):
            P.H(b0+s*0.5,s*2,(0.6 if s%2==0 else 0.4)*lvl,o=0.0,art='tip',arc=a)

for sec,nb,lvl,sp in [('INTRO',4,0.7,True), ('V1',8,0.8,True),('CH1',8,0.9,False),
                      ('V2',8,0.85,True),('CH2',8,0.95,False),('OUT',4,0.8,True)]:
    for i in range(nb):
        b=bar_at(sec,i); a=[1.0,0.98,1.02,1.05][i%4]
        vgroove(b,lvl,a,sparse=sp)
        if sec.startswith('CH') and i%2==0:
            P.CR(b,0,0.6*lvl,size=1.0)

noise_sw(fx,0,T(END),0.012,True,150,4000)

for sec,nb,seq,g,chm_ in [('INTRO',4,VCH,0.08,False),
                          ('V1',8,VCH,0.09,False),
                          ('CH1',8,CCH,0.11,True),
                          ('V2',8,VCH,0.09,False),
                          ('CH2',8,CCH,0.12,True),
                          ('OUT',4,CCH,0.09,False)]:
    for i in range(nb):
        prog_bar(bar_at(sec,i),seq,i,g=g,chimes=chm_)

# Vocals
V1=[(0,.5,'E3','a','w'),(.5,.5,'G3','e','n'),(1,.5,'E3','i','l'),(1.5,.5,'C3','o','m'),
    (2,1.0,'D3','a','w')]
CH=[(0,1.0,'A3','a','f'),(1,1.0,'G3','o','r'),(2,1.5,'C4','a','m')]

for i in range(8):
    line(vx,bar_at('V1',i),V1,g=0.18,style='whisper',breath=1.2,seedbase=i*27)
    line(vx,bar_at('V2',i),V1,g=0.19,style='whisper',breath=1.2,seedbase=i*27+100)
for i in range(8):
    b=bar_at('CH1',i)
    line(vx,b,CH,g=0.20,style='croon',oct8=0.3,breath=0.8,seedbase=200+i*27)
    chant(vx,b,CH,g=0.12,n=2,spread=8,style='croon',seedbase=300+i)
    b=bar_at('CH2',i)
    line(vx,b,CH,g=0.21,style='croon',oct8=0.4,breath=0.8,seedbase=400+i*27)

P.apply_chokes()
DRUMS=mix_kit(P.bus,room_amount=0.4,oh_amount=0.8,lofi=0.0,lpf=8000)

STEMS=[(nyl,-0.4,0.7,0.4),(chm,0.5,0.6,0.3),(bw,0.0,0.5,0.5),(fx,0.0,1.0,0.0)]
MAPT=[(n,a,b_,4.0) for n,a,b_ in MAP]

run(NAME, lambda voc: mixdown(NAME,vx,STEMS,DRUMS,bs,MAPT,vocals=voc,
    wet=0.35,decay=2.5,wide=1.4,drum_gain=0.6,bass_gain=0.75,crush_amt=0.05,
    rms_target=0.15), MAPT)
