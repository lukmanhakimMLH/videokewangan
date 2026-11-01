import numpy as np
from scipy.signal import butter,sosfilt,fftconvolve
from scipy.io import wavfile
SR=48000;rng=np.random.default_rng(7)
def t(d):return np.arange(int(SR*d))/SR
def save(n,x,st=False):
    x=x/ (np.max(np.abs(x))+1e-9)*0.9
    if not st: x=np.stack([x,x],1)
    wavfile.write(f"sfx/{n}.wav",SR,(x*32767).astype(np.int16))
def rev(x,d=1.6,mix=0.3):
    ir=rng.standard_normal(int(SR*d))*np.exp(-t(d)*4.5);ir=sosfilt(butter(2,6000,'low',fs=SR,output='sos'),ir)
    w=fftconvolve(x,ir)[:len(x)+len(ir)-1];w/=np.max(np.abs(w))+1e-9
    y=np.zeros(len(w));y[:len(x)]=x/(np.max(np.abs(x))+1e-9)
    return y*(1-mix)+w*mix
# whoosh: noise through sweeping bandpass (chunked)
def whoosh(d=0.7,f0=300,f1=4000,rise=0.6):
    n=rng.standard_normal(int(SR*d));out=np.zeros_like(n);ch=512
    for i in range(0,len(n),ch):
        p=i/len(n);f=f0*(f1/f0)**(min(p/rise,1) if p<rise else 1-(p-rise)/(1-rise)*0.6)
        sos=butter(2,[max(f*0.6,40),min(f*1.6,20000)],'band',fs=SR,output='sos');out[i:i+ch]=sosfilt(sos,n[i:i+ch])
    tt=t(d);env=np.sin(np.pi*np.clip(tt/d,0,1))**2;return out*env
save("whoosh",rev(whoosh(),1.0,0.25))
save("whoosh_soft",rev(whoosh(0.5,500,2500,0.5),0.8,0.3))
# impact boom
tt=t(2.2);f=38+50*np.exp(-tt*9);ph=2*np.pi*np.cumsum(f)/SR
boom=np.sin(ph)*np.exp(-tt*2.2)+0.5*np.sin(2*ph)*np.exp(-tt*5)
cl=sosfilt(butter(2,[800,6000],'band',fs=SR,output='sos'),rng.standard_normal(len(tt)))*np.exp(-tt*35)*0.6
save("impact",rev(np.tanh((boom+cl)*1.6),2.0,0.35))
# riser
tt=t(1.6);n=sosfilt(butter(2,[2000,9000],'band',fs=SR,output='sos'),rng.standard_normal(len(tt)))
f=200*(8)**(tt/1.6);tone=np.sin(2*np.pi*np.cumsum(f)/SR)*0.25
save("riser",(n*0.6+tone)*(tt/1.6)**2.2)
# shimmer / sparkle
tt=t(2.0);x=np.zeros(len(tt))
for k in range(14):
    on=rng.uniform(0,0.7);fr=rng.choice([1567.98,2093,2349.3,2637,3135.96,3520,4186])*rng.choice([1,1,0.5])
    m=tt>=on;x[m]+=np.sin(2*np.pi*fr*(tt[m]-on))*np.exp(-(tt[m]-on)*5)*rng.uniform(0.3,1)
save("shimmer",rev(x,2.0,0.45))
# soft tick
tt=t(0.12);save("tick",rev(np.sin(2*np.pi*1800*tt)*np.exp(-tt*60)+0.3*sosfilt(butter(2,3000,'high',fs=SR,output='sos'),rng.standard_normal(len(tt)))*np.exp(-tt*120),0.4,0.2))
# deep hit (sub drop) for key line
tt=t(1.5);f=60*np.exp(-tt*1.5)+30;save("subdrop",np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*2.5))
# ambient pad bed: Am F C G (A minor), 21s
D=24.6;tt=t(D);L=np.zeros(len(tt));R=np.zeros(len(tt))
ch=[[220,261.63,329.63,440],[174.61,220,261.63,349.23],[130.81,196,261.63,329.63],[196,246.94,293.66,392]]
seg=D/4
for i,c in enumerate(ch*1):
    s=i*seg;e=s+seg+1.2;m=(tt>=s)&(tt<e);lt=tt[m]-s
    env=np.minimum(1,lt/1.2)*np.minimum(1,np.clip((e-tt[m])/1.2,0,1))
    for j,fr in enumerate(c):
        for det,side in ((-0.6,0),(0.6,1)):
            v=(np.sin(2*np.pi*(fr+det)*lt)+0.3*np.sin(2*np.pi*2*(fr+det)*lt))*env*(0.5 if j==0 else 0.35)
            (L if side==0 else R)[m]+=v
    # sub bass
    b=np.sin(2*np.pi*c[0]/2*lt)*env*0.5;L[m]+=b;R[m]+=b
sos=butter(2,1800,'low',fs=SR,output='sos');L=sosfilt(sos,L);R=sosfilt(sos,R)
# gentle piano-like plucks on beat
for k in range(int(D/1.0)):
    s=k*1.0+0.5;c=ch[min(int(s/seg),3)];fr=c[(k*2)%4]*2;m=(tt>=s)&(tt<s+1.5);lt=tt[m]-s
    v=np.sin(2*np.pi*fr*lt)*np.exp(-lt*3.5)*0.18;L[m]+=v;R[m]+=v*0.9
st=np.stack([rev(L,2.5,0.4),rev(R,2.5,0.4)],1)[:len(tt)]
fade=np.minimum(1,tt/1.5)*np.minimum(1,(D-tt)/2.0);st*=fade[:,None]
save("pad",st,True)
