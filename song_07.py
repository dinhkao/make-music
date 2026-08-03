from engine import *

NAME="07-mirage"
BAR=4.0
SECS=[('INTRO',4),('V1',8),('CH1',8),('V2',8),('CH2',8),('OUT',4)]
S={}; _b=0.0
for _n,_c in SECS: S[_n]=_b; _b+=_c*BAR
END=_b
TOTAL = configure(115, 116, END+2)
MAP=[(n,S[n],S[n]+c*BAR) for n,c in SECS]
def bar_at(sec,i): return S[sec]+i*BAR
hseed(7)

wur=buf(); gsp=buf(); tb=buf(); shk=buf(); vx=buf(); bs=buf(); fx=buf()

# Chords: C, Eb, F, G
VCH=[('C2',['E4','G4','C5']), ('Eb2',['G4','Bb4','Eb5']), ('F2',['A4','C5','F5']), ('G2',['B4','D5','G5'])]
CCH=VCH

def prog_bar(b0,seq,i,g=0.075,organ_play=False):
    bass,tops=seq[i%len(seq)]
    bm=nn(bass)
    
    # Sub Bass
    subbass(bs,ht(b0,0.005),bm,hd(SPB(b0)*3.5),hg(0.28))
    
    # Wurli chords
    for off,acc in [(0.0,1.0), (1.5,0.8), (2.5,0.9)]:
        for j,x in enumerate(tops):
            wurli(wur,ht(b0+off,0.01)+j*0.02,nn(x),hd(SPB(b0)*1.2),hg(g*acc),det=-3+3*j)
            
    if organ_play:
        gospelorgan(gsp,ht(b0,0.015),[nn(x) for x in tops],hd(BAR*SPB(b0)*0.95),g=0.09)

K=Kit(seed=107); P=Performer(K,T,SPB,TOTAL,seed=27,style='indie'); P.hum=0.85

def vgroove(b0,lvl=1.0,a=1.0):
    P.K(b0,0,1.0*lvl,a,tune=48); P.K(b0+1.75,7,0.7*lvl,a,tune=48)
    P.K(b0+2.5,10,0.8*lvl,a,tune=48)
    P.S(b0+1,4,1.0*lvl,'center',a); P.S(b0+3,12,1.0*lvl,'center',a)
    for gp in (1.5, 2.25, 3.5, 3.75): P.S(b0+gp,int(gp*4)%16,0.5*lvl,'ghost',a)
    for s in range(8):
        P.H(b0+s*0.5,s*2,(0.8 if s%2==0 else 0.5)*lvl,o=0.0,art='tip',arc=a)
    for s in range(8):
        P.SH(b0+s*0.5,s*2,0.5*lvl,a)

for sec,nb,lvl in [('INTRO',4,0.85), ('V1',8,0.9),('CH1',8,1.05),('V2',8,0.95),('CH2',8,1.1),('OUT',4,0.9)]:
    for i in range(nb):
        b=bar_at(sec,i); a=[1.0,0.97,1.03,1.05][i%4]
        vgroove(b,lvl,a)
        if sec.startswith('CH'):
            P.CR(b,0,0.8*lvl,size=1.1)
            for s in range(4): P.TB(b+s*1.0,s*4,0.6*lvl,a)
        if i==nb-1:
            P.fill(b+2.0,2.0,'stutter',1.0)

noise_sw(fx,0,T(END),0.01,True,300,5000)

for sec,nb,seq,g,org in [('INTRO',4,VCH,0.08,False),
                         ('V1',8,VCH,0.09,False),
                         ('CH1',8,CCH,0.11,True),
                         ('V2',8,VCH,0.09,False),
                         ('CH2',8,CCH,0.12,True),
                         ('OUT',4,CCH,0.09,True)]:
    for i in range(nb):
        prog_bar(bar_at(sec,i),seq,i,g=g,organ_play=org)

# Vocals
V1=[(0,.5,'C4','a','d'),(.5,.5,'Eb4','o','n'),(1,.5,'F4','a','m'),(1.5,.5,'G4','o','t'),
    (2,.5,'F4','a','l'),(2.5,.5,'Eb4','e','w'),(3,1.0,'C4','a','b')]
CH=[(0,1.0,'G4','a','sh'),(1,1.0,'F4','o','w'),(2,1.0,'Eb4','a','r'),(3,1.0,'C4','e','n')]

for i in range(8):
    line(vx,bar_at('V1',i),V1,g=0.20,style='croon',breath=0.3,seedbase=i*29)
    line(vx,bar_at('V2',i),V1,g=0.22,style='croon',breath=0.3,seedbase=i*29+100)
for i in range(8):
    b=bar_at('CH1',i)
    line(vx,b,CH,g=0.24,style='croon',oct8=0.5,breath=0.2,seedbase=200+i*29)
    chant(vx,b,CH,g=0.15,n=4,spread=18,style='shout',seedbase=300+i)
    b=bar_at('CH2',i)
    line(vx,b,CH,g=0.26,style='croon',oct8=0.6,breath=0.2,seedbase=400+i*29)
    chant(vx,b,CH,g=0.18,n=5,spread=20,style='shout',seedbase=500+i)

P.apply_chokes()
DRUMS=mix_kit(P.bus,room_amount=0.25,oh_amount=0.88,lofi=0.0,lpf=11000)

STEMS=[(wur,-0.4,0.7,0.4),(gsp,0.4,0.6,0.4),(fx,0.0,1.0,0.0)]
MAPT=[(n,a,b_,4.0) for n,a,b_ in MAP]

run(NAME, lambda voc: mixdown(NAME,vx,STEMS,DRUMS,bs,MAPT,vocals=voc,
    wet=0.22,decay=1.5,wide=1.4,drum_gain=0.8,bass_gain=0.88,crush_amt=0.15,
    rms_target=0.175), MAPT)
