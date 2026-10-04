"""Measured WDI summaries and explicitly uncalibrated economic simulations."""
from pathlib import Path
import json,hashlib
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
B=Path(__file__).resolve().parent;F=B/'figures';F.mkdir(exist_ok=True)
raw={id:json.loads((B/'data'/f'{id}.json').read_text()) for id in ['NY.GDP.PCAP.KD','SI.POV.GINI']}
records=[]
for id,value in raw.items():
 assert value[0]['pages']==1
 for row in value[1]:records.append({'indicator':id,'country':row['countryiso3code'],'name':row['country']['value'],'year':int(row['date']),'value':row['value']})
df=pd.DataFrame(records);df.to_csv(B/'data/observations.csv',index=False)
q=np.array([.5,.4,.1]);start=np.array([1.,4.,20.]);alpha=.35;delta=.05
policies={'unequal_accumulation':(0.,np.array([.1,.2,.3]),.01),'balanced_rebate':(.3,np.array([.1,.2,.3]),.01),'equal_saving_access':(.3,np.array([.2,.2,.2]),.01),'productivity_scenario':(.3,np.array([.2,.2,.2]),.015)}
def gini(v):return float(np.sum(q[:,None]*q[None,:]*np.abs(v[:,None]-v[None,:]))/(2*q@v))
trajectories={};summary={}
for name,(tax,saving,growth) in policies.items():
 wealth=start.copy();rows=[]
 for t in range(61):
  K=float(q@wealth);A=np.exp(growth*t);Y=A*K**alpha;wage=(1-alpha)*Y;rent=alpha*Y/K;rebate=tax*alpha*Y
  disposable=wage+(1-tax)*rent*wealth+rebate;consumption=(1-saving)*disposable
  assert np.isclose(q@disposable,Y) and (disposable>0).all()
  rows.append([t,K,Y,gini(wealth),gini(disposable),float(q@consumption),*wealth,*disposable])
  new=(1-delta)*wealth+saving*disposable
  assert np.isclose(q@new,(1-delta)*K+q@(saving*disposable))
  wealth=new
 arr=np.array(rows);trajectories[name]=arr
 columns=['period','capital','output','wealth_gini','disposable_income_gini','mean_consumption','wealth_group1','wealth_group2','wealth_group3','income_group1','income_group2','income_group3']
 pd.DataFrame(arr,columns=columns).to_csv(B/f'data/{name}.csv',index=False)
 summary[name]={'capital_final':float(arr[-1,1]),'output_final':float(arr[-1,2]),'wealth_gini_final':float(arr[-1,3]),'disposable_income_gini_final':float(arr[-1,4]),'mean_consumption_final':float(arr[-1,5]),'capital_tax':tax,'saving_rates':saving.tolist(),'exogenous_productivity_growth':growth,'lowest_group_income_final':float(arr[-1,9])}
plt.rcParams.update({'font.size':9,'axes.titlesize':11})
def save(fig,name):
 fig.savefig(F/f'{name}.pdf',bbox_inches='tight');fig.savefig(F/f'{name}.png',dpi=180,bbox_inches='tight');plt.close(fig)
fig,ax=plt.subplots(figsize=(10,4.5),layout='constrained');country_summary=[]
for code in ['USA','DEU','CHN','IND','BRA','ZAF']:
 g=df[(df.country==code)&(df.indicator=='NY.GDP.PCAP.KD')].sort_values('year');h=df[(df.country==code)&(df.indicator=='SI.POV.GINI')&df.value.notna()].sort_values('year');ratio=float(g.iloc[-1].value/g.iloc[0].value)
 country_summary.append({'country':code,'name':g.iloc[0]['name'],'gdp_2010':float(g.iloc[0].value),'gdp_2024':float(g.iloc[-1].value),'gdp_growth_2010_2024_pct':(ratio-1)*100,'annualized_growth_pct':(ratio**(1/14)-1)*100,'gini_observations':len(h),'latest_gini_year':int(h.iloc[-1].year) if len(h) else None,'latest_gini':float(h.iloc[-1].value) if len(h) else None})
 ax.plot(g.year,100*g.value/g.iloc[0].value,label=code)
 figc,axs=plt.subplots(1,2,figsize=(9,3.5),layout='constrained');axs[0].plot(g.year,g.value,'o-',color='#0072b2');axs[0].set(xlabel='Year',ylabel='Constant 2015 US$ per person',title=code+' GDP per capita')
 axs[1].plot(h.year,h.value,'o',color='#d55e00');axs[1].set(xlabel='Observed survey year',ylabel='Reported Gini index',title=code+' reported inequality',ylim=(0,100));save(figc,'country-'+code)
ax.set(xlabel='Year',ylabel='GDP per capita index, 2010 = 100',title='Measured national-accounts trajectories; within-country change');ax.legend();ax.grid(alpha=.2);save(fig,'growth-index')
fig,axs=plt.subplots(2,2,figsize=(10,7),layout='constrained')
for name,a in trajectories.items():
 for ax,k in zip(axs.ravel(),[2,3,4,9]):ax.plot(a[:,0],a[:,k],label=name.replace('_',' '))
for ax,title in zip(axs.ravel(),['Output','Wealth Gini (0-1)','Disposable-income Gini (0-1)','Lowest-group disposable income']):ax.set(xlabel='Synthetic period',title=title);ax.legend(fontsize=6);ax.grid(alpha=.2)
save(fig,'policy-trajectories')
fig=plt.figure(figsize=(9,5));ax=fig.add_subplot(111,projection='3d');K,L=np.meshgrid(np.linspace(.2,12,60),np.linspace(.2,4,60));Y=K**alpha*L**(1-alpha);ax.plot_surface(K,L,Y,cmap='viridis',linewidth=0);ax.set(xlabel='Assumed capital',ylabel='Assumed labor',zlabel='Output',title='Analytic Cobb-Douglas surface, A = 1, alpha = 0.35');save(fig,'production-surface')
fig,ax=plt.subplots(figsize=(9,4),layout='constrained');taxes=np.linspace(0,1,101);ginis=[]
for tax in taxes:
 capital=q@start;output=capital**alpha;income=(1-alpha)*output+(1-tax)*alpha*output*start/capital+tax*alpha*output;ginis.append(gini(income))
ax.plot(taxes,ginis,color='#009e73');ax.set(xlabel='Assumed capital-income tax and equal rebate',ylabel='Disposable-income Gini (0-1)',title='Static redistribution at fixed gross output');ax.grid(alpha=.2);save(fig,'static-redistribution')
# Static dispersion theorem: y_i(tau)=(1-tau)y_i(0)+tau*mean(y(0)).
g0=ginis[0];assert np.allclose(ginis,(1-taxes)*g0)
# Small closed-economy accounting checks, not a policy-impact estimate.
assert abs(gini(np.ones(3)))<1e-12 and np.isclose(gini(start*2),gini(start))
result={'status':'measured WDI descriptions plus synthetic scenarios; no causal policy estimate','retrieved_date':'2026-10-04','api_last_updated':raw['NY.GDP.PCAP.KD'][0]['lastupdated'],'source_nonnull_observations':int(df.value.notna().sum()),'missing_observations':int(df.value.isna().sum()),'countries':country_summary,'synthetic_parameters':{'population_shares':q.tolist(),'initial_wealth':start.tolist(),'capital_share':alpha,'depreciation':delta,'periods':60},'synthetic_policy_results':summary,'checks_passed':True,'sources':{id:{'url':f'https://api.worldbank.org/v2/country/USA%3BDEU%3BCHN%3BIND%3BBRA%3BZAF/indicator/{id}?format=json&date=2010:2024&per_page=1000','sha256':hashlib.sha256((B/'data'/f'{id}.json').read_bytes()).hexdigest()} for id in raw},'scope_notes':['GDP constant-dollar levels are not PPP welfare comparisons.','Gini observations may measure income or consumption and have differing survey definitions; no missing values interpolated.','Synthetic policy responses are consequences of assumptions; coefficients are not fitted to WDI.','Wealth inequality in the toy model differs from WDI income/consumption inequality.']}
(B/'results.json').write_text(json.dumps(result,indent=2));print(json.dumps({'observations':result['source_nonnull_observations'],'countries':country_summary,'checks_passed':True},indent=2))
