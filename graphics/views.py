from django.shortcuts import render
import plotly.express as px
import plotly.io as pio
import pandas as pd


def grafico_acidentes(request):
    # Carregar os dados do CSV
    df = pd.read_csv('files\\tb_ocorrencias.csv')

    # Garantir que a coluna 'data_inversa' seja convertida corretamente para datetime
    df['data_inversa'] = pd.to_datetime(
        df['data_inversa'],
        dayfirst=True, errors='coerce')

    # Verificar e formatar as datas no padrão 'DD/MM/AAAA'
    df['data_formatada'] = df['data_inversa'].dt.strftime('%d/%m/%Y')

    # Extrair o ano da data para fazer a contagem de acidentes por ano
    df['ano'] = df['data_inversa'].dt.year

    # Formatar as datas no padrão desejado, por exemplo, 'DD/MM/AAAA'
    # df['ano'] = df['ano'].strftime('%d/%m/%Y')

    # Contagem de acidentes por ano
    acidentes_por_ano = df['ano'].value_counts().sort_index()

    # Criar um DataFrame com o número de acidentes por ano
    df_acidentes_ano = pd.DataFrame({
        'ano': acidentes_por_ano.index,
        'num_acidentes': acidentes_por_ano.values
    })

    # Criar o gráfico de linha usando Plotly
    fig = px.line(
        df_acidentes_ano, x='ano', y='num_acidentes',
        title='Total de Acidentes por Ano (2007 até 2020)',
        labels={'ano': 'Ano', 'num_acidentes': 'Número de Acidentes'}
    )

    # Gerar o gráfico interativo em HTML
    graph = pio.to_html(fig, full_html=False)

    # Passar o gráfico para o template
    return render(request, 'graphics/graphics.html', {'grafico': graph})
