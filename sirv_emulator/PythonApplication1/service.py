
from flask import Flask, render_template
app = Flask(__name__)
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True



def SIRV_model(vaccine_rate_1000=1,V0=0,N =6587940,I0 = 16089,vaccine_eff=0.50,mortality_rate=1.9e-2,percentual_infectados=0.001,day_interval=30):
    import yaml
    import numpy as np
    import math
    import pandas as pd
    from yaml.loader import SafeLoader
    import pandas as pd
    from datetime import  datetime
    from datetime import timedelta
    import altair as alt



    # Open the file and load the file
    with open('config.yml') as f:
        data = yaml.load(f, Loader=SafeLoader)
    
    casos=pd.read_json(data['url'])
    
    
    #casos.data=pd.to_datetime(casos.data)

    total_infectados=sum(casos.quantidade.values)
    
    print(casos[-5:]['data'].values[0])
    data_inicial=casos[-5:]['data'].values[0]
    infectados=casos[-5:]['quantidade'].values[0]
    
    N=8843000-total_infectados
    
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
    prediction_end_date=datetime.strptime('Dec 12 2023', '%b %d %Y')

    tdays=(prediction_end_date-start_date).days
    
    T=tdays
    
    vaccine_rate=vaccine_rate_1000*N/1000
    I0=I0/N 
    R0=R0/N


    
    def vaccine_pulse(vaccine_number,days):

        u=[(vaccine_number/N) for i in range (0,days)]
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
        dS = (-beta*I[t]*(S[t]/(1+0.2*S[t]))-alpha*u[t]) * dt
        dI = (beta*I[t]*(S[t]/(1+0.2*S[t])) - gamma*I[t]) * dt
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
    casos.data=[ datetime.strptime(d, '%d/%m/%Y') for d in casos.data.values]   
    
    
    casos_anteriores=alt.Chart(casos).mark_line().encode(x='data',y='quantidade')
    novos_casos=alt.Chart(df).mark_line().encode(x='data',y='infectados')
    grafico=alt.vconcat(casos_anteriores+novos_casos,novos_casos)
    grafico.save('templates/chart.html')
    
    
    
    return grafico

@app.route('/<string:eficacia_vacina>/<string:velocidade_vacinacao>/<string:novos_infectados>/<string:dias_novos_infectados>/')
def home(eficacia_vacina,velocidade_vacinacao,novos_infectados,dias_novos_infectados):
   grafico=SIRV_model(vaccine_eff=float(eficacia_vacina),vaccine_rate_1000=float(velocidade_vacinacao),percentual_infectados=float(novos_infectados),day_interval=int(dias_novos_infectados))
   return render_template('chart.html')
if __name__ == '__main__':
   app.run()