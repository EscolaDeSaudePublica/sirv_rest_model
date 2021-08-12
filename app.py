
from flask import Flask, render_template
from flask_cors import CORS
from altair import *
from threading import Timer
from timeloop import Timeloop
from datetime import timedelta
import yaml
from yaml.loader import SafeLoader

app = Flask(__name__)
CORS(app)

app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True


# Open the file and load the file

tl = Timeloop()

@tl.job(interval=timedelta(seconds=10))
def update_file():  
    try:
        with open('config.yml') as f:
            data = yaml.load(f, Loader=SafeLoader)
        casos=pd.read_json(data['url'])
        casos=casos[casos.quantidade>0]
        casos.to_json('dados.txt')
        print('Dados atualizados')
    except Exception as ex:
        print(ex)

tl.start()


def SIRV_model(vaccine_rate_1000=0.002,V0=0,N =6587940,I0 = 16089,vaccine_eff=0.50,mortality_rate=1.9e-2,percentual_infectados=0.001,day_interval=30,speed_factor=0.02):
    import yaml
    import numpy as np
    import math
    import pandas as pd
    from yaml.loader import SafeLoader
    import pandas as pd
    from datetime import  datetime
    from datetime import timedelta
    import altair as alt



    
    
    casos=pd.read_json('dados.txt')
    
    casos['quantidade_nao_normalizada']=casos.quantidade.values
    
    total_infectados=sum(casos.quantidade_nao_normalizada.values)
    
    N=9000000-total_infectados
    
    casos.quantidade=casos.quantidade/N
    

    
    
    
    #casos.data=pd.to_datetime(casos.data)

   
    
    print(casos[-5:]['data'].values[0])
    data_inicial=casos[-5:]['data'].values[0]
    infectados=casos[-5:]['quantidade_nao_normalizada'].values[0]
    
    
    
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
    import pandas as pd
    df=pd.DataFrame(columns=['data','infectados','sucetiveis','removidos','vacinados'])
    df['data']=date_list
    df['infectados']=infectados
    df['sucetiveis']=sucetiveis
    df['removidos']=removidos

    df['vacinados']=vacinados
    df['infectados_acumulados'] = df['infectados'].cumsum()
    
    df['vacinados_acumulados'] = df['vacinados'].cumsum()
    casos.data=[ datetime.strptime(d, '%d/%m/%Y') for d in casos.data.values]   
    casos['infectados_acumulados']=casos.quantidade.cumsum()
    
    maximo_quantidade=np.max(casos.infectados_acumulados)
    
    print('maximo',maximo_quantidade)
    
    df['infectados_acumulados'] =df['infectados_acumulados']+maximo_quantidade
    
    

    
    casos_anteriores=alt.Chart(casos)\
        .mark_line(clip=True)\
        .encode(x='data',y=Y('quantidade_nao_normalizada',scale=Scale(domain=[0,10000])))\
        .properties(
            width=600,
    title=alt.TitleParams(
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
            width=600,
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
            width=600,
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
            width=600,
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
            width=600,
    title=alt.TitleParams(
        ['','','Projeção dos vacinados acumulados de Covid de acordo com o modelo SIRV.'],
        baseline='bottom',
        orient='bottom',
        anchor='end',
        fontWeight='normal',
        fontSize=10
    ))
    grafico=alt.vconcat(casos_anteriores+novos_casos,novos_casos,casos_acumulados+novos_casos_acumulados,vacinados_acumulados_casos_acumulados)
    grafico.save('templates/chart.html')
    
    
    
    return grafico


@app.route('/<string:eficacia_vacina>/<string:velocidade_vacinacao>/<string:novos_infectados>/<string:dias_novos_infectados>/<string:speed_factor>/')
def home(eficacia_vacina,velocidade_vacinacao,novos_infectados,dias_novos_infectados,speed_factor):
   grafico=SIRV_model(vaccine_eff=float(eficacia_vacina),vaccine_rate_1000=float(velocidade_vacinacao),percentual_infectados=float(novos_infectados),day_interval=int(dias_novos_infectados),speed_factor=float(speed_factor))
   return render_template('chart.html')
if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5100,ssl_context='adhoc')