import sys, unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from demo import synthetic_regions,fit,residual_moran
class SpatialDemoTests(unittest.TestCase):
    def test_key_integrity(self):
        f=synthetic_regions();f.loc[1,'region_id']=f.loc[0,'region_id']
        with self.assertRaises(ValueError):fit(f)
    def test_missing_predictor_rejected(self):
        f=synthetic_regions();f.loc[0,'context_1']=np.nan
        with self.assertRaises(ValueError):fit(f)
    def test_ols_matches_lstsq(self):
        f=synthetic_regions();m=fit(f);X=np.column_stack([np.ones(len(f)),f[[f'context_{i+1}' for i in range(4)]]])
        np.testing.assert_allclose(m.params,np.linalg.lstsq(X,f.synthetic_count,rcond=None)[0],rtol=1e-10)
    def test_permutation_reproducible(self):
        f=synthetic_regions();m=fit(f)
        a=residual_moran(f[['x','y']],m.resid);b=residual_moran(f[['x','y']],m.resid)
        self.assertEqual(a,b);self.assertGreaterEqual(a[1],1/200)
if __name__=='__main__':unittest.main()
