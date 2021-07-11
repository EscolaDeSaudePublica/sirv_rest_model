function [S,I,R,V] = SIRV_model(alpha,beta,gamma,I0,R0,V0,T,dt,u)
    S = zeros(1,ceil(T/dt));
    R = zeros(1,ceil(T/dt));
    I = zeros(1,ceil(T/dt));
    V = zeros(1,ceil(T/dt));
    S(1) =1-I0-R0-V0; 
    I(1) = I0;
    R(1)=R0;
    V(1)=V0;
    display('interval');
    display(ceil(T/dt)-1);
    for t = 1:ceil(T/dt)-1
        %Boundary control
        if S(t)<=0
            u(t)=0;
            S(t)=0;
        end
        % Equations of the model
        dS = (-beta*I(t)*(S(t)/(1+0.2*S(t)))-alpha*u(t)) * dt;
        dI = (beta*I(t)*(S(t)/(1+0.2*S(t))) - gamma*I(t)) * dt;
        dR = (gamma*I(t)) * dt;
        dV=alpha*u(t) * dt;
        
        r = rem(t, 30);
        display(r);
        display(t);
        if r==0 && S(t)>0
            %display('r equals 0')
            %S(t+1)=S(t)+dS+0.001;
            I(t+1) = I(t) + dI;%+0.0001;
            S(t+1) = S(t) + dS;
            %
            %display('o valor de t e ')
            %display(t)
            %display('t divisivel por 10');
            %display(r);
            %display('sucetiveis ');
            %display(S(t));
            %display(S(t+1));
            %display('ds ');
            %display(dS);
            %display('I ');
            %display(I(t));
            %display('dI ');
            %display(dI);
            
        else
            S(t+1) = S(t) + dS;
            I(t+1) = I(t) + dI;  
        endif
        
        R(t+1) = R(t) + dR;
        V(t+1) = V(t) + dV;

    end
end