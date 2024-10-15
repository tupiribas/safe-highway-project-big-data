import pandas as pd
from django.shortcuts import render
import plotly.express as px
import plotly.io as pio
import os
from django.conf import settings


def grafico_acidentes(request):
    # Construir o caminho completo para o arquivo CSV dentro da pasta media
    csv_path = os.path.join(settings.MEDIA_ROOT, 'tb_ocorrencias.csv')

    # Carregar o arquivo CSV em chunks
    chunksize = 10000
    chunk_list = []
    for chunk in pd.read_csv(csv_path, chunksize=chunksize, low_memory=True):
        chunk_list.append(chunk)

    df = pd.concat(chunk_list)

    # Garantir que a coluna 'data_inversa' seja convertida corretamente para datetime
    df['data_inversa'] = pd.to_datetime(df['data_inversa'], dayfirst=True, errors='coerce')

    # Gráfico de Acidentes por Ano
    start_date_ano = request.GET.get('start_date_ano')
    end_date_ano = request.GET.get('end_date_ano')

    df_ano = df.copy()
    if start_date_ano and end_date_ano:
        start_date_ano = pd.to_datetime(start_date_ano)
        end_date_ano = pd.to_datetime(end_date_ano)
        df_ano = df_ano[(df_ano['data_inversa'] >= start_date_ano) & (df_ano['data_inversa'] <= end_date_ano)]

    df_ano['ano'] = df_ano['data_inversa'].dt.year
    acidentes_por_ano = df_ano['ano'].value_counts().sort_index()

    df_acidentes_ano = pd.DataFrame({
        'ano': acidentes_por_ano.index,
        'num_acidentes': acidentes_por_ano.values
    })

    title_ano = f'Total de Acidentes por Ano ({start_date_ano.strftime("%d/%m/%Y")} até {end_date_ano.strftime("%d/%m/%Y")})' if start_date_ano and end_date_ano else 'Total de Acidentes por Ano (2007 até 2020)'

    fig1 = px.line(df_acidentes_ano, x='ano', y='num_acidentes', title=title_ano, labels={'ano': 'Ano', 'num_acidentes': 'Número de Acidentes'})

    # Gráfico de Acidentes por Estado
    start_date_estado = request.GET.get('start_date_estado')
    end_date_estado = request.GET.get('end_date_estado')

    df_estado = df.copy()
    if start_date_estado and end_date_estado:
        start_date_estado = pd.to_datetime(start_date_estado)
        end_date_estado = pd.to_datetime(end_date_estado)
        df_estado = df_estado[(df_estado['data_inversa'] >= start_date_estado) & (df_estado['data_inversa'] <= end_date_estado)]

    acidentes_por_estado = df_estado['uf'].value_counts()

    title_ano_estado = f'Total de Acidentes por Estado ({start_date_ano.strftime("%d/%m/%Y")} até {end_date_ano.strftime("%d/%m/%Y")})' if start_date_ano and end_date_ano else 'Total de Acidentes por Estado (2007 até 2020)'
    # Gráfico de acidentes por estado
    acidentes_por_estado = df_estado['uf'].value_counts()
    fig2 = px.bar(
        acidentes_por_estado, x=acidentes_por_estado.index,
        y=acidentes_por_estado.values, title=title_ano_estado,
        labels={'uf': 'Estado (UF)', 'acidentes_por_estado': 'QTDE'}
    )
    
    # Gráfico de Tipos de Acidentes
    acidentes_por_tipo = df['tipo_acidente'].value_counts()
    top_3_acidentes = acidentes_por_tipo.nlargest(4)
    outros = acidentes_por_tipo.iloc[4:].sum()
    acidentes_agrupados = pd.concat([top_3_acidentes, pd.Series([outros], index=['Outros'])])

    fig3 = px.pie(acidentes_agrupados, names=acidentes_agrupados.index, values=acidentes_agrupados.values, title='Distribuição dos Tipos de Acidentes')

    # Gráfico de Horários Mais Comuns
    # Extrair a hora da coluna 'horario' e contar as ocorrências de cada horário
    df['hora'] = pd.to_datetime(df['horario'], errors='coerce').dt.hour
    horarios_mais_comuns = df['hora'].value_counts().sort_index()

    df_horarios = pd.DataFrame({
        'hora': horarios_mais_comuns.index,
        'num_acidentes': horarios_mais_comuns.values
    })

    fig4 = px.bar(df_horarios, x='hora', y='num_acidentes', title='Horários Mais Comuns de Acidentes', labels={'hora': 'Hora do Dia', 'num_acidentes': 'Número de Acidentes'})

    # Transformar os outros acidentes em uma lista de dicionários para exibir no template
    outros_acidentes_lista = [{'tipo': tipo, 'quantidade': quantidade} for tipo, quantidade in acidentes_por_tipo.items()]

    # Gerar os gráficos interativos em HTML
    graph1 = pio.to_html(fig1, full_html=False)
    graph2 = pio.to_html(fig2, full_html=False)
    graph3 = pio.to_html(fig3, full_html=False)
    graph4 = pio.to_html(fig4, full_html=False)

    # Passar todos os gráficos para o template
    return render(request, 'graphics/graphics.html', {
        'grafico_ano': graph1,
        'grafico_estado': graph2,
        'grafico_tipo': graph3,
        'grafico_horario': graph4,  # Novo gráfico de horários
        'outros_acidentes': outros_acidentes_lista
    })


    title_ano_estado = f'Total de Acidentes por Estado ({start_date_ano.strftime("%d/%m/%Y")} até {end_date_ano.strftime("%d/%m/%Y")})' if start_date_ano and end_date_ano else 'Total de Acidentes por Estado (2007 até 2020)'
    # Gráfico de acidentes por estado
    acidentes_por_estado = df_estado['uf'].value_counts()
    fig2 = px.bar(
        acidentes_por_estado, x=acidentes_por_estado.index,
        y=acidentes_por_estado.values, title=title_ano_estado,
        labels={'uf': 'Estado (UF)', 'acidentes_por_estado': 'QTDE'}
    )