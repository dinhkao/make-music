#!/usr/bin/env python3
"""Drum pattern trung bình: xác suất hit trên 16 slot của 1 bar, in dạng số."""
import numpy as np, subprocess, sys
from scipy import signal as sg
SR=22050
def load(f):
    raw=subprocess.run(["ffmpeg","-v","quiet","-i",f,"-ar",str(SR),"-ac","1","-f","f32le","-"],capture_output=True).stdout
    return np.frombuffer(raw,dtype=np.float32)
def band(x,lo,hi):
    b,a=sg.butter(4,[lo/(SR/2),hi/(SR/2)],'band')
    return sg.lfilter(b,a,x)
def avg_pattern(f, bpm, secs, bands, height=0.20):
    x=load(f)
    print(f"\n== {os.path.basename(f)} ==")
    for nm,lo,hi in bands:
        y=band(x,lo,hi)
        fv,tv,Z=sg.stft(y,fs=SR,nperseg=1024,noverlap=1024-256)
        fl=np.clip(np.diff(np.abs(Z),axis=1),0,None).mean(0)
        env=fl/fl.max()
        pk,_=sg.find_peaks(env,height=height,distance=6)
        ons=tv[pk]
        beat=60.0/bpm; bar=4*beat; g=16
        for s0,s1 in secs:
            slots=np.zeros(g); nb=0
            for b0 in np.arange(s0,s1-bar,bar):
                nb+=1
                for t in ons:
                    if b0<=t<b0+bar:
                        slots[int((t-b0)/bar*g)]+=1
            pat=" ".join(f"{v/nb:4.1f}" for v in slots)
            print(f"  {nm:6s} [{s0:3.0f}-{s1:3.0f}s] {pat}")
import os
if __name__=="__main__":
    f=sys.argv[1]; bpm=float(sys.argv[2])
    secs=[tuple(map(float,a.split("-"))) for a in sys.argv[3:]]
    avg_pattern(f,bpm,secs,[("kick",40,140),("snare",150,600),("hat",6000,10000)])
