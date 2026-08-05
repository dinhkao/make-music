# ============================================================ BAI 6: A VOICE BEYOND THE YEARS
# Model: Mew - "Her Voice Is Beyond Her Years" (Frengers 2003) - Eb, 136 BPM, NGAN ~2:50
#   intro power chords Eb5-Bb5-F5-C5 (goc tab G5-D5-E5-B5, nua cung len)
#   verse Eb-Bb-F-C / Ab-Eb-F-C; bass riff 8ths C3-Bb2 lap (do tu stem that)
#   drums: drive 8th hats + kick offbeat (Nick Villa), punchy
#   BAI NGAN, khong intro dai, dap thang vao
BAR=4.0
NAME="06-a-voice-beyond-the-years"
SECS=[('IN',4),('V1',8),('V2',8),('CH',8),('V3',8),('CH2',8),('BR',8),('CH3',8),('V4',8),('CH4',8),('OUT',14)]
S={}; _b=0.0
for _n,_c in SECS: S[_n]=_b; _b+=_c*BAR
END=_b
configure(136,136,END+3)
MAP=[(n,S[n],S[n]+c*BAR) for n,c in SECS]
def bar_at(sec,i): return S[sec]+i*BAR
print(NAME,int(END/BAR),"bars ->",round(TOTAL,1),"s")

PC=[[nn('Eb4'),nn('Bb4')],[nn('Bb3'),nn('F4')],[nn('F3'),nn('C4')],[nn('C4'),nn('G4')]]  # power chords Eb-Bb-F-C
VCH=[[nn('Eb2'),nn('G3'),nn('Bb3')],[nn('Bb2'),nn('D4'),nn('F4')],[nn('F2'),nn('A3'),nn('C4')],[nn('C3'),nn('E4'),nn('G4')]]
AB=[[nn('Ab2'),nn('C4'),nn('Eb4')],[nn('Eb2'),nn('G3'),nn('Bb3')],[nn('F2'),nn('A3'),nn('C4')],[nn('C3'),nn('E4'),nn('G4')]]
def pc(i): return PC[i%4]
def vch(i): return VCH[i%4]
def abch(i): return AB[i%4]

def bassriff(b,b0,g=0.24):   # riff 8ths C3-Bb2-C3-Bb2... (do tu stem Her Voice)
    for s in range(8):
        m=nn('C3') if s%2==0 else nn('Bb2')
        bassn(bs,T(b0+s*0.25),m,SPB(b)*0.8,hg(g))

K=Kit(seed=1216); P=Performer(K,T,SPB,TOTAL,seed=11,style='indie'); P.hum=0.74
def villa(b,lvl=0.8,arc=1.0,mode='drive'):
    a=arc
    if mode=='drive':
        for s in range(16):
            P.H(b+s*0.25,s,0.55*lvl if s%2==1 else 0.4*lvl,o=0.0,art='tip',arc=a)
        P.K(b+0.5,2,0.85*lvl,a); P.K(b+2.5,10,0.85*lvl,a); P.K(b+3.25,13,0.5*lvl,a)
        P.S(b+1,4,0.6*lvl,'ghost',a); P.S(b+3,12,0.7*lvl,'ghost',a)
    else:
        for s in range(16):
            P.H(b+s*0.25,s,0.62*lvl if s%4==0 else 0.44*lvl,o=0.0,art=('edge' if s%4==0 else 'tip'),arc=a)
        P.K(b,0,1.0*lvl,a); P.K(b+1.5,6,0.55*lvl,a); P.K(b+2.75,11,0.6*lvl,a)
        P.S(b+1,4,0.95*lvl,'center',a); P.S(b+3,12,1.0*lvl,'center',a)
        P.S(b+0.5,2,0.3*lvl,'ghost',a); P.S(b+2.5,10,0.28*lvl,'ghost',a)
        if int(b*136/60)%4==3:
            P.TM(b+2.5,10,0.7*lvl,150); P.TM(b+3.25,13,0.8*lvl,118)

vn=buf(); gtL=buf(); gtR=buf(); st=buf(); bs=buf(); vx=buf(); dr_extra=buf()

# ---- INTRO: power chords crunch + bassriff ----
for i in range(4):
    b=bar_at('IN',i)
    chchord(crunch,gtL,b,pc(i),SPB(b)*0.8,hg(0.09),i,dt=0.007)
    chchord(crunch,gtR,b+0.011,pc(i),SPB(b)*0.8,hg(0.09),i+50,dt=0.007)
    bassriff(b,b,0.2)
    villa(b,hg(0.45),arc=0.7,mode='drive')
# ---- V1 ----
for i in range(8):
    b=bar_at('V1',i); c=vch(i)
    chchord(crunch,gtL,b,c,SPB(b)*0.8,hg(0.085),i,dt=0.007)
    chchord(crunch,gtR,b+0.011,c,SPB(b)*0.8,hg(0.085),i+50,dt=0.007)
    bassriff(b,b)
    strings(st,T(b),[c[0],c[2]],SPB(b)*3.4,hg(0.035),atk=0.7,seed=i+20)
    villa(b,hg(0.55),arc=0.85,mode='drive')
    if i%4==0:
        line(vx,b,[(0,.75,'G4','a',''),(.75,.5,'Eb4','o',''),(1.25,1.0,'F4','a',''),(2.5,.75,'G4','e',''),(3.25,.75,'Bb4','a','')],
             g=0.15,style='falsetto',breath=0.3,seedbase=10+i)
# ---- V2 ----
for i in range(8):
    b=bar_at('V2',i); c=abch(i)
    chchord(crunch,gtL,b,c,SPB(b)*0.8,hg(0.09),i,dt=0.007)
    chchord(crunch,gtR,b+0.011,c,SPB(b)*0.8,hg(0.09),i+50,dt=0.007)
    bassriff(b,b)
    glassarp(st,T(b+0.5),c[2]+12,SPB(b)*1.4,hg(0.05),seed=i)
    strings(st,T(b),[c[0],c[2]],SPB(b)*3.4,hg(0.04),atk=0.6,seed=i+40)
    villa(b,hg(0.6),arc=0.9,mode='drive')
    line(vx,b,[(0,.5,'G4','o',''),(.5,.75,'Ab4','a',''),(1.25,.5,'F4','e',''),(2.0,.5,'Eb4','a',''),(2.75,1.25,'F4','i','')],
         g=0.155,style='falsetto',breath=0.3,seedbase=100+i)
# ---- CH ----
for i in range(8):
    b=bar_at('CH',i); c=vch(i)
    strum8(crunch,gtL,b,c,SPB(b)*0.65,hg(0.11),i)
    strum8(crunch,gtR,b+0.011,c,SPB(b)*0.65,hg(0.11),i+50)
    bassriff(b,b,0.28)
    strings(st,T(b),c,SPB(b)*3.4,hg(0.05),atk=0.35,seed=i+60)
    villa(b,hg(0.78),arc=1.0,mode='chorus')
    if i%4==0:
        line(vx,b,[(0,.5,'Bb4','a',''),(.5,.5,'C5','o',''),(1.0,.75,'Bb4','a',''),(1.75,.5,'G4','i',''),(2.5,1.5,'F4','a','')],
             g=0.16,style='falsetto',breath=0.32,seedbase=200+i)
# ---- V3 ----
for i in range(8):
    b=bar_at('V3',i); c=vch(i)
    chchord(crunch,gtL,b,c,SPB(b)*0.8,hg(0.09),i,dt=0.007)
    chchord(crunch,gtR,b+0.011,c,SPB(b)*0.8,hg(0.09),i+50,dt=0.007)
    bassriff(b,b)
    strings(st,T(b),[c[0],c[2]],SPB(b)*3.4,hg(0.045),atk=0.6,seed=i+80)
    villa(b,hg(0.62),arc=0.92,mode='drive')
    line(vx,b,[(0,.5,'G4','a',''),(.5,.75,'Bb4','e',''),(1.25,.5,'C5','o',''),(2.0,.75,'Bb4','a',''),(2.75,1.25,'G4','i','n')],
         g=0.16,style='falsetto',breath=0.3,seedbase=300+i)
# ---- CH2 ----
for i in range(8):
    b=bar_at('CH2',i); c=vch(i)
    strum8(crunch,gtL,b,c,SPB(b)*0.65,hg(0.12),i)
    strum8(crunch,gtR,b+0.011,c,SPB(b)*0.65,hg(0.12),i+50)
    bassriff(b,b,0.3)
    strings(st,T(b),c,SPB(b)*3.4,hg(0.055),atk=0.3,seed=i+100)
    villa(b,hg(0.85),arc=1.0,mode='chorus')
    if i==3: P.fill(b+2.0,1.5,'tom',1.0,next_crash_beat=b+4)
    line(vx,b,[(0,.5,'Bb4','a',''),(.5,.5,'C5','a',''),(1.0,.75,'D5','i',''),(1.75,.5,'C5','a',''),(2.5,1.5,'Bb4','a','')],
         g=0.165,style='falsetto',breath=0.34,seedbase=400+i)
# ---- BR: Fm-Ab-Eb-Bb (buildup) ----
BRC=[[nn('F2'),nn('Ab3'),nn('C4')],[nn('Ab2'),nn('C4'),nn('Eb4')],[nn('Eb2'),nn('G3'),nn('Bb3')],[nn('Bb2'),nn('D4'),nn('F4')]]
for i in range(8):
    b=bar_at('BR',i); c=BRC[i%4]
    organ(gtL,ht(b,j=0.005),c,SPB(b)*1.6,hg(0.05))
    organ(gtR,ht(b+0.01,j=0.005),c,SPB(b)*1.6,hg(0.05))
    bassriff(b,b,0.24)
    strings(st,T(b),c,SPB(b)*3.4,hg(0.05),atk=0.5,seed=i+120)
    villa(b,hg(0.72),arc=0.95,mode='chorus')
    if i%4==2:
        line(vx,b,[(0,1.0,'C5','o',''),(1.0,1.0,'D5','a',''),(2.0,2.0,'Eb5','e','v')],
             g=0.165,style='falsetto',breath=0.32,seedbase=500+i)
# ---- CH3 ----
for i in range(8):
    b=bar_at('CH3',i); c=vch(i)
    strum8(crunch,gtL,b,c,SPB(b)*0.65,hg(0.13),i)
    strum8(crunch,gtR,b+0.011,c,SPB(b)*0.65,hg(0.13),i+50)
    bassriff(b,b,0.32)
    strings(st,T(b),c+[x+12 for x in c[:2]],SPB(b)*3.4,hg(0.065),atk=0.25,seed=i+140)
    villa(b,hg(0.92),arc=1.0,mode='chorus')
    if i==2: P.fill(b+2.0,2.0,'burst32',1.0,next_crash_beat=b+4)
    line(vx,b,[(0,.5,'Bb4','a',''),(.5,.5,'D5','o',''),(1.0,.75,'C5','a',''),(1.75,.5,'Bb4','i',''),(2.5,1.5,'G4','a','')],
         g=0.17,style='falsetto',breath=0.36,seedbase=600+i)
# ---- V4 ----
for i in range(8):
    b=bar_at('V4',i); c=vch(i)
    chchord(crunch,gtL,b,c,SPB(b)*0.8,hg(0.09),i,dt=0.007)
    chchord(crunch,gtR,b+0.011,c,SPB(b)*0.8,hg(0.09),i+50,dt=0.007)
    bassriff(b,b)
    strings(st,T(b),[c[0],c[2]],SPB(b)*3.4,hg(0.045),atk=0.6,seed=i+80)
    villa(b,hg(0.62),arc=0.92,mode='drive')
    line(vx,b,[(0,.5,'G4','a',''),(.5,.75,'Bb4','e',''),(1.25,.5,'C5','o',''),(2.0,.75,'Bb4','a',''),(2.75,1.25,'G4','i','n')],
         g=0.16,style='falsetto',breath=0.3,seedbase=330+i)
# ---- CH4 ----
for i in range(8):
    b=bar_at('CH4',i); c=vch(i)
    strum8(crunch,gtL,b,c,SPB(b)*0.65,hg(0.13),i)
    strum8(crunch,gtR,b+0.011,c,SPB(b)*0.65,hg(0.13),i+50)
    bassriff(b,b,0.32)
    strings(st,T(b),c+[x+12 for x in c[:2]],SPB(b)*3.4,hg(0.065),atk=0.25,seed=i+140)
    villa(b,hg(0.92),arc=1.0,mode='chorus')
    if i==2: P.fill(b+2.0,2.0,'burst32',1.0,next_crash_beat=b+4)
    line(vx,b,[(0,.5,'Bb4','a',''),(.5,.5,'D5','o',''),(1.0,.75,'C5','a',''),(1.75,.5,'Bb4','i',''),(2.5,1.5,'G4','a','')],
         g=0.17,style='falsetto',breath=0.36,seedbase=660+i)
# ---- V4 ----
for i in range(8):
    b=bar_at('V4',i); c=vch(i)
    chchord(crunch,gtL,b,c,SPB(b)*0.8,hg(0.09),i,dt=0.007)
    chchord(crunch,gtR,b+0.011,c,SPB(b)*0.8,hg(0.09),i+50,dt=0.007)
    bassriff(b,b)
    strings(st,T(b),[c[0],c[2]],SPB(b)*3.4,hg(0.045),atk=0.6,seed=i+80)
    villa(b,hg(0.62),arc=0.92,mode='drive')
    line(vx,b,[(0,.5,'G4','a',''),(.5,.75,'Bb4','e',''),(1.25,.5,'C5','o',''),(2.0,.75,'Bb4','a',''),(2.75,1.25,'G4','i','n')],
         g=0.16,style='falsetto',breath=0.3,seedbase=330+i)
# ---- OUT: bass riff + giong lap "a voice beyond the years" ----
for i in range(8):
    b=bar_at('OUT',i); c=vch(i%4)
    chchord(crunch,gtL,b,c,SPB(b)*0.8,hg(0.09),i,dt=0.007)
    chchord(crunch,gtR,b+0.011,c,SPB(b)*0.8,hg(0.09),i+50,dt=0.007)
    bassriff(b,b,0.26)
    strings(st,T(b),c,SPB(b)*3.4,hg(0.045),atk=0.5,seed=i+160)
    villa(b,hg(0.7),arc=0.9,mode='chorus')
    if i%2==0:
        line(vx,b,[(0,.5,'G4','a','v'),(.5,.5,'G4','a',''),(1.0,.5,'F4','o',''),(1.5,.5,'Eb4','e',''),(2.0,.75,'F4','a',''),(2.75,1.25,'Eb4','o','')],
             g=0.15,style='falsetto',breath=0.3,seedbase=700+i//2)
    if i%4==3: P.fill(b+3.0,1.0,'snare',0.7)

P.apply_chokes()
P.bus['hat']=P.bus['hat']*2.6
DRUMS=mix_kit(P.bus,room_amount=0.25,oh_amount=1.0,lpf=15500)
DRUMS=DRUMS+hp(_fit(P.bus['hat'],len(DRUMS)),8000,2)*0.90
DRUMS=DRUMS*(0.05/max(rms_(DRUMS),1e-9))
bs=bs*(0.075/max(rms_(bs),1e-9))
noise_sw(dr_extra,0,T(END),0.004,True,90,1600)

STEMS=[(vn,-0.35,0.78,0.38,0.0),(gtL,-0.92,2.30,0.30,0.0),(gtR,0.92,2.30,0.30,0.0),
       (st,0.35,1.25,0.12,9.0),(dr_extra,0.0,0.8,0.0,0.0)]
MAPT=[(n,a,b,(5.5 if n=='OUT' else 2.6)) for n,a,b in MAP]
run(NAME, lambda voc: mixdown(NAME,vx,STEMS,DRUMS,bs,MAPT,vocals=voc,
    wet=0.26,decay=1.8,wide=3.0,drum_gain=0.95,bass_gain=0.95,crush_amt=0.16,
    rms_target=0.205), MAPT)
