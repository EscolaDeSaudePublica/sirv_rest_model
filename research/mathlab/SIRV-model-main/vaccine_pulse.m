% pulse function for the vaccine
function u=vaccine_pulse(vaccine_number,vaccine_start_day,vaccine_end_day,T,dt,N)

u=(vaccine_number/N)*[zeros(1,vaccine_start_day/dt) ones(1,(vaccine_end_day-vaccine_start_day)/dt) zeros(1,(T-vaccine_end_day)/dt)];

end