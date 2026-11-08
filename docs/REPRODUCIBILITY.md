# Research reproduction

## Portable public example

Install requirements.txt and run scripts/demo.py. It has no ArcGIS dependency. The generated input is fictitious and the output is not the historical study.

## Authorized local research workspace

The Desktop copy includes ignored data/private inputs. Run:

```bash
python scripts/prepare_research.py
python -m pip install -r requirements-research.txt
python -m jupyter notebook outputs/research_workspace/Final.ipynb
```

Open the notebook with outputs/research_workspace as the working directory. This avoids editing the published notebook or original source. The preparation script checks required inputs, copies local research files and copies the notebook. It does not invent or download missing data. A GitHub-only clone reports the missing inputs clearly.

Required relative paths include data/Final_Cleaned_Dataset_for_Homelessness_Modified.csv, data/PIT_dataset - 2021.csv and data/hud_coc_boundaries with all shapefile companions. The archived map-verification cell depends on original export bytes and saved notebook state. It is retained for historical context but disabled in the portable research copy, since cleared outputs cannot prove a completed prior execution. Re-execute the numerical cells and inspect the newly saved notebook directly.

The full 1,000-iteration coordinate permutation exercise can be expensive. ArcPy map exports are separate: use ArcGIS Pro Python, set the APRX template path in the copied script, and supply authorized spatial inputs. They are not part of GitHub CI. Study inputs and regenerated outputs stay ignored.
