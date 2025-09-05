import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import openpyxl as px

MIN_DATE = datetime(2000, 1, 1).date()
MAX_DATE = datetime(2050, 12, 31).date()
DATA_CONCLUSAO = 7306 # 20 anos (em dias) 

carreira = [[0 for _ in range(10)] for _ in range(DATA_CONCLUSAO)]

st.set_page_config(page_title="SIMULADOR GGDP", layout="wide")

tabs = st.tabs(['**Cálculo Individual**', '**Cálculo Múltiplo**', '**Resultados**'])

def calcular_planilha(arquivo):
    import numpy as np
    result_niveis = []
    arq = px.load_workbook(arquivo, data_only=True)  
    aba = arq.active  # pega a aba ativa
    
    # pega os valores das células
    data = list(aba.values)

    # primeira linha = cabeçalho
    colunas = data[1]
    valores = data[2:]
    
    # cria DataFrame
    df = pd.DataFrame(valores, columns=colunas).drop_duplicates() 
    df = df.replace([None, np.nan], '')
    df.columns = [str(c) if c not in [None, np.nan] else f""
              for i, c in enumerate(df.columns)]
    cols = ["Data de Enquadramento ou Última Evolução"]
    
    st.dataframe(
        df.style.format({col: lambda x: x.strftime("%d/%m/%Y") if pd.notnull(x) else "" for col in cols}),
        hide_index=True
    )

    for i in range (len(df)):
        st.divider()
        identificador = df["ID"].iloc[i]
        if identificador in ('None', 'NaT', 'Nan','', None): 
            break

        st.write(f"ID: {identificador}")

        data_inicio = df["Data de Enquadramento ou Última Evolução"].iloc[i].date()
        st.write("Data:", data_inicio.strftime("%d/%m/%Y"))
        
        DATA_FIM = data_inicio + relativedelta(years=20)
        carreira = [
            [data_inicio + timedelta(days=i)] + [0] * 9
            for i in range(DATA_CONCLUSAO)
        ]
        
        pts_remanescentes = df["Pontos Última Evolução"].iloc[i]
        if pts_remanescentes in ('None', 'NaT', 'Nan','', None): 
            pts_remanescentes = 0

        st.write(f"Pts: {pts_remanescentes}")

        coluna = st.columns(2)

        mes_falta = str(df["Mês"].iloc[i])
        mes_falta = mes_falta.split(';')
        qntd_faltas = str(df["N° de faltas"].iloc[i])
        qntd_faltas = qntd_faltas.split(';')

        mes_curso = str(df["Data de Conclusão"].iloc[i])
        mes_curso = mes_curso.split(';')
        hrs_curso = df["Carga Horaria"].iloc[i].split(';')

        mes_tit = str(df["Data de Conclusao"].iloc[i])
        mes_tit = mes_tit.split(';')
        tipo_tit = df["Tipo"].iloc[i].split(';')
        
        artigos = df["Artigos"].iloc[i].split(';')
        livros = df["Livros"].iloc[i].split(';')
        pesquisas = df["Pesquisas"].iloc[i].split(';')
        registros = df["Registros"].iloc[i].split(';')
        cursos = df["Cursos"].iloc[i].split(';')
        
        art_id, art_nid = [], []
        for art in artigos:
            partes = art.split('-')
            if len(partes) < 3:
                continue  # pula se não tiver o formato esperado

            numero, tipo, data = partes[0], partes[1], partes[2]
            numero = int(numero)
            
            if tipo == 'ID':
                art_id.append((numero,data))
            elif tipo == 'NID':
                art_nid.append((numero,data))
            elif tipo not in ('ID','NID'):
                st.error("Erro de Codigo em Artigos")

        lv_org, lv_cap, lv_comp = [], [], []
        for lv in livros:
            partes = lv.split('-')
            if len(partes) < 3:
                continue  # pula se não tiver o formato esperado

            numero, tipo, data = partes[0], partes[1], partes[2]
            numero = int(numero)
            
            if tipo == 'O':
                lv_org.append((numero,data))
            elif tipo == 'C':
                lv_cap.append((numero,data))
            elif tipo == 'L':
                lv_comp.append((numero,data))
            elif tipo not in ('O','C','L'):
                st.error("Erro de Codigo em Livros")

        pesq_est, pesq_reg, pesq_nac, pesq_int = [], [], [], []
        for pesq in pesquisas:
            partes = pesq.split('-')
            if len(partes) < 3:
                continue  # pula se não tiver o formato esperado

            numero, tipo, data = partes[0], partes[1], partes[2]
            numero = int(numero)
            
            if tipo == 'E':
                pesq_est.append((numero,data))
            elif tipo == 'R':
                pesq_reg.append((numero,data))
            elif tipo == 'N':
                pesq_nac.append((numero,data))
            elif tipo == 'I':
                pesq_int.append((numero,data))
            elif tipo not in ('E','R','N','I'):
                st.error("Erro de Codigo em Pesquisas")
        
        reg_pat, reg_cult = [], []
        for reg in registros:
            partes = reg.split('-')
            if len(partes) < 3:
                continue  # pula se não tiver o formato esperado-

            numero, tipo, data = partes[0], partes[1], partes[2]
            numero = int(numero)
            
            if tipo == 'P':
                reg_pat.append((numero,data))
            elif tipo == 'C':
                reg_cult.append((numero,data))
            elif tipo not in ('P','C'):
                st.error("Erro de Codigo em Registros")

        doc_1, doc_2, doc_3, doc_4, doc_5 = [], [], [], [], []
        pt_curso = {
            'P1': 6,   
            'P2': 8,   
            'P3': 12,  
            'P4': 24,
            'P5': 48 
        }
        for doc in cursos:
            partes = doc.split('-')
            if len(partes) < 2:
                continue  # pula se não tiver o formato esperado

            tipo, data = partes[0], partes[1]
            
            if tipo == 'P1':
                doc_1.append((pt_curso.get(tipo, 0),data))
            elif tipo == 'P2':
                doc_2.append((pt_curso.get(tipo, 0),data))
            elif tipo == 'P3':
                doc_3.append((pt_curso.get(tipo, 0),data))
            elif tipo == 'P4':
                doc_4.append((pt_curso.get(tipo, 0),data))
            elif tipo == 'P5':
                doc_5.append((pt_curso.get(tipo, 0),data))
            elif tipo not in ('P1','P2','P3','P4','P5'):
                st.error("Erro de Codigo em Cursos")

        c_comissao = df["C.Comissão"].iloc[i].split(';')
        f_comissionada = df["F.Comissionada"].iloc[i].split(';')
        f_designada = df["F.Designada"].iloc[i].split(';')
        a_agente = df["A.Agente"].iloc[i].split(';')
        a_conselho = df["A.Conselho"].iloc[i].split(';')
        a_prioritaria = df["A.Prioritária"].iloc[i].split(';')
        
        resp_c_comissao = []
        pt_cargos = {
            "DAS1": 1.000, "DAS2": 1.000,
            "DAS3": 0.889, "DAS4": 0.889,
            "DAS5": 0.800, "DAS6": 0.800, "DAS7": 0.800, "DAID1A": 0.800, "AEG": 0.800,
            "DAI1": 0.667, "DAID1": 0.667, "DAID1B": 0.667, "DAID2": 0.667, "AE1": 0.667, "AE2": 0.667,
            "DAI2": 0.500, "DAI3": 0.500, "DAID4": 0.500, "DAID5": 0.500, "DAID6": 0.500, "DAID7": 0.500,
            "DAID8": 0.500, "DAID9": 0.500, "DAID10": 0.500, "DAID11": 0.500, "DAID12": 0.500,
            "DAID13": 0.500, "DAID14": 0.500
        }
        for cargo in c_comissao:
            partes = cargo.split('-')
            if len(partes) < 3:
                continue  # pula se não tiver o formato esperado

            tipo, data_i, data_f = partes[0], partes[1], partes[2]
            
            if tipo in list(pt_cargos.keys()):
                resp_c_comissao.append((tipo,data_i,data_f))
            elif tipo not in list(pt_cargos.keys()):
                st.error("Erro de Codigo em C.Comissão")
            
        resp_f_comissionada = []
        pt_func_c = {
            "T1": 0.333, 
            "T2": 0.364, 
            "T3": 0.400, 
            "T4": 0.444,  
            "T5": 0.500
        }
        for func in f_comissionada:
            partes = func.split('-')
            if len(partes) < 3:
                continue  # pula se não tiver o formato esperado

            tipo, data_i, data_f = partes[0], partes[1], partes[2]
            
            if tipo in list(pt_func_c.keys()):
                resp_f_comissionada.append((tipo,data_i,data_f))
            elif tipo not in list(pt_func_c.keys()):
                st.error("Erro de Codigo em F.Comissionada")

        resp_f_designada = []
        for func in f_designada:
            partes = func.split('-')
            if len(partes) < 2:
                continue  # pula se não tiver o formato esperado

            data_i, data_f = partes[0], partes[1]
            
            if data_i and data_f is not None:
                resp_f_designada.append((data_i,data_f))
            
        resp_a_agente = []
        pt_agente = {
            "I": 0.333, 
            "II": 0.364, 
            "III": 0.400, 
            "IV": 0.444,  
            "V": 0.500
        }
        for at in a_agente:
            partes = at.split('-')
            if len(partes) < 3:
                continue  # pula se não tiver o formato esperado

            tipo, data_i, data_f = partes[0], partes[1], partes[2]
            
            if tipo in list(pt_agente.keys()):
                resp_a_agente.append((tipo,data_i,data_f))
            elif tipo not in list(pt_agente.keys()):
                st.error("Erro de Codigo em A.Agente")

        resp_a_conselho = []
        for func in a_conselho:
            partes = func.split('-')
            if len(partes) < 2:
                continue  # pula se não tiver o formato esperado

            data_i, data_f = partes[0], partes[1]
            
            if data_i and data_f is not None:
                resp_a_conselho.append((data_i,data_f))
            

        resp_a_prioritaria = []
        for func in a_prioritaria:
            partes = func.split('-')
            if len(partes) < 2:
                continue  # pula se não tiver o formato esperado

            data_i, data_f = partes[0], partes[1]
            
            if data_i and data_f is not None:
                resp_a_prioritaria.append((data_i,data_f))

####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####
        ### ---------- AFASTAMENTOS ---------- ###
        st.session_state.afast_pl = []
        for mes_str, falta_str in zip(mes_falta, qntd_faltas):
            if mes_str and falta_str:  
                mes_date = pd.to_datetime(mes_str, dayfirst=True, errors="coerce").date()
                mes_date = mes_date.strftime("%m/%Y")
                faltas_int = int(float(falta_str))
                st.session_state.afast_pl.append((mes_date, faltas_int))
        
        with coluna[0]:
            for idx, valor in enumerate(st.session_state.afast_pl, start=1): 
                if valor is not None:
                    st.write(f"Mês Falta {idx}:", valor[0])  
        with coluna[1]:
            for _, valor in st.session_state.afast_pl: 
                if valor is not None:
                    st.write(f"N° de Faltas: {valor}")

        for i in range(len(carreira)):
            data_atual = carreira[i][0]
            falta = 0

            # procura se existe afastamento nesse mês
            falta += next((faltas for mes, faltas in st.session_state.afastamentos
                          if data_atual.month == mes.month and data_atual.year == mes.year), 0)

            desconto = 0.0067 * falta
            desconto_des = 0.05 * falta

            # Pega o primeiro dia do próximo mês
            if data_atual.month == 12:
                prox_mes = datetime(data_atual.year + 1, 1, 1)
            else:
                prox_mes = datetime(data_atual.year, data_atual.month + 1, 1)

            ultimo_dia_mes = prox_mes - timedelta(days=1)

            if (data_atual.year == ultimo_dia_mes.year and
            data_atual.month == ultimo_dia_mes.month and
            data_atual.day == ultimo_dia_mes.day):
                
                carreira[i][1] = 0.2
                carreira[i][3] = 1.5
                carreira[i][2] = max(min(0.2 - desconto, 0.2), 0)
                carreira[i][4] = max(min(1.5 - desconto_des, 1.5), 0)
                
            else:
                carreira[i][1] = carreira[i][2] = carreira[i][3] = carreira[i][4] = 0
####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####
        ### ---------- APERFEIÇOAMENTOS ---------- ###
        st.session_state.aperf_pl = []
        for mes_str, falta_str in zip(mes_curso, hrs_curso):
            if mes_str.strip() and falta_str.strip():  
                mes_date = pd.to_datetime(mes_str, dayfirst=True, errors="coerce").date()
                mes_date = mes_date.strftime("%d/%m/%Y")
                faltas_int = int(falta_str.strip())
                st.session_state.aperf_pl.append((mes_date, faltas_int))
        
        with coluna[0]:
            for idx, valor in enumerate(mes_curso[0:], start=1): 
                if valor is not None:
                    st.write(f"Data de Conclusão {idx}:", valor)  
        with coluna[1]:
            for idx, valor in enumerate(hrs_curso[0:], start=1): 
                if valor is not None:
                    st.write(f"Carga Horaria:", valor)

        total_horas = 0  
        st.session_state.aperf_pl_ordenado = sorted(st.session_state.aperf_pl, key=lambda data: data[0])

        # Percorre todos os aperfeiçoamentos cadastrados
        for data_conclusao, horas_curso in st.session_state.aperf_pl_ordenado:
            data_conclusao = pd.to_datetime(data_conclusao).date()
            # Quanto desse curso ainda pode ser aproveitado
            horas_restantes = max(0, 100 - total_horas)
            horas_aproveitadas = min(horas_curso, horas_restantes)

            # Atualiza acumulado de horas
            total_horas += horas_aproveitadas

            # Só calcula pontos se ainda tiver horas aproveitáveis
            if horas_aproveitadas > 0:
                pontos = horas_aproveitadas * 0.09

                # Encontra a linha na matriz carreira e insere os pontos
                for idx, linha in enumerate(carreira):
                    data_linha = linha[0]
                    if (data_linha.year == data_conclusao.year and 
                        data_linha.month == data_conclusao.month and 
                        data_linha.day == data_conclusao.day):
                        carreira[idx][5] += pontos
                        break
####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####
        ### ---------- TITULAÇÕES ---------- ###
        valores_tit = {
            'Nenhuma': None,
            'Graduação': 6,   # Graduação
            'Especialização': 12,   # Especialização
            'Mestrado': 24,  # Mestrado
            'Doutorado': 48    # Doutorado
        }

        st.session_state.tit_pl = []
        for mes_str, tipo_str in zip(mes_tit, tipo_tit):
            if mes_str and tipo_str:  
                mes_date = pd.to_datetime(mes_str, dayfirst=True, errors="coerce").date()
                mes_date = mes_date.strftime("%d/%m/%Y")
                tipo_int = str(tipo_str.strip())
                st.session_state.tit_pl.append((mes_date, tipo_int))
        
        with coluna[0]:
            for idx, valor in enumerate(st.session_state.tit_pl, start=1): 
                if valor is not None:
                    st.write(f"Mês de Conclusão {idx}:", valor[0])  
        with coluna[1]:
            for idx, valor in enumerate(tipo_tit[0:], start=1): 
                if valor is not None:
                    st.write(f"Titulação:", valor)

        total_pontos_tit = 0
        LIMITE_TIT = 144
        st.session_state.tit_pl_ordenado = sorted(st.session_state.tit_pl, key=lambda data: data[0])

        for data_concl, tipo in st.session_state.tit_pl_ordenado:
            data_concl = pd.to_datetime(data_concl).date()
            pontos_titulo = valores_tit.get(tipo, 0)
            pontos_restantes = max(0, LIMITE_TIT - total_pontos_tit)
            pontos_aproveitados = min(pontos_titulo, pontos_restantes)
            total_pontos_tit += pontos_aproveitados

            if pontos_aproveitados > 0:
                for i, linha in enumerate(carreira):
                    d = linha[0]
                    if d.year == data_concl.year and d.month == data_concl.month and d.day == data_concl.day:
                        carreira[i][6] += pontos_aproveitados
                        break

####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####
    ### ---------- RESPONSABILIDADES ---------- ###
        LIMITE_RESP = 144
        pts_acumulado_ru = 0

        ### ---------- ARTIGOS ---------- ###
        st.session_state.pts_artigos_pl =  0
        with coluna[0]:
            for valor in art_id: 
                st.write(f"Indexados: {valor[0]} - {valor[1]}")  
        with coluna[1]:
             for valor in art_nid: 
                st.write(f"Não Indexados: {valor[0]} - {valor[1]}")

        st.session_state.artigos_lista_pl = []
        for numero, data_dt in art_id:
            st.session_state.artigos_lista_pl.append((numero, 0, data_dt))  
        for numero, data_dt in art_nid:
            st.session_state.artigos_lista_pl.append((0, numero, data_dt)) 
        
        # Calculando total de pontos
        total_pts = 0
        for nid, art_id, _ in st.session_state.artigos_lista_pl:
            total_pts += (nid * 0.5) + (art_id * 4)
        st.session_state.pts_artigos_pl = total_pts
        pts_artigos_pl = st.session_state.pts_artigos_pl if 'pts_artigos_pl' in st.session_state else 0
        
        # Agrupar por data e aplicar limite
        art_dict = {}
        for  art_id, nid, data_art in st.session_state.artigos_lista_pl:
            if nid is not None and nid != 0:
                pontos = nid * 0.5 
            if art_id is not None and art_id != 0:
                pontos = art_id * 4
            if data_art in art_dict:
                art_dict[data_art] += pontos
            else:
                art_dict[data_art] = pontos
        
        for data_art, pontos in art_dict.items():
            data_dt = datetime.strptime(data_art, "%d/%m/%Y").date()
            if pts_acumulado_ru + pontos > LIMITE_RESP:
                pontos_aj = max(0, LIMITE_RESP - pts_acumulado_ru)
            else:
                pontos_aj = pontos
            if pontos_aj <= 0:
                continue
            
            # Aplicar na matriz carreira (coluna 7)
            for i, linha in enumerate(carreira):
                d = linha[0]
                if d.year == data_dt.year and d.month == data_dt.month and d.day == data_dt.day:
                    carreira[i][7] = pontos_aj
                    pts_acumulado_ru += pontos_aj
                    break
            
        ### ---------- LIVROS ---------- ###
        colunas = st.columns(3)
        st.session_state.pts_livros_pl =  0
        with colunas[0]:
            for valor in lv_org: 
                st.write(f"Organizador: {valor[0]} - {valor[1]}")  
        with colunas[1]:
             for valor in lv_cap: 
                st.write(f"Capitulo: {valor[0]} - {valor[1]}")
        with colunas[2]:
             for valor in lv_comp: 
                st.write(f"Completo: {valor[0]} - {valor[1]}")

        st.session_state.livros_lista_pl = []
        for numero, data_dt in lv_org:
            st.session_state.livros_lista_pl.append((numero, 0, 0, data_dt))  
        for numero, data_dt in lv_cap:
            st.session_state.livros_lista_pl.append((0, numero, 0, data_dt))  
        for numero, data_dt in lv_comp:
            st.session_state.livros_lista_pl.append((0, 0, numero, data_dt)) 

        # Calculando total de pontos
        total_pts = 0
        for org, cap, comp, _ in st.session_state.livros_lista_pl:
            total_pts += (org * 1) + (cap * 4) + (comp * 6)
        st.session_state.pts_livros_pl = total_pts
        pts_livros_pl = st.session_state.pts_livros_pl if 'pts_livros_pl' in st.session_state else 0
        
        # Agrupar por data e aplicar limite
        lv_dict = {}
        for org, cap, comp, data_lv in st.session_state.livros_lista_pl:
            if org is not None and org != 0:
                pontos = org * 1
            if cap is not None and cap != 0:
                pontos = cap * 4
            if comp is not None and comp != 0:
                pontos = comp * 6

            if data_lv in lv_dict:
                lv_dict[data_lv] += pontos
            else:
                lv_dict[data_lv] = pontos
        
        for data_lv, pontos in lv_dict.items():
            data_dt = datetime.strptime(data_lv, "%d/%m/%Y").date()
            if pts_acumulado_ru + pontos > LIMITE_RESP:
                pontos_aj = max(0, LIMITE_RESP - pts_acumulado_ru)
            else:
                pontos_aj = pontos
            if pontos_aj <= 0:
                continue
            
            # Aplicar na matriz carreira (coluna 7)
            for i, linha in enumerate(carreira):
                d = linha[0]
                if d.year == data_dt.year and d.month == data_dt.month and d.day == data_dt.day:
                    carreira[i][7] = pontos_aj
                    pts_acumulado_ru += pontos_aj
                    break

        ### ---------- PESQUISAS ---------- ###
        colunas = st.columns(4)
        st.session_state.pts_pesquisas_pl =  0
        with colunas[0]:
            for valor in pesq_est: 
                st.write(f"Estadual: {valor[0]} - {valor[1]}")  
        with colunas[1]:
             for valor in pesq_reg: 
                st.write(f"Regional: {valor[0]} - {valor[1]}")
        with colunas[2]:
             for valor in pesq_nac: 
                st.write(f"Nacional: {valor[0]} - {valor[1]}")
        with colunas[3]:
             for valor in pesq_int: 
                st.write(f"Internacional: {valor[0]} - {valor[1]}")

        st.session_state.pesq_lista_pl = []
        for numero, data_dt in pesq_est:
            st.session_state.pesq_lista_pl.append((numero, 0, 0, 0, data_dt))  
        for numero, data_dt in pesq_reg:
            st.session_state.pesq_lista_pl.append((0, numero, 0, 0, data_dt))  
        for numero, data_dt in pesq_nac:
            st.session_state.pesq_lista_pl.append((0, 0, numero, 0, data_dt)) 
        for numero, data_dt in pesq_int:
            st.session_state.pesq_lista_pl.append((0, 0, 0, numero, data_dt)) 

        # Calculando total de pontos
        total_pts = 0
        for est, reg, nac, inter, _ in st.session_state.pesq_lista_pl:
            total_pts += (est * 1) + (reg * 3) + (nac * 3) + (inter * 4)
        st.session_state.pts_pesquisas_pl = total_pts
        pts_pesquisas_pl = st.session_state.pts_pesquisas_pl if 'pts_pesquisas_pl' in st.session_state else 0
        
        # Agrupar por data e aplicar limite
        pesq_dict = {}
        for est, reg, nac, inter, data_pesq in st.session_state.pesq_lista_pl:
            if est is not None and est != 0:
                pontos = est * 1
            if reg is not None and reg != 0:
                pontos = reg * 3
            if nac is not None and nac != 0:
                pontos = nac * 3
            if inter is not None and inter != 0:
                pontos = inter * 4

            if data_pesq in pesq_dict:
                pesq_dict[data_pesq] += pontos
            else:
                pesq_dict[data_pesq] = pontos
        
        for data_pesq, pontos in pesq_dict.items():
            data_dt = datetime.strptime(data_pesq, "%d/%m/%Y").date()
            if pts_acumulado_ru + pontos > LIMITE_RESP:
                pontos_aj = max(0, LIMITE_RESP - pts_acumulado_ru)
            else:
                pontos_aj = pontos
            if pontos_aj <= 0:
                continue
            
            # Aplicar na matriz carreira (coluna 7)
            for i, linha in enumerate(carreira):
                d = linha[0]
                if d.year == data_dt.year and d.month == data_dt.month and d.day == data_dt.day:
                    carreira[i][7] = pontos_aj
                    pts_acumulado_ru += pontos_aj
                    break
           
        ### ---------- REGISTROS ---------- ###
        colunas = st.columns(2)
        st.session_state.pts_registros_pl =  0
        with colunas[0]:
            for valor in reg_pat: 
                st.write(f"Patente: {valor[0]} - {valor[1]}")  
        with colunas[1]:
            for valor in reg_cult: 
                st.write(f"Cultivar: {valor[0]} - {valor[1]}")

        st.session_state.reg_lista_pl = []
        for numero, data_dt in reg_pat:
            st.session_state.reg_lista_pl.append((numero, 0, data_dt))  
        for numero, data_dt in reg_cult:
            st.session_state.reg_lista_pl.append((0, numero, data_dt))  
        
        # Calculando total de pontos
        total_pts = 0
        for pat, cult, _ in st.session_state.reg_lista_pl:
            total_pts += (pat * 8) + (cult * 8)
        st.session_state.pts_registros_pl = total_pts
        pts_registros_pl = st.session_state.pts_registros_pl if 'pts_registros_pl' in st.session_state else 0
        
        # Agrupar por data e aplicar limite
        reg_dict = {}
        for pat, cult, data_reg in st.session_state.reg_lista_pl:
            if pat is not None and pat != 0:
                pontos = pat * 8
            if cult is not None and cult != 0:
                pontos = cult * 8
            if data_reg in reg_dict:
                reg_dict[data_reg] += pontos
            else:
                reg_dict[data_reg] = pontos
        
        for data_reg, pontos in reg_dict.items():
            data_dt = datetime.strptime(data_reg, "%d/%m/%Y").date()
            if pts_acumulado_ru + pontos > LIMITE_RESP:
                pontos_aj = max(0, LIMITE_RESP - pts_acumulado_ru)
            else:
                pontos_aj = pontos
            if pontos_aj <= 0:
                continue
            
            # Aplicar na matriz carreira (coluna 7)
            for i, linha in enumerate(carreira):
                d = linha[0]
                if d.year == data_dt.year and d.month == data_dt.month and d.day == data_dt.day:
                    carreira[i][7] = pontos_aj
                    pts_acumulado_ru += pontos_aj
                    break

        ### ---------- CURSOS ---------- ###
        colunas = st.columns(5)
        st.session_state.pts_cursos_pl =  0
        with colunas[0]:
            for valor in doc_1: 
                st.write(f"P1: {valor[0]} - {valor[1]}")  
        with colunas[1]:
             for valor in doc_2: 
                st.write(f"P2: {valor[0]} - {valor[1]}")
        with colunas[2]:
             for valor in doc_3: 
                st.write(f"P3: {valor[0]} - {valor[1]}")
        with colunas[3]:
             for valor in doc_4: 
                st.write(f"P4: {valor[0]} - {valor[1]}")
        with colunas[4]:
             for valor in doc_5: 
                st.write(f"P5: {valor[0]} - {valor[1]}")

        st.session_state.cursos_lista_pl = []
        for tipo, data_dt in doc_1:
            st.session_state.cursos_lista_pl.append((tipo, data_dt))  
        for tipo, data_dt in doc_2:
            st.session_state.cursos_lista_pl.append((tipo, data_dt))  
        for tipo, data_dt in doc_3:
            st.session_state.cursos_lista_pl.append((tipo, data_dt)) 
        for tipo, data_dt in doc_4:
            st.session_state.cursos_lista_pl.append((tipo, data_dt)) 
        for tipo, data_dt in doc_5:
            st.session_state.cursos_lista_pl.append((tipo, data_dt)) 

        # Calculando total de pontos
        total_pts = 0
        for tipo, _ in st.session_state.cursos_lista_pl:
            total_pts += tipo
        st.session_state.pts_cursos_pl = total_pts
        pts_cursos_pl = st.session_state.pts_cursos_pl if 'pts_cursos_pl' in st.session_state else 0
        
        # Agrupar por data e aplicar limite
        doc_dict = {}
        for tipo, data_doc in st.session_state.cursos_lista_pl:
            if tipo is not None and tipo != 0:
                pontos = tipo

            if data_doc in doc_dict:
                doc_dict[data_doc] += pontos
            else:
                doc_dict[data_doc] = pontos
        
        for data_doc, pontos in doc_dict.items():
            data_dt = datetime.strptime(data_doc, "%d/%m/%Y").date()
            if pts_acumulado_ru + pontos > LIMITE_RESP:
                pontos_aj = max(0, LIMITE_RESP - pts_acumulado_ru)
            else:
                pontos_aj = pontos
            if pontos_aj <= 0:
                continue
            
            # Aplicar na matriz carreira (coluna 7)
            for i, linha in enumerate(carreira):
                d = linha[0]
                if d.year == data_dt.year and d.month == data_dt.month and d.day == data_dt.day:
                    carreira[i][7] = pontos_aj
                    pts_acumulado_ru += pontos_aj
                    break
        
        ### ---------- C.COMISSÃO ---------- ###
        colunas = st.columns(3)
        with colunas[0]:
            for valor in resp_c_comissao: 
                st.write(f"Cargo: {valor[0]} - {valor[1]} - {valor[2]}") 

        st.session_state.comissao_lista_pl = []
        for tipo, data_i, data_f in resp_c_comissao:
            data_dti = datetime.strptime(data_i, "%d/%m/%Y").date()
            data_dtf = datetime.strptime(data_f, "%d/%m/%Y").date() if data_f != 'SF' else DATA_FIM
            delta_ano = data_dtf.year - data_dti.year
            delta_mes = data_dtf.month - data_dti.month
            qntd_meses = delta_ano * 12 + delta_mes
            st.session_state.comissao_lista_pl.append((tipo, data_dti, qntd_meses))

        for cargo_c in st.session_state.comissao_lista_pl:
            inicio = cargo_c[1]
            pontos = pontuacao_cargos.get(cargo_c[0], 0)
            meses = cargo_c[2]
            
            for i in range(len(carreira)):
                d = carreira[i][0]
                
                # Verifica se d é último dia do mês
                prox_dia = d + timedelta(days=1)
                if prox_dia.day != 1:
                    continue  # Não é último dia, pula
                
                # Verifica se d está dentro do período da responsabilidade
                delta_ano = d.year - inicio.year
                delta_mes = d.month - inicio.month
                total_meses = delta_ano * 12 + delta_mes
                
                if 0 <= total_meses < meses:
                    carreira[i][8] += pontos

        ### ---------- F.COMISSIONADA ---------- ###
        with colunas[1]:
            for valor in resp_f_comissionada: 
                st.write(f"Func C: {valor[0]} - {valor[1]} - {valor[2]}") 

        st.session_state.func_c_lista_pl = []
        for tipo, data_i, data_f in resp_f_comissionada:
            data_dti = datetime.strptime(data_i, "%d/%m/%Y").date()
            data_dtf = datetime.strptime(data_f, "%d/%m/%Y").date() if data_f != 'SF' else DATA_FIM
            delta_ano = data_dtf.year - data_dti.year
            delta_mes = data_dtf.month - data_dti.month
            qntd_meses = delta_ano * 12 + delta_mes
            st.session_state.func_c_lista_pl.append((tipo, data_dti, qntd_meses))

        for func_c in st.session_state.func_c_lista_pl:
            inicio = func_c[1]
            pontos = pontuacao_func_c.get(func_c[0], 0)
            meses = func_c[2]
            
            for i in range(len(carreira)):
                d = carreira[i][0]
                
                # Verifica se d é último dia do mês
                prox_dia = d + timedelta(days=1)
                if prox_dia.day != 1:
                    continue  # Não é último dia, pula
                
                # Verifica se d está dentro do período da responsabilidade
                delta_ano = d.year - inicio.year
                delta_mes = d.month - inicio.month
                total_meses = delta_ano * 12 + delta_mes
                
                if 0 <= total_meses < meses:
                    carreira[i][8] += pontos

        ### ---------- F.DESIGNADA ---------- ###
        with colunas[2]:
            for valor in resp_f_designada: 
                st.write(f"Func D: {valor[0]} - {valor[1]}") 

        st.session_state.func_d_lista_pl = []
        for data_i, data_f in resp_f_designada:
            data_dti = datetime.strptime(data_i, "%d/%m/%Y").date()
            data_dtf = datetime.strptime(data_f, "%d/%m/%Y").date() if data_f != 'SF' else DATA_FIM
            delta_ano = data_dtf.year - data_dti.year
            delta_mes = data_dtf.month - data_dti.month
            qntd_meses = delta_ano * 12 + delta_mes
            st.session_state.func_d_lista_pl.append((data_dti, qntd_meses))

        for func_d in st.session_state.func_d_lista_pl:
            inicio = func_d[0]
            pontos = 0.333
            meses = func_d[1]
            
            for i in range(len(carreira)):
                d = carreira[i][0]
                
                # Verifica se d é último dia do mês
                prox_dia = d + timedelta(days=1)
                if prox_dia.day != 1:
                    continue  # Não é último dia, pula
                
                # Verifica se d está dentro do período da responsabilidade
                delta_ano = d.year - inicio.year
                delta_mes = d.month - inicio.month
                total_meses = delta_ano * 12 + delta_mes
                
                if 0 <= total_meses < meses:
                    carreira[i][8] += pontos

        ### ---------- A.AGENTE ---------- ###
        with colunas[0]:
            for valor in resp_a_agente: 
                st.write(f"At. Agente: {valor[0]} - {valor[1]} - {valor[2]}") 

        st.session_state.agente_lista_pl = []
        for tipo, data_i, data_f in resp_a_agente:
            data_dti = datetime.strptime(data_i, "%d/%m/%Y").date()
            data_dtf = datetime.strptime(data_f, "%d/%m/%Y").date() if data_f != 'SF' else DATA_FIM
            delta_ano = data_dtf.year - data_dti.year
            delta_mes = data_dtf.month - data_dti.month
            qntd_meses = delta_ano * 12 + delta_mes
            st.session_state.agente_lista_pl.append((tipo, data_dti, qntd_meses))

        for at_agente in st.session_state.agente_lista_pl:
            inicio = at_agente[1]
            pontos = pontuacao_agente.get(at_agente[0], 0)
            meses = at_agente[2]
            
            for i in range(len(carreira)):
                d = carreira[i][0]
                
                # Verifica se d é último dia do mês
                prox_dia = d + timedelta(days=1)
                if prox_dia.day != 1:
                    continue  # Não é último dia, pula
                
                # Verifica se d está dentro do período da responsabilidade
                delta_ano = d.year - inicio.year
                delta_mes = d.month - inicio.month
                total_meses = delta_ano * 12 + delta_mes
                
                if 0 <= total_meses < meses:
                    carreira[i][8] += pontos

        ### ---------- A.CONSELHO ---------- ###
        with colunas[1]:
            for valor in resp_a_conselho: 
                st.write(f"At. Conselho: {valor[0]} - {valor[1]}") 

        st.session_state.a_conselho_lista_pl = []
        for data_i, data_f in resp_a_conselho:
            data_dti = datetime.strptime(data_i, "%d/%m/%Y").date()
            data_dtf = datetime.strptime(data_f, "%d/%m/%Y").date() if data_f != 'SF' else DATA_FIM
            delta_ano = data_dtf.year - data_dti.year
            delta_mes = data_dtf.month - data_dti.month
            qntd_meses = delta_ano * 12 + delta_mes
            st.session_state.a_conselho_lista_pl.append((data_dti, qntd_meses))

        for at_conselho in st.session_state.a_conselho_lista_pl:
            inicio = at_conselho[0]
            pontos = 0.333
            meses = at_conselho[1]
            
            for i in range(len(carreira)):
                d = carreira[i][0]
                
                # Verifica se d é último dia do mês
                prox_dia = d + timedelta(days=1)
                if prox_dia.day != 1:
                    continue  # Não é último dia, pula
                
                # Verifica se d está dentro do período da responsabilidade
                delta_ano = d.year - inicio.year
                delta_mes = d.month - inicio.month
                total_meses = delta_ano * 12 + delta_mes
                
                if 0 <= total_meses < meses:
                    carreira[i][8] += pontos

        ### ---------- A.PRIORITARIA ---------- ###
        with colunas[2]:
            for valor in resp_a_prioritaria: 
                st.write(f"At. Prioritaria: {valor[0]} - {valor[1]}") 

        st.session_state.a_prioritaria_lista_pl = []
        for data_i, data_f in resp_a_prioritaria:
            data_dti = datetime.strptime(data_i, "%d/%m/%Y").date()
            data_dtf = datetime.strptime(data_f, "%d/%m/%Y").date() if data_f != 'SF' else DATA_FIM
            delta_ano = data_dtf.year - data_dti.year
            delta_mes = data_dtf.month - data_dti.month
            qntd_meses = delta_ano * 12 + delta_mes
            st.session_state.a_prioritaria_lista_pl.append((data_dti, qntd_meses))

        for at_prioritaria in st.session_state.a_prioritaria_lista_pl:
            inicio = at_prioritaria[0]
            pontos = 0.333
            meses = at_prioritaria[1]
            
            for i in range(len(carreira)):
                d = carreira[i][0]
                
                # Verifica se d é último dia do mês
                prox_dia = d + timedelta(days=1)
                if prox_dia.day != 1:
                    continue  # Não é último dia, pula
                
                # Verifica se d está dentro do período da responsabilidade
                delta_ano = d.year - inicio.year
                delta_mes = d.month - inicio.month
                total_meses = delta_ano * 12 + delta_mes
                
                if 0 <= total_meses < meses:
                    carreira[i][8] += pontos
        
####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####
        for i in range(DATA_CONCLUSAO):
            if i == 0:
                carreira[i][9] = carreira[i][2] + carreira[i][4] + carreira[i][5] + carreira[i][6] + carreira[i][7] + carreira[i][8] + pts_remanescentes
            else:
                carreira[i][9] = carreira[i-1][9] + carreira[i][2] + carreira[i][4] + carreira[i][5] + carreira[i][6] + carreira[i][7] + carreira[i][8]
####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####

### ---------- RESULTADOS ---------- ###
# Dados iniciais
        dt_inicial = carreira[0][0]  # primeira data 
        evolucao = None
        meses_ate_evolucao = None
        pts_resto = None

        for i in range(DATA_CONCLUSAO):            
            dt_atual = carreira[i][0]
            pts_loop = carreira[i][9]

            ano_loop = dt_atual.year - dt_inicial.year
            mes_loop = dt_atual.month - dt_inicial.month
            meses_passados = ano_loop*12 + mes_loop

            data_prevista12 = dt_inicial + relativedelta(months=12)
            data_prevista18 = dt_inicial + relativedelta(months=18)

            if dt_atual < data_prevista12:
                continue

            if data_prevista12 <= dt_atual < data_prevista18 :
                if pts_loop >= 96:     
                    evolucao = dt_atual
                    meses_ate_evolucao = meses_passados
                    pts_resto = pts_loop - 48
                    break

            if dt_atual >= data_prevista18:
                if pts_loop >= 48:
                    evolucao = dt_atual
                    meses_ate_evolucao = meses_passados
                    pts_resto = pts_loop - 48
                    break
            
        desempenho, aperfeicoamento = 0, 0
        if evolucao:
            for linha in carreira:
                data = linha[0]
                if data <= evolucao:
                    desempenho += linha[2] 
                    aperfeicoamento += linha[5]

        col = st.columns(2)
        col[0].metric(f"Pontos de Desempenho:", value=round(desempenho,4))
        col[1].metric(f"Pontos de Aperfeiçoamento:", value=round(aperfeicoamento,4))

        total_horas = 0
        pendencias = False
        motivo = ""

        if not evolucao:
            pendencias = True
            motivo = "Não atingiu pontuação mínima"
        elif round(aperfeicoamento, 4) < 5.4:
            pendencias = True
            motivo = "Não atingiu requisito de Aperfeiçoamento"
        elif round(desempenho, 4) < 2.4:
            pendencias = True
            motivo = "Não atingiu requisito de Desempenho"

        if pendencias:
            result_niveis.append({
                "ID": identificador,
                "Data da Próxima Evolução": "-",
                "Meses Gastos para Evolução": "-",
                "Pontos Remanescentes": "-",
                "Status": "Não apto a evoluir",
                "Motivo": motivo
            })
        else:
            result_niveis.append({
                "ID": identificador,
                "Data da Próxima Evolução": evolucao.strftime("%d/%m/%Y"),
                "Meses Gastos para Evolução": meses_ate_evolucao,
                "Pontos Remanescentes": round(pts_resto, 4),
                "Status": "Apto",
                "Motivo": "-"
            })
        
    df_results = pd.DataFrame(result_niveis)
    st.dataframe(df_results, hide_index=True, height=700)

    import io 
    excel_buffer = io.BytesIO()
    df_results.to_excel(excel_buffer, index=False, engine='openpyxl')
    excel_buffer.seek(0)
    
    st.download_button(
            label="Exportar",
            data=excel_buffer.getvalue(),
            file_name="Resultado Evoluções.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

### ---------- MAIN ---------- ###
####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####
### ---------- PONTOS PADRÕES ---------- ###

with tabs[0]:
    subtab = st.tabs(['**Obrigatorios**', '**Responsabilidades**']) 
    with subtab[0]:
        if "obrigatorios" not in st.session_state:
            st.session_state.obrigatorios = []  # Lista de (mes, faltas)

        st.subheader("Obrigatorios")

        col = st.columns([2, 2, 2])
        with col[0]:
            data_inicial = st.date_input("Data do Enquadramento ou Ultima Evolução", format="DD/MM/YYYY", value=MIN_DATE, min_value=MIN_DATE, max_value=MAX_DATE)
            DATA_FIM = data_inicial + relativedelta(years=20)
        with col[1]:
            pts_remanescentes = st.number_input("Pontos Remanescentes da Última Evolução", min_value=0.000)
        with col[2]:
            if st.button("Adicionar", key="obg"):
                if pts_remanescentes > 0:
                    st.session_state.obrigatorios.append((data_inicial, pts_remanescentes))
                else:
                    st.error("Todas as informações precisam ser preenchidas.")

        # Mostrar pontos cadastrados
        if st.session_state.obrigatorios:
            st.write("**Pontos Vindos da Última Evolução:**")
            cols = st.columns(6)
            for i, (data, pts) in enumerate(st.session_state.obrigatorios):
                col = cols[i % 6]  # escolhe a coluna certa
                with col:
                    st.write(f"{pts} ponto(s) ")
                    if st.button(f"Remover", key=f"remover_obg{i}"):
                        st.session_state.obrigatorios.pop(i)
                        st.rerun() 

        if "afastamentos" not in st.session_state:
            st.session_state.afastamentos = []  # Lista de (mes, faltas)

        st.subheader("Afastamentos")

        # Entrada de um novo afastamento
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            mes_faltas = st.date_input("Mês", format="DD/MM/YYYY", value=data_inicial, min_value=MIN_DATE, max_value=MAX_DATE, key="mes_afast", help="SERÁ CONTADO SERÁ SOMENTE O MÊS")
        with col2:
            qntd_faltas = st.number_input("Faltas", min_value=0, step=1, key="qntd_afast")
        with col3:
            if st.button("Adicionar", key="afast"):
                if qntd_faltas > 0:
                    st.session_state.afastamentos.append((mes_faltas, qntd_faltas))
                else:
                    st.error("Todas as informações precisam ser preenchidas.")

        # Mostrar afastamentos cadastrados
        if st.session_state.afastamentos:
            st.write("**Afastamentos cadastrados:**")
            cols = st.columns(6)
            for i, (mes, faltas) in enumerate(st.session_state.afastamentos):
                col = cols[i % 6]  # escolhe a coluna certa
                with col:
                    st.write(f"{mes.strftime('%m/%Y')} → {faltas} falta(s) |")
                    if st.button(f"Remover", key=f"remover_afast{i}"):
                        st.session_state.afastamentos.pop(i)
                        st.rerun()    

        # Coluna de datas
        carreira = [
            [data_inicial + timedelta(days=i)] + [0] * 9
            for i in range(DATA_CONCLUSAO)
        ]

        # pontos_base
        for i in range(len(carreira)):
            data_atual = carreira[i][0]
            falta = 0

            # procura se existe afastamento nesse mês
            falta += next((faltas for mes, faltas in st.session_state.afastamentos
                          if data_atual.month == mes.month and data_atual.year == mes.year), 0)

            desconto = 0.0067 * falta
            desconto_des = 0.05 * falta

            # Pega o primeiro dia do próximo mês
            if data_atual.month == 12:
                prox_mes = datetime(data_atual.year + 1, 1, 1)
            else:
                prox_mes = datetime(data_atual.year, data_atual.month + 1, 1)

            ultimo_dia_mes = prox_mes - timedelta(days=1)

            if (data_atual.year == ultimo_dia_mes.year and
            data_atual.month == ultimo_dia_mes.month and
            data_atual.day == ultimo_dia_mes.day):
                
                carreira[i][1] = 0.2
                carreira[i][3] = 1.5
                carreira[i][2] = max(min(0.2 - desconto, 0.2), 0)
                carreira[i][4] = max(min(1.5 - desconto_des, 1.5), 0)
                
            else:
                carreira[i][1] = carreira[i][2] = carreira[i][3] = carreira[i][4] = 0

        ### ---------- CONCLUIDO ---------- ###
####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####
        ### ---------- APERFEIÇOAMENTO ---------- ###

        if "aperfeicoamentos" not in st.session_state:
            st.session_state.aperfeicoamentos = []
            
        st.subheader("Aperfeiçoamento")

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            data_conclusao = st.date_input("Data de Conclusão", format="DD/MM/YYYY", value=data_inicial, min_value=MIN_DATE, max_value=MAX_DATE, key="mes_aperf")
        with col2:
            horas_curso = st.number_input("Horas do Curso", min_value=0, max_value=100, step=1, key="hrs_aperf")
        with col3:
            if st.button("Adicionar", key="aperf"):
                if data_conclusao and horas_curso > 0:
                    st.session_state.aperfeicoamentos.append((data_conclusao, horas_curso))
                else:
                    st.error("Todas as informações precisam ser preenchidas.")

        # Mostrar aperfeiçoamentos cadastrados
        if st.session_state.aperfeicoamentos:
            st.write("**Aperfeiçoamentos cadastrados:**")
            cols = st.columns(6)
            for i, (data, horas) in enumerate(st.session_state.aperfeicoamentos):
                col = cols[i % 6]  # escolhe a coluna certa
                with col:
                    st.write(f"{data.strftime('%d/%m/%Y')} → {horas} hora(s) |")
                    if st.button(f"Remover", key=f"remover_aperf{i}"):
                        st.session_state.aperfeicoamentos.pop(i)
                        st.rerun()    

        total_horas = 0  
        st.session_state.aperfeicoamentos_ordenado = sorted(st.session_state.aperfeicoamentos, key=lambda data: data[0])

        # Percorre todos os aperfeiçoamentos cadastrados
        for data_conclusao, horas_curso in st.session_state.aperfeicoamentos_ordenado:
            # Quanto desse curso ainda pode ser aproveitado
            horas_restantes = max(0, 100 - total_horas)
            horas_aproveitadas = min(horas_curso, horas_restantes)

            # Atualiza acumulado de horas
            total_horas += horas_aproveitadas

            # Só calcula pontos se ainda tiver horas aproveitáveis
            if horas_aproveitadas > 0:
                pontos = horas_aproveitadas * 0.09

                # Encontra a linha na matriz carreira e insere os pontos
                for idx, linha in enumerate(carreira):
                    data_linha = linha[0]
                    if (data_linha.year == data_conclusao.year and 
                        data_linha.month == data_conclusao.month and 
                        data_linha.day == data_conclusao.day):
                        carreira[idx][5] += pontos
                        break

        ### ---------- CONCLUIDO ---------- ###
####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####
        ### ---------- TITULAÇÕES ---------- ###
        valores_tit = {
            'Nenhuma': None,
            'Graduação': 6,   # Graduação
            'Especialização': 12,   # Especialização
            'Mestrado': 24,  # Mestrado
            'Doutorado': 48    # Doutorado
        }

        if "titulacoes" not in st.session_state:
            st.session_state.titulacoes = []
            
        st.subheader("Titulações")

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            data_conclusao_tit = st.date_input("Data de Conclusão", format="DD/MM/YYYY", value=data_inicial, min_value=MIN_DATE, max_value=MAX_DATE, key="mes_tit")
        with col2:
            tipo_tit = st.selectbox("Tipo", list(valores_tit.keys()))
            
        with col3:
            if st.button("Adicionar", key="tit"):
                if data_conclusao_tit and tipo_tit != 'Nenhuma':
                    st.session_state.titulacoes.append((data_conclusao_tit, tipo_tit))
                else:
                    st.error("Todas as informações precisam ser preenchidas.")

        # Mostrar titulações cadastradas
        if st.session_state.titulacoes:
            st.write("**Titulações cadastradas:**")
            cols = st.columns(6)
            for i, (data, tipo) in enumerate(st.session_state.titulacoes):
                col = cols[i % 6]
                with col:
                    st.write(f"{data.strftime('%d/%m/%Y')} → {tipo} |")
                    if st.button("Remover", key=f"remover_tit{i}"):
                        st.session_state.titulacoes.pop(i)
                        st.rerun()  

        total_pontos_tit = 0
        LIMITE_TIT = 144
        st.session_state.titulacoes_ordenado = sorted(st.session_state.titulacoes, key=lambda data: data[0])

        for data_concl, tipo in st.session_state.titulacoes_ordenado:
            pontos_titulo = valores_tit.get(tipo, 0)
            pontos_restantes = max(0, LIMITE_TIT - total_pontos_tit)
            pontos_aproveitados = min(pontos_titulo, pontos_restantes)
            total_pontos_tit += pontos_aproveitados

            if pontos_aproveitados > 0:
                for i, linha in enumerate(carreira):
                    d = linha[0]
                    if d.year == data_concl.year and d.month == data_concl.month and d.day == data_concl.day:
                        carreira[i][6] += pontos_aproveitados
                        break

        ### ---------- CONCLUIDO ---------- ###
####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####
    with subtab[1]:
        pts_responsabilidade_unic = 0.0
        pts_responsabilidade_mensais = 0.0

        sub_tabs = st.tabs(["**Responsabilidades Únicas**", "**Responsabilidades Mensais**","**Resultados**"])
        cols = st.columns(2)

    ### ---------- RESPONSABILIDADES MENSAIS ---------- ###
        with sub_tabs[1]:
            ### ---------- CARGO DE COMISSÃO ---------- ###    
            qntd_meses_comissao = 0
            pontuacao_cargos = {
                "DAS-1": 1.000, "DAS-2": 1.000,
                "DAS-3": 0.889, "DAS-4": 0.889,
                "DAS-5": 0.800, "DAS-6": 0.800, "DAS-7": 0.800, "DAID-1A": 0.800, "AEG": 0.800,
                "DAI-1": 0.667, "DAID-1": 0.667, "DAID-1B": 0.667, "DAID-2": 0.667, "AE-1": 0.667, "AE-2": 0.667,
                "DAI-2": 0.500, "DAI-3": 0.500, "DAID-4": 0.500, "DAID-5": 0.500, "DAID-6": 0.500, "DAID-7": 0.500,
                "DAID-8": 0.500, "DAID-9": 0.500, "DAID-10": 0.500, "DAID-11": 0.500, "DAID-12": 0.500,
                "DAID-13": 0.500, "DAID-14": 0.500
            }

            if "comissao_lista" not in st.session_state:
                st.session_state.comissao_lista = []

            if st.checkbox("Exercício em Cargo de Comissão", value=False):   
                cols = st.columns([1, 1, 1, 1])
                with cols[0]:
                    cargo_comissao = st.selectbox("Cargo de Comissão", ["Nenhum"] + list(pontuacao_cargos.keys()))
                with cols[1]:
                    data_inicio_comissao = st.date_input("Data de Inicio", format="DD/MM/YYYY", value=MIN_DATE, min_value=MIN_DATE, max_value=MAX_DATE, key="dt_inicio_comissao")
                with cols[2]:
                    n_data = st.radio("", ['Sem Data', 'Escolher Data de Fim'], horizontal=True, key="modo_data")
                with cols[3]:
                    if n_data == 'Escolher Data de Fim':
                        data_fim_comissao = st.date_input("Data de Fim", format="DD/MM/YYYY", value=DATA_FIM, min_value=MIN_DATE, max_value=MAX_DATE, key="dt_fim_comissao")
                    else:
                        data_fim_comissao = DATA_FIM
                        st.date_input("Data de Fim", format="DD/MM/YYYY", value=DATA_FIM, disabled=True, key="dt_fim_comissao_disabled")

                    if st.button("Adicionar", key="comissao"):
                            if data_fim_comissao < data_inicio_comissao:
                                st.error("A data de fim não pode ser anterior à data de início.")
                            elif cargo_comissao != 'Nenhum' and data_inicio_comissao and data_fim_comissao and data_fim_comissao >= data_inicio_comissao:
                                delta_ano = data_fim_comissao.year - data_inicio_comissao.year
                                delta_mes = data_fim_comissao.month - data_inicio_comissao.month
                                qntd_meses_comissao = delta_ano * 12 + delta_mes
                                st.session_state.comissao_lista.append((data_inicio_comissao, cargo_comissao,  qntd_meses_comissao))
                            else:
                                st.error("Todas as informações precisam ser preenchidas.")

            pts_comissao_total =  sum(
                pontuacao_cargos[cargo] * meses
                for _, cargo, meses in st.session_state.comissao_lista
            )
            pts_comissao = sum(pontuacao_cargos[cargo] for _, cargo, _, in st.session_state.comissao_lista)

            for cargo_c in st.session_state.comissao_lista:
                inicio = cargo_c[0]
                pontos = pontuacao_cargos.get(cargo_c[1], 0)
                meses = cargo_c[2]
                
                for i in range(len(carreira)):
                    d = carreira[i][0]
                    
                    # Verifica se d é último dia do mês
                    prox_dia = d + timedelta(days=1)
                    if prox_dia.day != 1:
                        continue  # Não é último dia, pula
                    
                    # Verifica se d está dentro do período da responsabilidade
                    delta_ano = d.year - inicio.year
                    delta_mes = d.month - inicio.month
                    total_meses = delta_ano * 12 + delta_mes
                    
                    if 0 <= total_meses < meses:
                        carreira[i][8] += pontos
            
            ### ---------- FUNÇÃO COMISSIONADA ---------- ###  
            pontuacao_func_c = {
                "até R$ 750,00": 0.333, 
                " 751,00 - 1.200,00": 0.364, 
                " 1.201,00 - 1.650,00": 0.400, 
                " 1.651,00 - 2.250,00": 0.444,  
                "acima de 2.250,00": 0.500
            }

            if "func_c_lista" not in st.session_state:
                st.session_state.func_c_lista = []

            if st.checkbox("Exercício de Função Comissionada ou Gratificada", value=False):   
                cols = st.columns([1, 1, 1, 1])
                with cols[0]:
                    func_c = st.selectbox("Função", ["Nenhum"] + list(pontuacao_func_c.keys()))
                with cols[1]:
                    data_inicio_func_c = st.date_input("Data de Inicio", format="DD/MM/YYYY", value=MIN_DATE, min_value=MIN_DATE, max_value=MAX_DATE, key="dt_inicio_func_c")
                with cols[2]:
                    n_data = st.radio("", ['Sem Data', 'Escolher Data de Fim'], horizontal=True, key="modo_data2")
                with cols[3]:
                    if n_data == 'Escolher Data de Fim':
                        data_fim_func_c = st.date_input("Data de Fim", format="DD/MM/YYYY", value=DATA_FIM, min_value=MIN_DATE, max_value=MAX_DATE, key="dt_fim_func_c")
                    else:
                        data_fim_func_c = DATA_FIM
                        st.date_input("Data de Fim", format="DD/MM/YYYY", value=DATA_FIM, disabled=True, key="dt_fim_func_c_disabled")

                    if st.button("Adicionar", key="func_c"):
                        if data_fim_func_c < data_inicio_func_c:
                            st.error("A data de fim não pode ser anterior à data de início.")
                        elif func_c != 'Nenhum' and data_inicio_func_c and data_fim_func_c and data_fim_func_c >= data_inicio_func_c:
                            delta_ano = data_fim_func_c.year - data_inicio_func_c.year
                            delta_mes = data_fim_func_c.month - data_inicio_func_c.month
                            qntd_meses_func_c = delta_ano * 12 + delta_mes 
                            st.session_state.func_c_lista.append((data_inicio_func_c, func_c,  qntd_meses_func_c))
                        else:
                            st.error("Todas as informações precisam ser preenchidas.")

            pts_func_c_total =  sum(
                pontuacao_func_c[func] * meses
                for _, func, meses in st.session_state.func_c_lista
            )

            pts_func_c = sum(pontuacao_func_c[func] for _, func, _ in st.session_state.func_c_lista)

            for func_c in st.session_state.func_c_lista:
                inicio = func_c[0]
                pontos = pontuacao_func_c.get(func_c[1], 0)
                meses = func_c[2]
                
                for i in range(len(carreira)):
                    d = carreira[i][0]
                    
                    # Verifica se d é último dia do mês
                    prox_dia = d + timedelta(days=1)
                    if prox_dia.day != 1:
                        continue  # Não é último dia, pula
                    
                    # Verifica se d está dentro do período da responsabilidade
                    delta_ano = d.year - inicio.year
                    delta_mes = d.month - inicio.month
                    total_meses = delta_ano * 12 + delta_mes
                    
                    if 0 <= total_meses < meses:
                        carreira[i][8] += pontos

            ### ---------- FUNÇÃO DESIGNADA ---------- ###  
            if "func_d_lista" not in st.session_state:
                st.session_state.func_d_lista = []
            if "pts_func_d" not in st.session_state:
                st.session_state.pts_func_d = 0

            if st.checkbox("Exercício de Função Designada", value=False): 
                cols = st.columns([1, 1, 1])
                with cols[0]:
                    data_inicio_func_d = st.date_input("Data de Inicio", format="DD/MM/YYYY", value=MIN_DATE, min_value=MIN_DATE, max_value=MAX_DATE, key="dt_inicio_func_d")
                with cols[1]:
                    n_data = st.radio("", ['Sem Data', 'Escolher Data de Fim'], horizontal=True, key="modo_data3")
                with cols[2]:
                    if n_data == 'Escolher Data de Fim':
                        data_fim_func_d = st.date_input("Data de Fim", format="DD/MM/YYYY", value=DATA_FIM, min_value=MIN_DATE, max_value=MAX_DATE, key="dt_fim_func_d")
                    else:
                        data_fim_func_d = DATA_FIM
                        st.date_input("Data de Fim", format="DD/MM/YYYY", value=DATA_FIM, disabled=True, key="dt_fim_func_d_disabled")
                    
                    if st.button("Adicionar", key="func_d"):
                        if data_fim_func_d < data_inicio_func_d:
                            st.error("A data de fim não pode ser anterior à data de início.")
                        elif data_inicio_func_d and data_fim_func_d and data_fim_func_d >= data_inicio_func_d:
                            delta_ano = data_fim_func_d.year - data_inicio_func_d.year
                            delta_mes = data_fim_func_d.month - data_inicio_func_d.month
                            qntd_meses_func_d = delta_ano * 12 + delta_mes
                            st.session_state.func_d_lista.append((data_inicio_func_d, qntd_meses_func_d))
                        else:
                            st.error("Todas as informações precisam ser preenchidas.")
                        if data_fim_func_d > data_inicio_func_d:
                            st.session_state.pts_func_d = 0.333  

            pts_func_d = st.session_state.pts_func_d if 'pts_func_d' in st.session_state else 0
            
            pts_func_d_total = sum(
                0.333 * meses
                for _, meses in st.session_state.func_d_lista
            )

            for func_d in st.session_state.func_d_lista:
                inicio = func_d[0]
                pontos = 0.333
                meses = func_d[1]
                
                for i in range(len(carreira)):
                    d = carreira[i][0]
                    
                    # Verifica se d é último dia do mês
                    prox_dia = d + timedelta(days=1)
                    if prox_dia.day != 1:
                        continue  # Não é último dia, pula
                    
                    # Verifica se d está dentro do período da responsabilidade
                    delta_ano = d.year - inicio.year
                    delta_mes = d.month - inicio.month
                    total_meses = delta_ano * 12 + delta_mes
                    
                    if 0 <= total_meses < meses:
                        carreira[i][8] += pontos

            ### ---------- ATUAÇÃO COMO AGENTE ---------- ###  
            pontuacao_agente = {
                "I": 0.333, 
                "II": 0.364, 
                "III": 0.400, 
                "IV": 0.444,  
                "V": 0.500
            }

            if "agente_lista" not in st.session_state:
                st.session_state.agente_lista = []

            if st.checkbox("Atuação como Agente de Contratação, Gestor/Fiscal de Contratos/Convênios", value=False):   
                cols = st.columns([1, 1, 1, 1])
                with cols[0]:
                    agente = st.selectbox("Atuação", ["Nenhum"] + list(pontuacao_agente.keys()))
                with cols[1]:
                    data_inicio_agente = st.date_input("Data de Inicio", format="DD/MM/YYYY", value=MIN_DATE, min_value=MIN_DATE, max_value=MAX_DATE, key="dt_inicio_agente")
                with cols[2]:
                    n_data = st.radio("", ['Sem Data', 'Escolher Data de Fim'], horizontal=True, key="modo_data4")
                with cols[3]:
                    if n_data == 'Escolher Data de Fim':
                        data_fim_agente = st.date_input("Data de Fim", format="DD/MM/YYYY", value=DATA_FIM, min_value=MIN_DATE, max_value=MAX_DATE, key="dt_fim_agente")
                    else:
                        data_fim_agente = DATA_FIM
                        st.date_input("Data de Fim", format="DD/MM/YYYY", value=DATA_FIM, disabled=True, key="dt_fim_agente_disabled")

                    if st.button("Adicionar", key="agente"):
                        if data_fim_agente < data_inicio_agente:
                            st.error("A data de fim não pode ser anterior à data de início.")
                        elif agente != 'Nenhum' and data_inicio_agente and data_fim_agente and data_fim_agente >= data_inicio_agente:
                            delta_ano = data_fim_agente.year - data_inicio_agente.year
                            delta_mes = data_fim_agente.month - data_inicio_agente.month
                            qntd_meses_agente = delta_ano * 12 + delta_mes
                            st.session_state.agente_lista.append((data_inicio_agente, agente, qntd_meses_agente))
                        else:
                            st.error("Todas as informações precisam ser preenchidas.")

            pts_agente_total =  sum(
                pontuacao_agente[at] * meses
                for _, at, meses in st.session_state.agente_lista
            )

            pts_agente = sum(pontuacao_agente[cargo] for _, cargo, _ in st.session_state.agente_lista)

            for agente in st.session_state.agente_lista:
                inicio = agente[0]
                pontos = pontuacao_agente.get(agente[1], 0)
                meses = agente[2]
                
                for i in range(len(carreira)):
                    d = carreira[i][0]
                    
                    # Verifica se d é último dia do mês
                    prox_dia = d + timedelta(days=1)
                    if prox_dia.day != 1:
                        continue  # Não é último dia, pula
                    
                    # Verifica se d está dentro do período da responsabilidade
                    delta_ano = d.year - inicio.year
                    delta_mes = d.month - inicio.month
                    total_meses = delta_ano * 12 + delta_mes
                    
                    if 0 <= total_meses < meses:
                        carreira[i][8] += pontos

            ### ---------- ATUAÇÃO EM CONSELHO ---------- ###  
            if "conselho_lista" not in st.session_state:
                st.session_state.conselho_lista = []
            if "pts_conselho" not in st.session_state:
                st.session_state.pts_conselho = 0

            if st.checkbox("Atuação em Conselho, Comitê, Câmara Técnica, Comissão ou Grupo de Trabalho", value=False):   
                cols = st.columns([1, 1, 1])
                with cols[0]:
                    data_inicio_conselho = st.date_input("Data de Inicio", format="DD/MM/YYYY", value=MIN_DATE, min_value=MIN_DATE, max_value=MAX_DATE, key="dt_inicio_conselho")
                with cols[1]:
                    n_data = st.radio("", ['Sem Data', 'Escolher Data de Fim'], horizontal=True, key="modo_data5")
                with cols[2]:
                    if n_data == 'Escolher Data de Fim':
                        data_fim_conselho = st.date_input("Data de Fim", format="DD/MM/YYYY", value=DATA_FIM, min_value=MIN_DATE, max_value=MAX_DATE, key="dt_fim_conselho")
                    else:
                        data_fim_conselho = DATA_FIM
                        st.date_input("Data de Fim", format="DD/MM/YYYY", value=DATA_FIM, disabled=True, key="dt_fim_conselho_disabled")
                    
                    if st.button("Adicionar", key="conselho"):
                        if data_fim_conselho < data_inicio_conselho:
                            st.error("A data de fim não pode ser anterior à data de início.")
                        elif data_inicio_conselho and data_fim_conselho and data_fim_conselho >= data_inicio_conselho:
                            delta_ano = data_fim_conselho.year - data_inicio_conselho.year
                            delta_mes = data_fim_conselho.month - data_inicio_conselho.month
                            qntd_meses_conselho = delta_ano * 12 + delta_mes
                            st.session_state.conselho_lista.append((data_inicio_conselho, qntd_meses_conselho))
                        else:
                            st.error("Todas as informações precisam ser preenchidas.")
                        if data_fim_conselho > data_inicio_conselho:
                            st.session_state.pts_conselho = 0.333
            
            pts_conselho = st.session_state.pts_conselho if 'pts_conselho' in st.session_state else 0

            pts_conselho_total = sum(
                0.333 * meses
                for _, meses in st.session_state.conselho_lista
            )

            for conselho in st.session_state.conselho_lista:
                inicio = conselho[0]
                pontos = 0.333
                meses = conselho[1]
                
                for i in range(len(carreira)):
                    d = carreira[i][0]
                    
                    # Verifica se d é último dia do mês
                    prox_dia = d + timedelta(days=1)
                    if prox_dia.day != 1:
                        continue  # Não é último dia, pula
                    
                    # Verifica se d está dentro do período da responsabilidade
                    delta_ano = d.year - inicio.year
                    delta_mes = d.month - inicio.month
                    total_meses = delta_ano * 12 + delta_mes
                    
                    if 0 <= total_meses < meses:
                        carreira[i][8] += pontos

        ### ---------- ATUAÇÃO PRIORITÁRIA ---------- ###  
            if "prioritaria_lista" not in st.session_state:
                st.session_state.prioritaria_lista = []
            if "pts_prioritaria" not in st.session_state:
                st.session_state.pts_prioritaria = 0

            if st.checkbox("Exercício de Atuação Prioritária", value=False):   
                cols = st.columns([1, 1, 1])
                with cols[0]:
                    data_inicio_prioritaria = st.date_input("Data de Inicio", format="DD/MM/YYYY", value=MIN_DATE, min_value=MIN_DATE, max_value=MAX_DATE, key="dt_inicio_prioritaria")
                with cols[1]:
                    n_data = st.radio("", ['Sem Data', 'Escolher Data de Fim'], horizontal=True, key="modo_data6")
                with cols[2]:
                    if n_data == 'Escolher Data de Fim':
                        data_fim_prioritaria = st.date_input("Data de Fim", format="DD/MM/YYYY", value=DATA_FIM, min_value=MIN_DATE, max_value=MAX_DATE, key="dt_fim_prioritaria")
                    else:
                        data_fim_prioritaria = DATA_FIM
                        st.date_input("Data de Fim", format="DD/MM/YYYY", value=DATA_FIM, disabled=True, key="dt_fim_prioritaria_disabled")
                    
                    if st.button("Adicionar", key="prioritaria"):
                        if data_fim_prioritaria < data_inicio_prioritaria:
                            st.error("A data de fim não pode ser anterior à data de início.")
                        elif data_inicio_prioritaria and data_fim_prioritaria and data_fim_prioritaria >= data_inicio_prioritaria:
                            delta_ano = data_fim_prioritaria.year - data_inicio_prioritaria.year
                            delta_mes = data_fim_prioritaria.month - data_inicio_prioritaria.month
                            qntd_meses_prioritaria = delta_ano * 12 + delta_mes   
                            st.session_state.prioritaria_lista.append((data_inicio_prioritaria, qntd_meses_prioritaria))
                        else:
                            st.error("Todas as informações precisam ser preenchidas.")
                        if data_fim_prioritaria > data_inicio_prioritaria:
                            st.session_state.pts_prioritaria = 0.333

            pts_prioritaria = st.session_state.pts_prioritaria if 'pts_prioritaria' in st.session_state else 0

            pts_prioritaria_total = sum(
                0.333 * meses
                for _, meses in st.session_state.prioritaria_lista
            )

            for prioritaria in st.session_state.prioritaria_lista:
                inicio = prioritaria[0]
                pontos = 0.333
                meses = prioritaria[1]
                
                for i in range(len(carreira)):
                    d = carreira[i][0]
                    
                    # Verifica se d é último dia do mês
                    prox_dia = d + timedelta(days=1)
                    if prox_dia.day != 1:
                        continue  # Não é último dia, pula
                    
                    # Verifica se d está dentro do período da responsabilidade
                    delta_ano = d.year - inicio.year
                    delta_mes = d.month - inicio.month
                    total_meses = delta_ano * 12 + delta_mes
                    
                    if 0 <= total_meses < meses:
                        carreira[i][8] += pontos

            pts_responsabilidade_mensais = pts_comissao + pts_func_c + pts_func_d + pts_agente + pts_conselho + pts_prioritaria

            pts_responsabilidade_mensais_total = pts_comissao_total + pts_func_c_total + pts_func_d_total + pts_agente_total + pts_conselho_total + pts_prioritaria_total
            if pts_responsabilidade_mensais_total >= 144: pts_responsabilidade_mensais_total = 144

    ### ---------- CONCLUIDO ---------- ###
####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####
    ### ---------- RESPONSABILIDADES ÚNICAS ---------- ###
        pts_acumulado_ru = 0
        LIMITE_RESP = 144
        with sub_tabs[0]:
            ### ---------- ARTIGOS ---------- ###
            if "artigos_lista" not in st.session_state:
                st.session_state.artigos_lista = []
            if "pts_artigos" not in st.session_state:
                st.session_state.pts_artigos = 0

            if st.checkbox("Quantidade de Artigos Científicos Completos Publicados em Periódicos...", value=False):
                cols = st.columns([1, 1, 1])
                with cols[0]: 
                    qntd_periodicos_nid = st.number_input("**NÃO** Indexados", min_value=0, key="nid")
                with cols[1]: 
                    qntd_periodicos_id = st.number_input("Indexados", min_value=0, key="id")
                with cols[2]:
                    data_artigos = st.date_input("Data de Publicação", format="DD/MM/YYYY", value=MIN_DATE, min_value=MIN_DATE, max_value=MAX_DATE, key="dt_artigos")
                    if st.button("Adicionar", key="artigos"):
                        if qntd_periodicos_nid > 0 or qntd_periodicos_id > 0:
                            st.session_state.artigos_lista.append((qntd_periodicos_nid, qntd_periodicos_id, data_artigos))
                        else:
                            st.error("Todas as informações precisam ser preenchidas.")

            total_pts = 0
            for nid, id_, data_art in st.session_state.artigos_lista:
                total_pts += (nid * 0.5) + (id_ * 4)

            st.session_state.pts_artigos = total_pts
            pts_artigos = st.session_state.pts_artigos if 'pts_artigos' in st.session_state else 0

            art_dict = {}
            for nid, art_id, data_art in st.session_state.artigos_lista:
                pontos = 0
                if nid is not None and nid != 0:
                    pontos += nid * 0.5 
                if art_id is not None and art_id != 0:
                    pontos += art_id * 4

                if data_art in art_dict:
                    art_dict[data_art] += pontos
                else:
                    art_dict[data_art] = pontos

            for data_art, pontos in art_dict.items():
                # Ajusta para não ultrapassar limite
                if pts_acumulado_ru + pontos > LIMITE_RESP:
                    pontos_aj = max(0, LIMITE_RESP - pts_acumulado_ru)
                else:
                    pontos_aj = pontos
                if pontos_aj <= 0:
                    continue

                # Aplica na matriz carreira
                for i, linha in enumerate(carreira):
                    d = linha[0]
                    if d.year == data_art.year and d.month == data_art.month and d.day == data_art.day:
                        carreira[i][7] = pontos_aj
                        pts_acumulado_ru += pontos_aj
                        break   

            ### ---------- LIVROS ---------- ###
            if "livros_lista" not in st.session_state:
                st.session_state.livros_lista = []
            if "pts_livros" not in st.session_state:
                st.session_state.pts_livros = 0

            if st.checkbox("Quantidade de Publicações de Livros e Capítulos", value=False):
                cols = st.columns([1, 1, 1, 1])
                with cols[0]: 
                    qntd_org_livros = st.number_input("Publicações como 'Organizador de Livro'", min_value=0, key="org")
                with cols[1]: 
                    qntd_capitulos = st.number_input("Capitulos Publicados", min_value=0, key="cap")
                with cols[2]: 
                    qntd_livros_completos = st.number_input("Livros Completos Publicados", min_value=0, key="lv")
                with cols[3]:
                    data_livros = st.date_input("Data de Publicação", format="DD/MM/YYYY", value=MIN_DATE, min_value=MIN_DATE, max_value=MAX_DATE, key="dt_livros")
                    if st.button("Adicionar", key="livros"):
                        if qntd_org_livros > 0 or qntd_capitulos > 0 or qntd_livros_completos > 0:
                            st.session_state.livros_lista.append((qntd_org_livros, qntd_capitulos, qntd_livros_completos, data_livros))
                        else:
                            st.error("Todas as informações precisam ser preenchidas.")

            total_pts = 0
            for org, cap, lv, data_liv in st.session_state.livros_lista:
                total_pts += (org * 1) + (cap * 4) + (lv * 6)

            st.session_state.pts_livros = total_pts
            pts_livros = st.session_state.pts_livros if 'pts_livros' in st.session_state else 0
            
            liv_dict = {}
            for org, cap, lv, data_liv in st.session_state.livros_lista:
                pontos = 0
                if org is not None and org != 0:
                    pontos += org * 1
                if cap is not None and cap != 0:
                    pontos += cap * 4
                if lv is not None and lv != 0:
                    pontos += lv * 6

                if data_liv in liv_dict:
                    liv_dict[data_liv] += pontos
                else:
                    liv_dict[data_liv] = pontos

            for data_liv, pontos in liv_dict.items():
                # Ajusta para não ultrapassar limite
                if pts_acumulado_ru + pontos > LIMITE_RESP:
                    pontos_aj2 = max(0, LIMITE_RESP - pts_acumulado_ru)
                else:
                    pontos_aj2 = pontos
                if pontos_aj2 <= 0:
                    continue

                # Aplica na matriz carreira
                for i, linha in enumerate(carreira):
                    d = linha[0]
                    if d.year == data_liv.year and d.month == data_liv.month and d.day == data_liv.day:
                        carreira[i][7] = pontos_aj2
                        pts_acumulado_ru += pontos_aj2
                        break

            ### ---------- PESQUISAS CIENTÍFICAS ---------- ###
            if "pesquisas_lista" not in st.session_state:
                st.session_state.pesquisas_lista = []
            if "pts_pesquisas" not in st.session_state:
                st.session_state.pts_pesquisas = 0

            if st.checkbox("Quantidade de Publicações de Pesquisas Científicas Aprovadas", value=False):
                cols = st.columns([1, 1, 1, 1, 1])
                with cols[0]: 
                    qntd_estadual = st.number_input("Estadualmente",min_value = 0, key="est")
                with cols[1]: 
                    qntd_regional = st.number_input("Regionalmente",min_value = 0, key="reg")
                with cols[2]: 
                    qntd_nacional = st.number_input("Nacionalmente",min_value = 0, key="nac")
                with cols[3]:
                    qntd_internacional = st.number_input("Internacionalmente",min_value = 0, key="inter")
                with cols[4]:
                    data_pesquisas = st.date_input("Data de Aprovação", format="DD/MM/YYYY", value=MIN_DATE, min_value=MIN_DATE, max_value=MAX_DATE, key="dt_pesquisas")
                    if st.button("Adicionar", key="pesquisas"):
                        if qntd_estadual > 0 or qntd_regional > 0 or qntd_nacional > 0 or qntd_internacional > 0:
                            st.session_state.pesquisas_lista.append((qntd_estadual, qntd_regional, qntd_nacional, qntd_internacional, data_pesquisas))
                        else:
                            st.error("Todas as informações precisam ser preenchidas.")
                
            total_pts = 0
            for est, reg, nac, inter, data_ in st.session_state.pesquisas_lista:
                total_pts += (est * 1) + (reg * 3) + (nac * 3) + (inter * 4)

            st.session_state.pts_pesquisas = total_pts
            pts_pesquisas = st.session_state.pts_pesquisas if 'pts_pesquisas' in st.session_state else 0

            pesq_dict = {}
            for est, reg, nac, inter, data_pesq in st.session_state.pesquisas_lista:
                pontos = 0
                if est is not None and est != 0:
                    pontos += est * 1
                if reg is not None and reg != 0:
                    pontos += reg * 3
                if nac is not None and nac != 0:
                    pontos += nac * 3
                if inter is not None and inter != 0:
                    pontos += inter * 4

                if data_pesq in pesq_dict:
                    pesq_dict[data_pesq] += pontos
                else:
                    pesq_dict[data_pesq] = pontos

            for data_pesq, pontos in pesq_dict.items():
                # Ajusta para não ultrapassar limite
                if pts_acumulado_ru + pontos > LIMITE_RESP:
                    pontos_aj2 = max(0, LIMITE_RESP - pts_acumulado_ru)
                else:
                    pontos_aj2 = pontos
                if pontos_aj2 <= 0:
                    continue

                # Aplica na matriz carreira
                for i, linha in enumerate(carreira):
                    d = linha[0]
                    if d.year == data_pesq.year and d.month == data_pesq.month and d.day == data_pesq.day:
                        carreira[i][7] = pontos_aj2
                        pts_acumulado_ru += pontos_aj2
                        break

            ### ---------- REGISTROS DE PATENTES OU CULTIVAR ---------- ###
            if "patentes_lista" not in st.session_state:
                st.session_state.patentes_lista = []
            if "pts_patentes" not in st.session_state:
                st.session_state.pts_patentes = 0

            if st.checkbox("Quantidade de Registros de Patentes ou Cultivar", value=False):
                cols = st.columns([1, 1, 1])
                with cols[0]: 
                    qntd_patente = st.number_input("Patente", min_value=0, key="pat")
                with cols[1]: 
                    qntd_cultivar = st.number_input("Cultivar", min_value=0, key="cult")
                with cols[2]:
                    data_patentes = st.date_input("Data de Registro", format="DD/MM/YYYY", value=MIN_DATE, min_value=MIN_DATE, max_value=MAX_DATE, key="dt_patentes")
                    if st.button("Adicionar", key="patentes"):
                        if qntd_patente > 0 or qntd_cultivar > 0:
                            st.session_state.patentes_lista.append((qntd_patente, qntd_cultivar, data_patentes))
                        else:
                            st.error("Todas as informações precisam ser preenchidas.")

            total_pts = 0
            for pat, cult, data_pat in st.session_state.patentes_lista:
                total_pts += (pat * 8) + (cult * 8)

            st.session_state.pts_patentes = total_pts
            pts_patentes = st.session_state.pts_patentes if 'pts_patentes' in st.session_state else 0

            pat_dict = {}
            for pat, cult, data_pat in st.session_state.patentes_lista:
                pontos = 0
                if pat is not None and pat != 0:
                    pontos += pat * 8
                if cult is not None and cult != 0:
                    pontos += cult * 8

                if data_pat in pat_dict:
                    pat_dict[data_pat] += pontos
                else:
                    pat_dict[data_pat] = pontos

            for data_pat, pontos in pat_dict.items():
                # Ajusta para não ultrapassar limite
                if pts_acumulado_ru + pontos > LIMITE_RESP:
                    pontos_aj2 = max(0, LIMITE_RESP - pts_acumulado_ru)
                else:
                    pontos_aj2 = pontos
                if pontos_aj2 <= 0:
                    continue

                # Aplica na matriz carreira
                for i, linha in enumerate(carreira):
                    d = linha[0]
                    if d.year == data_pat.year and d.month == data_pat.month and d.day == data_pat.day:
                        carreira[i][7] = pontos_aj2
                        pts_acumulado_ru += pontos_aj2
                        break
            ### ---------- CURSOS ---------- ###
            valores_curso = {
                'Nenhum': None,
                'Estágio Pós-Doutoral no Orgão (6 meses)': 6,   
                'Pós-Doutorado (6 a 12 meses)': 8,   
                'Pós-Doutorado (13 a 24 meses)': 12,  
                'Pós-Doutorado (25 a 48 meses)': 24,
                'Pós-Doutorado (maior que 48 meses)': 48  
            }

            if "pts_cursos_lista" not in st.session_state:
                st.session_state.pts_cursos_lista = []
            if "pts_cursos_total" not in st.session_state:
                st.session_state.pts_cursos_total = 0

            if st.checkbox("Cursos e Treinamentos", value=False):
                cols = st.columns([1, 1, 1])
                with cols[0]:
                    qntd_curso = st.number_input("Quantidade de Cursos", min_value=0)
                with cols[1]:
                    tipo_doc = st.selectbox("Tipo", list(valores_curso.keys()))
                with cols[2]:
                    data_cursos = st.date_input("Data de Conclusão", format="DD/MM/YYYY", value=MIN_DATE, min_value=MIN_DATE, max_value=MAX_DATE, key="dt_cursos")
                    if st.button("Adicionar", key="cursos"):
                        if qntd_curso > 0 and tipo_doc != 'Nenhum':
                            pontos_curso = qntd_curso * valores_curso[tipo_doc]
                            st.session_state.pts_cursos_lista.append((qntd_curso, tipo_doc, data_cursos, pontos_curso))
                        else:
                            st.error("Todas as informações precisam ser preenchidas.")

            tot_pts_c = 0
            for qntd_c, tipo_c, data_curso, _ in st.session_state.pts_cursos_lista:
                pontos_cursos = valores_curso.get(tipo_c, 0)
                restantes = max(0, 144 - tot_pts_c)
                aproveitados = min(pontos_cursos * qntd_c, restantes)  # multiplica pela quantidade
                tot_pts_c += aproveitados

            st.session_state.pts_cursos_total = tot_pts_c
            pts_cursos = st.session_state.pts_cursos_total if 'pts_cursos_total' in st.session_state else 0
            
            cursos_ordenados = sorted(st.session_state.pts_cursos_lista, key=lambda data: data[2])
            for curso in cursos_ordenados:
                pontos_titulo = curso[3]
                pontos_restantes = max(0, LIMITE_RESP - pts_acumulado_ru)
                pontos_aproveitados = min(pontos_titulo, pontos_restantes)
                
                if pontos_aproveitados > 0:
                    # Encontra a data correspondente na matriz carreira
                    for i, linha in enumerate(carreira):
                        d = linha[0]
                        if d.year == curso[2].year and d.month == curso[2].month and d.day == curso[2].day:
                            carreira[i][6] += pontos_aproveitados  # Supondo que a coluna 6 é para cursos
                            pts_acumulado_ru += pontos_aproveitados
                            break

            pts_responsabilidade_unic = pts_artigos + pts_livros + pts_pesquisas + pts_patentes + pts_cursos 
            if pts_responsabilidade_unic >= 144: pts_responsabilidade_unic = 144
            
####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####
        ### ---------- RESULTADOS ---------- ###
        with sub_tabs[2]:
            pts_responsabilidade =  pts_responsabilidade_mensais_total + pts_responsabilidade_unic
            if pts_responsabilidade >= 144: pts_responsabilidade = 144
            
            ### ---------- MENSAIS ---------- ### 
            st.title("MENSAIS")
            coll = st.columns(3)
            with coll[0]:  # Mostrar comissões cadastradas
                if st.session_state.comissao_lista:
                    st.write("**Comissão(es) Cadastrada(s):**")
                    cols = st.columns(1)
                    for idx, (_, cargo, meses) in enumerate(st.session_state.comissao_lista):
                        pts = pontuacao_cargos.get(cargo,0)
                        col = cols[idx % 1]
                        with col:
                            st.write(f"{cargo} [{pts} ponto(s)] → Durante {meses} mês(es)")
                            if st.button("Remover", key=f"remover_comissao{idx}"):
                                st.session_state.comissao_lista = [
                                    item for i, item in enumerate(st.session_state.comissao_lista) if i != idx
                                ]
            with coll[1]: # Mostrar funções comissionadas cadastradas
                if st.session_state.func_c_lista:
                    st.write("**Função(es) Comissionada(s) Cadastrada(s):**")
                    cols = st.columns(1)
                    for idx2, (inicio, func, meses) in enumerate(st.session_state.func_c_lista):
                        pts = pontuacao_func_c.get(func, 0)
                        col = cols[idx2 % 1]
                        with col:
                            st.write(f"{func} [{pts} ponto(s)] → Durante {meses} mês(es)")
                            if st.button("Remover", key=f"remover_func_c{idx2}"):
                                st.session_state.func_c_lista = [
                                    item for i, item in enumerate(st.session_state.func_c_lista) if i != idx2
                                ]

            with coll[2]:  # Mostrar funções designadas cadastradas
                if st.session_state.func_d_lista:
                    st.write("**Função(es) Designada(s) Cadastrada(s):**")
                    cols = st.columns(1)
                    for idx3, (inicio, meses) in enumerate(st.session_state.func_d_lista):
                        col = cols[idx3 % 1]
                        with col:
                            st.write(f" 1 Função [0.333 ponto(s)] → Durante {meses} mês(es)")
                            if st.button("Remover", key=f"remover_func_d{idx3}"):
                                st.session_state.func_d_lista = [
                                    item for i, item in enumerate(st.session_state.func_d_lista) if i != idx3
                                ]

            with coll[0]:  # Mostrar atuações como agente cadastradas
                if st.session_state.agente_lista:
                    st.write("**Atuação(es) como Agente Cadastrada(s):**")
                    cols = st.columns(1)
                    for idx4, (inicio, at, meses) in enumerate(st.session_state.agente_lista):
                        pts = pontuacao_agente.get(at, 0)
                        col = cols[idx4 % 1]
                        with col:
                            st.write(f"Atuação: {at} [{pts} ponto(s)] → Durante {meses} mês(es)")
                            if st.button("Remover", key=f"remover_agente{idx4}"):
                                st.session_state.agente_lista = [
                                    item for i, item in enumerate(st.session_state.agente_lista) if i != idx4
                                ]

            with coll[1]: # Mostrar atuações em conselho cadastradas
                if st.session_state.conselho_lista:
                    st.write("**Atuação(es) em Conselho(s) Cadastrada(s):**")
                    cols = st.columns(1)
                    for idx5, (inicio, meses) in enumerate(st.session_state.conselho_lista):
                        col = cols[idx5 % 1]
                        with col:
                            st.write(f"1 Atuação em Conselho [0.333 ponto(s)] → Durante {meses} mês(es)")
                            if st.button("Remover", key=f"remover_conselho{idx5}"):
                                st.session_state.conselho_lista = [
                                    item for i, item in enumerate(st.session_state.conselho_lista) if i != idx5
                                ]

            with coll[2]: # Mostrar atuações prioritárias cadastradas
                if st.session_state.prioritaria_lista:
                    st.write("**Atuação(es) Prioritária(s) Cadastrada(s):**")
                    cols = st.columns(1)
                    for idx6, (inicio, meses) in enumerate(st.session_state.prioritaria_lista):
                        col = cols[idx6 % 1]
                        with col:
                            st.write(f"1 Atuação Prioritária [0.333 ponto(s)] → Durante {meses} mês(es)")
                            if st.button("Remover", key=f"remover_prioritaria{idx6}"):
                                st.session_state.prioritaria_lista = [
                                    item for i, item in enumerate(st.session_state.prioritaria_lista) if i != idx6
                                ]
            
            ### ---------- ÚNICAS ---------- ###   
            st.title("ÚNICAS")
            coll2 = st.columns(3)
            with coll2[0]:  # Mostrar artigos cadastradas
                if st.session_state.artigos_lista:
                    st.write("**Artigo(s) Cadastrado(s):**")
                    cols = st.columns(2)
                    for idx, (nid, id_, data) in enumerate(st.session_state.artigos_lista):
                        col = cols[idx % 2]
                        with col:
                            st.write(f"NÃO Indexados: {nid} | Indexados: {id_} | Data: {data.strftime('%d/%m/%Y')}")
                            if st.button("Remover", key=f"remover_artigo{idx}"):
                                st.session_state.artigos_lista = [
                                    item for i, item in enumerate(st.session_state.artigos_lista) if i != idx
                                ]
            
            with coll2[1]: # Mostrar livros cadastradas
                if st.session_state.livros_lista:
                    st.write("**Livro(s) ou Capitulo(s) Cadastrado(s):**")
                    cols = st.columns(2)
                    for idx2, (org, cap, lv, data) in enumerate(st.session_state.livros_lista):
                        col = cols[idx2 % 2]
                        with col:
                            st.write(f"Organizador: {org} | Capitulos: {cap}  Livro Completo: {lv} | Data: {data.strftime('%d/%m/%Y')}")
                            if st.button("Remover", key=f"remover_livro{idx2}"):
                                st.session_state.livros_lista = [
                                    item for i, item in enumerate(st.session_state.livros_lista) if i != idx2
                                ]

            with coll2[2]: # Mostrar pesquisas cadastradas
                if st.session_state.pesquisas_lista:
                    st.write("**Pesquisa(s) Aprovada(s) Cadastrada(s):**")
                    cols = st.columns(1)
                    for idx3, (est, reg, nac, inter, data) in enumerate(st.session_state.pesquisas_lista):
                        col = cols[idx3 % 1]
                        with col:
                            st.write(f"Estadualmente: {est} | Regionalmente: {reg} | Nacionalmente: {nac} | Internacionalmente: {inter} | Data: {data.strftime('%d/%m/%Y')}")
                            if st.button("Remover", key=f"remover_pesquisa{idx3}"):
                                st.session_state.pesquisas_lista = [
                                    item for i, item in enumerate(st.session_state.pesquisas_lista) if i != idx3
                                ]

            with coll2[0]: # Mostrar registros cadastradas
                if st.session_state.patentes_lista:
                    st.write("**Patente(s) ou Cultivar(es) Cadastrado(s):**")
                    cols = st.columns(3)
                    for idx4, (pat, cult, data) in enumerate(st.session_state.patentes_lista):
                        col = cols[idx4 % 3]
                        with col:
                            st.write(f"Patentes: {pat} | Cultivar: {cult} | Data: {data.strftime('%d/%m/%Y')}")
                            if st.button("Remover", key=f"remover_patente{idx4}"):
                                st.session_state.patentes_lista = [
                                    item for i, item in enumerate(st.session_state.patentes_lista) if i != idx4
                                ]

            with coll2[1]: # Mostrar cursos cadastradas
                if st.session_state.pts_cursos_lista:
                    st.write("**Curso(s) Cadastrado(s):**")
                    cols = st.columns(3)
                    for idx5, (qntd, tipo, data, _) in enumerate(st.session_state.pts_cursos_lista):
                        col = cols[idx5 % 3]
                        with col:
                            st.write(f"{qntd} → {tipo} | Data: {data.strftime('%d/%m/%Y')}")
                            if st.button("Remover", key=f"remover_doc{idx5}"):
                                st.session_state.pts_cursos_lista = [
                                    item for i, item in enumerate(st.session_state.pts_cursos_lista) if i != idx5
                                ]

### ---------- CONCLUIDO ---------- ###
####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####
### ---------- CALCULO MULTIPLO ---------- ###
with tabs[1]:
    if "file_reset" not in st.session_state:
        st.session_state.file_reset = 0

    st.session_state.arquivo = st.file_uploader("Arquivo", type=["xlsx","xls"], key=f"wb_{st.session_state.file_reset}")

    if st.session_state.arquivo is not None:
        calcular_planilha(st.session_state.arquivo)

### ---------- NÃO CONCLUIDO ---------- ###
####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####   
    ### ---------- ACUMULADO ---------- ###

    if "obrigatorios" in st.session_state and st.session_state.obrigatorios:
        pontos_ue = st.session_state.obrigatorios[-1][1]
    else:
        pontos_ue = 0

    for i in range(DATA_CONCLUSAO):
        if i == 0:
            carreira[i][9] = carreira[i][2] + carreira[i][4] + carreira[i][5] + carreira[i][6] + carreira[i][7] + carreira[i][8] + pontos_ue 
        else:
            carreira[i][9] = carreira[i-1][9] + carreira[i][2] + carreira[i][4] + carreira[i][5] + carreira[i][6] + carreira[i][7] + carreira[i][8] 
    
    ### ---------- CONCLUIDO ---------- ###
####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####
with tabs[2]:
    ### ---------- CÁLCULO DE TEMPO ---------- ###
    resultado_niveis = []

    # Dados iniciais
    data_inicio = carreira[0][0]  # primeira data 
    evolucao = None
    meses_ate_evolucao = None
    pts_resto = None

    for i in range(DATA_CONCLUSAO):
        data_atual = carreira[i][0]
        pontos = carreira[i][9]

        ano = data_atual.year - data_inicio.year
        mes = data_atual.month - data_inicio.month
        meses_passados = ano*12 + mes

        data_prevista18 = data_inicio + relativedelta(months=18)
        data_prevista12 = data_inicio + relativedelta(months=12)
        
        if meses_passados < 12:
            continue
        
        if data_prevista12 <= data_atual < data_prevista18 :
            if pontos >= 96:
                evolucao = data_atual
                meses_ate_evolucao = meses_passados
                pts_resto = pontos - 48
                break

        if data_atual >= data_prevista18:
            if pontos >= 48:
                evolucao = data_atual
                meses_ate_evolucao = meses_passados
                pts_resto = pontos - 48
                break
        
    diff = relativedelta(evolucao, data_inicial)
    qtd_meses = diff.years * 12 + diff.months
    desempenho = aperfeicoamento = 0
    for linha in carreira:
        data = linha[0]
        if data <= evolucao:
            desempenho += linha[2] 
            aperfeicoamento += linha[5]

    col = st.columns(2)
    col[0].metric(f"Pontos de Desempenho:", value=round(desempenho,4))
    col[1].metric(f"Pontos de Aperfeiçoamento:", value=round(aperfeicoamento,4))
    
    pendencias = False
    motivo = ""

    if not evolucao:
        pendencias = True
        motivo = "Não atingiu pontuação mínima"
    elif round(aperfeicoamento, 4) < 5.4:
        pendencias = True
        motivo = "Não atingiu requisito de Aperfeiçoamento"
    elif round(desempenho, 4) < 2.4:
        pendencias = True
        motivo = "Não atingiu requisito de Desempenho"

    if pendencias:
        resultado_niveis.append({
            "Data da Próxima Evolução": "-",
            "Meses Gastos para Evolução": "-",
            "Pontos Remanescentes": "-",
            "Status": "Não apto a evoluir",
            "Motivo": motivo
        })
    else:
        resultado_niveis.append({
            "Data da Próxima Evolução": evolucao.strftime("%d/%m/%Y"),
            "Meses Gastos para Evolução": meses_ate_evolucao,
            "Pontos Remanescentes": round(pts_resto, 4),
            "Status": "Apto",
            "Motivo": "-"
        })

    df_resultados = pd.DataFrame(resultado_niveis)
    st.dataframe(df_resultados, hide_index=True, height=700)

    ### ---------- CONCLUIDO ---------- ###
####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####
### ---------- DATAFRAME DE CONTROLE ---------- ###

    st.divider()
    # Criar DataFrame com as colunas
    df_carreira = pd.DataFrame(carreira, columns=[
        "Data",
        "Pontos Base (0.2)",
        "Pontos Base Descontado",
        "Desempenho",
        "Desempenho Descontado",
        "Aperfeiçoamento",
        "Titulação",
        "Resp. Únicas",
        "Resp. Mensais",
        "Total Acumulado" 
    ])

    # Arredondar para 4 casas decimais
    df_carreira = df_carreira.round(4)

    # Selecionar meses para exibição (primeiros 12 + um por ano após)
    meses_exibir = list(range(DATA_CONCLUSAO))
    df_exibir = df_carreira.iloc[meses_exibir]

    # Configurar formatação de exibição
    pd.options.display.float_format = '{:.4f}'.format

    # Mostrar tabela com colunas selecionadas
    st.dataframe(
        df_exibir[[
            "Data",
            "Pontos Base (0.2)",
            "Pontos Base Descontado",
            "Desempenho",
            "Desempenho Descontado",
            "Aperfeiçoamento",
            "Titulação",
            "Resp. Únicas",
            "Resp. Mensais",
            "Total Acumulado" 
        ]],
        height=600,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Data": st.column_config.DateColumn(format="DD/MM/YYYY"),
            "Pontos Base (0.2)": st.column_config.NumberColumn(format="%.4f"),
            "Pontos Base Descontado": st.column_config.NumberColumn(format="%.4f"),
            "Desempenho": st.column_config.NumberColumn(format="%.4f"),
            "Desempenho Descontado": st.column_config.NumberColumn(format="%.4f"),
            "Aperfeiçoamento": st.column_config.NumberColumn(format="%.4f"),
            "Titulação": st.column_config.NumberColumn(format="%.4f"),
            "Resp. Únicas":st.column_config.NumberColumn(format="%.4f"),
            "Resp. Mensais": st.column_config.NumberColumn(format="%.4f"),
            "Total Acumulado": st.column_config.NumberColumn(format="%.4f")
        }
    )


    ### ---------- CONCLUIDO ---------- ###
####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####