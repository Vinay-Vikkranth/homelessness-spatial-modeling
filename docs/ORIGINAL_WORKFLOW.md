# Homelessness Interpretation Stability Project

`Final.ipynb` is the main analysis of geographic associations in 141 CoCs, using official 2021 PIT homelessness counts and geo-enriched predictors.

## Structure

```text
Final.ipynb          Main notebook, explanations, and saved results
README.md            Guide and verification status
requirements.txt     Python dependencies
data/                Current source CSVs and HUD boundaries
  reference/         Earlier enriched dataset retained for provenance
outputs/             Generated datasets, results, and teaching images
  arcgis_export/     Spatial verification and coefficient exports
scripts/             Moran teaching-image regeneration script
Paper/               Manuscript and paper figures
```

## Run

Open `Final.ipynb` with the project root as its working directory and run top to bottom. Install the dependencies listed in `requirements.txt`. The 1,000-iteration Monte Carlo test can take several minutes or longer.

The workflow matches CoC codes, excludes Burglary and Rape Index before predictor selection, filters sparse predictors, applies VIF <= 7, and performs backward p-value elimination at 0.05. Phase 2 repeats selection for four additional PIT outcomes. Primary OLS and GWR use the same four selected predictors and 141 observations.

Spatial operations use regional WGS84 Azimuthal Equidistant centroids, centered at 39.5 degrees N, 77.5 degrees W. Residual Moran tests use 9,999 permutations with documented deterministic seeds. The separate GWR variability test uses 1,000 coordinate permutations, seed 5536, and reselects bandwidth for each iteration.

## Inputs and outputs

| Path | Purpose |
|---|---|
| `data/Final_Cleaned_Dataset_for_Homelessness_Modified.csv` | Current enriched input |
| `data/PIT_dataset - 2021.csv` | Source PIT counts |
| `data/hud_coc_boundaries/` | HUD geometry and shapefile companion files |
| `data/reference/Final_Cleaned_Dataset_for_Homelessness.csv` | Distinct earlier input, retained for provenance |
| `outputs/PIT_dataset_2021_cleaned.csv` | Generated cleaned PIT data |
| `outputs/analysis_merged_141cocs.csv` | Generated keyed analysis table |
| `outputs/diagnostics.csv` | Primary model metrics |
| `outputs/interpretation_stability_table.csv` | Stability and variability summary |
| `outputs/gwr_local_stability_long.csv` | Local coefficients and classifications |
| `outputs/spatial_variability_pvalues.csv` | Raw p-values, display text, exceedances, iterations, seed |
| `outputs/arcgis_export/` | Spatial verification CSV, shapefile, GeoPackage, veteran coefficients |
| `outputs/*.png` | Correlation plots and teaching illustrations |
| `scripts/draw_actual_moran_explainer.py` | Recreates the project teaching image; run from project root |

Shapefile `.shp`, `.shx`, `.dbf`, `.prj`, and `.cpg` files form one dataset; retain them together. Shapefile and GeoPackage exports serve different ArcGIS format needs. The teaching-image script uses 999 illustrative shuffles; authoritative residual tests use the notebook's 9,999 permutations.

## Verification and remaining work

See the original local verification report at outputs/project_verification.md (not distributed in this public copy) for the September 28 independent audit. Numeric reproduction passed, but that deeper review found strong NY-600 influence, heteroskedasticity/inference sensitivity, negative count predictions, and some local collinearity. The project is ready for analysis review, not yet for publication certification.

The October 12, 2026 notebook expansion adds an explained evidence trail, a glossary, worked real-CoC examples, and a paper-correction index. The complete analysis ran top to bottom, including all 1,000 spatial-variability iterations; the final added verification cell also ran. All 52 code cells have saved outputs with no notebook-cell errors. Checks cover official PIT alignment, count accounting, 141 spatial records, 564 local predictor records, stability percentages, actual simulation exceedances, and agreement with the recorded ArcGIS input hashes. Windows joblib emitted temporary-worker cleanup messages after the calculations completed; these did not change the saved results.

New evidence includes the variable-selection ledger, worked scaling/prediction/R² calculation, all five outcome-model performance rows, all-pairs projection comparison, named reversal CoCs, coefficient-deviation examples, actual Monte Carlo distributions, influence and fixed-predictor NY-600 sensitivity, HC3 uncertainty, negative fitted counts, local collinearity, and geometry-repair sensitivity. The baseline specification is preserved. The generated evidence files are `outputs/paper_model_performance.csv`, `outputs/paper_results_evidence.csv`, `outputs/spatial_variability_simulations.csv`, and `outputs/paper_figure5_stability.png`.

Current primary OLS: R2 = 0.918943733; adjusted R2 = 0.916559725; RMSE = 1634.793685. GWR bandwidth = 53. Predictors: Hispanic Pacific Islander population, civilian veteran population, Total Crime Index, and Tapestry Segment 12D population. Significant reversals: seven CoCs for Crime and three for Tapestry.

The original manuscript is `Paper/Homelessness Paper_Final-V2.docx`; the current annotated correction guide is `Paper/Homelessness Paper_Final-V2_Corrections_Below_Original_v3.docx`. The notebook's paper evidence index links the proposed corrections to their calculations. This expansion does not apply changes to the Word manuscript or certify bibliography accuracy. Existing ArcGIS exports match the input snapshots generated by this run; they were displayed and their recorded input hashes checked, rather than rebuilt during notebook execution.

The analysis measures exploratory, in-sample geographic associations. Fit scores are not held-out prediction accuracy. Conventional OLS p-values follow data-driven variable selection, and OLS residuals remain spatially clustered. Some predictors are from 2022/2024 while the outcome is from 2021. Record source provenance and boundary vintage when finalizing the paper. These qualifications concern interpretation rather than successful execution.

## Cleanup record

Moved inputs to `data/`, generated root tables to `outputs/`, ArcGIS exports to `outputs/arcgis_export/`, and the reusable image script to `scripts/`. Removed `morans_I_final_cleaned.csv` after verifying it was byte-for-byte identical to the earlier enriched dataset preserved in `data/reference/`. Removed the empty `outputs/.gitkeep`. Preserved distinct data, manuscript files, teaching images, boundary metadata, and Git history. Added the missing seaborn dependency.
