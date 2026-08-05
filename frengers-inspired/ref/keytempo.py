#!/usr/bin/env python3
"""Đo key (Krumhansl-Schmuckler chroma) + tempo (onset autocorrelation) cho 1 file wav."""
import sys, numpy as np
from scipy import signal as sg

SR=22050
# Krumhansl-Kessler profiles
MAJ=np.array([6.35,2.23,3.48,2.33,4.38,4.09,2.52,5.19,2.39,3.66,2.29,2.88])
MIN=np.array([6.33,2.68,3.52,5.38,2.60,3.53,2.54,4.75,3.98,2.69,3.34,3.17])

def load(f):
    import subprocess
    raw=subprocess.run(["ffmpeg","-v","quiet","-i",f,"-ar",str(SR),"-ac","1","-f","f32le","-"],
                       capture_output=True).stdout
    x=np.frombuffer(raw,dtype=np.float32)
    return x

def chroma(x, hop=2048, nfft=4096):
    f,t,Z=sg.stft(x,fs=SR,nperseg=nfft,noverlap=nfft-hop)
    Z=np.abs(Z)
    # map bin->pitch class
    bins=np.arange(len(f)); pc=np.round(12*np.log2(f[1]*np.maximum(bins,1)/440)+69).astype(int)%12
    C=np.zeros((12,Z.shape[1]))
    for p in range(12):
        m=pc==p
        if m.sum(): C[p]=Z[m].sum(0)
    return C

def keydetect(x):
    C=chroma(x)
    # 4s blocks, trung bình có trọng số
    blk=SR*4//2048
    n=C.shape[1]
    best=[]
    for t0 in range(0,n,blk):
        c=C[:,t0:t0+blk].mean(1)
        c=c/c.max()
        ks=[]
        for i in range(12):
            ks.append(float(np.corrcoef(np.roll(MAJ,i),c)[0,1]))
            ks.append(float(np.corrcoef(np.roll(MIN,i),c)[0,1]))
        best.append(int(np.argmax(ks)))
    k=int(np.bincount(best).argmax())
    maj = k%2==0
    pc=k//2
    names=['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
    return names[pc]+(' major' if maj else ' minor')

def tempo(x):
    # spectral flux onset envelope
    f,t,Z=sg.stft(x,fs=SR,nperseg=1024,noverlap=1024-512)
    Z=np.abs(Z)
    fl=np.diff(Z,axis=1); fl=np.clip(fl,0,None).mean(0)
    fl=sg.lfilter([1],[1,-0.94],fl)
    # autocorr 30..240 bpm (lag range)
    sr_env=SR/512
    lags=np.arange(int(sr_env*60/240),int(sr_env*60/30))
    ac=np.correlate(fl,fl,'full')[len(fl)-1:]
    ac=ac[lags]
    ac/= (ac[0]+1e-9)
    # peak
    cand=lags[np.argmax(ac[10:])+10]
    bpm=60.0*sr_env/cand
    return bpm

for f in sys.argv[1:]:
    x=load(f)
    k=keydetect(x)
    b=tempo(x)
    print(f"{f:40s} key={k:10s} tempo={b:6.1f} bpm  dur={len(x)/SR/60:.2f}min")
