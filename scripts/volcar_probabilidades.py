"""Ejecuta una copia del cuaderno hasta 4.4.5 y vuelca las probabilidades de cada modelo del ensamble de R1 en la semana de prueba
(figuras/sust_probabilidades.json). La sustentación las usa en la escena del ensamble. No modifica el cuaderno.
Uso (necesita nbclient e ipykernel): python scripts/volcar_probabilidades.py"""
import os, nbformat
from nbclient import NotebookClient

raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
nb = nbformat.read(os.path.join(raiz, 'Proyecto4_Planta2.ipynb'), as_version=4)
i_fin = next(i for i, c in enumerate(nb.cells) if c.cell_type == 'code' and 'Apertura de la prueba (R4)' in c.source)
nb.cells = nb.cells[:i_fin + 1]
nb.cells.append(nbformat.v4.new_code_cell('''import json
Pm = []
for nom in ENS_MODELOS:
    est, rej = ENS_REJILLAS[nom]
    gs = GridSearchCV(clone(est), rej, cv=cv, scoring='f1_macro', n_jobs=1).fit(train_d[COLS_D], ytr)
    Pm.append(probs3(gs.best_estimator_, test_d[COLS_D]))
Pm = np.array(Pm); assert np.allclose(Pm.mean(0), ens_80['P'])
json.dump({'Pm': Pm.tolist(), 'P': ens_80['P'].tolist(), 'pred_final': [int(x) for x in pred_te], 'pred_ens': [int(x) for x in ens_80['sin_umbral']],
           'pred_comb': [int(x) for x in pred_comb_te], 'pred_ant': [int(x) for x in ens_ant['sin_umbral']], 'tau': float(ens_80['tau']), 'ens_modelos': list(ENS_MODELOS),
           'y': [int(x) for x in yte], 'dia': [str(x) for x in test.fecha], 'hora': [float(x) for x in test.hora]},
          open('figuras/sust_probabilidades.json', 'w', encoding='utf-8'))
print('volcado', Pm.shape)'''))
NotebookClient(nb, timeout=None, kernel_name='python3', resources={'metadata': {'path': raiz}}).execute()
print('listo')
