from engine import *

NAME="09-paper-tigers"
BAR=4.0
SECS=[('INTRO',4),('V1',8),('CH1',8),('V2',8),('CH2',8),('OUT',4)]
S={}; _b=0.0
for _n,_c in SECS: S[_n]=_b; _b+=_c*BAR
END=_b
TOTAL = configure(145, 147, END+2)
MAP=[(n,S[n],S[n]+c*BAR) for n,c in SECS]
def bar_at(sec,i): return S[sec]+i*BAR
hseed(9)

jg=buf(); org=buf(); vx=buf(); bs=buf(); fx=buf()

# Chords: C, G/B, Am, G, F
VCH=[('C2',['C4','E4','G4']), ('B1',['D4','G4','B4']), ('A1',['C4','E4','A4']), ('G1',['B3','D4','G4'])]
CCH=[('F1',['C4','F4','A4']), ('C2',['C4','E4','G4']), ('G1',['B3','D4','G4']), ('A1',['C4','E4','A4'])]

def prog_bar(b0,seq,i,g=0.075,organ_play=False):
    bass,tops=seq[i%len(seq)]
    bm=nn(bass)
    
    # Finger Bass (Busy 8ths)
    for off in [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]:
        b_note = bm+12 if off%1.0==0 else bm+24
        fingerbass(bs,ht(b0+off,0.005),b_note,hd(SPB(b0)*0.5),hg(0.24),gl=1,dead=(off%1.0!=0))
    
    # Jangle
    for off,acc in [(0.0,1.0), (0.75,0.7), (1.5,0.8), (2.0,0.9), (2.75,0.7), (3.5,0.8)]:
        for j,x in enumerate(tops):
            jangle(jg,ht(b0+off,0.015)+j*0.02,nn(x),hd(SPB(b0)*1.2),hg(g*acc),seed=(i+j)%6)
            
    if organ_play:
        organ(org,ht(b0,0.02),[nn(x) for x in tops],hd(BAR*SPB(b0)*0.95),g=0.08)

K=Kit(seed=109); P=Performer(K,T,SPB,TOTAL,seed=29,style='indie'); P.hum=0.8

def vgroove(b0,lvl=1.0,a=1.0):
    P.K(b0,0,0.9*lvl,a,tune=48); P.K(b0+1.5,6,0.7*lvl,a,tune=48)
    P.K(b0+2.5,10,0.8*lvl,a,tune=48)
    P.S(b0+1,4,1.1*lvl,'center',a); P.S(b0+3,12,1.1*lvl,'center',a)
    for gp in (1.75, 2.25, 3.75): P.S(b0+gp,int(gp*4)%16,0.5*lvl,'ghost',a)
    # Syncopated ride patterns
    for s in range(8):
        P.RD(b0+s*0.5,s*2,(0.9 if s%2==0 else 0.6)*lvl,bell=(s%4==0),arc=a)
    # Claps on backbeat
    P.CL(b0+1,4,0.7*lvl,a); P.CL(b0+3,12,0.7*lvl,a)

for sec,nb,lvl in [('INTRO',4,0.85), ('V1',8,0.9),('CH1',8,1.05),('V2',8,0.95),('CH2',8,1.1),('OUT',4,1.1)]:
    for i in range(nb):
        b=bar_at(sec,i); a=[1.0,0.98,1.02,1.05][i%4]
        vgroove(b,lvl,a)
        if sec.startswith('CH') or sec=='OUT':
            P.CR(b,0,0.8*lvl,size=1.1)
        if i==nb-1:
            P.fill(b+2.0,2.0,'stutter',1.0)

noise_sw(fx,0,T(END),0.015,True,300,5000)

for sec,nb,seq,g,org_ in [('INTRO',4,VCH,0.08,False),
                          ('V1',8,VCH,0.09,False),
                          ('CH1',8,CCH,0.11,True),
                          ('V2',8,VCH,0.09,False),
                          ('CH2',8,CCH,0.12,True),
                          ('OUT',4,CCH,0.11,True)]:
    for i in range(nb):
        prog_bar(bar_at(sec,i),seq,i,g=g,organ_play=org_)

# Vocals
V1=[(0,.5,'G3','a','d'),(.5,.5,'F3','o','n'),(1,.5,'E3','a','m'),(1.5,.5,'D3','o','t'),
    (2,.5,'C3','a','l'),(2.5,.5,'C3','e','w'),(3,1.0,'G3','a','b')]
CH=[(0,1.0,'A3','a','sh'),(1,1.0,'C4','o','w'),(2,1.0,'B3','a','r'),(3,1.0,'G3','e','n')]

for i in range(8):
    line(vx,bar_at('V1',i),V1,g=0.20,style='croon',breath=0.2,seedbase=i*33)
    line(vx,bar_at('V2',i),V1,g=0.22,style='croon',breath=0.2,seedbase=i*33+100)
for i in range(8):
    b=bar_at('CH1',i)
    line(vx,b,CH,g=0.24,style='shout',oct8=0.4,breath=0.3,seedbase=200+i*33)
    chant(vx,b,CH,g=0.15,n=4,spread=18,style='shout',seedbase=300+i)
    b=bar_at('CH2',i)
    line(vx,b,CH,g=0.26,style='shout',oct8=0.5,breath=0.3,seedbase=400+i*33)
    chant(vx,b,CH,g=0.18,n=5,spread=20,style='shout',seedbase=500+i)

P.apply_chokes()
DRUMS=mix_kit(P.bus,room_amount=0.25,oh_amount=0.9,lofi=0.0,lpf=12000)

STEMS=[(jg,-0.5,0.7,0.4),(org,0.5,0.6,0.4),(fx,0.0,1.0,0.0)]
MAPT=[(n,a,b_,4.0) for n,a,b_ in MAP]

run(NAME, lambda voc: mixdown(NAME,vx,STEMS,DRUMS,bs,MAPT,vocals=voc,
    wet=0.2,decay=1.5,wide=1.4,drum_gain=0.85,bass_gain=0.9,crush_amt=0.1,
    rms_target=0.18), MAPT)
