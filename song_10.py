from engine import *

NAME="10-echoes-in-the-well"
BAR=4.0
SECS=[('INTRO',4),('V1',8),('CH1',8),('V2',8),('CH2',8),('OUT',8)]
S={}; _b=0.0
for _n,_c in SECS: S[_n]=_b; _b+=_c*BAR
END=_b
TOTAL = configure(105, 107, END+2)
MAP=[(n,S[n],S[n]+c*BAR) for n,c in SECS]
def bar_at(sec,i): return S[sec]+i*BAR
hseed(10)

wd=buf(); cg=buf(); sl=buf(); sd=buf(); vx=buf(); bs=buf(); fx=buf()

# Chords: Am, Em, F, Dm
VCH=[('A1',['C4','E4','A4']), ('E1',['B3','E4','G4']), ('F1',['C4','F4','A4']), ('D2',['D4','F4','A4'])]
CCH=[('F1',['C4','F4','A4']), ('D2',['D4','F4','A4']), ('A1',['C4','E4','A4']), ('E1',['B3','E4','G4'])]

def prog_bar(b0,seq,i,g=0.075,drone=False):
    bass,tops=seq[i%len(seq)]
    bm=nn(bass)
    
    # Sub Bass
    subbass(bs,T(b0),bm,SPB(b0)*3.8,0.28)
    
    # Slide Guitar
    for off,acc in [(0.0,1.0), (1.5,0.7), (2.0,0.8)]:
        slidegtr(sl,ht(b0+off,0.015),nn(tops[0]),nn(tops[-1])+12,hd(SPB(b0)*1.8),hg(g*acc),seed=i+int(off),drive=2.0)
            
    if drone:
        saw_drone(sd,ht(b0,0.02),nn(tops[0])-12,hd(BAR*SPB(b0)),g=0.06,det=2.0,seed=i)

K=Kit(seed=110); P=Performer(K,T,SPB,TOTAL,seed=30,style='indie'); P.hum=0.95

def vgroove(b0,lvl=1.0,a=1.0):
    P.K(b0,0,1.0*lvl,a,tune=42); P.K(b0+2.0,8,0.8*lvl,a,tune=42)
    # Tribal Toms
    P.TM(b0+1,4,0.8*lvl,tune=90); P.TM(b0+2.5,10,0.7*lvl,tune=112)
    P.TM(b0+3,12,0.9*lvl,tune=90); P.TM(b0+3.5,14,0.7*lvl,tune=112)
    
    # Congas and Woods
    for s in range(8):
        P.CG(b0+s*0.5,s*2,(0.8 if s%2==0 else 0.5)*lvl,tune=220,art='open' if s%4==0 else 'slap',arc=a)
        if s%3==0:
            P.WD(b0+s*0.5+0.25,s*2+1,0.6*lvl,tune=850,arc=a)

for sec,nb,lvl in [('INTRO',4,0.8), ('V1',8,0.85),('CH1',8,1.0),('V2',8,0.9),('CH2',8,1.05),('OUT',8,1.1)]:
    for i in range(nb):
        b=bar_at(sec,i); a=[1.0,0.98,1.02,1.05][i%4]
        vgroove(b,lvl,a)
        if sec.startswith('CH') or sec=='OUT':
            P.S(b+1,4,0.9*lvl,'rim',a); P.S(b+3,12,0.9*lvl,'rim',a)
        if i==nb-1:
            P.fill(b+2.0,2.0,'trib',1.0)

noise_sw(fx,0,T(END),0.02,True,100,2000)

for sec,nb,seq,g,drn in [('INTRO',4,VCH,0.08,False),
                          ('V1',8,VCH,0.09,False),
                          ('CH1',8,CCH,0.11,True),
                          ('V2',8,VCH,0.09,False),
                          ('CH2',8,CCH,0.12,True),
                          ('OUT',8,CCH,0.12,True)]:
    for i in range(nb):
        prog_bar(bar_at(sec,i),seq,i,g=g,drone=drn)

# Vocals (Spoken word / Deadpan)
V1=[(0,.25,'E3','a','w'),(.25,.25,'E3','e','n'),(.5,.25,'E3','i','l'),(.75,.25,'E3','o','m'),
    (1,.5,'D3','a','w'),(2,.5,'C3','o','r'),(3,1.0,'A2','e','m')]
CH=[(0,1.0,'A3','a','f'),(1,1.0,'C4','o','r'),(2,1.5,'D4','a','m')]

for i in range(8):
    line(vx,bar_at('V1',i),V1,g=0.20,style='deadpan',breath=0.6,seedbase=i*35)
    line(vx,bar_at('V2',i),V1,g=0.22,style='deadpan',breath=0.6,seedbase=i*35+100)
for i in range(8):
    b=bar_at('CH1',i)
    line(vx,b,CH,g=0.24,style='shout',oct8=0.2,breath=0.4,seedbase=200+i*35)
    chant(vx,b,CH,g=0.15,n=3,spread=12,style='shout',seedbase=300+i)
    b=bar_at('CH2',i)
    line(vx,b,CH,g=0.26,style='shout',oct8=0.3,breath=0.4,seedbase=400+i*35)
    chant(vx,b,CH,g=0.18,n=4,spread=14,style='shout',seedbase=500+i)
for i in range(8):
    line(vx,bar_at('OUT',i),V1,g=0.20,style='deadpan',breath=0.8,seedbase=600+i*35)

P.apply_chokes()
DRUMS=mix_kit(P.bus,room_amount=0.35,oh_amount=0.85,lofi=0.0,lpf=9000)

STEMS=[(sl,-0.5,0.65,0.4),(sd,0.5,0.5,0.5),(fx,0.0,1.0,0.0)]
MAPT=[(n,a,b_,4.0) for n,a,b_ in MAP]

run(NAME, lambda voc: mixdown(NAME,vx,STEMS,DRUMS,bs,MAPT,vocals=voc,
    wet=0.3,decay=2.0,wide=1.5,drum_gain=0.75,bass_gain=0.85,crush_amt=0.1,
    rms_target=0.16), MAPT)
