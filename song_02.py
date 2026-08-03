from engine import *

NAME="02-plastic-crown"
BAR=4.0
SECS=[('INTRO',4),('V1',8),('CH1',8),('V2',8),('CH2',8),('OUT',4)]
S={}; _b=0.0
for _n,_c in SECS: S[_n]=_b; _b+=_c*BAR
END=_b
TOTAL = configure(110, 112, END+2)
MAP=[(n,S[n],S[n]+c*BAR) for n,c in SECS]
def bar_at(sec,i): return S[sec]+i*BAR
hseed(2)

cl=buf(); sl=buf(); mr=buf(); vx=buf(); bs=buf(); fx=buf()

# Chords: C, Bb, F, Fm
VCH=[('C2',['E4','G4','C5']), ('Bb1',['D4','F4','Bb4']), ('F2',['C4','F4','A4']), ('F2',['C4','F4','Ab4'])]
CCH=[('C2',['E4','G4','C5']), ('F2',['C4','F4','A4']), ('Bb1',['D4','F4','Bb4']), ('F2',['C4','F4','Ab4'])]

def prog_bar(b0,seq,i,g=0.075,slide=False,marim=False):
    bass,tops=seq[i%len(seq)]
    bm=nn(bass)
    # Finger bass
    fingerbass(bs,ht(b0,0.005),bm+12,hd(SPB(b0)*1.8),hg(0.28),gl=1)
    fingerbass(bs,ht(b0+2.5,0.005),bm+12,hd(SPB(b0)*0.8),hg(0.22))
    fingerbass(bs,ht(b0+3.5,0.005),bm+19,hd(SPB(b0)*0.4),hg(0.18))
    
    # Clavinet
    for off,acc in [(0.0,1.0),(1.5,0.7),(2.0,0.85),(3.5,0.75)]:
        for j,x in enumerate(tops):
            clav(cl,ht(b0+off,0.008)+j*0.01,nn(x),hd(SPB(b0)*0.3),hg(g*acc),seed=(i+j)%7)
            
    if slide:
        slidegtr(sl,ht(b0,0.01),nn(tops[0]),nn(tops[-1]),hd(BAR*SPB(b0)*0.8),hg(0.12),seed=i,drive=3.0)
            
    if marim:
        for off,acc in [(0.0,1.0), (1.0,0.6), (2.0,0.8), (3.0,0.6)]:
            for j,x in enumerate(tops):
                marimba(mr,ht(b0+off,0.008)+j*0.02,nn(x)+12,hd(SPB(b0)*0.4),hg(0.09*acc),metal=False,seed=j+i)

K=Kit(seed=102); P=Performer(K,T,SPB,TOTAL,seed=22,style='indie'); P.hum=0.85

def vgroove(b0,lvl=1.0,a=1.0):
    P.K(b0,0,1.0*lvl,a,tune=46); P.K(b0+1.75,7,0.6*lvl,a,tune=46)
    P.K(b0+2.5,10,0.8*lvl,a,tune=46)
    P.S(b0+1,4,1.0*lvl,'rim',a); P.S(b0+3,12,1.0*lvl,'rim',a)
    for gp in (2.25, 3.75): P.S(b0+gp,int(gp*4)%16,0.4*lvl,'ghost',a)
    for s in range(8):
        P.H(b0+s*0.5,s*2,(0.7 if s%2==0 else 0.4)*lvl,o=0.0,art='edge',arc=a)

for sec,nb,lvl in [('INTRO',4,0.8), ('V1',8,0.9),('CH1',8,1.0),('V2',8,0.95),('CH2',8,1.05),('OUT',4,0.9)]:
    for i in range(nb):
        b=bar_at(sec,i); a=[1.0,0.97,1.03,1.05][i%4]
        vgroove(b,lvl,a)
        if sec.startswith('CH'):
            P.RD(b,0,0.8*lvl,bell=True)
            P.RD(b+2,8,0.7*lvl,bell=True)
            P.S(b+1,4,1.1*lvl,'center',a); P.S(b+3,12,1.1*lvl,'center',a)
        if i==nb-1:
            P.fill(b+2.5,1.5,'tom',1.0)

noise_sw(fx,0,T(END),0.01,True,300,4000)

for sec,nb,seq,g,sld,mrm in [('INTRO',4,VCH,0.08,False,True),
                             ('V1',8,VCH,0.09,False,True),
                             ('CH1',8,CCH,0.10,True,True),
                             ('V2',8,VCH,0.09,False,True),
                             ('CH2',8,CCH,0.11,True,True),
                             ('OUT',4,VCH,0.08,True,False)]:
    for i in range(nb):
        prog_bar(bar_at(sec,i),seq,i,g=g,slide=sld,marim=mrm)

# Vocals
V1=[(0,.5,'G3','e','k'),(.5,.5,'F3','a','n'),(1,.5,'E3','o','t'),(1.5,.5,'D3','a','l'),
    (2,.5,'C3','o','w'),(2.5,.5,'D3','e','r'),(3,1.0,'E3','a','m')]
CH=[(0,1.0,'C4','a','sh'),(1,1.0,'Bb3','o','w'),(2,1.0,'A3','a','r'),(3,1.0,'Ab3','e','n')]

for i in range(8):
    line(vx,bar_at('V1',i),V1,g=0.20,style='croon',breath=0.25,seedbase=i*19)
    line(vx,bar_at('V2',i),V1,g=0.22,style='croon',breath=0.25,seedbase=i*19+100)
for i in range(8):
    b=bar_at('CH1',i)
    line(vx,b,CH,g=0.24,style='falsetto',oct8=0.4,breath=0.2,seedbase=200+i*19)
    b=bar_at('CH2',i)
    line(vx,b,CH,g=0.26,style='falsetto',oct8=0.5,breath=0.2,seedbase=400+i*19)

P.apply_chokes()
DRUMS=mix_kit(P.bus,room_amount=0.2,oh_amount=0.85,lofi=0.0,lpf=10000)

STEMS=[(cl,-0.5,0.65,0.4),(sl,0.5,0.6,0.5),(mr,0.0,0.5,0.5),(fx,0.0,1.0,0.0)]
MAPT=[(n,a,b_,4.0) for n,a,b_ in MAP]

run(NAME, lambda voc: mixdown(NAME,vx,STEMS,DRUMS,bs,MAPT,vocals=voc,
    wet=0.25,decay=1.6,wide=1.3,drum_gain=0.75,bass_gain=0.85,crush_amt=0.1,
    rms_target=0.17), MAPT)
