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

    # Garantir que a coluna 'data_inversa' seja convertida corretamente para dt
    df['data_inversa'] = pd.to_datetime(
        df['data_inversa'],
        dayfirst=True, errors='coerce')

    # Adicionar novas visualizações: Gráficos por estado e tipo de acidente
    df['data_formatada'] = df['data_inversa'].dt.strftime('%d/%m/%Y')
    df['ano'] = df['data_inversa'].dt.year

    # Contagem de acidentes por ano
    acidentes_por_ano = df['ano'].value_counts().sort_index()

    # Gráfico de acidentes por ano
    df_acidentes_ano = pd.DataFrame({
        'ano': acidentes_por_ano.index,
        'num_acidentes': acidentes_por_ano.values
    })
    fig1 = px.line(
        df_acidentes_ano, x='ano', y='num_acidentes',
        title='Total de Acidentes por Ano (2007 até 2020)',
        labels={'ano': 'Ano', 'num_acidentes': 'Número de Acidentes'})

    # Novo gráfico de acidentes por estado
    acidentes_por_estado = df['uf'].value_counts()
    fig2 = px.bar(
        acidentes_por_estado, x=acidentes_por_estado.index,
        y=acidentes_por_estado.values, title='Acidentes por Estado',
        labels={'uf': 'Estado (UF)',
                'acidentes_por_estado': 'QTDE'})

    # Gráfico de pie chart por tipo de acidente
    acidentes_por_tipo = df['tipo_acidente'].value_counts()

    top_3_acidentes = acidentes_por_tipo.nlargest(4)

    # Agrupar os restantes em "Outros"
    outros = acidentes_por_tipo.iloc[4:].sum()

    # Capturar os outros tipos de acidentes
    outros_acidentes = acidentes_por_tipo.iloc[3:]

    # Criar um novo DataFrame com os 3 maiores e "Outros"
    acidentes_agrupados = pd.concat(
        [top_3_acidentes, pd.Series([outros], index=['Outros'])])

    # Gerar o gráfico de pizza com os dados agrupados
    fig3 = px.pie(
        acidentes_agrupados, names=acidentes_agrupados.index,
        values=acidentes_agrupados.values,
        title='Distribuição dos Tipos de Acidentes'
    )

    # Transformar os outros acidentes em uma lista de dicionários para exibir no template
    outros_acidentes_lista = [
        {'tipo': tipo, 'quantidade': quantidade} for tipo,
        quantidade in outros_acidentes.items()]

    # Gerar os gráficos interativos em HTML
    graph1 = pio.to_html(fig1, full_html=False)
    graph2 = pio.to_html(fig2, full_html=False)
    graph3 = pio.to_html(fig3, full_html=False)

    # Passar todos os gráficos para o template
    return render(request, 'graphics/graphics.html', {
        'grafico_ano': graph1,
        'grafico_estado': graph2,
        'grafico_tipo': graph3,
        'outros_acidentes': outros_acidentes_lista
    })
