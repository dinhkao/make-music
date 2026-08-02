# ============================================================ BAI 2: BORROWED LIGHT
# Model: Black Country, New Road - "Athens, France" (For the first time, 2021).
# through-composed PATCHWORK of tonal centres (no single song-long key):
#   1) drop-D-style low-pedal riff cycle  Cm - G - Abm  (the "Gm-D-Ebm" move
#      transposed to Cm; chromatic Ab/B/Eb colour)
#   2) warm  Cm <-> Abmaj7  arpeggio section (the "Am<->Fmaj7" move) + violin
#   3) big  Eb -> Fm  two-chord hit (the "D->Em, E lands late on beat 2" push)
#   4) 12/8 Abmaj7 outro vamp with "chucka chucka" muted stabs + bass walk
#      Ab - Ab - F(vi) - Db(IV)  (the "C-C-A-F" 12/8 outro)
# Palette only from 20-frantic-choir.py: ks/crunch (gtr), bassn/subbass (bass),
#   wurli/tackpiano (keys), bowed (violin), hbone (sax), mellotron (choir),
#   say/line/chant (vocals), Kit+Performer (Nick Villa).
BAR=4.0
NAME="02-borrowed-light"
SECS=[('IN',18),('ARP',18),('PUSH',18),('OUT',22),('TAG',2)]
S={}; _b=0.0
for _n,_c in SECS: S[_n]=_b; _b+=_c*BAR
END=_b
configure(118,119,END+3)
MAP=[(n,S[n],S[n]+c*BAR) for n,c in SECS]
def bar_at(sec,i): return S[sec]+i*BAR
print(NAME,int(END/BAR),"bars ->",round(TOTAL,1),"s")

K=Kit(seed=2210); P=Performer(K,T,SPB,TOTAL,seed=12,style='indie'); P.hum=0.58
sl=buf(); vx=buf(); bs=buf(); fx=buf(); ch=buf(); gt=buf()

# ---- chords ----
Cm=[nn('C2'),nn('C3'),nn('Eb3'),nn('G3')]
Gn=[nn('G2'),nn('B2'),nn('D3')]          # V(maj) chromatic B natural
Abm=[nn('Ab2'),nn('B2'),nn('Eb3')]       # vi deg -> Ab-B-Eb
Abmaj7=[nn('Ab2'),nn('C3'),nn('Eb3'),nn('G3')]
Eb=[nn('Eb2'),nn('G2'),nn('Bb2'),nn('Eb3')]
Fm=[nn('F2'),nn('Ab2'),nn('C3'),nn('F3')]
CYCLE=[Cm,Gn,Abm]
def villa(b,lvl=0.8,arc=1.0,busy=False,climax=False,fill_to=None,with_ride=False):
    for s in range(16):
        acc=0.70 if s%4==0 else 0.40
        P.H(b+s*0.25,s,acc*lvl,o=0.0,art=('edge' if s%4==0 else 'tip'),arc=arc)
    kicks=[(0.0,1.0),(0.75,0.6),(2.0,0.55),(2.75,0.7)] if not busy else \
          [(0.0,1.0),(0.75,0.7),(1.5,0.6),(2.5,0.7),(3.0,0.6),(3.75,0.5)]
    for bb,vv in kicks: P.K(b+bb,int(bb*4)%16,vv*lvl,arc)
    if climax:
        P.S(b+1,4,0.92*lvl,'center',arc); P.S(b+3,12,0.96*lvl,'center',arc)
        for gp in (0.75,1.5,2.25,2.5,3.5): P.S(b+gp,int(gp*4)%16,0.30*lvl,'ghost',arc)
        P.CL(b+1+0.004,4,0.6*lvl,arc); P.CL(b+3+0.004,12,0.62*lvl,arc)
        if with_ride:
            P.RD(b,0,0.50*lvl,bell=True,arc=arc); P.RD(b+2,8,0.42*lvl,bell=True,arc=arc)
    else:
        P.S(b+1,4,0.62*lvl,'center',arc); P.S(b+3,12,0.66*lvl,'center',arc)
        if busy:
            for gp in (0.75,2.5): P.S(b+gp,int(gp*4)%16,0.26*lvl,'ghost',arc)
    if fill_to is not None:
        # fill into the "two-and" (2.5) then crash next bar
        kind=['stutter','snare','tom'][int((fill_to)//4)%3]
        P.fill(b+2.5,1.0,kind,0.85*lvl,next_crash_beat=fill_to)

# SECTION 1: drop-D pedal riff cycle Cm-G-Abm, chromatic Eb-E-G upper mel
def riff1(b,i,g):
    R=np.random.default_rng(i*7+1)
    crunch(sl,T(b),nn('C2'),SPB(b)*3.7,hg(0.10*g),drive=2.4,seed=i)   # low D-pedal-style drone (drop-D feel)
    mel=[nn('Eb3'),nn('E3'),nn('G3')]; offs=[0.0,0.66,1.6]
    for n_,o in zip(mel,offs):
        crunch(sl,T(b)+o*SPB(b)+float(R.normal(0,0.012)),n_,hd(SPB(b)*0.5),hg(0.06*g),drive=1.8,seed=i*3+int(o*5))
for i in range(18):
    b=bar_at('IN',i); c=CYCLE[i%3]; f=1+0.014*i
    if i>=10: mellotron(ch,T(b),c[1],SPB(b)*3.7,hg(0.025*f),'choir',seed=i)
    bassn(bs,T(b),c[0],SPB(b)*3.7,hg(0.14*f))
    if i>=5: subbass(bs,T(b),c[0]-12,SPB(b)*3.7,0.10*f)
    riff1(b,i,f*0.7)
    villa(b,hg((0.42 if i<9 else 0.55)*f),arc=0.5+0.025*i,busy=(i>=12))
    if i==17:
        villa(b,hg(0.80*f),arc=0.98,fill_to=S['ARP'])
    if i>=6:
        line(vx,b,[(0,.5,'C4','a','h'),(.5,.5,'Eb4','o',''),(1,.5,'E4','a','s'),(1.5,1.0,'G4','o','')],
             g=0.06*f,style='deadpan',breath=0.30,seedbase=i*71)
# SECTION 2: Cm <-> Abmaj7 warm arpeggio + violin (the Am<->Fmaj7 move)
ch2=[Cm,Abmaj7]
for i in range(18):
    b=bar_at('ARP',i); c=ch2[i%2]; f=1+0.03*i
    mellotron(ch,T(b),c[1],SPB(b)*3.7,hg(0.05*f),'choir',seed=i+9)
    wurli(ch,T(b),c[0],SPB(b)*3.6,hg(0.06*f))
    bassn(bs,T(b),c[0],SPB(b)*3.5,hg(0.26*f))
    # arpeggiate chord up with ks plucks, human spacing
    R=np.random.default_rng(i*9+3)
    for k_,n_ in enumerate(c):
        clav(sl,T(b)+k_*0.48*SPB(b)+float(R.normal(0,0.012)),n_,hd(SPB(b)*0.7),hg(0.06*f),seed=k_+i*4)
    bowed(sl,T(b)+0.45*BAR,c[-1]+12,SPB(b)*2.6,hg(0.12*f),det=float(R.normal(0,7)),seed=i)
    villa(b,hg(0.7*f),arc=0.7+0.02*i,busy=True,fill_to=(S['PUSH'] if i==17 else None),with_ride=(i%2==1))
    line(vx,b,[(0,.5,'Eb4','a','h'),(.5,.5,'G4','o',''),(1,.5,'C5','a','n'),(1.5,1.5,'Eb5','o','w')],
         g=0.13*f,style='croon',oct8=0.0,breath=0.27,seedbase=200+i)
# SECTION 3: Eb -> Fm big two-chord, Fm "lands on beat 2" push, dist gtr
ch3=[Eb,Fm]
for i in range(18):
    b=bar_at('PUSH',i); c=ch3[i%2]; f=1+0.06*i
    mellotron(ch,T(b),c[1]+12,SPB(b)*3.6,hg(0.07*f),'choir',seed=i+18)
    bassn(bs,T(b),c[0],SPB(b)*3.5,hg(0.30*f))
    subbass(bs,T(b),c[0]-12,SPB(b)*3.5,0.24*f)
    # Fm enters at beat 2 (the push)
    if i%2==1:
        mellotron(ch,T(b)+1*BAR*0.0+SPB(b),Fm[2]+12,SPB(b)*2.6,hg(0.06*f),'choir',seed=i+99)
        bassn(bs,T(b)+SPB(b),nn('F2'),SPB(b)*2.4,hg(0.28))
    motif=[nn('Bb3'),nn('C4'),nn('Eb4'),nn('C4'),nn('Bb3')]
    R=np.random.default_rng(i*5+7)
    for k_,n_ in enumerate(motif):
        crunch(gt,T(b)+k_*0.50*SPB(b)+float(R.normal(0,0.010)),n_+(0 if i%2==0 else 2),hd(SPB(b)*0.45),hg(0.07*f),drive=5.8,seed=k_+i*8)
    hbone(ch,T(b),c[-1],SPB(b)*2.8,hg(0.10*f),growl=0.5,seed=i)
    crunch(gt,T(b)+SPB(b)*1.0,c[2]+12,SPB(b)*2.0,hg(0.08*f),drive=6.5,seed=i)
    villa(b,hg(0.95*f),arc=1.0,busy=True,climax=True,with_ride=True,fill_to=(S['OUT'] if i==17 else None))
    chant(vx,b,[(0,.5,'Bb3','a','h'),(.5,.5,'C4','o',''),(1,1.0,'Eb4','a','y'),(2,.5,'Eb4','a','')],g=0.11*f,n=5,style='shout',seedbase=400+i)
# SECTION 4: 12/8 Abmaj7 outro vamp + chucka triplets + bass walk Ab-Ab-F-Db
out=Abmaj7
bass_out=[nn('Ab1'),nn('Ab1'),nn('F1'),nn('Db2')]
for i in range(22):
    b=bar_at('OUT',i); f=min(1.25,0.72+0.045*i)
    mellotron(ch,T(b),out[1],SPB(b)*3.7,hg(0.06*f),'choir',seed=i+27)
    wurli(ch,T(b),out[2],SPB(b)*3.6,hg(0.06*f))
    bassn(bs,T(b),bass_out[i%4],SPB(b)*3.6,hg(0.26*f))
    subbass(bs,T(b),bass_out[i%4],SPB(b)*3.6,0.16*f)
    bowed(sl,T(b)+0.3*BAR,out[-1]+12,SPB(b)*3.0,hg(0.10*f),det=float(np.random.default_rng(i).normal(0,8)),seed=i)
    # "chucka chucka" triplet stabs (3 per beat) - muted ks
    R=np.random.default_rng(900+i)
    for beat in range(4):
        for ti in range(3):
            tt=T(b)+beat*SPB(b)+ti*SPB(b)/3.0+float(R.normal(0,0.006))
            col=out[2] if ti in (0,2) else out[3]
            crunch(gt,tt,col,hd(SPB(b)*0.16),hg(0.05*f),drive=1.6,seed=beat*3+ti)
    # light 12/8 sway drums: ride bell 1&4, kick 1&4, cross-stick 2&4, hat triplets
    P.RD(b,0,0.40*f,bell=True); P.RD(b+3,12,0.34*f,bell=True)
    P.K(b,0,0.46*f); P.K(b+3,12,0.42*f)
    P.S(b+1,4,0.34*f,'cross'); P.S(b+3,12,0.34*f,'cross')
    for beat in range(4):
        for ti in range(3):
            P.H(b+beat*1.0+ti*(SPB(b)/3.0),beat*4+ti,0.30*f,o=0.0,art='tip')
    line(vx,b,[(0,1.5,out[-1],'a','h'),(1.5,2.5,out[2],'o','y')],g=0.07*f,style='croon',breath=0.30,seedbase=700+i)
# TAG: one Cm riff + held Cm
b=bar_at('TAG',0)
riff1(b,99,1.0)
bassn(bs,T(b),nn('C2'),SPB(b)*3.6,hg(0.24))
subbass(bs,T(b),nn('C1'),SPB(b)*3.6,0.20)
for m in Cm: mellotron(ch,T(b),m,SPB(b)*3.6,0.07,'choir',seed=int(m))
P.K(b,0,1.0); P.S(b,0,0.9,'center'); P.CR(b,0,0.8,size=1.2)
P.RD(b+2,8,0.5,bell=True)
line(vx,b,[(0,2.0,'C4','a','h'),(2.0,2.0,'Eb4','o','y')],g=0.12,style='whisper',breath=0.34,seedbase=999)

P.apply_chokes()
DRUMS=mix_kit(P.bus,room_amount=0.24,oh_amount=0.9,lpf=9800)
noise_sw(fx,0,T(END),0.007,True,70,1400)
STEMS=[(sl,-0.40,0.62,0.40,0.0),(gt,0.50,0.56,0.40,7.0),(ch,0.10,0.66,0.22,0.0),(fx,0.0,0.9,0.0,0.0)]
MAPT=[(n,a,b_,(7.0 if n in('IN','TAG') else 2.7)) for n,a,b_ in MAP]
run(NAME, lambda voc: mixdown(NAME,vx,STEMS,DRUMS,bs,MAPT,vocals=voc,
    wet=0.21,decay=1.6,wide=1.42,drum_gain=0.78,bass_gain=0.88,crush_amt=0.20,
    rms_target=0.170), MAPT)