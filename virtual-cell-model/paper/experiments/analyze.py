"""Produce all manuscript statistics and original vector figures from saved data."""
from pathlib import Path
import csv,json,hashlib,platform
from datetime import datetime, timezone
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, Circle, Rectangle
P=Path(__file__).resolve().parents[1]; F=P/'figures'; F.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'ps.fonttype':42,'axes.labelcolor':'#193b37','text.color':'#193b37','axes.titleweight':'bold','savefig.facecolor':'white'})
colors=['#24786d','#b95c37','#758da6','#a28b42']; names=['Prior only','Valid relations','Shuffled relations','Shared wrong labels']; modes=['prior','valid','shuffled','shared_wrong']
def read(name):return list(csv.DictReader((P/'data'/name).open()))
def save(fig,name):
 fig.savefig(F/(name+'.pdf'),bbox_inches='tight',metadata={'CreationDate':datetime(2026,11,11,tzinfo=timezone.utc),'ModDate':datetime(2026,11,11,tzinfo=timezone.utc)});fig.savefig(F/(name+'.png'),dpi=180,bbox_inches='tight');plt.close(fig)
def bootstrap(values,seed=9817):
 x=np.asarray(values);rng=np.random.default_rng(seed); means=x[rng.integers(0,len(x),(5000,len(x)))].mean(axis=1)
 return [float(np.quantile(means,.025)),float(np.quantile(means,.975))]
rows=read('compatibility.csv'); grouped={m:[r for r in rows if r['condition']==m] for m in modes}
stats={'compatibility':{},'paired':{}}
for m in modes:
 stats['compatibility'][m]={}
 for k in ['accuracy','brier','entropy','iterations','converged']:
  vals=np.array([float(r[k]) for r in grouped[m]])
  stats['compatibility'][m][k]={'mean':float(vals.mean()),'ci95':bootstrap(vals)}
for m in modes[1:]:
 diff=np.array([float(r['accuracy']) for r in grouped[m]])-np.array([float(r['accuracy']) for r in grouped['prior']])
 stats['paired'][m]={'accuracy_difference':float(diff.mean()),'ci95':bootstrap(diff)}
# 1: architectural responsibilities.
fig,ax=plt.subplots(figsize=(10,5.5));ax.set(xlim=(0,10),ylim=(0,5.5));ax.axis('off')
def box(ax,x,y,w,h,title,body='',color='#e6eee5'):
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.05',facecolor=color,edgecolor='#65877b'))
 ax.text(x+w/2,y+h*.72,title,ha='center',va='center',weight='bold',fontsize=10)
 if body:ax.text(x+w/2,y+h*.32,body,ha='center',va='center',fontsize=8)
def arrow(ax,a,b):ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','color':'#9c5033','lw':1.6})
box(ax,.2,4.25,9.5,.9,'PersonModel','Common owner; biological and behavioral energy ledgers remain distinct')
box(ax,.2,1.95,2.6,1.7,'Body','Organ → tissue → cell\n→ molecular composition')
box(ax,3.3,1.95,3.2,1.7,'Brain and relational memory','Identity IDs · names · typed edges\nself-model · opponent models')
box(ax,7,1.95,2.7,1.7,'Governor','Permission → feasibility\n→ Pareto set → valuation')
box(ax,3.3,.15,6.4,1.05,'Experience and summaries','Predicted / observed outcomes · provenance · forecast error')
for x in [1.5,4.9,8.35]:arrow(ax,(x,4.25),(x,3.7))
arrow(ax,(6.5,2.8),(7,2.8));arrow(ax,(8.3,1.95),(8.3,1.25));arrow(ax,(4.9,1.25),(4.9,1.95))
ax.text(.3,.6,'Implementation architecture\nNo fitted biological dynamics',fontsize=9)
save(fig,'fig01_architecture')
# 2: compatibility measured.
fig,axes=plt.subplots(2,2,figsize=(9.5,6.4))
for ax,key,label in zip(axes.flat,['accuracy','brier','entropy','iterations'],['Label accuracy','Binary squared strength error','Mean label entropy (nats)','Iterations to tolerance']):
 means=[stats['compatibility'][m][key]['mean'] for m in modes];ci=[stats['compatibility'][m][key]['ci95'] for m in modes]
 err=np.array([[v-c[0],c[1]-v] for v,c in zip(means,ci)]).T
 ax.bar(range(4),means,color=colors,yerr=err,capsize=3);ax.set_xticks(range(4),['Prior','Valid','Shuffled','Wrong'],rotation=15);ax.set_ylabel(label)
 if key=='accuracy':ax.set_ylim(0,1)
 ax.text(-.12,1.04,chr(97+list(axes.flat).index(ax)),transform=ax.transAxes,weight='bold',fontsize=13)
fig.tight_layout();save(fig,'fig02_compatibility')
# 3: paired accuracy changes.
fig,ax=plt.subplots(figsize=(8,3.6))
for i,m in enumerate(modes[1:]):
 diff=(np.array([float(r['accuracy']) for r in grouped[m]])-np.array([float(r['accuracy']) for r in grouped['prior']]))*100
 ax.scatter(np.full(len(diff),i)+np.random.default_rng(100+i).uniform(-.19,.19,len(diff)),diff,s=8,alpha=.28,color=colors[i+1])
 ci=np.array(stats['paired'][m]['ci95'])*100;mean=stats['paired'][m]['accuracy_difference']*100
 ax.errorbar(i,mean,yerr=[[mean-ci[0]],[ci[1]-mean]],fmt='o',color='black',capsize=5)
ax.axhline(0,color='gray',lw=1);ax.set_xticks(range(3),names[1:]);ax.set_ylabel('Accuracy difference from prior (percentage points)');fig.tight_layout();save(fig,'fig03_paired')
# 4: convergence sensitivity.
grid=read('convergence.csv');gammas=[0,.5,1.5,3,6];damps=[.2,.5,.8,1]
fig,axes=plt.subplots(1,3,figsize=(11,3.8))
for ax,key,title in zip(axes,['accuracy','iterations','converged'],['Mean label accuracy','Mean iterations','Converged fraction']):
 matrix=np.array([[np.mean([float(r[key]) for r in grid if float(r['coupling'])==g and float(r['damping'])==d]) for g in gammas]for d in damps])
 im=ax.imshow(matrix,aspect='auto',cmap='viridis',vmin=0 if key!='iterations' else None,vmax=1 if key!='iterations' else None)
 for i in range(4):
  for j in range(5):ax.text(j,i,f'{matrix[i,j]:.2f}' if key!='iterations' else f'{matrix[i,j]:.0f}',ha='center',va='center',color='white' if matrix[i,j]<(matrix.min()+matrix.max())/2 else 'black',fontsize=7)
 ax.set_xticks(range(5),gammas);ax.set_yticks(range(4),damps);ax.set_xlabel('Coupling');ax.set_ylabel('Damping');ax.set_title(title,fontsize=10);fig.colorbar(im,ax=ax,shrink=.7)
fig.tight_layout();save(fig,'fig04_convergence')
# 5: multiobjective weights and threshold.
policy=read('policies.csv');stats['policy']={'count':len(policy),'C':sum(r['selection']=='0' for r in policy),'D':sum(r['selection']=='1' for r in policy),'mathematical_ties':sum(int(r['resources'])==25 for r in policy),'boundary_C':sum(int(r['resources'])==25 and r['selection']=='0' for r in policy),'boundary_D':sum(int(r['resources'])==25 and r['selection']=='1' for r in policy)}
h=np.array([float(r['health'])/100 for r in policy]);rel=np.array([float(r['relationships'])/100 for r in policy]);money=np.array([float(r['resources'])/100 for r in policy]);select=np.array([int(r['selection']) for r in policy])
fig,axes=plt.subplots(1,2,figsize=(9.5,4))
x=rel+.5*money;y=money*np.sqrt(3)/2
axes[0].scatter(x,y,c=np.where(select==0,colors[0],colors[1]),s=5,rasterized=True)
axes[0].plot([0,1,.5,0],[0,0,np.sqrt(3)/2,0],color='#193b37');axes[0].text(-.03,-.07,'Health',ha='center');axes[0].text(1,-.07,'Relationships',ha='center');axes[0].text(.5,.92,'Resources',ha='center');axes[0].set_aspect('equal');axes[0].axis('off');axes[0].set_title('Policy regions over 5,151 weight vectors')
t=np.linspace(0,1,101);axes[1].plot(t,(1-t)*7.5+t*3,label='C',color=colors[0]);axes[1].plot(t,(1-t)*5.5+t*9,label='D',color=colors[1]);axes[1].axvline(.25,color='gray',ls='--');axes[1].set(xlabel='Resource weight (other weights equal)',ylabel='Weighted score');axes[1].legend();fig.tight_layout();save(fig,'fig05_policy')
# 6: forecast diagnostics.
forecasts=read('forecasts.csv');stats['forecasts']={};fig,axes=plt.subplots(1,3,figsize=(11,3.5))
y=np.array([float(r['outcome'])for r in forecasts]);
for key,color in zip(['calibrated','overconfident','underconfident'],colors):
 p=np.array([float(r[key])for r in forecasts]);bs=(p-y)**2;logloss=-np.log(np.where(y==1,p,1-p))
 perseed=np.array([bs[i:i+200].mean()for i in range(0,len(bs),200)])
 stats['forecasts'][key]={'brier':float(bs.mean()),'brier_ci95':bootstrap(perseed),'logloss':float(logloss.mean())}
 xx=[];yy=[]
 for lo,hi in zip(np.linspace(0,1,11)[:-1],np.linspace(0,1,11)[1:]):
  mask=(p>=lo)&(p<hi)
  if mask.any():xx.append(p[mask].mean());yy.append(y[mask].mean())
 axes[0].plot(xx,yy,'o-',label=key,color=color)
axes[0].plot([0,1],[0,1],'--',color='gray');axes[0].set(xlabel='Mean forecast probability',ylabel='Observed event fraction');axes[0].legend(fontsize=7)
for ax,metric,label in [(axes[1],'brier','Brier score'),(axes[2],'logloss','Mean log loss (nats)')]:
 ax.bar(range(3),[stats['forecasts'][k][metric]for k in stats['forecasts']],color=colors[:3]);ax.set_xticks(range(3),['Oracle p','Overconf.','Underconf.'],rotation=20);ax.set_ylabel(label)
fig.tight_layout();save(fig,'fig06_forecasts')
# 7: shared summaries.
summaries=read('summaries.csv');b=np.array([int(r['branches'])for r in summaries]);fig,axes=plt.subplots(1,2,figsize=(9,3.5))
axes[0].plot(b,[int(r['computed_observations'])for r in summaries],'o-',label='Visited-ID summary',color=colors[0]);axes[0].plot(b,2*b,'s--',label='Path-count baseline',color=colors[1]);axes[0].set(xlabel='Branches sharing one observation',ylabel='Observation count');axes[0].legend()
axes[1].plot(b,[float(r['mean_health'])for r in summaries],'o-',label='Unique records',color=colors[0]);axes[1].plot(b,np.full(len(b),5),'s--',label='Path-weighted baseline',color=colors[1]);axes[1].set(xlabel='Branches',ylabel='Mean health proxy');axes[1].legend();fig.tight_layout();save(fig,'fig07_summaries')
# 8: topology and routes.
fig,axes=plt.subplots(1,3,figsize=(10,3.4));points=np.array([[.1,.1],[.9,.1],[.5,.8]])
for j,ax in enumerate(axes):
 if j==1:ax.add_patch(Polygon(points,facecolor='#b7d9ca',alpha=.8))
 for i in range(3):
  a=points[i];b=points[(i+1)%3];ax.plot([a[0],b[0]],[a[1],b[1]],color=colors[0],lw=2)
 ax.scatter(points[:,0],points[:,1],s=90,color=colors[0],zorder=3)
 if j==2:
  for i,k in [(0,2),(2,1)]:arrow(ax,tuple(points[i]+[0,.06]),tuple(points[k]+[0,.06]))
 for i,p in enumerate(points):ax.text(*p,str(i),color='white',ha='center',va='center',fontsize=8)
 ax.set(xlim=(-.1,1.1),ylim=(-.1,1));ax.axis('off');ax.set_title(['Pairwise contacts','Declared 2-simplex','Ordered route 0 → 2 → 1'][j],fontsize=10)
 ax.text(.5,-.05,['V=3, E=3, F=0; χ=0','V=3, E=3, F=1; χ=1','Traversal order is separate'][j],ha='center',fontsize=8)
save(fig,'fig08_topology')
# 9: chess positions derived from the saved source PGN.
import chess,chess.pgn
source=P/'data'/'chess_cases.pgn'
games=[]
with source.open() as f:
 while (g:=chess.pgn.read_game(f))is not None:
  if g.headers.get('GameId')in ['UYo057a7','g3J5EH39']:games.append(g)
boards={g.headers['GameId']:g.end().board()for g in games};assert boards['UYo057a7'].is_checkmate();assert boards['g3J5EH39'].is_stalemate()
(P/'data'/'chess_cases.pgn').write_text('\n\n'.join(str(g)for g in games)+'\n')
fig,axes=plt.subplots(1,2,figsize=(9,4.8))
for ax,key,title in zip(axes,['UYo057a7','g3J5EH39'],['Queen–rook coordination: checkmate','No legal move, no check: stalemate']):
 board=boards[key]
 for rank in range(8):
  for file in range(8):
   ax.add_patch(Rectangle((file,rank),1,1,facecolor='#d7e2d4'if(file+rank)%2==0 else'#faf8ed'))
   piece=board.piece_at(chess.square(file,rank))
   if piece:
    ax.text(file+.5,rank+.5,piece.symbol().upper(),ha='center',va='center',weight='bold',fontsize=16,color='white'if piece.color else'#193b37',bbox={'facecolor':'#193b37'if piece.color else'#f0bd8c','edgecolor':'none','boxstyle':'circle,pad=.12'})
 ax.set(xlim=(0,8),ylim=(0,8),xticks=np.arange(8)+.5,yticks=np.arange(8)+.5,xticklabels=list('abcdefgh'),yticklabels=range(1,9));ax.set_aspect('equal');ax.set_title(title,fontsize=10);ax.tick_params(length=0)
 if key=='UYo057a7':arrow(ax,(4.5,1.5),(6.5,1.5))
fig.tight_layout();save(fig,'fig09_chess')
# 10: ledgers and sequential stages.
fig,axes=plt.subplots(1,2,figsize=(9,3.8))
axes[0].bar([0,1],[5,2],label='Available',color=colors[0]);axes[0].bar([0,1],[0,3],bottom=[5,2],label='Transition ledger',color=colors[1]);axes[0].set_xticks([0,1],['Before','After']);axes[0].set_ylabel('Toy energy units');axes[0].legend()
axes[1].axis('off');axes[1].set(xlim=(0,5),ylim=(0,5))
for i,(title,body)in enumerate([('Propose','Describe a candidate transition'),('Evaluate','Permission, energy, preferences'),('Execute','Apply state and ledger changes'),('Observe','Retain outcome and provenance')]):
 box(axes[1],.2,3.8-i*1.1,4.5,.8,title,body)
 if i<3:arrow(axes[1],(2.45,3.8-i*1.1),(2.45,3.55-i*1.1))
fig.tight_layout();save(fig,'fig10_ledgers')
# 11: nonconvergence.
osc=read('oscillation.csv');fig,axes=plt.subplots(1,2,figsize=(9,3.5))
for d,color in [(1,colors[1]),(.2,colors[0])]:
 r=[x for x in osc if float(x['damping'])==d];x=[int(z['budget'])for z in r]
 axes[0].plot(x,[float(z['strength'])for z in r],label=f'damping={d}',color=color)
 axes[1].semilogy(x,[max(1e-16,float(z['delta']))for z in r],color=color)
axes[0].set(xlabel='Iteration budget',ylabel='Label-0 strength');axes[0].legend();axes[1].axhline(1e-8,color='gray',ls='--');axes[1].set(xlabel='Iteration budget',ylabel='Final maximum change');fig.tight_layout();save(fig,'fig11_oscillation')
# 12: relation namespaces and aliases.
fig,ax=plt.subplots(figsize=(9,4));ax.axis('off');ax.set(xlim=(0,10),ylim=(0,4.5))
box(ax,.2,2.9,2.3,1,'Name A','queen–rook mate');box(ax,.2,.9,2.3,1,'Name B','UYo057a7 finish')
box(ax,4,1.8,2.4,1.2,'One modeled identity','NodeId = k');box(ax,7.5,1.8,2.2,1.2,'External event','Historical game')
arrow(ax,(2.5,3.3),(4,2.6));arrow(ax,(2.5,1.3),(4,2.2));arrow(ax,(6.4,2.4),(7.5,2.4))
ax.text(6.9,2.8,'refers to',ha='center',fontsize=8);ax.text(5,.3,'Names, modeled identities, and external referents have different roles.',ha='center',fontsize=10)
save(fig,'fig12_identity')
# Data-driven manuscript tables and numbers.
(P/'data'/'statistics.json').write_text(json.dumps(stats,indent=2))
lines=[]
for name,m in zip(names,modes):
 s=stats['compatibility'][m];lines.append(f"{name} & {100*s['accuracy']['mean']:.2f} & {s['brier']['mean']:.4f} & {s['entropy']['mean']:.4f} & {s['iterations']['mean']:.2f} \\\\")
(P/'source'/'compatibility_rows.tex').write_text('\n'.join(lines)+'\n')
lines=[]
for name,m in zip(names[1:],modes[1:]):
 s=stats['paired'][m];lines.append(f"{name} & {100*s['accuracy_difference']:+.2f} & [{100*s['ci95'][0]:+.2f}, {100*s['ci95'][1]:+.2f}] \\\\")
(P/'source'/'paired_rows.tex').write_text('\n'.join(lines)+'\n')
lines=[]
for k,v in stats['forecasts'].items():lines.append(f"{k.title()} & {v['brier']:.4f} & [{v['brier_ci95'][0]:.4f}, {v['brier_ci95'][1]:.4f}] & {v['logloss']:.4f} \\\\")
(P/'source'/'forecast_rows.tex').write_text('\n'.join(lines)+'\n')
print(json.dumps(stats,indent=2))
