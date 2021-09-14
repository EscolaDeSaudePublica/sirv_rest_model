
from flask import Flask, render_template
from flask_cors import CORS, cross_origin
from altair import *
from threading import Timer
from timeloop import Timeloop
from datetime import timedelta
from yaml.loader import SafeLoader
import yaml
import numpy as np
import math
import pandas as pd
from datetime import  datetime
from datetime import timedelta
import altair as alt
import unicodedata
import time

app = Flask(__name__)
CORS(app, supports_credentials=True)

app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['CORS_HEADERS'] = 'Content-Type'


# Open the file and load the file

tl = Timeloop()

@tl.job(interval=timedelta(seconds=600))
def update_file():  
    try:
        print('Atualizando dados ')
        with open('config.yml') as f:
            data = yaml.load(f, Loader=SafeLoader)
        print('Arquivo de configuração carregado')
        casos=pd.read_json(data['url'])
        casos=casos[casos.quantidade>0]
        casos.to_json('dados.txt')
       
    except Exception as ex:
        print(ex)


@tl.job(interval=timedelta(seconds=600))
def update_integrasus_municipios():  
    try:
       
        with open('config.yml') as f:
            data = yaml.load(f, Loader=SafeLoader)
      
        casos=pd.read_json(data['url_integrasus_casos'])
        casos.to_json('dados_municipios.txt')
    
    except Exception as ex:
        print(ex)


@tl.job(interval=timedelta(seconds=600))
def update_integrasus_municipios_casos():  
    try:
       
        with open('config.yml') as f:
            data = yaml.load(f, Loader=SafeLoader)
       
        casos=pd.read_json(data['url_integrasus_casos'])
        casos.to_json('dados_municipios.txt')
       
    except Exception as ex:
        print(ex)


@tl.job(interval=timedelta(seconds=10))
def update_integrasus_municipios_casos_por_municipio_vacinacao():  
    try:
        with open('config.yml') as f:
            data = yaml.load(f, Loader=SafeLoader)

        df=pd.read_csv('new_ibge-X_cidade.csv')
        print(df)
        for _,r in df.iterrows():
            url=data['url_vacina']
       
            url_municipio=url.replace('todos',str(r['new_ibge']))
         
            casos=pd.read_json(url_municipio)

            nome_municipio = ''.join(ch for ch in unicodedata.normalize('NFKD', r['nome']) 
    if not unicodedata.combining(ch))
            nome_municipio = nome_municipio.upper()

            casos.to_json('dados_casos_vacinacao_'+nome_municipio+'.txt')

            time.sleep(10)
       
    except Exception as ex:
        print(ex)


@tl.job(interval=timedelta(seconds=600))
def update_integrasus_municipios_casos_por_municipio():  
    try:
        with open('config.yml') as f:
            data = yaml.load(f, Loader=SafeLoader)

        df=pd.read_json('dados_municipios.txt')
        for _,r in df.iterrows():
            url=data['url_municipio_integrasus_casos']
         
            url_municipio=url.replace('@',str(int(r['idMunicipio'])))
           
            casos=pd.read_json(url_municipio)

            
            nome_municipio = ''.join(ch for ch in unicodedata.normalize('NFKD', r['municipio']) 
    if not unicodedata.combining(ch))
            nome_municipio = nome_municipio.upper()


            casos.to_json('dados_casos_'+nome_municipio+'.txt')

            time.sleep(10)
       
    except Exception as ex:
        print(ex)




@tl.job(interval=timedelta(seconds=600))
def update_file_vacinacao():  
    try:
        with open('config.yml') as f:
            data = yaml.load(f, Loader=SafeLoader)
        casos=pd.read_json(data['url_vacina'])
        
        casos.to_json('dados_vacinacao.txt')
       
    except Exception as ex:
        print(ex)







print('Iniciando metodo assincrono')
tl.start()


def SIRV_model(vaccine_rate_1000=0.002,V0=0,N =6587940,I0 = 16089,vaccine_eff=0.50
               ,mortality_rate=1.9e-2,percentual_infectados=0.001,day_interval=30
               ,speed_factor=0.02,death_factor=0.028,hospitalization_factor=0.1,municipio='Todos'):
   


    import pandas as pd

    
    if municipio=='Todos':
        casos=pd.read_json('dados.txt')
    else:

        nome_municipio = ''.join(ch for ch in unicodedata.normalize('NFKD', municipio) 
    if not unicodedata.combining(ch))
        nome_municipio = nome_municipio.upper()

        print('dados_casos_'+nome_municipio+'.txt')
        casos=pd.read_json('dados_casos_'+nome_municipio+'.txt')
        casos.quantidade=pd.to_numeric(casos.quantidade)
        now = pd.to_datetime("now")
        casos['data_date']=pd.to_datetime(casos.data, format='%d/%m/%Y', errors='coerce')
        print(casos)
        print(now)
        casos=casos[casos.data_date<now]
        
        print('casos')
        print(casos)
    
    casos['quantidade_nao_normalizada']=casos.quantidade.values
    
    total_infectados=sum(casos.quantidade_nao_normalizada.values)
    
    N=9000000-total_infectados
    
    casos.quantidade=casos.quantidade/N
    

    
    
    
    #casos.data=pd.to_datetime(casos.data)

   
    
    print(casos[-5:]['data'].values[0])
    data_inicial=casos[-5:]['data'].values[0]
    infectados=casos[-15:]['quantidade_nao_normalizada'].values[0]
    
    
    
    I0=infectados


    
    rate_of_removal=7.81e-2
    rate_of_infection= 9.76e-2
    alpha=vaccine_eff
    beta =rate_of_infection
    gamma =rate_of_removal
    mu=mortality_rate
    R0 = 0
    

   
    dt=1
    print(data_inicial)

    start_date=  datetime.strptime( data_inicial, '%d/%m/%Y')
    end_date=  datetime.strptime('Jun 8 2021', '%b %d %Y')
    prediction_end_date=datetime.strptime('Jan 30 2023', '%b %d %Y')

    tdays=(prediction_end_date-start_date).days
    
    T=tdays
    
    vaccine_rate=vaccine_rate_1000
    I0=I0/N 
    R0=R0/N


    
    def vaccine_pulse(vaccine_number,days):

        u=[ vaccine_number for i in range(0,days)]
        return u

    u=vaccine_pulse(vaccine_rate,tdays)
    S = [0 for i in range(0,math.ceil(T/dt))]
    R = [0 for i in range(0,math.ceil(T/dt))]
    I = [0 for i in range(0,math.ceil(T/dt))]
    V = [0 for i in range(0,math.ceil(T/dt))]
    
    S[0] =1-I0-R0-V0 
    I[0] = I0
    R[0]=R0
    V[0]=V0

    for t in range(0,math.ceil(T/dt)-1):
        #Boundary control
        if S[t]<=0:
            u[t]=0
            S[t]=0
        
        # Equations of the model
        dS = (-beta*I[t]*(S[t]/(1+speed_factor*S[t]))-alpha*u[t]) * dt
        dI = (beta*I[t]*(S[t]/(1+speed_factor*S[t])) - gamma*I[t]) * dt
        dR = (gamma*I[t]) * dt
        dV=alpha*u[t] * dt
        
        r = t % day_interval

        if r==0 and S[t]>0:
            
            I[t+1] = I[t] + dI+percentual_infectados
            S[t+1] = S[t] + dS
          
        else:
            S[t+1] = S[t] + dS
            I[t+1] = I[t] + dI  
        
        
        R[t+1] = R[t] + dR
        V[t+1] = V[t] + dV

    date_list = [timedelta(days=x)+start_date for x in range(tdays)]    
    removidos=[r*N for r in R]    
    vacinados=[v*N for v in V]        
    sucetiveis=[s*N for s in S]
    infectados=[i*N for i in I]
    mortos=[i*death_factor for i in infectados]
    hospitalizacao=[i*hospitalization_factor for i in infectados]

    import pandas as pd
    df=pd.DataFrame(columns=['data','infectados','sucetiveis','removidos','vacinados'])
    df['data']=date_list
    df['infectados']=infectados
    df['sucetiveis']=sucetiveis
    df['removidos']=removidos
    df['óbitos']=mortos
    df['hospitalizações']=hospitalizacao
    df['vacinados']=vacinados
    df['infectados_acumulados'] = df['infectados'].cumsum()
    
    df['vacinados_acumulados'] = df['vacinados'].cumsum()
    casos.data=[ datetime.strptime(d, '%d/%m/%Y') for d in casos.data.values]   
    casos['infectados_acumulados']=casos.quantidade.cumsum()
    
    maximo_quantidade=np.max(casos.infectados_acumulados)
    
    print('maximo',maximo_quantidade)
    
    df['infectados_acumulados'] =df['infectados_acumulados']+maximo_quantidade


    return df,casos
    
    
@app.route('/casos/')
def casos():
    casos=pd.read_json('dados.txt')
   
    print(casos)
    return casos.to_json(orient="table")

#process.env.REACT_APP_BASE_URL_ 

@app.route('/casos/<string:municipio>')
def casos_por_municipio(municipio):
    try:
        if municipio=='Todos':
            casos=pd.read_json('dados.txt')
        else:

            nome_municipio = ''.join(ch for ch in unicodedata.normalize('NFKD', municipio) 
    if not unicodedata.combining(ch))
            nome_municipio = nome_municipio.upper()
            casos=pd.read_json('dados_casos_'+nome_municipio.upper()+'.txt')
        print(casos)
        return casos.to_json(orient="table")
    except:
        casos=pd.DataFrame()
        return casos.to_json(orient="table")


@app.route('/total_vacinados/<string:municipio>')
def total_vacinados(municipio):

   
    if municipio=='Todos':
        casos=pd.read_json('dados_vacinacao.txt')
    
    else:

        nome_municipio = ''.join(ch for ch in unicodedata.normalize('NFKD', municipio) 
if not unicodedata.combining(ch))
        nome_municipio = nome_municipio.upper()
        casos=pd.read_json('dados_casos_vacinacao_'+nome_municipio.upper()+'.txt')
   
    casos=casos.fillna(0)
    casos=casos.reset_index()
    casos['Total'] = casos.sum(axis=1)

    print(casos)
    return casos.to_json(orient="table")


@app.route('/populacao_cidades/')
def populacao_cidades():
    populacao=pd.read_csv('populacao.csv')
    return populacao.to_json(orient="table")
  
    
@app.route('/filter_date/<string:eficacia_vacina>/<string:velocidade_vacinacao>/<string:novos_infectados>/<string:dias_novos_infectados>/<string:speed_factor>/<string:death_factor>/<string:hospitalization_factor>/<string:start_date>/<string:end_date>/')
def filter_date(eficacia_vacina,velocidade_vacinacao,novos_infectados,dias_novos_infectados,speed_factor,death_factor,hospitalization_factor,start_date,end_date):
   df,casos=SIRV_model(vaccine_eff=float(eficacia_vacina),vaccine_rate_1000=float(velocidade_vacinacao)
                      ,percentual_infectados=float(novos_infectados),
                      day_interval=int(dias_novos_infectados)
                      ,speed_factor=float(speed_factor),
                      death_factor=float(death_factor),
                      hospitalization_factor=float(hospitalization_factor))


   
   start_date_=datetime.strptime(start_date,'%Y-%m-%d')
   end_date_=datetime.strptime(end_date,'%Y-%m-%d')
   print(start_date_)
   print(end_date_)

  
   print('Antes do filtro de data ') 
   print(df)

   df=df[(df.data>=start_date_) &  (df.data<=end_date_)]

   print('Depois do filtro de data ') 
   print(df)

   
   df=df[['data','infectados','óbitos','hospitalizações']]
   df.columns=['Data','Infectados','Óbitos','Hospitalizações']

   df=df.reset_index(drop=True)
   df.index+=1 

   df.loc['Total']= df.sum(numeric_only=True, axis=0)

   print(df)
   
   return df.to_json(orient="records")
    



@app.route('/json_model_data/<string:eficacia_vacina>/<string:velocidade_vacinacao>/<string:novos_infectados>/<string:dias_novos_infectados>/<string:speed_factor>/<string:death_factor>/<string:hospitalization_factor>/')
def json_model_data(eficacia_vacina,velocidade_vacinacao,novos_infectados,dias_novos_infectados,speed_factor,death_factor,hospitalization_factor):
    velocidade_vacinacao_=float(velocidade_vacinacao)/9000000
    percentual_infectados_=float(novos_infectados)/9000000
    print('velocidade vacinacao ',velocidade_vacinacao_)
    df,casos=SIRV_model(vaccine_eff=float(eficacia_vacina),vaccine_rate_1000=velocidade_vacinacao_
                      ,percentual_infectados=percentual_infectados_,
                      day_interval=int(dias_novos_infectados)
                      ,speed_factor=float(speed_factor),
                      death_factor=float(death_factor),
                      hospitalization_factor=float(hospitalization_factor))
    

    
    return df.to_json(orient="table")


@app.route('/json_model_data_municipio/<string:eficacia_vacina>/<string:velocidade_vacinacao>/<string:novos_infectados>/<string:dias_novos_infectados>/<string:speed_factor>/<string:death_factor>/<string:hospitalization_factor>/<string:municipio>/')
@cross_origin(supports_credentials=True)
def json_model_data_por_municipio(eficacia_vacina,velocidade_vacinacao,novos_infectados,dias_novos_infectados,speed_factor,death_factor,hospitalization_factor,municipio):
    
    try:
        if municipio=='Todos':
            print('Municipio igual a todos')
            velocidade_vacinacao_=float(velocidade_vacinacao)/9000000
            percentual_infectados_=float(novos_infectados)/9000000

        else:
            populacao=pd.read_csv('populacao.csv')
            populacao=populacao[populacao.nome.str.upper()==municipio.upper()]
            total_populacao=int(populacao.iloc[0,:].populacao)
            velocidade_vacinacao_=float(velocidade_vacinacao)/total_populacao
            percentual_infectados_=float(novos_infectados)/total_populacao

        df,casos=SIRV_model(vaccine_eff=float(eficacia_vacina),vaccine_rate_1000=float(velocidade_vacinacao_)
                          ,percentual_infectados=float(percentual_infectados_),
                          day_interval=int(dias_novos_infectados)
                          ,speed_factor=float(speed_factor),
                          death_factor=float(death_factor),
                          hospitalization_factor=float(hospitalization_factor),municipio=municipio)
    
    except Exception as e:
        print(e)
        df=pd.DataFrame()
    
    return df.to_json(orient="table")


@app.route('/<string:eficacia_vacina>/<string:velocidade_vacinacao>/<string:novos_infectados>/<string:dias_novos_infectados>/<string:speed_factor>/<string:death_factor>/<string:hospitalization_factor>/')
def home(eficacia_vacina,velocidade_vacinacao,novos_infectados,dias_novos_infectados,speed_factor,death_factor,hospitalization_factor):
   df,casos=SIRV_model(vaccine_eff=float(eficacia_vacina),vaccine_rate_1000=float(velocidade_vacinacao)
                      ,percentual_infectados=float(novos_infectados),
                      day_interval=int(dias_novos_infectados)
                      ,speed_factor=float(speed_factor),
                      death_factor=float(death_factor),
                      hospitalization_factor=float(hospitalization_factor))
    


   casos_anteriores=alt.Chart(casos)\
                                    .mark_line(clip=True)\
                                    .encode(x='data',y=Y('quantidade_nao_normalizada',scale=Scale(domain=[0,10000])))\
                                    .properties(width=500,title=alt.TitleParams(
                                    ['','Gráfico com o Número de infectados por Covid e projeção com o modelo SIRV.'],
                                        baseline='bottom',
                                        orient='bottom',
                                        anchor='end',
                                        fontWeight='normal',
                                        fontSize=10
                                    ))


   casos_acumulados=alt.Chart(casos)\
            .mark_line(clip=True)\
            .encode(x='data',y=Y('infectados_acumulados',scale=Scale(domain=[0,4000000])))\
            .properties(
                width=500,
        title=alt.TitleParams(
            ['','Gráfico com o Número de infectados por Covid e projeção com o modelo SIRV.'],
            baseline='bottom',
            orient='bottom',
            anchor='end',
            fontWeight='normal',
            fontSize=10
        ))

   novos_casos=alt.Chart(df)\
            .mark_line(clip=True)\
            .encode(x='data',y=Y('infectados',scale=Scale(domain=[0,10000])),color=alt.value('red'))\
            .properties(
               width=500,
        title=alt.TitleParams(
            ['','','Projeção dos casos de Covid de acordo com o modelo SIRV.'],
            baseline='bottom',
            orient='bottom',
            anchor='end',
            fontWeight='normal',
            fontSize=10
        ))


   novos_casos_acumulados=alt.Chart(df)\
            .mark_line(clip=True)\
            .encode(x='data',y='infectados_acumulados',color=alt.value('red'))\
            .properties(
                width=500,
        title=alt.TitleParams(
            ['','','Projeção dos casos acumulados de Covid de acordo com o modelo SIRV.'],
            baseline='bottom',
            orient='bottom',
            anchor='end',
            fontWeight='normal',
            fontSize=10
        ))

   vacinados_acumulados_casos_acumulados=alt.Chart(df)\
            .mark_line()\
            .encode(x='data',y='vacinados',color=alt.value('red'))\
            .properties(
                width=500,
        title=alt.TitleParams(
            ['','','Projeção dos vacinados acumulados de Covid de acordo com o modelo SIRV.'],
            baseline='bottom',
            orient='bottom',
            anchor='end',
            fontWeight='normal',
            fontSize=10
        ))


   obitos_grafico=alt.Chart(df)\
            .mark_line()\
            .encode(x='data',y='óbitos',color=alt.value('red'))\
            .properties(
                width=500,
        title=alt.TitleParams(
            ['','','Projeção dos óbitos de Covid de acordo com o modelo SIRV.'],
            baseline='bottom',
            orient='bottom',
            anchor='end',
            fontWeight='normal',
            fontSize=10
        ))


   hospitalizacoes_grafico=alt.Chart(df)\
            .mark_line()\
            .encode(x='data',y='hospitalizações',color=alt.value('red'))\
            .properties(
                width=500,
        title=alt.TitleParams(
            ['','','Projeção das hospitalizações por Covid de acordo com o modelo SIRV.'],
            baseline='bottom',
            orient='bottom',
            anchor='end',
            fontWeight='normal',
            fontSize=10
        ))


   autosize = alt.AutoSizeParams(contains="content", resize=True, type='fit-x')

   grafico=alt.vconcat(casos_anteriores+novos_casos,novos_casos,
                        casos_acumulados+novos_casos_acumulados,
                        vacinados_acumulados_casos_acumulados,obitos_grafico,hospitalizacoes_grafico)
   grafico .save('templates/chart.html')
    
   return render_template('chart.html')



if __name__ == '__main__':
   print('Iniciando aplicacao')
   app.run(host='0.0.0.0', port=5100)