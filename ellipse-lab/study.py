"""Synthetic ellipse fitting benchmark; target labels are evaluation-only."""
from pathlib import Path
import json, inspect, time
import numpy as np
from scipy.optimize import least_squares
from skimage.measure import EllipseModel, ransac
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent

def canonical(p):
 x,y,a,b,t=map(float,p)
 if b>a:a,b,t=b,a,t+np.pi/2
 return np.array([x,y,a,b,t%np.pi])

def curve(p,n=360):
 x,y,a,b,t=p;u=np.linspace(0,2*np.pi,n)
 return np.column_stack((x+a*np.cos(u)*np.cos(t)-b*np.sin(u)*np.sin(t),y+a*np.cos(u)*np.sin(t)+b*np.sin(u)*np.cos(t)))

def scene(seed=42,noise=150,sigma=.8,theta=np.pi/6):
 rng=np.random.RandomState(seed);truth=np.array([50,50,32,14,theta]);target=curve(truth,70)
 target[:,0]+=rng.normal(0,sigma,70);target[:,1]+=rng.normal(0,sigma,70)
 clutter=np.column_stack((rng.uniform(0,100,noise),rng.uniform(0,100,noise)))
 return np.vstack((target,clutter)),truth

def original(points):
 bounds=[(35,65),(35,65),(15,45),(5,25),(0,np.pi)];best_score=-1;best=None
 for it in range(4):
  grids=np.meshgrid(*[np.linspace(*b,n) for b,n in zip(bounds,[6,6,5,5,6])],indexing='ij');hyp=np.stack([g.ravel() for g in grids],axis=1);scores=[]
  for batch in np.array_split(hyp,30):
   x,y,a,b,t=batch.T;dx=points[:,0,None]-x;dy=points[:,1,None]-y
   u=dx*np.cos(t)+dy*np.sin(t);v=-dx*np.sin(t)+dy*np.cos(t)
   res=np.abs(u*u/a**2+v*v/b**2-1);s=(res<.25).sum(axis=0)*np.exp(-1.8*np.minimum(res,1).mean(axis=0));s[(a<=3)|(b<=3)|(a>70)|(b>70)]=0;scores.extend(s)
  idx=int(np.argmax(scores));p=hyp[idx]
  if scores[idx]>best_score:best_score=scores[idx];best=p.copy()
  span=.4/(it+1);bounds=[(max(lo,v-w*span),min(hi,v+w*span)) for v,w,lo,hi in zip(p,[15,15,10,8,.5],[0,0,5,3,0],[100,100,50,30,np.pi])]
 return canonical(best)

def distances(p,points):
 m=EllipseModel();m.params=tuple(p);return m.residuals(points)

def sampson(p,points):
 x,y,a,b,t=p;dx=points[:,0]-x;dy=points[:,1]-y;u=dx*np.cos(t)+dy*np.sin(t);v=-dx*np.sin(t)+dy*np.cos(t)
 return ((u/a)**2+(v/b)**2-1)/np.maximum(2*np.sqrt(u*u/a**4+v*v/b**4),1e-9)

class FastEllipseModel(EllipseModel):
 """First-order geometric residual for fast RANSAC hypothesis scoring."""
 def residuals(self,data):return np.abs(sampson(self.params,data))

def robust(points,seed=0,threshold=2.4):
 kw={'rng':np.random.default_rng(seed)} if 'rng' in inspect.signature(ransac).parameters else {'random_state':seed}
 def valid(model,*_):
  if model.params is None:return False
  x,y,a,b,t=canonical(model.params);return -20<x<120 and -20<y<120 and 4<b<=a<90 and a/b<8
 model,mask=ransac(points,FastEllipseModel,min_samples=5,residual_threshold=threshold,max_trials=2000,stop_probability=.999,is_model_valid=valid,**kw)
 if model is None:raise RuntimeError('No valid consensus')
 initial=canonical(model.params);p=initial.copy()
 for _ in range(4):
  mask=distances(p,points)<threshold
  q=canonical(least_squares(sampson,p,args=(points[mask],),bounds=([-20,-20,4,4,-10],[120,120,90,90,10]),loss='soft_l1',f_scale=.8,max_nfev=150).x)
  before=distances(p,points);after=distances(q,points)
  if np.minimum(after**2,threshold**2).sum()<np.minimum(before**2,threshold**2).sum():p=q
  else:break
 return canonical(p),initial

def metrics(p,truth,points):
 mask=distances(p,points)<2.4
 return {'center_error':float(np.linalg.norm(p[:2]-truth[:2])),'major_error':float(abs(p[2]-truth[2])),'minor_error':float(abs(p[3]-truth[3])),'angle_error_deg':float(np.degrees(abs((p[4]-truth[4]+np.pi/2)%np.pi-np.pi/2))),'boundary_rmse':float(np.sqrt(np.mean(distances(p,curve(truth,720))**2))),'precision':float(mask[:70].sum()/max(mask.sum(),1)),'recall':float(mask[:70].mean())}

def run():
 results=[];examples=[]
 scenarios=[('original',150,.8,30),('horizontal',150,.8,0),('near-wrap',150,.8,177),('noisier',150,1.6,60),('more-clutter',300,.8,110),('stress',500,1.6,145)]
 for name,n,sigma,angle in scenarios:
  for seed in [42,7,19,83,101]:
   pts,truth=scene(seed,n,sigma,np.radians(angle));fitted,initial=robust(pts,seed);allpoints=EllipseModel();allpoints.estimate(pts)
   fits={'original_grid':original(pts),'all_points':canonical(allpoints.params),'ransac':initial,'refined':fitted}
   for method,p in fits.items():results.append({'scenario':name,'seed':seed,'method':method,'params':p.tolist(),**metrics(p,truth,pts)})
   if seed==42:examples.append({'name':name,'sigma':sigma,'clutter':n,'truth':truth.tolist(),'points':pts.tolist(),'fits':{k:v.tolist() for k,v in fits.items()}})
  print('Finished',name,flush=True)
 (ROOT/'results.json').write_text(json.dumps({'threshold':2.4,'trials':2000,'results':results,'examples':examples},indent=2)+'\n')
 fig,axes=plt.subplots(2,3,figsize=(15,10))
 for ax,e in zip(axes.flat,examples):
  pts=np.array(e['points']);ax.scatter(*pts[70:].T,s=8,c='#bbc1c7',label='Clutter');ax.scatter(*pts[:70].T,s=10,c='#267ac4',label='Target samples')
  for method,color,style in [('original_grid','#cf6943','--'),('ransac','#8e71b3',':'),('refined','#16856a','-')]:
   xy=curve(e['fits'][method]);ax.plot(*xy.T,style,color=color,label=method)
  xy=curve(e['truth']);ax.plot(*xy.T,':',color='black',label='Truth');ax.set(xlim=(0,100),ylim=(0,100),title=e['name'],aspect='equal')
 axes.flat[0].legend(fontsize=7);fig.tight_layout();fig.savefig(ROOT/'comparison.png',dpi=160);plt.close(fig)
 for method in ['original_grid','all_points','ransac','refined']:
  rs=[r for r in results if r['method']==method];v=np.array([r['boundary_rmse'] for r in rs]);print(method,'median',np.median(v),'worst',v.max(),'success',(v<2).sum(),'/30',flush=True)
if __name__=='__main__':run()
