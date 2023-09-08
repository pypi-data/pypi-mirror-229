import numpy as np

# Equação de Stefan-boltsman
def sb(Temp, emissividade=0.95, tempo='s'):
    '''
    Docstring
    Emissividade de um corpo pela lei de Stefan-Boltsman
    Sintaxe: sb(Temperatura de um corpo em °C,
                Emissividade (padrão=0.95,
                Tempo de resposta(padrão= 's' instantaneo))
    '''
    if tempo=='s':
        const_sb=5.67e-8 # W/m2 (w= j/s) = Instantaneo
    else:
        const_sb = 4.903e-9 # Mj/m2dia
    conta= np.round(emissividade*const_sb*(Temp+273.15)**4,4) # round para DF ou varios valores devo usar o Numpy (trabalha com matrizes)
    return conta

# Calculando o comprimento de ondas pela lei de wien

def wien(temp):
    '''
    Lei de Wien
    Calcula o comprimento de onda de maxima frequencia em 
    função da temperatura de um corpo
    temp = temperatura de um corpo em °C
    Resposta em nanometros    
    '''
    return np.round(2893e3/(temp+273.15),4)

def graus(graus,minutos, segundos,hemisferio = 's'):
    '''
    Transforma Graus, minutos e segundos em GRAUS decimais!
    Padrão Hemisferio SUL = s
    '''
    calc_min = segundos/60
    calc_grau = (minutos+calc_min)/60
    if hemisferio =='s':
        sinal=-1
    else:
        sinal=1
    return np.round((graus+calc_grau)*sinal,4)

def corr(NDA):
    '''correção da distancia relativa da terra ao sol e função do dia juliano
    CORR = 1 + 0,033 cos (360 NDA / 365)''' # não usar graus, usar radianos
    return 1+0.033*np.cos(np.radians(360*NDA/365))
# Desafio Calcular o dia juliano ou o numero do dia do ano

def decli(NDA):
    '''
    decli =  declinação solar = 23,45 sen ((360/365).(NDA - 80))
    '''
    return 23.45*np.sin(np.radians((360/365)*(NDA-80)))

def ah (hora, min, seg):
    '''
    h = ângulo horário = (Hora local (décimos) - 12).15
    '''
    hora_calc = graus(hora, min, seg, hemisferio='n')
    return (hora_calc-12)*15
    
def cosz(latgrau, latmin, latseg, nda, hora, minuto, segundo, hemisferio='s'):
    '''
    cos Z = sen(LAT) sen(DECLI) + cos(LAT) cos(DECLI) cos ah'''
    lat_calc = graus(latgrau, latmin, latseg, hemisferio)
    decli_calc = decli(nda)
    ah_calc = ah(hora, minuto, segundo)
    cosz_calc = np.sin(np.radians(lat_calc)) * np.sin(np.radians(decli_calc)) + np.cos(np.radians(lat_calc)) * np.cos(np.radians(decli_calc)) * np.cos(np.radians(ah_calc))
    return cosz_calc

def iz(latitude,nda,hora):
    '''Irradiância solar global no topo da atmosfera instantanea
    iz = Jo.Corr.CosZ
    latitude em graus
    hora em decimos'''
    corr_calc = corr(nda)
    decli_calc = decli(nda)
    ah_calc = (hora-12)*15
    cosz_calc = np.sin(np.radians(latitude)) * np.sin(np.radians(decli_calc)) + np.cos(np.radians(latitude)) * np.cos(np.radians(decli_calc)) * np.cos(np.radians(ah_calc))
    return 1367*corr_calc*cosz_calc

def hn(latitude,nda):
    '''Retorna o angulo do nascer do sol
    hn = arcos(-tan(latitude)*tan(declinação))'''
    decli_calc = decli(nda)
    tan_lat = np.tan(np.radians(latitude))
    tan_decli = np.tan(np.radians(decli_calc))
    hnascer = np.degrees(np.arccos(-tan_lat*tan_decli))
    return hnascer

def Qo(latitude, nda):
    decli_calc = decli(nda)
    corr_calc   = corr(nda)
    hn_calc    = hn(latitude,nda)
    sen_lat    = np.sin(np.radians(latitude))
    sen_decli  = np.sin(np.radians(decli_calc))
    cos_lat    = np.cos(np.radians(latitude))
    cos_decli  = np.cos(np.radians(decli_calc))
    sen_hn     = np.sin(np.radians(hn_calc))
    qo_calc    = 37.6*corr_calc*((np.pi/180)*hn_calc*sen_lat*sen_decli+cos_lat*cos_decli*sen_hn)
    return qo_calc

def fotop(hn):
    '''Fotoperiodo
    hn= Ângulo na hora do nascer do sol já calculado'''
    return 2*hn/15

def Qg(latitude, nda, a, b, n):
    '''Calculando radiação global na superficie
    Equação de Angstron-Prescott
    Qg = Qo.(a+b.n/N)
    a,b = coeficientes de ajuste, sem unidade
    n = insolação (heliógrafo), horas
    N= fotoperiodo, horas'''
    qo_calc = Qo(latitude,nda)
    hn_calc = hn(latitude,nda)
    foto_calc = fotop(hn_calc)
    return qo_calc*(a+b*n/foto_calc)

def par_absorvida(latitude, nda, a, b, n, k, iaf):
    '''PARabs= (0.337 - 0,45. e**(k.IAF))*Qg'''
    qg_calc = Qg(latitude, nda, a, b, n)
    return (0.337 - 0.45 * np.exp(k*iaf))*qg_calc

def par_abs_pratica(latitude, nda, n, iaf,k=.95):
    '''PARabs= (0.337 - 0,45. e**(k.iaf))*Qg'''
    a = 0.29* np.cos(np.radians(latitude))
    b = 0.52
    qg_calc = Qg(latitude, nda, a, b, n)
    return (0.337 - 0.45 * np.exp(k*iaf))*qg_calc

def nda(day,month):
    day_mes = [0,31,28,31,30,31,30,31,31,30,31,30,31]
    s = 0
    for i in range(0,month):
        s = s+day_mes[i]
    return s + day