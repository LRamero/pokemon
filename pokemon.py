import numpy as np
import random as rd
import pandas as pd
import math
import time

global log

def get_iv():
    # IV generados random [HP, Att, Def, Sp.Att, Sp.Def, Speed]
    iv = [rd.randrange(0, 31, 1), rd.randrange(0, 31, 1), rd.randrange(0, 31, 1), rd.randrange(0, 31, 1),
            rd.randrange(0, 31, 1), rd.randrange(0, 31, 1)]
    return iv

def get_ev():
    # EV generados random [HP, Att, Def, Sp.Att, Sp.Def, Speed]
    ev = [rd.randrange(0, 255, 1), rd.randrange(0, 255, 1), rd.randrange(0, 255, 1), rd.randrange(0, 255, 1),
            rd.randrange(0, 255, 1), rd.randrange(0, 255, 1)]
    if sum(ev) > 510:
        ev[:] = [math.floor(x/(sum(ev)/510)) for x in ev]
    return ev

def get_hp_eff(hp, iv_hp, ev_hp, nivel):
    hp_eff = math.floor(((2 * hp + iv_hp + (ev_hp/4)) * nivel)/100 + 10)
    return hp_eff

def get_stat_eff(stt, iv_stt, ev_stt, nivel, nat):
    stt_eff = math.floor((((2 * stt + iv_stt + (ev_stt/4)) * nivel)/100 + 5) * nat)
    return stt_eff

def unique_sorted_values(array):
    unique = array.unique().tolist()
    unique.sort()
    return unique

def unique_sorted_values_plus_NONE(array):
    NONE = 'NONE'
    unique = array.unique().tolist()
    unique.sort()
    unique.insert(0, NONE)
    return unique

def get_pds():
    url = 'https://drive.google.com/file/d/1NulAOMTMRPDzsfh9-DBMdiiPlKQWZoEH/view?usp=sharing'
    path = 'https://drive.google.com/uc?export=download&id=' + url.split('/')[-2]
    pk1 = pd.read_csv(path)
    pk1.rename(columns = {'Name':'Nombre', 'Species':'Especie', 'Variant':'Variante', 'Generation':'Generación', 'Rarity':'Rareza',
                        'Evolves_from':'Evoluciona de', 'Has_gender_diff':'Diferencia_género', 'Type1':'Tipo1', 'Type2':'Tipo2',
                        'HP':'Vida', 'Attack':'Ataque', 'Defense':'Defensa', 'Sp. Atk': 'Ataque esp', 'Sp. Def':'Defensa esp',
                        'Speed':'Velocidad', 'VGC2022_rules': 'Permiso VGC2022'}, inplace = True)
    pk2 = pk1[~(pk1['Nombre'].str.contains('Gigantamax'))]
    pk = pk2[~(pk2['Nombre'].str.contains('Mega'))]
    pk['Tipo2'] = pk['Tipo2'].fillna("Nada")
    pk.reset_index()

    ## Información sobre los distintos movimientos, tipo de ataque, tipo de daño, presición, etc.
    url = 'https://drive.google.com/file/d/10bN4zif5RYgSEtNByuorwvWnvqWmSKgv/view?usp=sharing'
    path = 'https://drive.google.com/uc?export=download&id=' + url.split('/')[-2]
    moves = pd.read_csv(path)
    moves['Power'] = moves['Power'].fillna(0)
    moves['Cant'] = moves['Cant'].fillna(0)
    moves['Cant'] = moves['Cant'].astype(str)
    moves['Acc.'] = moves['Acc.'].fillna(100)

    ## Información sobre la naturaleza del Pokemon y como afecta las estadísticas del mismo (incrementa o decrementa cada stat en 10%)
    url = 'https://drive.google.com/file/d/1af9KS4H6NkTCMPJBvXx70j9TDk12cfk9/view?usp=sharing'
    path = 'https://drive.google.com/uc?export=download&id=' + url.split('/')[-2]
    nat = pd.read_csv(path)
    
    ## Información sobre pokemones utilizados en conjunto en el mismo equipo
    url = 'https://drive.google.com/file/d/194RGr9hAuo3QTsg01Dnyw2MCAoBNeEvz/view?usp=sharing'
    path = 'https://drive.google.com/uc?export=download&id=' + url.split('/')[-2]
    pwp = pd.read_csv(path)
    pwp.rename(columns = {'Use_Percentage (%)':'Uso(%)', 'Pokemon':'Pokemon', 'Teammate':'Compañero'}, inplace = True)
    pwp['Uso(%)'] = pwp['Uso(%)'].apply(lambda x: x.replace("%", ""))
    pwp = pwp.astype({'Uso(%)': 'float64'})
    
    ## Efectividad de tipos
    url = 'https://drive.google.com/file/d/1MeRyRnwszQlp1HZegznslQash2pCAdcX/view?usp=sharing'
    path = 'https://drive.google.com/uc?export=download&id=' + url.split('/')[-2]
    eff = pd.read_csv(path)
    eff["Effectiveness"] = eff["Effectiveness"].apply(lambda x: 1 if str(x).find('Normal') != -1 else (0.5 if str(x).find('Not very') != -1 else (2 if str(x).find('Super-') != -1 else 0)))
    
    ## Movimientos que puede aprender un Pokemon
    url = 'https://drive.google.com/file/d/1sbpvpGnUYM6p4tJcWT3qEqyWUCZyvDNs/view?usp=sharing'
    path = 'https://drive.google.com/uc?export=download&id=' + url.split('/')[-2]
    m_learn = pd.read_csv(path)
    
    return pk, moves, nat, pwp, eff, m_learn

class Poke:
    def __init__(self, name):
        self.nombre = name
        self.nivel = 50
        self.iv = get_iv()
        self.ev = get_ev()
        self.natur = 'NONE'
        self.vida = get_hp_eff(int(pk[pk["Nombre"] == name]["Vida"].values), self.iv[0], self.ev[0], self.nivel)
        self.vida_inicial = get_hp_eff(int(pk[pk["Nombre"] == name]["Vida"].values), self.iv[0], self.ev[0], self.nivel)
        self.ataque = get_stat_eff(int(pk[pk["Nombre"] == name]["Ataque"].values), self.iv[1], self.ev[1], self.nivel, 1)
        self.defensa = get_stat_eff(int(pk[pk["Nombre"] == name]["Defensa"].values), self.iv[2], self.ev[2], self.nivel, 1)
        self.ataqueesp = get_stat_eff(int(pk[pk["Nombre"] == name]["Ataque esp"].values), self.iv[3], self.ev[3], self.nivel, 1)
        self.defensaesp = get_stat_eff(int(pk[pk["Nombre"] == name]["Defensa esp"].values), self.iv[4], self.ev[4], self.nivel, 1)
        self.velocidad = get_stat_eff(int(pk[pk["Nombre"] == name]["Velocidad"].values), self.iv[5], self.ev[5], self.nivel, 1)
        self.tipo1 = (pk[pk["Nombre"] == name]["Tipo1"].values)[0]
        self.tipo2 = (pk[pk["Nombre"] == name]["Tipo2"].values)[0]
        self.atk1 = None
        self.atk2 = None
        self.atk3 = None
        self.atk4 = None
        self.estado = []
        self.cont_turno = []
        self.var_respaldo = []
        # atk, def, spatk, spdef, spd, acc, ev
        self.stg = [0, 0, 0, 0, 0, 0, 0]
        
    def __str__(self):
        return f"""{self.nombre} HP:({self.vida}) Inicial:({self.vida_inicial})
        Atk:({self.ataque}) Def:({self.defensa})
        Sp.Atk:({self.ataqueesp}) Sp.Def:({self.defensaesp})
        Vel:({self.velocidad}) Estado: ({self.estado})
        Tipo1:({self.tipo1}) Tipo2:({self.tipo2})
        {self.atk1.nombre} Pot:({self.atk1.potencia})
        {self.atk2.nombre} Pot:({self.atk2.potencia})
        {self.atk3.nombre} Pot:({self.atk3.potencia})
        {self.atk4.nombre} Pot:({self.atk4.potencia})
        """
    
    def set_atk(self, name1, name2, name3, name4):
        self.atk1 = Atk(name1)
        self.atk2 = Atk(name2)
        self.atk3 = Atk(name3)
        self.atk4 = Atk(name4)
        
    def set_natur(self, natur):
        self.natur = natur
        nat_tmp = nat.copy()
        nat_tmp = nat_tmp.set_index('Nature')
        
        nat_p = nat_tmp.loc[natur]['Increases']
        nat_m = nat_tmp.loc[natur]['Decreases']
        
        nat_att = 1
        nat_def = 1
        nat_aesp = 1
        nat_desp = 1
        nat_vel = 1

        if (nat_p != 'NONE'):
            if (nat_p == 'Attack'):
                nat_att == 1.1
            elif (nat_p == 'Sp. Atk'):
                nat_aesp == 1.1
            elif (nat_p == 'Defense'):
                nat_def == 1.1
            elif (nat_p == 'Sp. Def'):
                nat_desp == 1.1
            elif (nat_p == 'Speed'):
                nat_vel == 1.1

        if (nat_m != 'NONE'):
            if (nat_m == 'Attack'):
                nat_att == 0.9
            elif (nat_m == 'Sp. Atk'):
                nat_aesp == 0.9
            elif (nat_m == 'Defense'):
                nat_def == 0.9
            elif (nat_m == 'Sp. Def'):
                nat_desp == 0.9
            elif (nat_m == 'Speed'):
                nat_vel == 0.9

        self.ataque = get_stat_eff(self.ataque, self.iv[1], self.ev[1], self.nivel, nat_att)
        self.defensa = get_stat_eff(self.defensa, self.iv[2], self.ev[2], self.nivel, nat_def)
        self.ataqueesp = get_stat_eff(self.ataqueesp, self.iv[3], self.ev[3], self.nivel, nat_aesp)
        self.defensaesp = get_stat_eff(self.defensaesp, self.iv[4], self.ev[4], self.nivel, nat_desp)
        self.velocidad = get_stat_eff(self.velocidad, self.iv[5], self.ev[5], self.nivel, nat_vel)

class Atk:
    def __init__(self, name):
        self.nombre = name
        self.potencia = int((moves[moves["Name"] == name]["Power"].values)[0])
        self.clase = (moves[moves["Name"] == name]["Damage_class"].values)[0]
        self.tipo = (moves[moves["Name"] == name]["Type"].values)[0]
        self.precision = 100 if (pd.isna((moves[moves["Name"] == name]["Acc."].values)[0]) or 
                                 (moves[moves["Name"] == name]["Acc."].values)[0] == '∞') else int((moves[moves["Name"] == name]["Acc."].values)[0])
        self.efecto = moves[moves["Name"] == name]["Effect"].values[0].replace(' ', '').split(",")
        if type(moves[moves["Name"] == name]["Prob. (%)"].values[0]) == str: 
            self.prob = moves[moves["Name"] == name]["Prob. (%)"].values[0].replace(' ', '').split("%") 
            self.prob = list(map(float, self.prob))
        else:
            self.prob = moves[moves["Name"] == name]["Prob. (%)"].values[0]
        if type(moves[moves["Name"] == name]["Cant"].values[0]) == str: 
            self.cant = moves[moves["Name"] == name]["Cant"].values[0].replace(' ', '').split("%") 
            self.cant = list(map(float, self.cant))
        else:
            self.cant = moves[moves["Name"] == name]["Cant"].values[0]
        
    def __str__(self):
        return f"""{self.nombre} Pot:({self.potencia}) Acc:({self.precision})
                    Clase:({self.clase}) Tipo:({self.tipo})
                    """
    
    def get_pot(self):
        return self.potencia
    
    def get_clase(self):
        return self.clase, self.tipo
    
    def get_precision(self):
        return self.precision
    
    def get_efecto(self):
        return self.efecto, self.prob

def atk_dano(att, deff, pot, acc, effi, stab, nivel, prob_c):
    
    ## att = ataque efectivo del Pokemon atacante
    ## deff = defensa efectiva del Pkemon contrincante
    ## pot = potencia del ataque utilizado
    ## acc = presición
    ## eff = eficacia del ataque por tipo
    ## stab = bonus por tipo de ataque igual a tipo de Pokemon
    ## nivel = nivel del Pokemon atacante
    
    values = [1, 1.5]
    critic = rd.choices(values, weights=(100-prob_c, prob_c), k=1)
    
    
    values2 = [1, 0]
    precis = rd.choices(values2, weights=(int(acc), (100 - int(acc))), k=1)
    
    var = (rd.randrange(85, 100, 1))/100
    
    dano = math.floor(((((((2 * nivel)/5)+2) * pot * (att/deff))/50) + 2) * critic[0] * effi * var * stab * precis[0])
    if critic[0] > 1:
        crit = True
    else:
        crit = False
    
    log.append("Golpea: " + str(dano))

    return dano, crit, precis[0]

def cambio_stats(pk_att, pk_def, atk):
    log.append("Cambio stats")
    tmp_stg = []
    efecto = atk.efecto
    cantidad = atk.cant
    prob = atk.prob
    
    if ("MAX_ATK" in efecto):
        pk_att.stg[0] = 6
        
    if ("SWITCH" in efecto):
        ind = efecto.index("SWITCH")
        tmp = prob[ind]
        if(rd.choices([1, 0], weights=(int(tmp), (100 - int(tmp))), k=1)):
            tmp_stg = pk_att.stg
            pk_att.stg = pk_def.stg
            pk_def.stg = tmp_stg
        
    if ("SWITCH_ST" in efecto):
        ind = efecto.index("SWITCH_ST")
        tmp = prob[ind]
        if(rd.choices([1, 0], weights=(int(tmp), (100 - int(tmp))), k=1)):
            tmp_stg = pk_att.stg
            pk_att.stg = pk_def.stg
            pk_def.stg = tmp_stg
    
    if "O_SPD" in efecto:
        ind = efecto.index("O_SPD")
        tmp = prob[ind]
        if(rd.choices([1, 0], weights=(int(tmp), (100 - int(tmp))), k=1)):        
            i = efecto.index('O_SPD')
            cant = int(cantidad[i])
            tmp = pk_def.stg[4]
            if tmp-cant < -6:
                pk_def.stg[4] = -6
            elif tmp-cant > 6:
                pk_def.stg[4] = 6
            else:
                pk_def.stg[4] = tmp-cant
    
    if "P_SPD" in efecto:
        ind = efecto.index("P_SPD")
        tmp = prob[ind]
        if(rd.choices([1, 0], weights=(int(tmp), (100 - int(tmp))), k=1)): 
            i = efecto.index('P_SPD')
            cant = int(cantidad[i])
            tmp = pk_att.stg[4]
            if tmp+cant < -6:
                pk_att.stg[4] = -6
            elif tmp+cant > 6:
                pk_att.stg[4] = 6
            else:
                pk_att.stg[4] = tmp+cant
            
    if "O_SPDEF" in efecto:
        ind = efecto.index("O_SPDEF")
        tmp = prob[ind]
        if(rd.choices([1, 0], weights=(int(tmp), (100 - int(tmp))), k=1)): 
            i = efecto.index('O_SPDEF')
            cant = int(cantidad[i])
            tmp = pk_def.stg[3]
            if tmp-cant < -6:
                pk_def.stg[3] = -6
            elif tmp-cant > 6:
                pk_def.stg[3] = 6
            else:
                pk_def.stg[3] = tmp-cant
    
    if "P_SPDEF" in efecto:
        ind = efecto.index("P_SPDEF")
        tmp = prob[ind]
        if(rd.choices([1, 0], weights=(int(tmp), (100 - int(tmp))), k=1)):
            i = efecto.index('P_SPDEF')
            cant = int(cantidad[i])
            tmp = pk_att.stg[3]
            if tmp+cant < -6:
                pk_att.stg[3] = -6
            elif tmp+cant > 6:
                pk_att.stg[3] = 6
            else:
                pk_att.stg[3] = tmp+cant
        
    if "O_DEF" in efecto:
        ind = efecto.index("O_DEF")
        tmp = prob[ind]
        if(rd.choices([1, 0], weights=(int(tmp), (100 - int(tmp))), k=1)):
            i = efecto.index('O_DEF')
            cant = int(cantidad[i])
            tmp = pk_def.stg[1]
            if tmp-cant < -6:
                pk_def.stg[1] = -6
            elif tmp-cant > 6:
                pk_def.stg[1] = 6
            else:
                pk_def.stg[1] = tmp-cant
    
    if "P_DEF" in efecto:
        ind = efecto.index("P_DEF")
        tmp = prob[ind]
        if(rd.choices([1, 0], weights=(int(tmp), (100 - int(tmp))), k=1)):
            i = efecto.index('P_DEF')
            cant = int(cantidad[i])
            tmp = pk_att.stg[1]
            if tmp+cant < -6:
                pk_att.stg[1] = -6
            elif tmp+cant > 6:
                pk_att.stg[1] = 6
            else:
                pk_att.stg[1] = tmp+cant

    if "O_ATK" in efecto:
        ind = efecto.index("O_ATK")
        tmp = prob[ind]
        if(rd.choices([1, 0], weights=(int(tmp), (100 - int(tmp))), k=1)):
            i = efecto.index('O_ATK')
            cant = int(cantidad[i])
            tmp = pk_def.stg[0]
            if tmp-cant < -6:
                pk_def.stg[0] = -6
            elif tmp-cant > 6:
                pk_def.stg[0] = 6
            else:
                pk_def.stg[0] = tmp-cant
    
    if "P_ATK" in efecto:
        ind = efecto.index("P_ATK")
        tmp = prob[ind]
        if(rd.choices([1, 0], weights=(int(tmp), (100 - int(tmp))), k=1)):
            i = efecto.index('P_ATK')
            cant = int(cantidad[i])
            tmp = pk_att.stg[0]
            if tmp+cant < -6:
                pk_att.stg[0] = -6
            elif tmp+cant > 6:
                pk_att.stg[0] = 6
            else:
                pk_att.stg[0] = tmp+cant
            
    if "O_SPATK" in efecto:
        ind = efecto.index("O_SPATK")
        tmp = prob[ind]
        if(rd.choices([1, 0], weights=(int(tmp), (100 - int(tmp))), k=1)):
            i = efecto.index('O_SPATK')
            cant = int(cantidad[i])
            tmp = pk_def.stg[2]
            if tmp-cant < -6:
                pk_def.stg[2] = -6
            elif tmp-cant > 6:
                pk_def.stg[2] = 6
            else:
                pk_def.stg[2] = tmp-cant
    
    if "P_SPATK" in efecto:
        ind = efecto.index("P_SPATK")
        tmp = prob[ind]
        if(rd.choices([1, 0], weights=(int(tmp), (100 - int(tmp))), k=1)):
            i = efecto.index('P_SPATK')
            cant = int(cantidad[i])
            tmp = pk_att.stg[2]
            if tmp+cant < -6:
                pk_att.stg[2] = -6
            elif tmp+cant > 6:
                pk_att.stg[2] = 6
            else:
                pk_att.stg[2] = tmp+cant
            
    if "O_ACC" in efecto:
        ind = efecto.index("O_ACC")
        tmp = prob[ind]
        if(rd.choices([1, 0], weights=(int(tmp), (100 - int(tmp))), k=1)):
            i = efecto.index('O_ACC')
            cant = int(cantidad[i])
            tmp = pk_def.stg[5]
            if tmp-cant < -6:
                pk_def.stg[5] = -6
            elif tmp-cant > 6:
                pk_def.stg[5] = 6
            else:
                pk_def.stg[5] = tmp-cant
    
    if "P_ACC" in efecto:
        ind = efecto.index("P_ACC")
        tmp = prob[ind]
        if(rd.choices([1, 0], weights=(int(tmp), (100 - int(tmp))), k=1)):
            i = efecto.index('P_ACC')
            cant = int(cantidad[i])
            tmp = pk_att.stg[5]
            if tmp+cant < -6:
                pk_att.stg[5] = -6
            elif tmp+cant > 6:
                pk_att.stg[5] = 6
            else:
                pk_att.stg[5] = tmp+cant
            
    if "O_EV" in efecto:
        ind = efecto.index("O_EV")
        tmp = prob[ind]
        if(rd.choices([1, 0], weights=(int(tmp), (100 - int(tmp))), k=1)):
            i = efecto.index('O_EV')
            cant = int(cantidad[i])
            tmp = pk_def.stg[6]
            if tmp-cant < -6:
                pk_def.stg[6] = -6
            elif tmp-cant > 6:
                pk_def.stg[6] = 6
            else:
                pk_def.stg[6] = tmp-cant
    
    if "P_EV" in efecto:
        ind = efecto.index("P_EV")
        tmp = prob[ind]
        if(rd.choices([1, 0], weights=(int(tmp), (100 - int(tmp))), k=1)):
            i = efecto.index('P_EV')
            cant = int(cantidad[i])
            tmp = pk_att.stg[6]
            if tmp+cant < -6:
                pk_att.stg[6] = -6
            elif tmp+cant > 6:
                pk_att.stg[6] = 6
            else:
                pk_att.stg[6] = tmp+cant
        
    if "O_RND" in efecto:
        ind = efecto.index("O_RND")
        tmp = prob[ind]
        if(rd.choices([1, 0], weights=(int(tmp), (100 - int(tmp))), k=1)):
            st = rd.randrange(0, 6, 1)
            i = efecto.index('O_RND')
            cant = int(cantidad[i])
            tmp = pk_def.stg[st]
            if tmp-cant < -6:
                pk_def.stg[st] = -6
            elif tmp-cant > 6:
                pk_def.stg[st] = 6
            else:
                pk_def.stg[st] = tmp-cant
    
    if "P_RND" in efecto:
        ind = efecto.index("P_RND")
        tmp = prob[ind]
        if(rd.choices([1, 0], weights=(int(tmp), (100 - int(tmp))), k=1)):
            st = rd.randrange(0, 6, 1)
            i = efecto.index('P_RND')
            cant = int(cantidad[i])
            tmp = pk_att.stg[st]
            if tmp+cant < -6:
                pk_att.stg[st] = -6
            elif tmp+cant > 6:
                pk_att.stg[st] = 6
            else:
                pk_att.stg[st] = tmp+cant
    
    if "O_ALL" in efecto:
        ind = efecto.index("O_ALL")
        tmp = prob[ind]
        if(rd.choices([1, 0], weights=(int(tmp), (100 - int(tmp))), k=1)):
            i = efecto.index('O_ALL')
            cant = int(cantidad[i])
            for st in range(0,7):
                tmp = pk_def.stg[st]
                if tmp-cant < -6:
                    pk_def.stg[st] = -6
                elif tmp-cant > 6:
                    pk_def.stg[st] = 6
                else:
                    pk_def.stg[st] = tmp-cant
    
    if "P_ALL" in efecto:
        ind = efecto.index("P_ALL")
        tmp = prob[ind]
        if(rd.choices([1, 0], weights=(int(tmp), (100 - int(tmp))), k=1)):
            i = efecto.index('P_ALL')
            cant = int(cantidad[i])
            for st in range(0,7):
                tmp = pk_att.stg[st]
                if tmp+cant < -6:
                    pk_att.stg[st] = -6
                elif tmp+cant > 6:
                    pk_att.stg[st] = 6
                else:
                    pk_att.stg[st] = tmp+cant
    
    if "RESET" in efecto:
        ind = efecto.index("RESET")
        tmp = prob[ind]
        if(rd.choices([1, 0], weights=(int(tmp), (100 - int(tmp))), k=1)):
            for st in range(0,7):
                pk_att.stg[st] = 0
            for st in range(0,7):
                pk_def.stg[st] = 0
            
    if "O_STATES_DEL" in efecto:
        ind = efecto.index("O_STATES_DEL")
        tmp = prob[ind]
        if(rd.choices([1, 0], weights=(int(tmp), (100 - int(tmp))), k=1)):
            for st in range(0,7):
                pk_def.stg[st] = 0
            
    if "COP_STATS" in efecto:
        ind = efecto.index("COP_STATS")
        tmp = prob[ind]
        if(rd.choices([1, 0], weights=(int(tmp), (100 - int(tmp))), k=1)):
            for st in range(0,7):
                if pk_def.stg[st] > 0:
                    pk_att.stg[st] = pk_def.stg[st]
            
def dano_estado(pk):
    estado = pk.estado
    tmp = 1
    pego = 0
    
    if "POIS" in estado:
        pk.vida -= (pk.vida_inicial)/8
        pego = 1
    
    if "BAD_POIS" in estado:
        if ~("bd_po" in pk.var_respaldo):
            pk.var_respaldo.append("bd_po")
            pk.var_respaldo.append(1)
        else:
            ind = pk.var_respaldo.index("bd_po")
            tmp = pk.var_respaldo[ind+1]
            pk.var_respaldo[ind+1] = tmp+1
        pk.vida -= tmp*((pk.vida_inicial)/16)
        pego = 1
    
    if "BURN" in estado:
        pk.vida -= (pk.vida_inicial)/16
        pego = 1
    
    if pego:
        log.append("Daño por estado: " + ' '.join(map(str, pk.estado)))
    
def cambio_estado(pk_att, pk_def, atk):
    o_estados = ["POIS", "BAD_POIS", "BURN", "FREEZ", "RETRO", "PARAL", "CONF"]
    p_estados = ["HEALING", "ATK_RED", "SPATK_RED"]
    efecto = atk.efecto
    prob = atk.prob
    
    for valor in o_estados:
        if valor in efecto:
            ind = efecto.index(valor)
            tmp = prob[ind]
            if(rd.choices([1, 0], weights=(int(tmp), (100 - int(tmp))), k=1)):
                pk_def.estado.append(valor)
                
    for valor in p_estados:
        if valor in efecto:
            ind = efecto.index(valor)
            tmp = prob[ind]
            if(rd.choices([1, 0], weights=(int(tmp), (100 - int(tmp))), k=1)):
                pk_att.estado.append(valor)
    
    if "AATK_RED" in efecto:
        ind = efecto.index("AATK_RED")
        tmp = prob[ind]
        if(rd.choices([1, 0], weights=(int(tmp), (100 - int(tmp))), k=1)):
            pk_def.estado.append("AATK_RED")
            pk_def.var_respaldo.append("atkred_count")
            pk_def.var_respaldo.append(5)
    
    if "SLEEP" in efecto:
        ind = efecto.index("SLEEP")
        tmp = prob[ind]
        if(rd.choices([1, 0], weights=(int(tmp), (100 - int(tmp))), k=1)):
            pk_def.estado.append("SLEEP")
            pk_def.var_respaldo.append("sl_count")
            pk_def.var_respaldo.append(rd.randrange(1, 3, 1))
    
    if "A_BURN" in efecto:
        ind = efecto.index("A_BURN")
        tmp = prob[ind]
        if(rd.choices([1, 0], weights=(int(tmp), (100 - int(tmp))), k=1)):
            pk_att.estado.append("BURN")
    if "A_RETRO" in efecto:
        ind = efecto.index("A_RETRO")
        tmp = prob[ind]
        if(rd.choices([1, 0], weights=(int(tmp), (100 - int(tmp))), k=1)):
            pk_att.estado.append("RETRO")
    if "A_SLEEP" in efecto:
        ind = efecto.index("A_SLEEP")
        tmp = prob[ind]
        if(rd.choices([1, 0], weights=(int(tmp), (100 - int(tmp))), k=1)):
            pk_att.estado.append("SLEEP")
        
    if "CURE" in efecto:
        pk_att.estado = []
        if "bd_po" in pk_att.var_respaldo:
            ind = pk_att.var_respaldo.index("bd_po")
            pk_att.var_respaldo.pop(ind+1)
            pk_att.var_respaldo.pop(ind)
        if "sl_count" in pk_att.var_respaldo:
            ind = pk_att.var_respaldo.index("sl_count")
            pk_att.var_respaldo.pop(ind+1)
            pk_att.var_respaldo.pop(ind)
        if "atkred_count" in pk_att.var_respaldo:
            ind = pk_att.var_respaldo.index("atkred_count")
            pk_att.var_respaldo.pop(ind+1)
            pk_att.var_respaldo.pop(ind)
    
    if "TRANSFER_STAT" in efecto:
        t_estados = ["BURN", "PARAL", "POIS", "SLEEP"]
        for valor in t_estados:
            if valor in pk_att.estado:
                ind = pk_att.estado.index(valor)
                pk_att.estado.pop(ind)
                pk_def.estado.append(valor)
    
    if "ESPERA" in efecto:
        pk_att.estado.append("ESPERA")
    if "RECARGA" in efecto:
        pk_att.estado.append("RECARGA")
    if "NO_CRIT" in efecto:
        pk_att.estado.append("NO_CRIT")
    if "N_PROB" in efecto:
        pk_att.estado.append("N_PROB")
        
def ataque(pk_att, pk_def, atk, eff, pr):
    log.append("Ataque con " + atk.nombre)
    rpt = 0
    dano = 0
    if "NO_CRIT" in pk_def.estado:
        pk_def.estado.remove("NO_CRIT")
        prob_c = 0
    elif "CRIT" in atk.efecto:
        prob_c = 100
    else:
        prob_c = 5
        
    if pk_att.tipo1 == atk.tipo:
        stab = 1.5
    else:
        stab = 1
    
    if ~("ST_IGN" in atk.efecto):
        if atk.clase == "Physical":
            att_type = "Phy"

            stg_atk = ((2 + abs(pk_att.stg[0]))/2)**(pk_att.stg[0]/abs(pk_att.stg[0]) if pk_att.stg[0] != 0 else 1)
            stg_deff = ((2 + abs(pk_def.stg[1]))/2)**(pk_def.stg[1]/abs(pk_def.stg[1]) if pk_def.stg[1] != 0 else 1)
        else:
            att_type = "Sp"

            stg_atk = ((2 + abs(pk_att.stg[2]))/2)**(pk_att.stg[2]/abs(pk_att.stg[2]) if pk_att.stg[2] != 0 else 1)
            stg_deff = ((2 + abs(pk_def.stg[3]))/2)**(pk_def.stg[3]/abs(pk_def.stg[3]) if pk_def.stg[3] != 0 else 1)

        acc = atk.precision
        prec = ((3 + abs(pk_att.stg[5]))/3)**(pk_att.stg[5]/abs(pk_att.stg[5]) if pk_att.stg[5] != 0 else 1)
        eva = ((3 + abs(pk_def.stg[6]))/3)**(pk_def.stg[6]/abs(pk_def.stg[6]) if pk_def.stg[6] != 0 else 1)
        if ("PROB" in atk.efecto):
            acc = 1
        elif ("N_PROB" in pk_att.estado):
            acc = 1
            pk_att.estado.remove("N_PROB")
        else:
            acc = acc * (prec/eva)
    else:
        stg_atk = 1
        stg_deff = 1
        acc = 1
    
    if "BURN" in pk_att.estado:
        burn = 0.5
    else:
        burn = 1
    
    if ("REPEAT" in atk.efecto) or ("MULTIPLE" in atk.efecto):
        if ("REPEAT" in atk.efecto):
            ind = atk.efecto.index("REPEAT")
        else:
            ind = atk.efecto.index("MULTIPLE")
        rep = atk.cant[ind]
        cant_golpe = rd.randrange(1, rep)
    else:
        cant_golpe = 1
        
    
    while rpt < cant_golpe:
        if pr == 1:
            if att_type == "Phy":
                dano1, crit, precis = atk_dano((pk_att.ataque * stg_atk * burn), (pk_def.defensa * stg_deff),
                                              atk.potencia, atk.precision, eff, stab, pk_att.nivel, prob_c)
            else:
                dano1, crit, precis = atk_dano((pk_att.ataqueesp * stg_atk), (pk_def.defensaesp * stg_deff),
                                              atk.potencia, acc, eff, stab, pk_att.nivel, prob_c)
            dano += dano1
            
            cambio_stats(pk_att, pk_def, atk)
            cambio_estado(pk_att, pk_def, atk)

            if("ABSORB" in atk.efecto):
                if ((pk_att.vida + dano/2) >= pk_att.vida_inicial):
                    pk_att.vida = pk_att.vida_inicial
                else:
                    pk_att.vida += dano/2

            if("HEAL" in atk.efecto):
                ind = atk.efecto.index("HEAL")
                tmp = atk.cant[ind]
                log.append(pk_att.nombre + " se curó " + str(pk_att.vida_inicial*(tmp/100)))
                if ((pk_att.vida + pk_att.vida_inicial*(tmp/100)) >= pk_att.vida_inicial):
                    pk_att.vida = pk_att.vida_inicial
                else:
                    pk_att.vida += pk_att.vida_inicial*(tmp/100)

            if ("RECOIL" in atk.efecto):
                ind = atk.efecto.index("RECOIL")
                tmp = atk.cant[ind]
                if (pk_def.vida - dano > 0):
                    pk_att.vida -= dano*tmp

            if ("RECOIL_HP" in atk.efecto):
                ind = atk.efecto.index("RECOIL_HP")
                tmp = atk.cant[ind]
                if (pk_def.vida - dano > 0):
                    pk_att.vida -= pk_att.vida_inicial*tmp

            if ("AUT_DANO" in atk.efecto):
                if (pk_def.vida - dano > 0):
                    pk_att.vida -= pk_att.vida_inicial*0.5

            if ("SAME_HP" in atk.efecto):
                if pk_def.vida > pk_att.vida:
                    pk_def.vida = pk_att.vida

            if ("SACRIFICIO" in atk.efecto):
                dano = pk_att.vida
                if (pk_def.vida - dano > 0):
                    pk_att.vida = 0

            if ("HP_HALF" in atk.efecto):
                dano = round((pk_def.vida/2)+0.1, 0)

            if ("DMG_LVL" in atk.efecto):
                tmp = rd.randrange(5, 15)
                dano = pk_att.nivel*(tmp/10)

            if ("ATK_RED" in pk_def.estado) & (atk.clase == "Physical"):
                pk_def.estado.remove("ATK_RED")            
                dano = dano * 0.5

            if ("SPATK_RED" in pk_def.estado) & (atk.clase == "Special"):
                pk_def.estado.remove("SPATK_RED")            
                dano = dano * 0.5

            if ("AATK_RED" in pk_def.estado):
                ind = pk_def.var_respaldo.index("atkred_count")
                pk_def.var_respaldo[ind+1] -= 1
                if pk_def.var_respaldo[ind+1] == 0:
                    pk_def.estado.remove("AATK_RED")
                    pk_def.var_respaldo.pop(ind+1)
                    pk_def.var_respaldo.pop(ind)           
                dano = dano * 0.5
            
            if ("ATK_SEGURO" in atk.efecto):
                dano = atk.potencia
            
            if ("RECOMPENSA" in atk.efecto):
                mejora = 0
                for st in pk_att.stg:
                    if st > 0:
                        mejora += st
                dano = 20*mejora
            
            if ("RND_DMG" in atk.efecto):
                pp = [10, 30, 50, 70, 90, 110, 150]
                mu, sigma = 3, (6 - 0) / 6 # media 3 y desviación estándar para que los valores estén entre 0 y 6
                ind = np.random.normal(mu, sigma)
                dano = pp[round(ind)]
            
            if ("MEMENTO" in atk.efecto):
                pk_att.vida = 0
                
            if ("KILLER" in atk.efecto):
                if pk_att.velocidad >= pk_def.velocidad:
                    dano = pk_def.vida
                else:
                    dano = 0
                    precis = 0
            
            if ("PETALO" in atk.efecto):
                if ~("CARGA" in pk_att.estado):
                    pk_att.estado.append("CARGA")
                    pk_att.var_respaldo.append("carga")
                    pk_att.var_respaldo.append(dano)
                    pk_att.var_respaldo.append(2)
                
            if ("DOBLE_CONF" in atk.efecto):
                if ~("CARGA_C" in pk_att.estado):
                    pk_att.estado.append("CARGA_C")
                    pk_att.var_respaldo.append("carga")
                    pk_att.var_respaldo.append(dano)
                    pk_att.var_respaldo.append(2)
            
            if ("CARGA" in atk.efecto):
                if ~("CARGA" in pk_att.estado):
                    pk_att.estado.append("CARGA")
                    pk_att.var_respaldo.append("carga")
                    pk_att.var_respaldo.append(dano)
                    pk_att.var_respaldo.append(4)
                
            if ("CARGA" in pk_att.estado) or ("CARGA_C" in pk_att.estado):
                ind = pk_att.var_respaldo.index("carga")
                cont = pk_att.var_respaldo[ind+2] - 1
                pk_att.var_respaldo[ind+2] = cont
                dano = pk_att.var_respaldo[ind+1]
                if cont <= 0:
                    pk_att.var_respaldo.pop(ind+2)
                    pk_att.var_respaldo.pop(ind+1)
                    pk_att.var_respaldo.pop(ind)
                    if "CARGA_C" in pk_att.estado:
                        pk_att.estado.remove("CARGA_C")
                        pk_att.estado.append("CONF")
                    else:
                        pk_att.estado.remove("CARGA")

        else:
            dano = 0
            crit = 0
            precis = 0
        
        rpt += 1

    return dano, crit, precis

def check_estado(pk_r, atk_r, pk_a, atk_a):
    if (("PROTECT" in atk_a.efecto) | ("FREEZ" in pk_r.estado) | ("RECARGA" in pk_r.estado) | 
        ("RETRO" in pk_r.estado) | ("SLEEP" in pk_r.estado) | ("ESPERA" in pk_r.estado)):
        if ("RECARGA" in pk_r.estado):
            pk_r.estado.remove("RECARGA")
        if ("RETRO" in pk_r.estado):
            pk_r.estado.remove("RETRO")
        if ("ESPERA" in pk_r.estado):
            pk_r.estado.remove("ESPERA")
        if ("SLEEP" in pk_r.estado):
            ind = pk_r.var_respaldo.index("sl_count")
            pk_r.var_respaldo[ind+1] -= 1
            if pk_r.var_respaldo[ind+1] == 0:
                pk_r.estado.remove("SLEEP")
                pk_r.var_respaldo.pop(ind+1)
                pk_r.var_respaldo.pop(ind)
        pr_r = 0
    else:
        pr_r = 1

    if (("PROTECT" in atk_r.efecto) | ("FREEZ" in pk_a.estado) | ("RECARGA" in pk_a.estado) | 
        ("RETRO" in pk_a.estado) | ("SLEEP" in pk_a.estado) | ("ESPERA" in pk_a.estado)):
        if ("RECARGA" in pk_a.estado):
            pk_a.estado.remove("RECARGA")
        if ("RETRO" in pk_a.estado):
            pk_a.estado.remove("RETRO")
        if ("ESPERA" in pk_a.estado):
            pk_a.estado.remove("ESPERA")
        if ("SLEEP" in pk_a.estado):
            ind = pk_a.var_respaldo.index("sl_count")
            pk_a.var_respaldo[ind+1] -= 1
            if pk_a.var_respaldo[ind+1] == 0:
                pk_a.estado.remove("SLEEP")
                pk_a.var_respaldo.pop(ind+1)
                pk_a.var_respaldo.pop(ind)
        pr_a = 0
    else:
        pr_a = 1

    if ("CURE" in atk_a.efecto):
        cambio_estado(pk_a, pk_r, atk_a)

    if ("CURE" in atk_r.efecto):
        cambio_estado(pk_r, pk_a, atk_r)

    if ("PARAL" in pk_r.estado):
        par_r = 0.5
        values2 = [pr_r, 0]
        pr_r = rd.choices(values2, weights=(75, 25), k=1)
    else:
        par_r = 1
    if ("PARAL" in pk_a.estado):
        par_a = 0.5
        values2 = [pr_a, 0]
        pr_a = rd.choices(values2, weights=(75, 25), k=1)
    else:
        par_a = 0
    
    return par_a, pr_a, par_r, pr_r


def combate(pk_r, pk_a):
    log.append("Combate entre " + pk_r.nombre + " y " + pk_a.nombre)
    while ((pk_r.vida > 0) and (pk_a.vida) > 0):
        
        if("HEALING" in pk_a.estado):
            log.append(pk_a.nombre + " se curó " + str(pk_a.vida_inicial/16))
            if ((pk_a.vida + pk_a.vida_inicial/16) >= pk_a.vida_inicial):
                pk_a.vida = pk_a.vida_inicial
            else:
                pk_a.vida += pk_a.vida_inicial/16
                
        if("HEALING" in pk_r.estado):
            log.append(pk_r.nombre + " se curó " + str(pk_r.vida_inicial/16))
            if ((pk_r.vida + pk_r.vida_inicial/16) >= pk_r.vida_inicial):
                pk_r.vida = pk_r.vida_inicial
            else:
                pk_r.vida += pk_r.vida_inicial/16
        
        #Define de forma aleatoria el ataque a utilizar
        atkr = rd.randrange(1, 4)
        atka = rd.randrange(1, 4)
        
        if (atkr == 1):
            atk_r = pk_r.atk1
        elif (atkr == 2):
            atk_r = pk_r.atk2
        elif (atkr == 3):
            atk_r = pk_r.atk3
        else:
            atk_r = pk_r.atk4
        
        if (atka == 1):
            atk_a = pk_a.atk1
        elif (atka == 2):
            atk_a = pk_r.atk2
        elif (atka == 3):
            atk_a = pk_a.atk3
        else:
            atk_a = pk_a.atk4

        #Calcula efectividad del ataque por tipo
        eff1 = eff[eff["Atk. Move Type"] == atk_r.tipo]
        eff2 = eff[eff["Atk. Move Type"] == atk_a.tipo]
        
        par_a, pr_a, par_r, pr_r = check_estado(pk_r, atk_r, pk_a, atk_a)
            
        if ("CONF" in pk_r.estado):
            values2 = [1, 0]
            conf = rd.choices(values2, weights=(33, 67), k=1)
            if conf:
                p_d = Atk("Pay Day")
                dano, crit, precis = ataque(pk_r, pk_r, p_d, 1, 1)
                pk_r.vida -= dano
                pr_r = 0
                if pk_r.vida < 1:
                    break
        if ("CONF" in pk_a.estado):
            values2 = [1, 0]
            conf = rd.choices(values2, weights=(33, 67), k=1)
            if conf:
                p_d = Atk("Pay Day")
                dano, crit, precis = ataque(pk_a, pk_a, p_d, 1, 1)
                pk_a.vida -= dano
                pr_a = 0
                if pk_r.vida < 1:
                    break  
        

        if pk_a.tipo2 == 'Nada':
            effi_r = float((eff1[eff1["Def. Pokemon Type"] == pk_a.tipo1])["Effectiveness"].values[0])
        else:
            effi_r = float((eff1[eff1["Def. Pokemon Type"] == pk_a.tipo1])["Effectiveness"].values[0]) * float(
                (eff1[eff1["Def. Pokemon Type"] == pk_a.tipo2])["Effectiveness"].values[0])
        if pk_r.tipo2 == 'Nada':
            effi_a = float((eff2[eff2["Def. Pokemon Type"] == pk_r.tipo1])["Effectiveness"].values[0])
        else:
            effi_a = float((eff2[eff2["Def. Pokemon Type"] == pk_r.tipo1])["Effectiveness"].values[0]) * float(
                (eff2[eff2["Def. Pokemon Type"] == pk_r.tipo2])["Effectiveness"].values[0])
        
        ##Ajusta la velocidad con el modificador correspondiente
        spd_stg1 = ((2 + abs(pk_r.stg[4]))/2)**(pk_r.stg[4]/abs(pk_r.stg[4]) if pk_r.stg[4] != 0 else 1)
        spd_stg2 = ((2 + abs(pk_a.stg[4]))/2)**(pk_a.stg[4]/abs(pk_a.stg[4]) if pk_a.stg[4] != 0 else 1)
        
        spd_r = (pk_r.velocidad * spd_stg1 * par_r)
        spd_a = (pk_a.velocidad * spd_stg2 * par_a)
        
        if (("M_PRIOR" in atk_r.efecto) or ("D_PRIOR" in pk_r.estado)) and not(
            ("M_PRIOR" in atk_a.efecto) or ("D_PRIOR" in pk_a.estado)):
            if ("D_PRIOR" in pk_r.estado):
                pk_r.estado.remove("D_PRIOR")
            dano_estado(pk_r)
            if pk_r.vida < 1:
                break
            dano, crit, precis = ataque(pk_r, pk_a, atk_r, effi_r, pr_r)
            par_a, pr_a, par_b, pr_b = check_estado(pk_r, atk_r, pk_a, atk_a)
            pk_a.vida -= dano
            if pk_a.vida < 1:
                break
            dano_estado(pk_a)
            if pk_a.vida < 1:
                break
            dano, crit, precis = ataque(pk_a, pk_r, atk_a, effi_a, pr_a)
            if ("DOB_ATK" in atk_a.efecto):
                dano += dano
            pk_r.vida -= dano
        
        elif (("M_PRIOR" in atk_a.efecto) or ("D_PRIOR" in pk_a.estado)) and not(
            ("M_PRIOR" in atk_r.efecto) or ("D_PRIOR" in pk_r.estado)):
            if ("D_PRIOR" in pk_a.estado):
                pk_a.estado.remove("D_PRIOR")
            dano_estado(pk_a)
            if pk_a.vida < 1:
                break
            dano, crit, precis = ataque(pk_a, pk_r, atk_a, effi_a, pr_a)
            par_a, pr_a, par_b, pr_b = check_estado(pk_r, atk_r, pk_a, atk_a)
            pk_r.vida -= dano
            if pk_r.vida < 1:
                break
            dano_estado(pk_r)
            if pk_r.vida < 1:
                break
            dano, crit, precis = ataque(pk_r, pk_a, atk_r, effi_r, pr_r)
            if ("DOB_ATK" in atk_r.efecto):
                dano += dano
            pk_a.vida -= dano
        
        elif ("M_DPRIOR" in atk_r.efecto):
            dano, crit, precis = ataque(pk_a, pk_r, atk_a, effi_a, pr_a)
            par_a, pr_a, par_b, pr_b = check_estado(pk_r, atk_r, pk_a, atk_a)
            dano_estado(pk_a)
            if pk_a.vida < 1:
                break
            pk_r.vida -= dano
            if pk_r.vida < 1:
                break
            dano_estado(pk_r)
            if pk_r.vida < 1:
                break
            dano, crit, precis = ataque(pk_r, pk_a, atk_r, effi_r, pr_r)
            if ("DOB_ATK" in atk_r.efecto):
                dano += dano
            pk_a.vida -= dano
            
        elif ("M_DPRIOR" in atk_a.efecto):
            dano_estado(pk_r)
            if pk_r.vida < 1:
                break
            dano, crit, precis = ataque(pk_r, pk_a, atk_r, effi_r, pr_r)
            par_a, pr_a, par_b, pr_b = check_estado(pk_r, atk_r, pk_a, atk_a)
            pk_a.vida -= dano
            if pk_a.vida < 1:
                break
            dano_estado(pk_a)
            if pk_a.vida < 1:
                break
            dano, crit, precis = ataque(pk_a, pk_r, atk_a, effi_a, pr_a)
            if ("DOB_ATK" in atk_a.efecto):
                dano += dano
            pk_r.vida -= dano
        
        elif (spd_r > spd_a):
            if ("D_PRIOR" in pk_r.estado):
                pk_r.estado.remove("D_PRIOR")
            if ("D_PRIOR" in atk_r.efecto):
                pk_r.estado.append("D_PRIOR")
            if ("D_PRIOR" in atk_a.efecto):
                pk_a.estado.append("D_PRIOR")
            dano_estado(pk_r)
            if pk_r.vida < 1:
                break
            dano, crit, precis = ataque(pk_r, pk_a, atk_r, effi_r, pr_r)
            par_a, pr_a, par_b, pr_b = check_estado(pk_r, atk_r, pk_a, atk_a)
            pk_a.vida -= dano
            if pk_a.vida < 1:
                break
            dano_estado(pk_a)
            if pk_a.vida < 1:
                break
            dano, crit, precis = ataque(pk_a, pk_r, atk_a, effi_a, pr_a)
            if ("DOB_ATK" in atk_a.efecto):
                dano += dano
            pk_r.vida -= dano
            
        else:
            if ("D_PRIOR" in pk_r.estado):
                pk_r.estado.remove("D_PRIOR")
            if ("D_PRIOR" in atk_r.efecto):
                pk_r.estado.append("D_PRIOR")
            if ("D_PRIOR" in atk_a.efecto):
                pk_a.estado.append("D_PRIOR")
            dano_estado(pk_a)
            if pk_a.vida < 1:
                break
            dano, crit, precis = ataque(pk_a, pk_r, atk_a, effi_a, pr_a)
            par_a, pr_a, par_b, pr_b = check_estado(pk_r, atk_r, pk_a, atk_a)
            pk_r.vida -= dano
            if pk_r.vida < 1:
                break
            dano_estado(pk_r)
            if pk_r.vida < 1:
                break
            dano, crit, precis = ataque(pk_r, pk_a, atk_r, effi_r, pr_r)
            if ("DOB_ATK" in atk_r.efecto):
                dano += dano
            pk_a.vida -= dano
            
        if len(log) > 500000:
            if pk_a.vida > pk_r.vida:
                pk_r.vida = 0
            else:
                pk_a.vida = 0
            
    
    if pk_r.vida < 1:
        winner = pk_a
        loser = pk_r
    if pk_a.vida < 1:
        winner = pk_r
        loser = pk_a
        
    return winner, loser

def main():
    pk, moves, nat, pwp, eff, m_learn = get_pds()

    combat = pd.DataFrame()

    print('Inicio proceso')
    for i in range(1):
        log = []
        
        #Elige al azar cada Pokemon, su naturaleza y los ataques que utilizará
        pok_r = Poke(pk['Nombre'].iloc[rd.randrange(0, len(pk)-1, 1)])
        pok_a = Poke(pk['Nombre'].iloc[rd.randrange(0, len(pk)-1, 1)])
        
        while(len(unique_sorted_values(m_learn['Move'].loc[m_learn["Pokemon"] == pok_r.nombre])) <= 1):
            pok_r = Poke(pk['Nombre'].iloc[rd.randrange(0, len(pk)-1, 1)])
            
        pok_r.set_natur(nat.loc[rd.randrange(0, len(nat)-1, 1), 'Nature'])
        

        while(len(unique_sorted_values(m_learn['Move'].loc[m_learn["Pokemon"] == pok_a.nombre])) <= 1):
            pok_a = Poke(pk['Nombre'].iloc[rd.randrange(0, len(pk)-1, 1)])
            
        pok_a.set_natur(nat.loc[rd.randrange(0, len(nat)-1, 1), 'Nature'])


        
        att_r = unique_sorted_values(m_learn['Move'].loc[m_learn["Pokemon"] == pok_r.nombre])
        atk_r1 = att_r[rd.randrange(0, len(att_r)-1, 1)]
        atk_r2 = att_r[rd.randrange(0, len(att_r)-1, 1)]
        atk_r3 = att_r[rd.randrange(0, len(att_r)-1, 1)]
        atk_r4 = att_r[rd.randrange(0, len(att_r)-1, 1)]
        pok_r.set_atk(atk_r1, atk_r2, atk_r3, atk_r4)    

        att_a = unique_sorted_values(m_learn['Move'].loc[m_learn["Pokemon"] == pok_a.nombre])
        atk_a1 = att_a[rd.randrange(0, len(att_a)-1, 1)]
        atk_a2 = att_a[rd.randrange(0, len(att_a)-1, 1)]
        atk_a3 = att_a[rd.randrange(0, len(att_a)-1, 1)]
        atk_a4 = att_a[rd.randrange(0, len(att_a)-1, 1)]
        pok_a.set_atk(atk_a1, atk_a2, atk_a3, atk_a4)
        
        log.append("Comienza el combate entre " + pok_a.nombre + " y " + pok_r.nombre)
        
        winner, loser = combate(pok_r, pok_a)
        
        combat.loc[i, 'First_pokemon'] = pok_r.nombre
        combat.loc[i, 'Second_pokemon'] = pok_a.nombre
        combat.loc[i, 'Winner'] = winner.nombre
        combat.loc[i, 'win_atk1'] = winner.atk1.nombre
        combat.loc[i, 'win_atk2'] = winner.atk2.nombre
        combat.loc[i, 'win_atk3'] = winner.atk3.nombre
        combat.loc[i, 'win_atk4'] = winner.atk4.nombre
        combat.loc[i, 'win_nature'] = winner.natur
        combat.loc[i, 'los_atk1'] = loser.atk1.nombre
        combat.loc[i, 'los_atk2'] = loser.atk2.nombre
        combat.loc[i, 'los_atk3'] = loser.atk3.nombre
        combat.loc[i, 'los_atk4'] = loser.atk4.nombre
        combat.loc[i, 'los_nature'] = loser.natur

    print(log)
    combat.head(10)

main()