"""Synthetic regional OLS example. It does not reproduce the 141-CoC study."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]

def synthetic_regions(seed=42,n=141):
    rng=np.random.default_rng(seed)
    x=rng.normal(size=(n,4)); coords=rng.uniform(-1,1,size=(n,2))
    y=1200+220*x[:,0]+140*x[:,1]+(100+90*coords[:,0])*x[:,2]-75*x[:,3]+rng.normal(0,95,n)
    return pd.DataFrame({'region_id':[f'SYN-{i:03}' for i in range(n)],'x':coords[:,0],'y':coords[:,1],
        **{f'context_{i+1}':x[:,i] for i in range(4)},'synthetic_count':y.round().astype(int)})

def fit(frame):
    if frame.region_id.duplicated().any():raise ValueError('Region IDs must be unique')
    cols=[f'context_{i+1}' for i in range(4)]
    if not np.isfinite(frame[cols+['synthetic_count']].to_numpy()).all():raise ValueError('Nonfinite inputs')
    model=sm.OLS(frame.synthetic_count,sm.add_constant(frame[cols])).fit()
    return model

def residual_moran(coords,residuals,k=6,permutations=199,seed=42):
    from sklearn.neighbors import NearestNeighbors
    neighbors=NearestNeighbors(n_neighbors=k+1).fit(coords).kneighbors(coords,return_distance=False)[:,1:]
    z=np.asarray(residuals)-np.mean(residuals)
    def statistic(v):return float(np.sum(v*np.mean(v[neighbors],axis=1))/np.dot(v,v))
    value=statistic(z);rng=np.random.default_rng(seed)
    # Two-sided permutation statistic, explicitly a demo choice.
    draws=np.array([statistic(rng.permutation(z)) for _ in range(permutations)])
    p=(1+np.sum(np.abs(draws)>=abs(value)))/(permutations+1)
    return value,float(p)

def main():
    frame=synthetic_regions();sample=ROOT/'data/sample/regions.csv';sample.parent.mkdir(parents=True,exist_ok=True)
    frame.to_csv(sample,index=False); model=fit(frame)
    mi,p=residual_moran(frame[['x','y']],model.resid)
    out=ROOT/'outputs/demo';out.mkdir(parents=True,exist_ok=True)
    result={'data':'SYNTHETIC','regions':len(frame),'in_sample_r2':model.rsquared,'residual_moran_i':mi,'permutation_p_demo':p,'permutations':199,'forecast_accuracy':None}
    (out/'metrics.json').write_text(json.dumps(result,indent=2))
    fig,axs=plt.subplots(1,2,figsize=(11,4.2),layout='constrained')
    axs[0].scatter(frame.synthetic_count,model.fittedvalues,c='#137c8b',s=18)
    lim=[min(frame.synthetic_count),max(frame.synthetic_count)];axs[0].plot(lim,lim,color='#c75b40')
    axs[0].set(xlabel='Synthetic observed count',ylabel='OLS fitted count',title='In sample fit, not forecast accuracy')
    pts=axs[1].scatter(frame.x,frame.y,c=model.resid,cmap='coolwarm',s=35);fig.colorbar(pts,ax=axs[1],label='Residual')
    axs[1].set(title='Synthetic region coordinates',xlabel='Arbitrary x',ylabel='Arbitrary y')
    fig.suptitle('Runnable synthetic example | no real CoC data');fig.savefig(ROOT/'docs/assets/demo.png',dpi=160);plt.close(fig)
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
