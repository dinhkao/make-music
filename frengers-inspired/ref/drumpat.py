#!/usr/bin/env python3
"""Trích drum pattern: tách kick/snare/hat từ stem trống rồi in grid 16ths theo bar."""
import sys, subprocess, numpy as np
from scipy import signal as sg

SR=22050
def load(f):
    raw=subprocess.run(["ffmpeg","-v","quiet","-i",f,"-ar",str(SR),"-ac","1","-f","f32le","-"],capture_output=True).stdout
    return np.frombuffer(raw,dtype=np.float32)

def onset_env(x, hop=256):
    f,t,Z=sg.stft(x,fs=SR,nperseg=1024,noverlap=1024-hop)
    Z=np.abs(Z)
    fl=np.clip(np.diff(Z,axis=1),0,None)
    # trọng số theo dải tần
    fr=f[1:]
    freqs=np.arange(len(fl))
    w=np.ones(len(fl))
    return fl.mean(0), t[1:]

def band(x,lo,hi):
    b,a=sg.butter(4,[lo/(SR/2),hi/(SR/2)],'band')
    return sg.lfilter(b,a,x)

def onsets(env, t, thresh=0.55, min_gap=0.045):
    # tìm đỉnh cục bộ trên env
    pk,_=sg.find_peaks(env,height=thresh,distance=int(min_gap/(t[1]-t[0])))
    return t[pk]

def grid_pattern(times, bpm, nbars, out_beat=0.5):
    """In pattern dạng chuỗi 16ths cho mỗi bar: kí tự = mật độ onset"""
    beat=60.0/bpm
    bar=4*beat
    grid=16
    res=[]
    for b in range(nbars):
        t0=b*bar
        slots=[0]*grid
        for t in times:
            if t0<=t<t0+bar:
                s=int((t-t0)/bar*grid)
                if 0<=s<grid: slots[s]=1
        res.append("".join("#" if v else "." for v in slots))
    return res

def section_pattern(x_drum, bpm, t_sec, secs, label):
    """secs: list (start_s, end_s) in giây"""
    k=band(x_drum,40,140)   # kick
    s=band(x_drum,150,600)  # snare body
    h=band(x_drum,6000,10000) # hats
    out=[]
    for f,envf,tf in [(k,'kick',None),(s,'snare',None),(h,'hat',None)]:
        env,t=onset_env(f)
        o=onsets(env,t,thresh=0.5)
        out.append((envf,o))
    print(f"\n### {label} @ {bpm}bpm")
    for sec in secs:
        s0,s1=sec
        print(f"  [{s0:.0f}-{s1:.0f}s]")
        for nm,o in out:
            pats=grid_pattern([tt for tt in o if s0<=tt<s1],bpm,int((s1-s0)/(4*60/bpm)))
            print(f"    {nm:6s} " + " | ".join(pats))

if __name__=="__main__":
    # args: file, bpm, label, list of (s0,s1)
    f=sys.argv[1]; bpm=float(sys.argv[2]); label=sys.argv[3]
    secs=[]
    for a in sys.argv[4:]:
        s0,s1=a.split("-"); secs.append((float(s0),float(s1)))
    x=load(f)
    section_pattern(x,bpm,0,secs,label)
