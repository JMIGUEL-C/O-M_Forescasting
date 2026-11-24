"""Regenera el objeto window.DATA de sustentacion.html a partir de figuras/ (resultados.json, los CSV y sust_probabilidades.json).
Conserva las claves que no dependen del modelo final (series, mapa, lags, km, ...) y reemplaza las que sí dependen de él.
Antes: python scripts/volcar_probabilidades.py. Después: python scripts/datos_sustentacion.py."""
import json, os, pickle
import numpy as np, pandas as pd
from sklearn.metrics import cohen_kappa_score, f1_score

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(RAIZ, 'figuras'); HTML = os.path.join(RAIZ, 'sustentacion.html')
r = json.load(open(os.path.join(FIG, 'resultados.json'), encoding='utf-8'))
ex = json.load(open(os.path.join(FIG, 'sust_probabilidades.json'), encoding='utf-8'))
leer = lambda n, **kw: pd.read_csv(os.path.join(FIG, n), encoding='utf-8-sig', **kw)
recs = lambda df: json.loads(df.to_json(orient='records', force_ascii=False))

lineas = open(HTML, encoding='utf-8').read().split('\n')
i_d = next(i for i, l in enumerate(lineas) if l.startswith('<script>window.DATA='))
js = lineas[i_d][len('<script>window.DATA='):]; fin = js.rfind('};</script>')
D = json.loads(js[:fin + 1])

# ---- meta
D['meta'].update({k: r[k] for k in ('finalf1', 'finalkappa', 'finalprecbajo', 'finalrecallbajo', 'persf1', 'wconv', 'naltotest', 'ndiassel', 'ndiasanid')})
D['meta']['cm'] = r['cm']; D['meta']['finaltipo'] = r['finaltipo']; D['meta']['busquedapaga'] = r['busquedapaga']
# ---- prueba: pred = modelo final (combinación); ens = ensamble de R1; M y P son del ensamble de R1
T = D['test']; assert len(T['y']) == len(ex['y']) and T['y'] == ex['y'], 'la semana de prueba debe ser la misma'
T['pred'] = ex['pred_final']; T['conv'] = ex['pred_comb']; T['ens'] = ex['pred_ens']; T['ant'] = ex['pred_ant']
T['P'] = ex['P']; T['M'] = np.transpose(np.array(ex['Pm']), (1, 0, 2)).tolist()
D['nombres_ens'] = ex['ens_modelos']
# ---- partición principal
t80 = leer('res_parteD_80_20.csv', index_col=0)
ren = {'Ensamble de R1 (sin umbral)': 'Ensamble (sin umbral)'}
D['principal'] = {ren.get(k, 'Ensamble + umbral para bajo' if k.startswith('Ensamble de R1 +') else ('Ensamble anterior' if k.startswith('Ensamble anterior') else k)): v for k, v in t80.to_dict(orient='index').items()}
# ---- evaluación día a día: selección y prueba
for clave, arch in (('wf_conf', 'res_walkforward_prueba.csv'), ('wf_dev', 'res_walkforward_seleccion.csv')):
    t = leer(arch, index_col=0); t.index.name = 'm'; D[clave] = recs(t.reset_index())
D['wf_boot'] = recs(leer('res_walkforward_bootstrap.csv'))
D['anidada'] = recs(leer('res_seleccion_anidada.csv'))
D.pop('decision', None); D.pop('wf', None); D.pop('wf_nombres', None)
# ---- costo y grupos
pe = leer('res_pesos.csv'); pe = pe.rename(columns={'diferencia frente a sin criterio (%)': 'diferencia frente a sin criterio (%)'}); D['costo'] = recs(pe)
g = leer('res_grupos.csv'); g = g.rename(columns={g.columns[0]: 'g'}); D['km_err'] = recs(g)
# ---- 17 candidatos en los días de selección (kd: primera mitad; kc: todos los días de selección)
META, PROB = pickle.load(open(os.path.join(FIG, 'wf_probabilidades.pkl'), 'rb'))
sel = (META.dia_idx < r['wfdiaprueba']).to_numpy(); mitad = (META.dia_idx < (14 + r['wfdiaprueba']) // 2).to_numpy() & sel; y = META.real.to_numpy()
viejo = {c['m'].replace(' (actual)', ' (base)'): c['m'] for c in D['cand']}
D['cand'] = [{'m': viejo[n], 'kd': float(cohen_kappa_score(y[mitad], PROB[n].argmax(1)[mitad])), 'kc': float(cohen_kappa_score(y[sel], PROB[n].argmax(1)[sel])),
              'f1': float(f1_score(y[sel], PROB[n].argmax(1)[sel], average='macro'))} for n in PROB]
assert len(D['cand']) == 17
cb = leer('res_combinatoria.csv'); cb = cb[cb.tipo == 'ensamble']
D['comb'] = {'t': cb['F1 sel'].round(5).tolist(), 'kd': cb['F1 A'].round(5).tolist(), 'kc': cb['F1 B'].round(5).tolist()}

nuevo = '<script>window.DATA=' + json.dumps(D, ensure_ascii=False, separators=(',', ':')) + ';</script>'
lineas[i_d] = nuevo
open(HTML, 'w', encoding='utf-8', newline='\n').write('\n'.join(lineas))
print('DATA regenerado:', len(nuevo), 'caracteres;', 'claves:', sorted(D))
