# Proyecto 4: nivel de generación solar de la Planta 2

Proyecto final de Analítica de Datos I (Universidad Icesi, 2026-02). A partir de los datos de una planta solar de la India (Planta 2, lecturas cada 15 minutos) se construye una herramienta de pronóstico de corto plazo para una empresa de operación y mantenimiento (O&M) que ofrecerá monitoreo a plantas solares en Colombia.

**Equipo:** David González Chois, Sara Castrillón y Juan Miguel Correa.

## Qué hace

- **Clasificación:** anticipa, 15 minutos antes, si la potencia de la planta estará en nivel *bajo*, *medio* o *alto*. El énfasis está en acertar cuando el modelo dice «bajo» (precisión de «bajo»), porque un falso «bajo» manda a una cuadrilla a intervenir con la planta produciendo.
- **Modelo final:** ensamble de cuatro modelos (bosque aleatorio, regresión logística ElasticNet, SVM lineal calibrada y regresión logística con distancias a K-Means), elegido entre 17 candidatos y 9 384 combinaciones. Solo usa información pasada y la hora del día (sin fuga de información), con partición cronológica por días.
- **Agrupamiento:** K-Means (K = 4) para describir los tipos de día.
- **Alertas:** el pronóstico alimenta ventanas de mantenimiento y alertas de desvío (se esperaba medio o alto y la planta generó bajo), incluidos los inversores en cero con sol.
- **Despliegue:** estrategia en AWS y simulación local del flujo en tiempo real (fase 6 del cuaderno).

Las cifras miden el método con datos de otro país, una planta y un mes; no el desempeño en una planta colombiana.

## Contenido

```
Final_Version/
├── Proyecto4_Planta2.ipynb        # cuaderno principal (CRISP-DM, fases 1 a 6)
├── experimento_anexo/
│   ├── Anexo_A_Calidad_de_datos.ipynb          # validaciones de calidad de datos
│   └── Anexo_B_Experimentos_de_modelado.ipynb  # variantes y experimentos de modelado
├── Informe_Proyecto4.pdf          # informe en formato IEEE
├── Informe/                       # fuente LaTeX del informe (Informe_Proyecto4.tex, valores.tex y figuras)
├── sustentacion.html              # presentación interactiva (ábrase en el navegador, funciona sin internet)
├── Data/                          # CSV de la Planta 1 y la Planta 2 (Kaggle)
├── Otros_Datos/capacidad_solar_simem.csv       # capacidad solar de Colombia (XM/SIMEM)
├── Bibliografia/                  # artículos y normas consultadas
├── requirements.txt
└── .gitignore
```

## Datos

Los datos están en `Data/` (unos 11 MB), tal como se descargan de Kaggle: *Solar Power Generation Data* (A. Kannal), <https://www.kaggle.com/datasets/anikannal/solar-power-generation-data>.

- `Plant_1_Generation_Data.csv` y `Plant_1_Weather_Sensor_Data.csv` (solo para comparar)
- `Plant_2_Generation_Data.csv` y `Plant_2_Weather_Sensor_Data.csv` (la planta del proyecto)

El cuaderno busca los CSV dentro de su propia carpeta, así que encuentra `Data/` sin configurar nada.

## Cómo ejecutarlo

```bash
python -m venv .venv
.venv\Scripts\activate          # en Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
jupyter lab
```

Abra `Proyecto4_Planta2.ipynb` y ejecute todas las celdas en orden (tarda unos 20 minutos). El cuaderno crea la carpeta `figuras/` con las gráficas y las tablas de resultados, y guarda las probabilidades día a día en `figuras/wf_probabilidades.pkl`.

Los anexos de `experimento_anexo/` se ejecutan **después** del cuaderno principal: el Anexo B lee ese `wf_probabilidades.pkl`. Ambos encuentran solos la carpeta `Data/`.

Para recompilar el informe: `pdflatex Informe_Proyecto4.tex` dentro de `Informe/` (dos veces). Las cifras del texto salen de `valores.tex`, generado a partir de los resultados del cuaderno.

## Presentación

Abra `sustentacion.html` en un navegador. Flechas ← → para avanzar, `F` para pantalla completa, arrastrar para girar las escenas en 3D.
