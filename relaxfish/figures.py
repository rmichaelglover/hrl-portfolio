#!/usr/bin/env python3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np,json,chess
from pathlib import Path
from experiment import role_field,C,ROLES
R=Path(__file__).resolve().parent;D=json.loads((R/'data/results.json').read_text());P=D['positions'];F=R/'figures'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':150,'savefig.dpi':300,'axes.titleweight':'bold'})
COL={'static':'#D55E00','relaxfish':'#0072B2','stockfish_2k':'#009E73'}
def save(fig,name):
 fig.tight_layout();fig.savefig(F/(name+'.png'),bbox_inches='tight');fig.savefig(F/(name+'.pdf'),bbox_inches='tight');plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(10,4.5))
p=P[1];q=np.array(p['q']);names=[chess.square_name(s) for s in p['squares']]
im=axs[0].imshow(q,aspect='auto',cmap='viridis',vmin=0,vmax=1);axs[0].set_yticks(range(len(names)),names,fontsize=6);axs[0].set_xticks(range(7),ROLES,rotation=55,ha='right');axs[0].set_title('a | Executed role field: Sicilian');fig.colorbar(im,ax=axs[0],label='Role weight')
for p in P:
 vals=np.array(p['potential']);axs[1].plot(range(len(vals)),vals-vals[0],alpha=.6,color=COL['relaxfish'])
axs[1].set(xlabel='Relaxation iteration',ylabel='Compatibility gain',title='b | All 24 measured trajectories');save(fig,'role_field')
fig,axs=plt.subplots(1,2,figsize=(10,4))
models=list(COL);x=np.arange(3)
for j,m in enumerate(models):
 y=[sum(p['models'][m]['agreement'] for p in P if p['category']==cat)/8 for cat in ['opening','middlegame','endgame']]
 axs[0].bar(x+(j-1)*.24,y,.24,label=m,color=COL[m])
axs[0].set_xticks(x,['Opening','Legal-random middle','Synthetic endgame']);axs[0].set(ylim=(0,1),ylabel='20k-node reference agreement',title='a | Exact move agreement');axs[0].legend(fontsize=7)
for m in models:
 y=[p['models'][m]['reference_gap_cp'] for p in P];axs[1].plot(range(1,25),y,'o-',label=m,color=COL[m],markersize=3,alpha=.8)
axs[1].axhline(0,color='black',lw=.7);axs[1].set_yscale('symlog',linthresh=50);axs[1].set(xlabel='Fixed fixture index',ylabel='Signed reference gap (cp; mate = 10,000)',title='b | Post-move diagnostic');save(fig,'reference_comparison')
fig,axs=plt.subplots(1,2,figsize=(10,4))
for m in models:
 axs[0].plot(range(1,25),[max(1e-5,p['models'][m]['seconds']) for p in P],'o-',color=COL[m],label=m,markersize=3)
axs[0].set_yscale('log');axs[0].set(xlabel='Fixture index',ylabel='Elapsed seconds (single measurements)',title='a | Implementation cost');axs[0].legend(fontsize=7)
a=np.array([p['models']['static']['reference_gap_cp'] for p in P]);b=np.array([p['models']['relaxfish']['reference_gap_cp'] for p in P]);axs[1].scatter(a,b,c=[{'opening':'#0072B2','middlegame':'#D55E00','endgame':'#009E73'}[p['category']] for p in P]);lims=[min(a.min(),b.min())-50,max(a.max(),b.max())+50];axs[1].plot(lims,lims,'k--',lw=.7);axs[1].set(xlabel='Static reference gap (cp)',ylabel='Relaxfish reference gap (cp)',title='b | Paired ablation');axs[1].set_xscale('symlog',linthresh=50);axs[1].set_yscale('symlog',linthresh=50);save(fig,'ablation_cost')
# Analytic probability bound: zero observed Bernoulli failures, fixed n.
n=np.logspace(1,8,180);fig,axs=plt.subplots(1,2,figsize=(10,4))
for delta in [.05,.01,.001]:axs[0].loglog(n,-np.expm1(np.log(delta)/n),label=f'delta={delta}')
axs[0].set(xlabel='Independent trials n',ylabel='Exact upper failure-probability bound',title='a | Zero-failure design calculation');axs[0].legend()
N,DEL=np.meshgrid(np.logspace(1,7,90),np.logspace(-6,-1,60));bound=-np.expm1(np.log(DEL)/N);im=axs[1].pcolormesh(N,DEL,np.log10(bound),cmap='viridis',shading='auto');axs[1].set_xscale('log');axs[1].set_yscale('log');axs[1].set(xlabel='Independent trials n',ylabel='Failure probability delta',title='b | Analytic confidence landscape');fig.colorbar(im,ax=axs[1],label='log10 upper bound');save(fig,'statistical_design')
fig=plt.figure(figsize=(9,5));ax=fig.add_subplot(111,projection='3d');ax.plot_surface(np.log10(N),np.log10(DEL),np.log10(bound),cmap='viridis',linewidth=0,alpha=.95);ax.set(xlabel='log10 n',ylabel='log10 delta',zlabel='log10 failure bound',title='Analytic 3D design surface: fixed-sample, zero failures');save(fig,'confidence_3d')
# Executed model landscape, preserving other coordinates and the row simplex.
board=chess.Board(P[1]['fen']);field=role_field(board);q=field['q'];aff=field['aff'];edges=field['edges'];triples=field['triples'];idx=field['squares'].index(chess.E4) if chess.E4 in field['squares'] else 0
XX,YY=np.meshgrid(np.linspace(0,1,55),np.linspace(0,1,55));ZZ=np.full(XX.shape,np.nan)
for k in np.ndindex(XX.shape):
 a,b=XX[k],YY[k]
 if a+b>1:continue
 qq=q.copy();rest=qq[idx,2:]/qq[idx,2:].sum();qq[idx]=np.r_[a,b,(1-a-b)*rest]
 ZZ[k]=np.sum(aff*qq)+.5*.18/len(q)*np.sum((edges@qq@C)*qq)+.12/max(1,len(triples))*sum(qq[i,0]*qq[j,0]*qq[l,0] for i,j,l in triples)
fig=plt.figure(figsize=(9,5));ax=fig.add_subplot(111,projection='3d');ax.plot_surface(XX,YY,ZZ,cmap='cividis',linewidth=0);ax.set(xlabel='Attacker weight',ylabel='Defender weight',zlabel='Compatibility potential',title=f'Executed potential slice: {chess.square_name(field["squares"][idx])}, Sicilian');save(fig,'potential_3d')
fig,ax=plt.subplots(figsize=(9,4));t=np.arange(13)
for p in P:ax.plot(t,p['entropy'],alpha=.5,color=COL['relaxfish'])
ax.set(xlabel='Relaxation iteration',ylabel='Mean role entropy (nats)',title='Measured concentration of the role field');save(fig,'entropy')
fig,ax=plt.subplots(figsize=(10,4));ax.axis('off')
labels=['Legal state\nand draw history','Role affinities\nand coalitions','Relaxation\n+ evaluation','Search /\nresponse oracles','Measured outcomes\n+ certified bounds'];xs=np.linspace(.07,.93,5)
for x,label in zip(xs,labels):ax.text(x,.6,label,ha='center',va='center',bbox={'boxstyle':'round,pad=.8','facecolor':'#E5F1F5','edgecolor':'#0072B2'},transform=ax.transAxes,fontsize=9)
for a,b in zip(xs[:-1],xs[1:]):ax.annotate('',xy=(b-.07,.6),xytext=(a+.07,.6),xycoords='axes fraction',arrowprops={'arrowstyle':'->','color':'#444'})
ax.text(.5,.15,'Architecture schematic. The pilot executes the first three stages with one-ply choice.\nThe separate habitat solver certifies exact WDL bounds; adversarial league testing is a specified next stage.',ha='center',transform=ax.transAxes,fontsize=10);save(fig,'architecture')
summary={'models':{m:{'agreement':sum(p['models'][m]['agreement'] for p in P),'median_gap_cp':float(np.median([p['models'][m]['reference_gap_cp'] for p in P])),'mean_gap_cp':float(np.mean([p['models'][m]['reference_gap_cp'] for p in P])),'median_seconds':float(np.median([p['models'][m]['seconds'] for p in P]))} for m in models},'changed_moves':sum(p['models']['static']['move']!=p['models']['relaxfish']['move'] for p in P),'minimum_potential_step':min(float(np.min(np.diff(p['potential']))) for p in P),'matches':D['matches']}
(R/'data/summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k!='matches'},indent=2))
