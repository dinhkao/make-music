from engine import *

NAME="03-sunken-city"
BAR=4.0
SECS=[('INTRO',4),('V1',8),('CH1',8),('V2',8),('CH2',8),('OUT',8)]
S={}; _b=0.0
for _n,_c in SECS: S[_n]=_b; _b+=_c*BAR
END=_b
TOTAL = configure(95, 96, END+2)
MAP=[(n,S[n],S[n]+c*BAR) for n,c in SECS]
def bar_at(sec,i): return S[sec]+i*BAR
hseed(3)

jg=buf(); sd=buf(); ml=buf(); vx=buf(); bs=buf(); fx=buf()

# Chords: Cmaj7, Dm7, Em7, Fmaj7
VCH=[('C2',['E4','G4','B4']), ('D2',['F4','A4','C5']), ('E2',['G4','B4','D5']), ('F2',['A4','C5','E5'])]
CCH=[('F2',['A4','C5','E5']), ('E2',['G4','B4','D5']), ('D2',['F4','A4','C5']), ('C2',['E4','G4','B4'])]

def prog_bar(b0,seq,i,g=0.075,choir=False):
    bass,tops=seq[i%len(seq)]
    bm=nn(bass)
    
    # Sub bass
    subbass(bs,T(b0),bm,SPB(b0)*3.8,0.3)
    
    # Jangle
    for off,acc in [(0.0,1.0),(1.0,0.8),(2.0,0.9),(3.0,0.8)]:
        for j,x in enumerate(tops):
            jangle(jg,ht(b0+off,0.015)+j*0.03,nn(x),hd(SPB(b0)*1.5),hg(g*acc),seed=(i+j)%5)
            
    # Saw Drone
    saw_drone(sd,ht(b0,0.02),nn(tops[0])-12,hd(BAR*SPB(b0)),g=0.05,det=0,seed=i)
            
    if choir:
        for j,x in enumerate(tops):
            mellotron(ml,ht(b0,0.01),nn(x),hd(BAR*SPB(b0)*0.95),g=0.08,kind='choir',seed=j+i)

K=Kit(seed=103); P=Performer(K,T,SPB,TOTAL,seed=23,style='indie'); P.hum=0.7

def vgroove(b0,lvl=1.0,a=1.0):
    P.K(b0,0,1.0*lvl,a,tune=42); P.K(b0+2.5,10,0.7*lvl,a,tune=42)
    P.S(b0+1,4,0.9*lvl,'center',a); P.S(b0+3,12,0.9*lvl,'center',a)
    for gp in (2.75, 3.5): P.S(b0+gp,int(gp*4)%16,0.3*lvl,'ghost',a)
    for s in range(8):
        # Open hats on offbeats
        op = 0.6 if s%2!=0 else 0.0
        P.H(b0+s*0.5,s*2,(0.6 if s%2==0 else 0.8)*lvl,o=op,art='tip',arc=a, choke_beat=(b0+s*0.5+0.5) if op else None)

for sec,nb,lvl in [('INTRO',4,0.8), ('V1',8,0.9),('CH1',8,1.0),('V2',8,0.95),('CH2',8,1.05),('OUT',8,1.1)]:
    for i in range(nb):
        b=bar_at(sec,i); a=[1.0,0.98,1.02,1.05][i%4]
        vgroove(b,lvl,a)
        if sec.startswith('CH') or sec=='OUT':
            P.CR(b,0,0.7*lvl,size=1.2)
        if i==nb-1:
            P.fill(b+2.0,2.0,'roll',0.8)

noise_sw(fx,0,T(END),0.015,True,500,6000)

for sec,nb,seq,g,chr in [('INTRO',4,VCH,0.08,False),
                         ('V1',8,VCH,0.09,False),
                         ('CH1',8,CCH,0.11,True),
                         ('V2',8,VCH,0.09,False),
                         ('CH2',8,CCH,0.12,True),
                         ('OUT',8,CCH,0.12,True)]:
    for i in range(nb):
        prog_bar(bar_at(sec,i),seq,i,g=g,choir=chr)

# Vocals
V1=[(0,.5,'E3','a','w'),(.5,.5,'G3','o','n'),(1,.5,'E3','e','l'),(1.5,.5,'C3','a','m'),
    (2,1.0,'D3','o','w')]
CH=[(0,1.0,'A3','a','f'),(1,1.0,'G3','o','r'),(2,1.5,'C4','a','m')]

for i in range(8):
    line(vx,bar_at('V1',i),V1,g=0.18,style='whisper',breath=0.8,seedbase=i*21)
    line(vx,bar_at('V2',i),V1,g=0.20,style='whisper',breath=0.8,seedbase=i*21+100)
for i in range(8):
    b=bar_at('CH1',i)
    line(vx,b,CH,g=0.22,style='croon',oct8=0.4,breath=0.4,seedbase=200+i*21)
    chant(vx,b,CH,g=0.12,n=3,spread=10,style='croon',seedbase=300+i)
    b=bar_at('CH2',i)
    line(vx,b,CH,g=0.24,style='croon',oct8=0.5,breath=0.4,seedbase=400+i*21)
    chant(vx,b,CH,g=0.15,n=4,spread=12,style='croon',seedbase=500+i)
for i in range(8):
    b=bar_at('OUT',i)
    line(vx,b,CH,g=0.20,style='whisper',oct8=0.3,breath=0.9,seedbase=600+i*21)

P.apply_chokes()
DRUMS=mix_kit(P.bus,room_amount=0.35,oh_amount=0.95,lofi=0.0,lpf=9000)

STEMS=[(jg,-0.6,0.65,0.4),(sd,0.6,0.5,0.5),(ml,0.0,0.6,0.5),(fx,0.0,1.0,0.0)]
MAPT=[(n,a,b_,4.0) for n,a,b_ in MAP]

run(NAME, lambda voc: mixdown(NAME,vx,STEMS,DRUMS,bs,MAPT,vocals=voc,
    wet=0.35,decay=2.2,wide=1.6,drum_gain=0.7,bass_gain=0.8,crush_amt=0.1,
    rms_target=0.16), MAPT)
