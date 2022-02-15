from locale import normalize
from flask import Flask, render_template, request, Response
import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
sns.__version__
import json
import io
import numpy as np



def configDataset():
    global dataset
    url_dados_simba = 'https://github.com/saratiedt/ocean-dataset/blob/main/requested_files/simba/Ocorr%C3%AAncias%20de%20fauna%20alvo%20individual%2028_09_2021%2020%2055.xlsx?raw=true'
    dadosSimba = pd.read_excel(url_dados_simba, index_col=0)

    url_dados_temperatura = 'https://github.com/saratiedt/ocean-dataset/blob/main/requested_files/noaaDataset.csv?raw=true'
    dadosTemperatura = pd.read_csv(url_dados_temperatura,index_col=0)

    url_dados_velocidade_mar_oeste = 'https://github.com/saratiedt/ocean-dataset/blob/main/requested_files/eatsward%20sea%20water%20velocity.csv?raw=true'
    dadosVelociadeMarOeste = pd.read_csv(url_dados_velocidade_mar_oeste,index_col=0)

    url_dados_velocidade_mar_norte = 'https://github.com/saratiedt/ocean-dataset/blob/main/requested_files/nortward%20sea%20water%20velocity.csv?raw=true'
    dadosVelociadeMarNorte = pd.read_csv(url_dados_velocidade_mar_norte,index_col=0)

    url_dados_clorofila = 'https://github.com/saratiedt/ocean-dataset/blob/main/requested_files/GLOBAL_ANALYSIS_FORECAST_BIO_001_028.csv?raw=true'
    dadosClorofila = pd.read_csv(url_dados_clorofila,index_col=0)

    mapaTemp = {'Data/Hora': 'DATE'}
    dadosSimba.rename(columns=mapaTemp, inplace=True)
    dadosSimba['DATE'] = pd.to_datetime(dadosSimba.DATE)
    dadosSimba['data_convertida'] = dadosSimba['DATE'].dt.date

    dadosTemperatura['DATE'] = pd.to_datetime(dadosTemperatura.DATE)
    dadosTemperatura['data_convertida'] = dadosTemperatura['DATE'].dt.date

    dadosClorofila.reset_index(inplace=True)
    dadosClorofila['DATE'] = pd.to_datetime(dadosClorofila.DATE)
    dadosClorofila['data_convertida'] = dadosClorofila['DATE'].dt.date
    
    
    dadosVelociadeMarOeste.reset_index(inplace=True)
    dadosVelociadeMarOeste['DATE'] = pd.to_datetime(dadosVelociadeMarOeste.DATE)
    dadosVelociadeMarOeste['data_convertida'] = dadosVelociadeMarOeste['DATE'].dt.date


    dadosVelociadeMarNorte.reset_index(inplace=True)
    dadosVelociadeMarNorte['DATE'] = pd.to_datetime(dadosVelociadeMarNorte.DATE)
    dadosVelociadeMarNorte['data_convertida'] = dadosVelociadeMarNorte['DATE'].dt.date

    
    
    dataset = pd.merge(dadosSimba, dadosTemperatura, on='data_convertida')
    datasetCopernicus = pd.merge(dadosVelociadeMarOeste, dadosClorofila, on='data_convertida')
    dataset = pd.merge(dataset, datasetCopernicus, on='data_convertida')
    dataset = pd.merge(dataset, dadosVelociadeMarNorte, on='data_convertida')

    dataset['Espécies - Indice']=dataset['Espécies - Espécie'].astype('category').cat.codes
    dataset['Classe - Indice']=dataset['Espécies - Classe'].astype('category').cat.codes

    dataset.dropna(subset = ["Espécies - Indice"], inplace=True)
    dataset.dropna(subset = ["SEA_SURF_TEMP"], inplace=True)

def create_figure(select1Image, select2Image):
    fig, ax = plt.subplots(figsize = (6,4))
    configDataset()
    plt.hist2d(dataset[select1Image["value"]], dataset[select2Image["value"]], bins=(30))
    plt.colorbar()
    plt.xlabel(select1Image["label"])
    plt.ylabel(select2Image["label"])
    ax = plt.gca()
    ax.axis('tight')

    return fig

def create_figure2(selectVariavel, selectClasse):
    fig, ax = plt.subplots(figsize = (6,4))
    configDataset()
    bla = int(selectClasse["value"])
    datasetClasse = dataset[(dataset['Classe - Indice']==bla)]
    valor = selectVariavel["value"]

    if(valor == "WIND_SPEED"):
        teste = datasetClasse.WIND_SPEED.value_counts().reset_index()
        
    elif(valor == "IND_FOR_PRECIP"):
        teste = datasetClasse.IND_FOR_PRECIP.value_counts().reset_index()
    elif(valor == "sea_water_velocity"):
        teste = datasetClasse.sea_water_velocity.value_counts().reset_index()
    elif(valor == "chl"):
        teste = datasetClasse.chl.value_counts().reset_index()
    elif(valor == "uo"):
        teste = datasetClasse.uo.value_counts().reset_index()
    elif(valor == "vo"):
        teste = datasetClasse.vo.value_counts().reset_index()
    else:
        teste = datasetClasse.SEA_SURF_TEMP.value_counts().reset_index()
        print(teste)
    
    plt.bar(teste["index"], teste[valor], width=1.0)
    plt.xlabel(selectVariavel["label"])
    plt.ylabel("Número de registros da classe " + selectClasse["label"])
    
    ax.axis('tight')
    return fig

app = Flask(__name__)

seletoresSelect1 = {
   "list": [
      {
        "label": "Velocidade do vento",
        "value": "WIND_SPEED"
    },
    {
        "label": "indice de precipitação",
        "value": "IND_FOR_PRECIP"
    },
    {
        "label": "temperatura do mar",
        "value": "SEA_SURF_TEMP"
    },
     {
         "label": "Velocidade do mar Leste e Oeste",
        "value": "uo"
    },
    {
         "label": "Velocidade do mar Sul e Norte",
        "value": "vo"
    },
     {
        "label": "Indice de clorofila",
        "value": "chl"
    },
   ]
}

seletoresSelect2 = {
   "list": [
      {
        "label": "Velocidade do vento",
        "value": "WIND_SPEED"
    },
    {
        "label": "Classe animal",
        "value": "Espécies - Indice"
    },
    {
        "label": "Índice de precipitação",
        "value": "IND_FOR_PRECIP"
    },
    {
        "label": "Temperatura do mar",
        "value": "SEA_SURF_TEMP"
    },
    {
        "label": "Velocidade do mar Leste e Oeste",
        "value": "uo"
    },
    {
         "label": "Velocidade do mar Sul e Norte",
        "value": "vo"
    },
     {
        "label": "Indice de clorofila",
        "value": "chl"
    },
   ]
}

especies = {
   "list": [
      {
        "label": "Aves",
        "value": "0"
    },
    {
        "label": "Mammalia",
        "value": "1"
    },
    {
        "label": "Reptilia",
        "value": "2"
    },
   ]
}

@app.route('/')
def index():
    
    return render_template('index.html',  data=seletoresSelect1['list'], seletores2 = seletoresSelect2["list"], especiesLista = especies["list"])


@app.route("/correlation" , methods=['GET', 'POST'])
def correlation():
    global select1, select2, select3
    teste = request.form.get('comp_select1')
    teste2 = request.form.get('comp_select2')

    teste = teste.replace("'", '"')
    select1 = json.loads(teste)


    teste2 = teste2.replace("'", '"')
    select2 = json.loads(teste2)

    if(select2["value"] == "Espécies - Indice"):
        teste3 = request.form.get('comp_select3')
        teste3 = teste3.replace("'", '"')
        select3 = json.loads(teste3)
        create_figure2(select1, select3)
    else:
        create_figure(select1, select2)
    
    #img = '/static/assets/gato.jpeg'

    return render_template('result.html')
    #return(str(select1) + '  ' +  str(select2)) # just to see what select is

@app.route('/plot.png')
def plot_png():
    if(select2["value"] == "Espécies - Indice"):
        fig = create_figure2(select1, select3)
    else:
        fig = create_figure(select1, select2)

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


if __name__=='__main__':
    app.run(debug=True)
