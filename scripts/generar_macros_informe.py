"""Genera Informe/valores.tex a partir de figuras/resultados.json y los CSV de figuras/.
Ninguna cifra del informe se escribe a mano: todo sale del cuaderno (Proyecto4_Planta2.ipynb).
Uso (desde la raíz del proyecto): python scripts/generar_macros_informe.py"""
import json, os
import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(RAIZ, 'figuras')
r = json.load(open(os.path.join(FIG, 'resultados.json'), encoding='utf-8'))
leer = lambda n, **kw: pd.read_csv(os.path.join(FIG, n), encoding='utf-8-sig', **kw)

def n0(x):                    # entero con separador de miles de LaTeX
    s = f'{int(round(x)):,}'.replace(',', r'\,'); return s
def f1(x): return f'{x:.1f}'
def f2(x): return f'{x:.2f}'
def f3(x): return f'{x:.3f}'
def sg3(x): return f'+{x:.3f}' if x >= 0 else f'$-${abs(x):.3f}'
M = {}

# ---- datos y preparación
for k, f in {'K': str, 'ndiasentr': str, 'ndiasprueba': str, 'ndiaswf': str, 'ndiassel': str, 'ndiasanid': str, 'nentrena': n0, 'nprueba': n0, 'nfilas': n0, 'nesperados': n0,
             'nausentes': str, 'nincompletos': n0, 'nregfaltan': n0, 'ntodocero': str, 'naltotest': str, 'ncandidatos': str, 'nsobre': str, 'ninstceroscon': str,
             'nnoche': n0, 'ndescarte': str, 'cortebm': n0, 'cortema': n0, 'nescenarios': str, 'nescpers': str, 'nescregla': str}.items():
    M[k] = f(r[k])
M['umbral'] = f2(r['umbral']); M['wconv'] = f2(r['wconv']); M['silh'] = f2(r['silh'])
for k in ('pctincompletos', 'pctregfaltan', 'errinterp', 'paltotest', 'invsobre'): M[k] = f1(r[k])
M['invbajook'] = f2(r['invbajook']); M['ete'] = n0(r['ete']); M['etr'] = n0(r['etr']); M['irrte'] = f1(r['irrte']); M['irrtr'] = f1(r['irrtr'])
M['corrpot'] = f2(r['corrpot']); M['corrirr'] = f2(r['corrirr']); M['aporteclima'] = sg3(r['aporteclima'])
M['fConjA'], M['fConjB'], M['fConjC'] = f3(r['f1A']), f3(r['f1B']), f3(r['f1C'])
M['habA'], M['habB'], M['habC'] = sg3(r['habA']), sg3(r['habB']), sg3(r['habC'])
M['psimcoincide'] = n0(r['psimcoincide'])
M['ncombinaciones'] = n0(r['ncombinaciones'] - r['ncandidatos'] - 2)         # combinaciones de 2 a 5 modelos
M['nopciones'] = n0(r['ncombinaciones'])                                    # + candidatos solos + 2 referencias
for k in ('fugaAccSin', 'fugaAccCon', 'fugaKappaSin', 'fugaKappaCon'): M[k] = f3(r[k])
for k in ('python', 'numpy', 'pandas', 'sklearn', 'matplotlib', 'xgboost'): M['v' + {'sklearn': 'scikitlearn'}.get(k, k)] = r[k]
for k in ('scipy', 'statsmodels', 'seaborn', 'missingno', 'joblib'): M['v' + k] = r['v' + k]
M['finalvecesbajo'], M['finalfalsosbajo'] = str(r['finalvecesbajo']), str(r['finalfalsosbajo'])
cm = r['cm']
# cm[real][predicho] con el orden bajo, medio, alto; el nombre de la macro es cm + real + predicho (b, m, a)
nom_cm = {0: 'b', 1: 'm', 2: 'a'}
for i in range(3):
    for j in range(3): M[f'cm{nom_cm[i]}{nom_cm[j]}'] = str(cm[i][j])
# SIMEM (capacidad solar de XM)
sim = pd.read_csv(os.path.join(RAIZ, 'Otros_Datos', 'capacidad_solar_simem.csv'))
M['simemMWIni'], M['simemMWFin'] = f1(sim.solar_operacion_MW.iloc[0]), n0(sim.solar_operacion_MW.iloc[-1])
M['simemAnioIni'] = sim.fecha.iloc[0][:4]; M['simemPlantasIni'], M['simemPlantasFin'] = str(sim.plantas_solar_operacion.iloc[0]), n0(sim.plantas_solar_operacion.iloc[-1])
M['simemPartIni'], M['simemPartFin'] = f1(sim.participacion_solar_operacion_pct.iloc[0]), f1(sim.participacion_solar_operacion_pct.iloc[-1])

# ---- reglas del árbol (hojas)
hojas = r['reglas']
bajo = max((h for h in hojas if h['nivel'] == 'bajo'), key=lambda h: h['pct']); alto = max((h for h in hojas if h['nivel'] == 'alto'), key=lambda h: h['pct'])
umb = lambda h, var, op: (min if op == '<=' else max)(c[2] for c in h['condiciones'] if c[0] == var and c[1] == op)
M['reglaBajoGuno'] = f2(umb(bajo, 'IRRADIATION_lag1', '<=')); M['reglaBajoGcuatro'] = f2(umb(bajo, 'IRRADIATION_lag4', '<='))
M['reglaBajoPct'] = f1(bajo['pct']); M['reglaBajoPureza'] = f1(bajo['pureza'])
M['reglaAltoG'] = f2(umb(alto, 'IRRADIATION_lag1', '>')); M['reglaAltoP'] = n0(umb(alto, 'AC_PLANTA_KW_lag1', '>'))
M['reglaAltoPct'] = f1(alto['pct']); M['reglaAltoPureza'] = f1(alto['pureza'])

# ---- semana de prueba, partición principal (modelo final, referencias y ensambles)
t80 = leer('res_parteD_80_20.csv', index_col=0)
fin = leer('res_prueba_final.csv', index_col=0)
CAMPOS = {'Acc': 'exactitud', 'Fmacro': 'F1 macro', 'Kappa': 'kappa', 'Prec': 'precisión de bajo', 'Rec': 'recall de bajo', 'FalsosBajo': 'falsos bajo', 'MWh': 'MWh en falsos bajo (cota)'}
fila = lambda t, ini: t[t.index.str.startswith(ini)].iloc[0]
FILAS = {'Clim': fila(t80, 'Climatolog'), 'Pers': fila(t80, 'Persistencia'), 'Comb': fila(t80, 'Combinación'), 'Mejor': fila(t80, 'Mejor modelo individual'),
         'Rone': fila(fin, 'Ensamble elegido por R1'), 'Ant': fila(fin, 'Ensamble anterior'), 'Fin': fin[fin['es el modelo final']].iloc[0]}
for tag, row in FILAS.items():
    for c, col in CAMPOS.items():
        M[f't{tag}{c}'] = str(int(row[col])) if c == 'FalsosBajo' else (f1(row[col]) if c == 'MWh' else f3(row[col]))
M['tDummyAcc'], M['tDummyFmacro'] = f3(r['dummyacc']), f3(r['dummyf1'])
# modelo final frente al ensamble de R1: bajos verdaderos y energía de los falsos bajo adicionales
M['tpFin'] = str(int(FILAS['Fin']['veces que dijo bajo'] - FILAS['Fin']['falsos bajo'])); M['tpRone'] = str(int(FILAS['Rone']['veces que dijo bajo'] - FILAS['Rone']['falsos bajo']))
M['tVecesRone'] = str(int(FILAS['Rone']['veces que dijo bajo']))
precio_kwh = leer('res_pesos.csv', index_col=0).filter(like='Modelo final', axis=0)['COP en falsos bajo (planta completa)'].iloc[0] / (FILAS['Fin']['MWh en falsos bajo (cota)'] * 1000)   # COP/kWh del cuaderno (PRECIO_COP_KWH)
dif_mwh = FILAS['Rone']['MWh en falsos bajo (cota)'] - FILAS['Fin']['MWh en falsos bajo (cota)']
M['mwhDifRone'] = f1(dif_mwh); M['copDifRone'] = f1(dif_mwh * 1000 * precio_kwh / 1e6)
M['fbExtraRone'] = str(int(FILAS['Rone']['falsos bajo'] - FILAS['Fin']['falsos bajo']))
# filas de la tabla de resultados, con el mejor valor de cada columna en negrita (el ensamble anterior no compite: no es válido)
cols = ['exactitud', 'F1 macro', 'kappa', 'precisión de bajo', 'recall de bajo', 'falsos bajo']
cands = ['Clim', 'Pers', 'Comb', 'Mejor', 'Rone']
mejores = {c: (min if c == 'falsos bajo' else max)(FILAS[t][c] for t in cands) for c in cols}
def celda(t, c):
    v = FILAS[t][c]; s = str(int(v)) if c == 'falsos bajo' else f3(v)
    return rf'\textbf{{{s}}}' if t in cands and v == mejores[c] else s
etiq = {'Clim': 'Climatolog\\\'ia', 'Pers': 'Persistencia', 'Comb': 'Persist.\\ + climatol.', 'Mejor': 'Bosque aleatorio (C, final)', 'Rone': 'Ensamble de R1 (4 modelos)', 'Ant': 'Ensamble anterior$^\\dagger$'}
filas_tex = [rf"Clase m\'as frecuente & {f3(r['dummyacc'])} & {f3(r['dummyf1'])} & 0.000 & -- & -- & -- \\"]
for t in ('Clim', 'Pers', 'Comb', 'Mejor', 'Rone', 'Ant'):
    filas_tex.append(f"{etiq[t]} & " + ' & '.join(celda(t, c) for c in cols) + r' \\')
M['filasResultados'] = '\n'.join(filas_tex)
assert r['finaltipo'] != 'individual' or FILAS['Fin']['F1 macro'] == FILAS['Mejor']['F1 macro'], 'el modelo final individual debe ser el mejor individual de la partición principal'

# ---- evaluación día a día de la semana de prueba
pru = leer('res_walkforward_prueba.csv', index_col=0)
for tag, nom in {'Pers': 'Persistencia', 'Fin': 'Modelo final', 'Rone': 'Ensamble (sin umbral)', 'Comb': 'Combinación persistencia-climatología', 'Ant': 'Ensamble anterior'}.items():
    for c, col in {'Fmacro': 'F1 macro', 'Kappa': 'kappa', 'Prec': 'precisión de bajo', 'Rec': 'recall de bajo'}.items(): M[f'pru{tag}{c}'] = f3(pru.loc[nom, col])
boot = leer('res_walkforward_bootstrap.csv')
A = {'Modelo final': 'Fin', 'Ensamble (sin umbral)': 'Rone', 'Ensamble + umbral para bajo': 'Umb'}
B = {'Persistencia': 'Pers', 'Combinación persistencia-climatología': 'Comb'}
Mt = {'F1 macro': 'Fmacro', 'kappa': 'Kappa', 'precisión de bajo': 'Prec', 'recall de bajo': 'Rec'}
for _, x in boot.iterrows():
    base = f'wf{A[x.A]}{B[x["frente a B"]]}{Mt[x["métrica"]]}'
    M[base], M[base + 'Lo'], M[base + 'Hi'] = sg3(x['diferencia (A − B)']), sg3(x['IC95 inferior']), sg3(x['IC95 superior'])

# ---- selección anidada temporal, mitades y combinatoria
an = leer('res_seleccion_anidada.csv'); an = an[an['frente a'] == 'Combinación persistencia-climatología'].set_index('métrica')
for m, c in Mt.items():
    M[f'anid{c}'], M[f'anid{c}Lo'], M[f'anid{c}Hi'] = sg3(an.loc[m, 'diferencia']), sg3(an.loc[m, 'IC95 inferior']), sg3(an.loc[m, 'IC95 superior'])
M['spearman'] = f2(r['rhomitades']); M['pctlMejorA'] = n0(100 * r['pctlmejorA']); M['pctlFinSel'] = n0(100 * r['percentilsel'])
M['nelegcomb'] = str(sum(1 for d in r['elegidasdia'] if d[2] == 'Combinación persistencia-climatología'))

# ---- grupos de días y subconjunto con inversores en cero
g = leer('res_grupos.csv', index_col=0)
for tag, i in (('Uno', 0), ('Dos', 1)):
    M[f'g{tag}Dias'] = str(int(g['días'].iloc[i])); M[f'g{tag}Err'] = f1(g['error %'].iloc[i]); M[f'g{tag}Kappa'] = f2(g['kappa'].iloc[i]); M[f'g{tag}Inv'] = f2(g['inversores en cero (prom.)'].iloc[i])
iec = leer('res_iec153.csv')
for sub, tag in (('todos los instantes', 'Todos'), ('sin inversores en cero', 'Sin'), ('con inversores en cero', 'Con')):
    for mod, mt in (('Random Forest', 'Fin'), ('Persistencia', 'Pers')):
        x = iec[(iec.instantes == sub) & iec.modelo.str.startswith(mod)].iloc[0]
        M[f'iec{tag}{mt}Fmacro'], M[f'iec{tag}{mt}FalsosBajo'], M[f'iec{tag}N'] = f3(x['F1 macro']), str(int(x['falsos bajo'])), str(int(x['n']))
assert r['finaltipo'] == 'individual', 'iec153 y pesos usan el modelo final; revisar las etiquetas si cambia'

# ---- costo en pesos (ilustrativo)
pe = leer('res_pesos.csv', index_col=0)
M['copFin'] = f1(pe[pe.index.str.startswith('Modelo final')]['COP en falsos bajo (planta completa)'].iloc[0] / 1e6)
M['copPers'] = f1(pe[pe.index.str.startswith('Persistencia')]['COP en falsos bajo (planta completa)'].iloc[0] / 1e6)
M['ahorroFin'] = f1(pe[pe.index.str.startswith('Modelo final')]['diferencia frente a sin criterio (%)'].iloc[0])
M['ahorroRegla'] = f1(pe[pe.index.str.startswith('Regla de horario')]['diferencia frente a sin criterio (%)'].iloc[0])

ruta = os.path.join(RAIZ, 'Informe', 'valores.tex')
with open(ruta, 'w', encoding='utf-8', newline='\n') as f:
    f.write('% Generado por scripts/generar_macros_informe.py; no editar a mano.\n')
    for k in sorted(M): f.write('\\newcommand{\\%s}{%s}\n' % (k, M[k]))
print(f'{len(M)} macros escritas en {ruta}')
