#!/usr/bin/env python3
"""QC số: peak, RMS, corrLR, dải 8-16k, dynamics theo khối 4s."""
import sys, subprocess, numpy as np
from scipy import signal as sg

def load_stereo(f):
    raw=subprocess.run(["ffmpeg","-v","quiet","-i",f,"-ar","44100","-ac","2","-f","f32le","-"],capture_output=True).stdout
    x=np.frombuffer(raw,dtype=np.float32).reshape(-1,2)
    return x

def report(f):
    x=load_stereo(f)
    L,R=x[:,0],x[:,1]
    mono=(L+R)/2
    peak=np.abs(x).max()
    rms=float(np.sqrt((mono**2).mean()))
    # corr LR
    c=np.corrcoef(L[::97],R[::97])[0,1]
    # nang luong 8-16k
    f_,t_,Z=sg.stft(mono,fs=44100,nperseg=4096,noverlap=3072)
    Z=np.abs(Z)**2
    fr=f_
    hi=Z[fr>8000].sum(); tot=Z.sum()
    hi_pct=100*hi/tot
    # dynamics: rms 4s blocks
    n=44100*4; k=len(mono)//n
    blk=np.sqrt((mono[:k*n].reshape(k,n)**2).mean(1))
    db=20*np.log10(blk+1e-9)
    print(f"{f.split('/')[-1]:40s} peak {peak:.3f} rms {rms:.4f} corrLR {c:.2f} 8-16k {hi_pct:.2f}% dyn {db.max()-db.min():.1f}dB")

for f in sys.argv[1:]:
    report(f)
