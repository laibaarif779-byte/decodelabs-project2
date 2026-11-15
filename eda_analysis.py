"""Project 2 - Exploratory Data Analysis. Usage: python eda_analysis.py Cleaned_Dataset.csv outdir"""
import sys, os, json, numpy as np, pandas as pd
from scipy import stats
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
SRC, OUT = sys.argv[1], sys.argv[2]; os.makedirs(f'{OUT}/charts', exist_ok=True)
d = pd.read_csv(SRC, parse_dates=['Date'])
d['Year']=d.Date.dt.year; d['Month']=d.Date.dt.month; d['YM']=d.Date.dt.to_period('M')
num=['Quantity','UnitPrice','ItemsInCart','TotalPrice']
INK,MUTED,GRID,ACC,WARN='#1f2933','#6b7785','#e3e7eb','#2563eb','#d9480f'
plt.rcParams.update({'font.family':'DejaVu Sans','axes.edgecolor':GRID,'axes.labelcolor':MUTED,'xtick.color':MUTED,'ytick.color':MUTED,
  'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.color':GRID,'grid.linewidth':.8,'axes.axisbelow':True})
R={}  # results

# ---- 1. descriptive stats
desc=d[num].agg(['count','mean','median','std','min','max']).T
desc['Q1']=d[num].quantile(.25); desc['Q3']=d[num].quantile(.75); desc['skew']=d[num].skew()
R['desc']=desc.round(2)
# ---- 2. outliers (IQR + Z)
out=[]
for c in num:
    q1,q3=d[c].quantile([.25,.75]); i=q3-q1; lo,hi=q1-1.5*i,q3+1.5*i
    out.append([c,round(lo,2),round(hi,2),int(((d[c]<lo)|(d[c]>hi)).sum()),int((np.abs(stats.zscore(d[c]))>3).sum())])
R['out']=pd.DataFrame(out,columns=['Column','IQR lower','IQR upper','IQR outliers','Z>3 outliers'])
q1,q3=d.TotalPrice.quantile([.25,.75]); hi=q3+1.5*(q3-q1)
O=d[d.TotalPrice>hi]; R['n_out']=len(O); R['out_thr']=hi; R['out_qty5']=bool((O.Quantity==5).all()); R['out_share']=O.TotalPrice.sum()/d.TotalPrice.sum()
R['top10']=d.TotalPrice.nlargest(int(len(d)*.1)).sum()/d.TotalPrice.sum()
# ---- 3. correlation
corr=d[num].corr(); R['corr']=corr.round(3)
# ---- 4. trend (monthly, normalised because 2025 has only Jan-Jun)
m=d.groupby('YM').TotalPrice.agg(['count','sum']).reset_index(); m['t']=range(len(m))
R['monthly']=m.assign(YM=m.YM.astype(str))
ya=d.groupby(['Year','Month']).TotalPrice.sum().groupby('Year').mean(); R['yr_month_rev']=ya.round(0)
R['yr_chg']=ya[2025]/ya[2023]-1
lr=stats.linregress(m.t,m['sum']); R['trend_p']=lr.pvalue; R['trend_slope']=lr.slope
mm=d.groupby(['Year','Month']).TotalPrice.sum().reset_index(); mm=mm[mm.Year<2025]
R['h1h2_p']=stats.mannwhitneyu(mm[mm.Month<=6].TotalPrice,mm[mm.Month>6].TotalPrice).pvalue
# ---- 5. status
bad=d.OrderStatus.isin(['Cancelled','Returned']); R['bad_rate']=bad.mean(); R['bad_value']=d[bad].TotalPrice.sum(); R['bad_value_share']=R['bad_value']/d.TotalPrice.sum()
R['bad_by_year']=d.groupby('Year').apply(lambda g:g.OrderStatus.isin(['Cancelled','Returned']).mean()).round(3)
st=d.OrderStatus.value_counts(); R['status']=st
R['pending_2023']=int(((d.OrderStatus=='Pending')&(d.Date<'2024-01-01')).sum()); R['pending_total']=int((d.OrderStatus=='Pending').sum())
R['chi_prod_status_p']=stats.chi2_contingency(pd.crosstab(d.Product,d.OrderStatus))[1]
# ---- 6. segments
seg={}
for c in ['Product','PaymentMethod','CouponCode','ReferralSource']:
    g=d.groupby(c).TotalPrice.agg(orders='count',revenue='sum',mean='mean',median='median').round(1).sort_values('revenue',ascending=False)
    g['p_kruskal']=round(stats.kruskal(*[x.TotalPrice for _,x in d.groupby(c)]).pvalue,3); seg[c]=g
R['seg']=seg
R['qty_mean']=d.groupby('Quantity').TotalPrice.mean().round(0)
R['rows']=len(d); R['rev']=d.TotalPrice.sum(); R['aov']=d.TotalPrice.mean(); R['med']=d.TotalPrice.median()
R['dates']=(str(d.Date.min().date()),str(d.Date.max().date()))

# ---- charts (static PNG: one insight each, accent on the point, grey elsewhere)
def save(f,n): f.savefig(f'{OUT}/charts/{n}.png',dpi=200,bbox_inches='tight'); plt.close(f)
# C1 monthly revenue
f,a=plt.subplots(figsize=(8,3.4)); x=np.arange(len(m))
a.plot(x,m['sum']/1e3,color=MUTED,lw=1.6,marker='o',ms=4,mfc='white')
a.plot(x,(lr.intercept+lr.slope*x)/1e3,color=ACC,lw=2.2)
a.set_xticks(x[::3]); a.set_xticklabels([str(p) for p in m.YM[::3]],rotation=0,fontsize=8); a.set_ylabel('Revenue per month ($K)')
a.annotate(f'Trend: {lr.slope/1e3:+.2f}K per month',xy=(x[-1],(lr.intercept+lr.slope*x[-1])/1e3),xytext=(-150,40),textcoords='offset points',color=ACC,fontsize=9,fontweight='bold')
save(f,'c1_trend')
# C2 distribution + boxplot
f,(a,b)=plt.subplots(2,1,figsize=(8,4.4),sharex=True,gridspec_kw={'height_ratios':[3,1]})
a.hist(d.TotalPrice,bins=36,color='#c5ccd3',edgecolor='white'); 
a.axvline(d.TotalPrice.mean(),color=WARN,lw=2); a.axvline(d.TotalPrice.median(),color=ACC,lw=2)
a.text(d.TotalPrice.mean()+40,a.get_ylim()[1]*.88,f'Mean ${d.TotalPrice.mean():,.0f}',color=WARN,fontsize=9,fontweight='bold')
a.text(d.TotalPrice.median()-40,a.get_ylim()[1]*.88,f'Median ${d.TotalPrice.median():,.0f}',color=ACC,fontsize=9,fontweight='bold',ha='right')
a.set_ylabel('Orders')
b.boxplot(d.TotalPrice,vert=False,widths=.6,patch_artist=True,boxprops=dict(facecolor='#c5ccd3',edgecolor=MUTED),medianprops=dict(color=ACC,lw=2),
  flierprops=dict(marker='o',mfc=WARN,mec=WARN,ms=5),whiskerprops=dict(color=MUTED),capprops=dict(color=MUTED)); b.set_yticks([]); b.set_xlabel('Order value ($)'); b.grid(axis='y',visible=False)
save(f,'c2_distribution')
# C3 correlation
f,a=plt.subplots(figsize=(5.2,4.2)); im=a.imshow(corr,cmap='Blues',vmin=0,vmax=1); a.grid(False)
a.set_xticks(range(4)); a.set_yticks(range(4)); a.set_xticklabels(num,rotation=25,ha='right',fontsize=8); a.set_yticklabels(num,fontsize=8)
for i in range(4):
    for j in range(4): a.text(j,i,f'{corr.iloc[i,j]:.2f}',ha='center',va='center',fontsize=9,color='white' if corr.iloc[i,j]>.55 else INK)
for s in a.spines.values(): s.set_visible(False)
save(f,'c3_corr')
# C4 status
order=['Cancelled','Returned','Pending','Shipped','Delivered']; sv=st.reindex(order)/len(d)*100
f,a=plt.subplots(figsize=(8,3)); cols=[WARN if s in('Cancelled','Returned') else '#c5ccd3' for s in order]
bars=a.barh(order[::-1],sv[::-1],color=cols[::-1],height=.62); a.grid(axis='y',visible=False); a.set_xlabel('Share of orders (%)')
for r,v in zip(bars,sv[::-1]): a.text(v+.4,r.get_y()+r.get_height()/2,f'{v:.1f}%',va='center',fontsize=9,color=INK)
a.set_xlim(0,max(sv)*1.15); save(f,'c4_status')
# C5 product revenue & AOV
pr=seg['Product'].sort_values('revenue'); f,a=plt.subplots(figsize=(8,3.2))
bars=a.barh(pr.index,pr.revenue/1e3,color='#c5ccd3',height=.62); a.grid(axis='y',visible=False); a.set_xlabel('Total order value ($K)')
for r,v in zip(bars,pr.revenue/1e3): a.text(v+2,r.get_y()+r.get_height()/2,f'${v:,.0f}K',va='center',fontsize=9,color=INK)
a.set_xlim(0,pr.revenue.max()/1e3*1.15); save(f,'c5_product')
# C6 bad rate by year
by=R['bad_by_year']*100; f,a=plt.subplots(figsize=(4.6,3)); bars=a.bar([str(y) if y<2025 else '2025\n(Jan-Jun)' for y in by.index],by.values,color=['#c5ccd3','#c5ccd3',WARN],width=.55)
a.grid(axis='x',visible=False); a.set_ylabel('Cancelled + returned (%)'); a.set_ylim(0,60)
for r,v in zip(bars,by.values): a.text(r.get_x()+r.get_width()/2,v+1,f'{v:.1f}%',ha='center',fontsize=9,color=INK)
save(f,'c6_badrate')

# ---- Excel
with pd.ExcelWriter(f'{OUT}/EDA_Statistics.xlsx') as w:
    R['desc'].to_excel(w,sheet_name='Descriptive_Stats'); R['out'].to_excel(w,sheet_name='Outliers',index=False)
    O[['OrderID','Date','Product','Quantity','UnitPrice','TotalPrice','OrderStatus']].to_excel(w,sheet_name='Outlier_Orders',index=False)
    R['corr'].to_excel(w,sheet_name='Correlation'); R['monthly'].to_excel(w,sheet_name='Monthly_Trend',index=False)
    for k,v in seg.items(): v.to_excel(w,sheet_name=f'By_{k}'[:31])
pd.to_pickle(R,f'{OUT}/results.pkl')
for k in ['rows','rev','aov','med','n_out','out_thr','out_qty5','out_share','top10','yr_chg','trend_p','trend_slope','h1h2_p','bad_rate','bad_value','bad_value_share','pending_2023','pending_total','chi_prod_status_p']: print(k,R[k])
print(R['yr_month_rev'].to_dict(),R['bad_by_year'].to_dict()); print(R['out']); print(R['corr'])
for k,v in seg.items(): print(k,v.p_kruskal.iloc[0])
