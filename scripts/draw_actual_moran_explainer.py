from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from matplotlib import cm
from libpysal.weights import KNN
from esda.moran import Moran
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression

cols=['2024 Hispanic Pacific Islander Pop','2022 Civilian Pop 18+: Veteran (ACS 5-Yr)','2024 Total Crime Index','2024 Pop 18+ in Tapestry Seg 12D']
# Run from the project root; this reproduces the 999-shuffle teaching image.
data=pd.read_csv('outputs/analysis_merged_141cocs.csv')
y=data['Overall Homeless, 2021_pit'].to_numpy()
x=MinMaxScaler().fit_transform(data[cols])
pred=LinearRegression().fit(x,y).predict(x)
fit=pd.DataFrame({'COCNUM':data.COCNUM,'actual':y,'predicted':pred,'residual':y-pred})
crs='+proj=aeqd +lat_0=39.5 +lon_0=-77.5 +datum=WGS84 +units=m +no_defs +type=crs'
hud=gpd.read_file(next(Path('data/hud_coc_boundaries').glob('*.shp')))
hud['COCNUM']=hud.COCNUM.astype(str).str.strip().str.upper()
hud=hud[~hud.COCNUM.str.startswith(('AK-','HI-'),na=False)].drop_duplicates('COCNUM')
g=hud[['COCNUM','geometry']].merge(fit,on='COCNUM',how='inner').to_crs(crs)
assert len(g)==141
w=KNN.from_dataframe(g,k=5); w.transform='r'
np.random.seed(5536)
mi=Moran(g.residual.to_numpy(),w,permutations=999)
shuffle=np.random.default_rng(5536).permutation(g.residual.to_numpy())
g['shuffled_residual']=shuffle
print('n',len(g),'I',mi.I,'p_sim',mi.p_sim,'sim greater',int((mi.sim>=mi.I).sum()))
print('DC',fit.loc[fit.COCNUM.eq('DC-500')].to_dict('records'))

fig=plt.figure(figsize=(14,9.2),facecolor='white')
gs=fig.add_gridspec(2,2,left=.055,right=.95,top=.87,bottom=.10,hspace=.25,wspace=.16)
fig.suptitle("Moran's I using your 141 CoCs and the current OLS model",fontsize=18,fontweight='bold',y=.965)
fig.text(.5,.916,'The projection is the approved regional Azimuthal Equidistant system; this illustration sets seed 5536 for 999 comparison shuffles.',ha='center',fontsize=10.5,color='#555')

ax=fig.add_subplot(gs[0,0]);ax.axis('off')
ax.set_title('1  What is one model error?',loc='left',fontsize=13,fontweight='bold',pad=8)
ax.text(.03,.78,'District of Columbia CoC (DC-500)',transform=ax.transAxes,fontsize=13,fontweight='bold')
ax.text(.05,.62,'Actual homeless count',transform=ax.transAxes,fontsize=12)
ax.text(.91,.62,'5,111',ha='right',transform=ax.transAxes,fontsize=14,fontweight='bold')
ax.text(.05,.51,'Model prediction',transform=ax.transAxes,fontsize=12)
ax.text(.91,.51,'1,566',ha='right',transform=ax.transAxes,fontsize=14,fontweight='bold')
ax.plot([.04,.93],[.46,.46],transform=ax.transAxes,color='#777',lw=1)
ax.text(.05,.34,'Error = actual − prediction',transform=ax.transAxes,fontsize=12)
ax.text(.91,.34,'+3,545',ha='right',transform=ax.transAxes,fontsize=14,fontweight='bold',color='#b34937')
ax.text(.05,.14,'Positive error: the model predicted too few.\nNegative error: the model predicted too many.',transform=ax.transAxes,fontsize=11,color='#444')

norm=TwoSlopeNorm(vmin=-5000,vcenter=0,vmax=5000)
cmap=cm.get_cmap('coolwarm')
for cell_index,field,title in [(1,'residual','2  Actual errors in their CoCs'),(2,'shuffled_residual','3  Same errors, randomly moved')]:
    ax=fig.add_subplot(gs[cell_index//2,cell_index%2])
    g.plot(ax=ax,column=field,cmap=cmap,norm=norm,edgecolor='#777',linewidth=.2)
    ax.set_title(title,loc='left',fontsize=13,fontweight='bold',pad=8)
    ax.axis('off')
    if cell_index==1:
        dc=g.loc[g.COCNUM.eq('DC-500')].geometry.centroid.iloc[0]
        ax.plot(dc.x,dc.y,'ko',markersize=5)
        ax.annotate('DC-500',xy=(dc.x,dc.y),xytext=(15,-18),textcoords='offset points',fontsize=9,arrowprops={'arrowstyle':'->','lw':1})
    else:
        ax.text(.02,.02,'Each CoC keeps its location; only the errors swap places.',transform=ax.transAxes,fontsize=10,bbox={'facecolor':'white','edgecolor':'none','alpha':.9})

ax=fig.add_subplot(gs[1,1]);ax.hist(mi.sim,bins=30,color='#a9bbc5',edgecolor='white')
ax.axvline(mi.I,color='#bf4e39',lw=3)
ax.text(.66,.83,f'Actual I = {mi.I:.3f}',transform=ax.transAxes,color='#a33a2b',fontsize=11,fontweight='bold')
ax.set_title('4  How unusual is the actual pattern?',loc='left',fontsize=13,fontweight='bold',pad=8)
ax.set_xlabel("Moran's I from each shuffle",fontsize=11);ax.set_ylabel('Number of shuffles',fontsize=11)
ax.text(.02,.97,f'999 shuffles with seed 5536\nSimulation p-value = {mi.p_sim:.3f}',transform=ax.transAxes,va='top',fontsize=11,bbox={'facecolor':'white','edgecolor':'#ccd5d9','alpha':.96})

fig.text(.055,.025,'Blue = predicted too many; red = predicted too few. Map colors are capped at ±5,000 for readability; Moran’s I uses the full, uncapped errors.',fontsize=9,color='#555')
out=Path('outputs/morans_real_project_explained.png');fig.savefig(out,dpi=180,bbox_inches='tight',facecolor='white')
