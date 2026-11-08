"""Build the Total Crime Index alternative to paper Figure 3 with ArcGIS Pro and the verified CoC-keyed data.

Run with ArcGIS Pro's licensed Python. The original APRX is read-only input.
The output APRX, geodatabase and 300-dpi figures are retained for manual editing.
"""
from pathlib import Path
import csv
import json
import hashlib
import arcpy

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'Paper' / 'ArcGIS_Figures' / 'Crime_Index'
SOURCE = Path.home() / 'Documents/ArcGIS/Projects/MyProject1/MyProject1.aprx'
OUT.mkdir(parents=True, exist_ok=True)
arcpy.env.overwriteOutput = True
gdb = OUT / 'Paper_Maps.gdb'
if not gdb.exists():
    arcpy.management.CreateFileGDB(str(OUT), gdb.name)
records = list(csv.DictReader((ROOT/'outputs/analysis_merged_141cocs.csv').open(encoding='utf-8-sig')))
data = {r['COCNUM']: r for r in records}
coords = {r['COCNUM']: r for r in csv.DictReader((ROOT/'outputs/arcgis_export/coc_spatial_verification.csv').open(encoding='utf-8-sig'))}
assert len(records) == len(data) == len(coords) == 141
assert data.keys() == coords.keys()
for key, r in data.items():
    assert float(r['Overall Homeless, 2021_pit']) == float(coords[key]['homeless'])

polygons = str(gdb/'Study_CoCs')
arcpy.management.CopyFeatures(str(ROOT/'outputs/arcgis_export/coc_boundaries_verification.shp'), polygons)
arcpy.management.AddFields(polygons, [['PIT2021','LONG','Overall Homeless (2021)'], ['CRIME2024','DOUBLE','Total Crime Index (2024)'], ['VET2022','LONG','Civilian Veteran Population (2022 ACS)']])
seen = set()
with arcpy.da.UpdateCursor(polygons, ['COCNUM','PIT2021','CRIME2024','VET2022']) as cursor:
    for row in cursor:
        key = row[0]; r = data[key]; seen.add(key)
        row[1:] = [int(float(r['Overall Homeless, 2021_pit'])), float(r['2024 Total Crime Index']), int(float(r['2022 Civilian Pop 18+: Veteran (ACS 5-Yr)']))]
        cursor.updateRow(row)
assert seen == data.keys()
with arcpy.da.SearchCursor(polygons, ['COCNUM', 'CRIME2024', 'PIT2021']) as check:
    for key, crime, pit in check:
        assert crime == float(data[key]['2024 Total Crime Index'])
        assert pit == int(float(data[key]['Overall Homeless, 2021_pit']))
crime_values = [float(r['2024 Total Crime Index']) for r in records]
assert min(crime_values) == 29 and max(crime_values) == 239
assert all(v.is_integer() for v in crime_values)
print('VERIFIED: 141 keyed crime values, integer range 29–239', flush=True)

points = str(gdb/'Homelessness_Centroids')
arcpy.management.CreateFeatureclass(str(gdb), 'Homelessness_Centroids', 'POINT', spatial_reference=arcpy.SpatialReference(4326))
arcpy.management.AddFields(points, [['COCNUM','TEXT'], ['PIT2021','LONG','Overall Homeless (2021)']])
with arcpy.da.InsertCursor(points, ['SHAPE@XY','COCNUM','PIT2021']) as cursor:
    for key, r in coords.items():
        cursor.insertRow([(float(r['centroid_lon']),float(r['centroid_lat'])), key, int(float(r['homeless']))])

context = str(gdb/'Other_CoCs')
where = 'COCNUM NOT IN (' + ','.join("'"+k+"'" for k in sorted(data)) + ')'
arcpy.conversion.ExportFeatures(str(ROOT/'data/hud_coc_boundaries/Continuum_of_Care_(CoC)_Grantee_Areas.shp'),context,where)

project = arcpy.mp.ArcGISProject(str(SOURCE))
project.defaultGeodatabase = str(gdb)
original_map = project.listMaps('Map')[0]
original_layout = project.listLayouts('Layout1')[0]
point_template = original_map.listLayers('Overall Homeless')[0].symbology
polygon_template = original_map.listLayers('fig6_gwr_vet')[0].symbology
colors = [[255,255,204,100],[254,217,118,100],[253,141,60,100],[227,26,28,100],[128,0,38,100]]
configs = [
    (3,'Total crime index and homelessness','CRIME2024','Total Crime Index (2024)',None,29)
]
audit = {'arcgis_pro': arcpy.GetInstallInfo()['Version'], 'original_project': str(SOURCE), 'study_cocs':141,
         'point_locations':'Regional AEQD polygon centroids transformed to WGS84, from the current notebook export',
         'map_projection':'WGS84 geographic, matching the original ArcGIS presentation; analysis projection unchanged',
         'classification':'Crime index: five ArcGIS Natural Breaks (Jenks) classes; yellow symbols use five count ranges, not continuously proportional areas',
         'homelessness_breaks':[425,1016,2336,5111,68358], 'figures':[], 'crime_source_field':'2024 Total Crime Index', 'crime_min':min(crime_values), 'crime_max':max(crime_values)}
audit['input_sha256'] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'outputs/analysis_merged_141cocs.csv', ROOT/'outputs/arcgis_export/coc_spatial_verification.csv']}
for number,title,field,layer_name,bounds,minimum in configs:
    m = project.copyItem(original_map, f'Figure {number} {title}')
    for layer in list(m.listLayers()):
        if layer.name not in ['Light Gray Reference','Light Gray Base']:
            m.removeLayer(layer)
    bg = m.addDataFromPath(context); bg.name='Other CoCs (outside study)'
    sym=bg.symbology; sym.renderer.symbol.color={'RGB':[218,220,221,100]}; sym.renderer.symbol.outlineColor={'RGB':[185,188,190,100]}; sym.renderer.symbol.outlineWidth=0.25; bg.symbology=sym
    poly=m.addDataFromPath(polygons); poly.name=layer_name
    sym=poly.symbology; sym.updateRenderer('GraduatedColorsRenderer'); sym.renderer.classificationField=field; sym.renderer.breakCount=5
    # Group the actual crime values with ArcGIS Natural Breaks; retain the veteran map palette.
    sym.renderer.classificationMethod='NaturalBreaks'
    poly.symbology=sym
    sym=poly.symbology
    bounds=[int(b.upperBound) for b in sym.renderer.classBreaks]
    print('Crime Natural Breaks:', bounds, flush=True)
    for i,b in enumerate(sym.renderer.classBreaks):
        b.upperBound=bounds[i]; b.label=f'{minimum if i==0 else bounds[i-1]+1:,} - {bounds[i]:,}'
        b.symbol.color={'RGB':colors[i]}; b.symbol.outlineColor={'RGB':[95,95,95,100]}; b.symbol.outlineWidth=0.35
    poly.symbology=sym
    sym=poly.symbology
    for i,b in enumerate(sym.renderer.classBreaks):
        b.label=f'{minimum if i==0 else bounds[i-1]+1:,} - {bounds[i]:,}'
    poly.symbology=sym
    pt=m.addDataFromPath(points); pt.name='Overall Homeless (2021)'
    pt.symbology=point_template
    sym=pt.symbology; sym.renderer.classificationField='PIT2021'; sym.renderer.breakCount=5
    pb=[425,1016,2336,5111,68358]
    for i,b in enumerate(sym.renderer.classBreaks):
        b.upperBound=pb[i]; b.label=f'{18 if i==0 else pb[i-1]+1:,} - {pb[i]:,}'
        b.symbol.color={'RGB':[245,245,0,100]}; b.symbol.outlineColor={'RGB':[85,85,70,100]}; b.symbol.outlineWidth=0.4; b.symbol.size=[4,7.5,11,14.5,18][i]
    pt.symbology=sym
    sym=pt.symbology
    for i,b in enumerate(sym.renderer.classBreaks):
        b.label=f'{18 if i==0 else pb[i-1]+1:,} - {pb[i]:,}'
    pt.symbology=sym
    # Disable ArcGIS automatic numeric relabeling, which otherwise restores
    # six decimal places for the DOUBLE index field on export.
    for layer,limits,lo in [(poly,bounds,minimum),(pt,pb,18)]:
        definition=layer.getDefinition('V3')
        definition.renderer.alwaysUpdateClassLabels=False
        for i,b in enumerate(definition.renderer.breaks):
            b.label=f'{lo if i==0 else limits[i-1]+1:,} - {limits[i]:,}'
        layer.setDefinition(definition)
    ref=m.listLayers('Light Gray Reference')[0]
    m.moveLayer(pt,ref,'BEFORE')
    layout=project.copyItem(original_layout, f'Figure {number}')
    frame=layout.listElements('MAPFRAME_ELEMENT')[0]; frame.map=m
    frame.camera.setExtent(arcpy.Extent(-88.1448871216,29.1990280872,-64.3009045352,47.6239237222))
    legend=layout.listElements('LEGEND_ELEMENT')[0]
    legend.syncNewLayer=False; legend.syncLayerVisibility=True; legend.syncLayerOrder=False
    for item in list(legend.items): legend.removeItem(item)
    legend.addItem(pt,'BOTTOM'); legend.addItem(poly,'BOTTOM'); legend.addItem(bg,'BOTTOM')
    legend.setAnchor('TOP_LEFT_CORNER'); legend.elementPositionX=7.2; legend.elementPositionY=4.65
    legend.elementWidth=3.55; legend.elementHeight=4.15; legend.fittingStrategy='AdjustFontSize'; legend.columnCount=1
    cim=legend.getDefinition('V3'); cim.titleGap=7; cim.itemGap=5; cim.classGap=2; cim.layerNameGap=3
    cim.titleSymbol.symbol.height=13
    for item in cim.items:
        item.showHeading=False; item.showLayerName=True; item.showGroupLayerName=False
        item.layerNameSymbol.symbol.height=10
        item.labelSymbol.symbol.height=9
        item.patchWidth=18; item.patchHeight=12
    cim.items[-1].showLayerName=False
    legend.setDefinition(cim)
    print('EXPORT',number,'legend_overflow',legend.isOverflowing,flush=True)
    layout.exportToPNG(str(OUT/f'Figure_{number}_ArcGIS.png'),300,'24-BIT_TRUE_COLOR',False,True,False)
    audit['figures'].append({'figure':number,'field':field,'breaks':bounds,'legend_overflow':legend.isOverflowing})
    print('EXPORTED',number,flush=True)

for layout in [original_layout]+project.listLayouts('Layout'):
    project.deleteItem(layout)
project.deleteItem(original_map)
project.saveACopy(str(OUT/'Homelessness_Paper_Maps.aprx'))
(OUT/'map_verification.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
print('DONE',OUT,flush=True)
