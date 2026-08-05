# ============================================================ BAI 1: GLASS OVER THE HARBOR
# Model: Mew - "Am I Wry? No" (Frengers 2003) - F major, 128 BPM
#   intro: riff guitar di xuong (V-vi-IV = C-Dm-Bb) + strings
#   verse: giong thap, bass thua, drums offbeat-8th (Nick Villa Image-style)
#   chorus: "I know you..." -> crunch F-Bb-C-Dm strum 8ths double-track L/R, backbeat
#   outro: lap "glass over the harbor" toi het (nhu "diamond ring"), bass 8ths bom,
#          vong A-F7-Bb7-Dm (III-I7-IV7-vi per Hooktheory)
BAR=4.0
NAME="01-glass-over-the-harbor"
SECS=[('IN',8),('V1',8),('V2',8),('CH',8),('IN2',4),('V3',8),('CH2',8),('BR',8),('CH3',8),('OUT',32)]
S={}; _b=0.0
for _n,_c in SECS: S[_n]=_b; _b+=_c*BAR
END=_b
configure(128,128,END+3)
MAP=[(n,S[n],S[n]+c*BAR) for n,c in SECS]
def bar_at(sec,i): return S[sec]+i*BAR
print(NAME,int(END/BAR),"bars ->",round(TOTAL,1),"s")

VCH=[[nn('F3'),nn('A3'),nn('C4')],[nn('Bb2'),nn('D4'),nn('F4')],[nn('C3'),nn('E4'),nn('G4')],[nn('D3'),nn('F4'),nn('A4')]]
OCH=[[nn('A2'),nn('C#4'),nn('E4')],[nn('F2'),nn('A3'),nn('E4')],[nn('Bb2'),nn('D4'),nn('A4')],[nn('D3'),nn('F4'),nn('A4')]]
def vch(i): return VCH[i%4]
def och(i): return OCH[i%4]

# helper: arp 8ths / strum 8ths - Bo Madsen style (guitar luon chay)
def arp8(fn,b_,b0,ch,dur,g,seedbase,dt=0.006):
    seq=[ch[0],ch[2],ch[1],ch[2]]
    for s in range(8):
        fn(b_,ht(b0+s*0.25,j=0.006),seq[s%4],dur,hg(g),seed=seedbase*10+s)
def strum8(fn,b_,b0,ch,dur,g,seedbase,dt=0.006):
    for s in range(8):
        for k,m in enumerate(ch):
            fn(b_,ht(b0+s*0.25,j=0.005)+k*dt,m,dur,hg(g/len(ch)))
def chord2(fn,b_,b0,ch,dur,g,seedbase,dt=0.006):
    for k,m in enumerate(ch):
        fn(b_,ht(b0,j=0.005)+k*dt,m,dur,hg(g/len(ch)))

K=Kit(seed=1211); P=Performer(K,T,SPB,TOTAL,seed=11,style='indie'); P.hum=0.7
def villa(b,lvl=0.8,arc=1.0,mode='offbeat'):
    a=arc
    if mode=='offbeat':   # Nick Villa Image-verse: kick noi tren "and" 8ths
        for s in range(16):
            P.H(b+s*0.25,s,0.55*lvl if s%2==1 else 0.38*lvl,o=0.0,art='tip',arc=a)
        P.K(b+0.5,2,0.85*lvl,a); P.K(b+2.5,10,0.85*lvl,a)
        P.K(b+3,12,0.5*lvl,a)
        P.S(b+1,4,0.55*lvl,'ghost',a); P.S(b+3,12,0.65*lvl,'ghost',a)
    elif mode=='back':
        for s in range(16):
            P.H(b+s*0.25,s,0.62*lvl if s%4==0 else 0.42*lvl,o=0.0,art=('edge' if s%4==0 else 'tip'),arc=a)
        P.K(b,0,1.0*lvl,a); P.K(b+1.5,6,0.55*lvl,a); P.K(b+2,8,0.7*lvl,a); P.K(b+3.5,14,0.5*lvl,a)
        P.S(b+1,4,0.9*lvl,'center',a); P.S(b+3,12,0.95*lvl,'center',a)
        P.S(b+0.5,2,0.28*lvl,'ghost',a); P.S(b+2.5,10,0.25*lvl,'ghost',a)
    elif mode=='pump':    # outro: kick 8ths bom nhu bass
        for s in range(16):
            P.H(b+s*0.25,s,0.58*lvl if s%4==0 else 0.4*lvl,arc=a)
            if s%2==0: P.K(b+s*0.25,s,0.8*lvl,a)
        P.S(b+1,4,0.92*lvl,'center',a); P.S(b+3,12,0.95*lvl,'center',a)
        if int(b*128/60)%4==3:
            P.TM(b+2.75,11,0.7*lvl,120); P.TM(b+3.25,13,0.8*lvl,98); P.TM(b+3.75,15,0.9*lvl,82)

vn=buf(); gtL=buf(); gtR=buf(); st=buf(); bs=buf(); vx=buf(); dr_extra=buf()

# ---- INTRO: riff di xuong C-Bb-A-G-F (double-track) + strings ----
RIFF=[nn('C5'),nn('Bb4'),nn('A4'),nn('G4'),nn('F4')]
for i in range(8):
    b=bar_at('IN',i)
    for j,m in enumerate(RIFF):
        airlead(gtL,T(b+j*0.4),m,SPB(b)*0.7,hg(0.10),seed=j+i*5)
        airlead(gtR,T(b+j*0.4+0.012),m,SPB(b)*0.7,hg(0.10),seed=j+i*5+37)
    strings(st,T(b),VCH[0]+[nn('C4')],SPB(b)*3.4,hg(0.05),atk=0.7,seed=i)
    bassn(bs,T(b+3),nn('F2'),SPB(b)*1.2,hg(0.16))
    villa(b,hg(0.5),arc=0.7,mode='offbeat')
# ---- V1: jangle arp 8ths ----
for i in range(8):
    b=bar_at('V1',i); c=vch(i)
    arp8(jangle,gtL,b,c,SPB(b)*0.9,hg(0.075),i,dt=0.007)
    arp8(jangle,gtR,b+0.009,c,SPB(b)*0.9,hg(0.075),i+50,dt=0.007)
    strings(st,T(b),[c[0],c[2]],SPB(b)*3.4,hg(0.035),atk=0.8,seed=i+20)
    bassn(bs,T(b+0.5),c[0],SPB(b)*2.2,hg(0.17))
    villa(b,hg(0.55),arc=0.85,mode='offbeat')
    if i%4==0:
        line(vx,b,[(0,.75,'A3','a',''),(.75,.5,'Bb3','o',''),(1.25,1.0,'C4','a','n'),(2.5,.5,'G3','e',''),(3.0,1.0,'A3','a','')],
             g=0.115,style='falsetto',breath=0.3,seedbase=10+i)
# ---- V2: + glassarp counter ----
for i in range(8):
    b=bar_at('V2',i); c=vch(i)
    arp8(jangle,gtL,b,c,SPB(b)*0.9,hg(0.08),i,dt=0.007)
    arp8(jangle,gtR,b+0.009,c,SPB(b)*0.9,hg(0.08),i+50,dt=0.007)
    glassarp(st,T(b+0.5),c[2]+12,SPB(b)*1.6,hg(0.05),seed=i)
    strings(st,T(b),[c[0],c[2]],SPB(b)*3.4,hg(0.04),atk=0.7,seed=i+40)
    bassn(bs,T(b+0.5),c[0],SPB(b)*2.2,hg(0.18))
    villa(b,hg(0.6),arc=0.9,mode='offbeat')
    line(vx,b,[(0,.5,'A3','o','h'),(.5,.75,'C4','a','n'),(1.25,.5,'D4','e',''),(2.0,.5,'Bb3','a',''),(2.75,1.25,'C4','i','s')],
         g=0.12,style='falsetto',breath=0.3,seedbase=100+i)
# ---- CH: strum 8ths double-track ----
for i in range(8):
    b=bar_at('CH',i); c=vch(i)
    strum8(crunch,gtL,b,c,SPB(b)*0.7,hg(0.105),i,dt=0.006)
    strum8(crunch,gtR,b+0.011,c,SPB(b)*0.7,hg(0.105),i+50,dt=0.006)
    strings(st,T(b),c,SPB(b)*3.4,hg(0.05),atk=0.35,seed=i+60)
    bassn(bs,T(b),c[0],SPB(b)*3.2,hg(0.24))
    villa(b,hg(0.75),arc=1.0,mode='back')
    if i%4==0:
        line(vx,b,[(0,.5,'F4','a',''),(.5,.5,'G4','o','u'),(1.0,.75,'A4','a',''),(1.75,.5,'Bb4','a',''),(2.5,1.5,'A4','i','')],
             g=0.13,style='falsetto',breath=0.32,seedbase=200+i)
# ---- IN2: nghi ----
for i in range(4):
    b=bar_at('IN2',i)
    glassarp(gtR,T(b+1),vch(i)[2]+12,SPB(b)*1.5,hg(0.05),seed=i)
    bassn(bs,T(b+2),nn('F2'),SPB(b)*1.5,hg(0.13))
    villa(b,hg(0.45),arc=0.6,mode='offbeat')
# ---- V3 ----
for i in range(8):
    b=bar_at('V3',i); c=vch(i)
    arp8(jangle,gtL,b,c,SPB(b)*0.9,hg(0.085),i,dt=0.007)
    arp8(jangle,gtR,b+0.009,c,SPB(b)*0.9,hg(0.085),i+50,dt=0.007)
    strings(st,T(b),[c[0],c[2]],SPB(b)*3.4,hg(0.045),atk=0.6,seed=i+80)
    bassn(bs,T(b+0.5),c[0],SPB(b)*2.2,hg(0.19))
    villa(b,hg(0.62),arc=0.92,mode='offbeat')
    line(vx,b,[(0,.5,'A3','a',''),(.5,.75,'Bb3','e',''),(1.25,.5,'C4','o',''),(2.0,.5,'D4','a',''),(2.5,1.5,'E4','i','n')],
         g=0.125,style='falsetto',breath=0.3,seedbase=300+i)
# ---- CH2 ----
for i in range(8):
    b=bar_at('CH2',i); c=vch(i)
    strum8(crunch,gtL,b,c,SPB(b)*0.7,hg(0.115),i,dt=0.006)
    strum8(crunch,gtR,b+0.011,c,SPB(b)*0.7,hg(0.115),i+50,dt=0.006)
    strings(st,T(b),c,SPB(b)*3.4,hg(0.055),atk=0.3,seed=i+100)
    bassn(bs,T(b),c[0],SPB(b)*3.2,hg(0.26))
    villa(b,hg(0.82),arc=1.0,mode='back')
    if i==3: P.fill(b+2.0,1.5,'tom',1.0,next_crash_beat=b+4)
    line(vx,b,[(0,.5,'F4','a',''),(.5,.5,'G4','a',''),(1.0,.75,'A4','i',''),(1.75,.5,'Bb4','a',''),(2.5,1.5,'A4','a','')],
         g=0.135,style='falsetto',breath=0.34,seedbase=400+i)
# ---- BR: Dm-Bb-C7-F ----
BRC=[[nn('D3'),nn('F4'),nn('A4')],[nn('Bb2'),nn('D4'),nn('F4')],[nn('C3'),nn('E4'),nn('Bb4')],[nn('F2'),nn('A3'),nn('C4')]]
for i in range(8):
    b=bar_at('BR',i); c=BRC[i%4]
    organ(gtL,ht(b,j=0.005),c,SPB(b)*1.8,hg(0.045))
    organ(gtR,ht(b+0.01,j=0.005),c,SPB(b)*1.8,hg(0.045))
    strings(st,T(b),c,SPB(b)*3.4,hg(0.05),atk=0.5,seed=i+120)
    bassn(bs,T(b),c[0],SPB(b)*3.2,hg(0.22))
    villa(b,hg(0.7),arc=0.95,mode='back')
    if i%4==2:
        line(vx,b,[(0,1.0,'F4','o',''),(1.0,1.0,'G4','a',''),(2.0,2.0,'A4','e','v')],
             g=0.125,style='falsetto',breath=0.32,seedbase=500+i)
# ---- CH3: cao nhat ----
for i in range(8):
    b=bar_at('CH3',i); c=vch(i)
    strum8(crunch,gtL,b,c,SPB(b)*0.7,hg(0.125),i,dt=0.006)
    strum8(crunch,gtR,b+0.011,c,SPB(b)*0.7,hg(0.125),i+50,dt=0.006)
    strings(st,T(b),c+[x+12 for x in c[:2]],SPB(b)*3.4,hg(0.065),atk=0.25,seed=i+140)
    bassn(bs,T(b),c[0],SPB(b)*3.2,hg(0.28))
    villa(b,hg(0.9),arc=1.0,mode='back')
    if i==2: P.fill(b+2.0,2.0,'burst32',1.0,next_crash_beat=b+4)
    line(vx,b,[(0,.5,'F4','a',''),(.5,.5,'G4','o',''),(1.0,.75,'A4','a',''),(1.75,.5,'C5','i',''),(2.5,1.5,'Bb4','a','')],
         g=0.14,style='falsetto',breath=0.36,seedbase=600+i)
# ---- OUT: lap "glass over the harbor", bass bom 8ths, A-F7-Bb7-Dm ----
for i in range(32):
    b=bar_at('OUT',i); c=och(i)
    strum8(crunch,gtL,b,c,SPB(b)*0.7,hg(0.10),i,dt=0.006)
    strum8(crunch,gtR,b+0.011,c,SPB(b)*0.7,hg(0.10),i+50,dt=0.006)
    strings(st,T(b),c,SPB(b)*3.4,hg(0.05),atk=0.4,seed=i+160)
    for s in range(4):
        bassn(bs,T(b+s*0.5),c[0],SPB(b)*0.9,hg(0.24))
    villa(b,hg(0.85),arc=1.0,mode='pump')
    if i%4==0:
        line(vx,b,[(0,.5,'A4','a','g'),(.5,.5,'A4','a',''),(1.0,.5,'G4','o',''),(1.5,.5,'F4','e',''),(2.0,.5,'A4','a',''),(2.5,1.5,'G4','o','')],
             g=0.12,style='falsetto',breath=0.3,seedbase=700+i//4)
    if i%8==7:
        P.fill(b+3.0,1.0,'snare',0.7)

P.apply_chokes()
P.bus['hat']=P.bus['hat']*2.6
DRUMS=mix_kit(P.bus,room_amount=0.25,oh_amount=1.0,lpf=15500)
DRUMS=DRUMS+hp(_fit(P.bus['hat'],len(DRUMS)),8000,2)*0.90
DRUMS=DRUMS*(0.052/max(rms_(DRUMS),1e-9))
bs=bs*(0.075/max(rms_(bs),1e-9))
noise_sw(dr_extra,0,T(END),0.004,True,90,1600)

STEMS=[(vn,-0.35,0.78,0.38,0.0),(gtL,-0.92,2.30,0.30,0.0),(gtR,0.92,2.30,0.30,0.0),
       (st,0.35,1.25,0.12,9.0),(dr_extra,0.0,0.8,0.0,0.0)]
MAPT=[(n,a,b,(5.5 if n=='OUT' else 2.6)) for n,a,b in MAP]
run(NAME, lambda voc: mixdown(NAME,vx,STEMS,DRUMS,bs,MAPT,vocals=voc,
    wet=0.26,decay=1.8,wide=3.0,drum_gain=0.95,bass_gain=0.95,crush_amt=0.16,
    rms_target=0.205), MAPT)
