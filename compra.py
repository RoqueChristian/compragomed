import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime
import plotly.express as px 
import locale

try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR')
    except locale.Error:
        print("Erro ao definir a localidade para português do Brasil.")

st.set_page_config(page_title="Go MED SAÚDE", page_icon=":bar_chart:", layout="wide")

df = pd.read_csv('df_compra.csv')

# Converter as colunas de data para o tipo datetime, tratando erros de parsing
df['data entrega prevista'] = pd.to_datetime(df['data entrega prevista'], errors='coerce')
df['data entrada'] = pd.to_datetime(df['data entrada'], errors='coerce')
df['data emissao'] = pd.to_datetime(df['data emissao'], format='%d/%m/%Y', errors='coerce')

def formatar_moeda(valor, simbolo_moeda="R$"):
    if pd.isna(valor):
        return ''
    return f"{simbolo_moeda} {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def aplicar_filtros(df, ano='todos', mes='todos', usuario='todos'):
    df_filtrado = df.copy()
    if ano != 'todos':
        df_filtrado = df_filtrado[df_filtrado['ano'] == ano]
    if mes != 'todos':
        df_filtrado = df_filtrado[df_filtrado['mes'] == mes]
    if usuario != 'todos':
        df_filtrado = df_filtrado[df_filtrado['usuario'] == usuario]
    return df_filtrado

col1, col2, col3 = st.columns(3)
with col1:
    ano = st.selectbox("Ano", ['todos'] + sorted(list(df['ano'].unique())))
with col2:
    mes = st.selectbox("Mês", ['todos'] + sorted(list(df['mes'].unique())))
with col3:
    usuario = st.selectbox("Usuário", ['todos'] + sorted(list(df['usuario'].unique())))

df_filtrado = aplicar_filtros(df, ano, mes, usuario)

def calcular_metricas(df):
    qunatidade_total_pedidos = df['numeropedido'].nunique()
    valor_total_pedidos = df['valor liquido item'].sum()
    quantidade_total_itens = df['qtd pedido item'].sum()
    quantidade_pedidos_entregues = df[df['status pedido'] == 'recebido']['numeropedido'].nunique()
    quantidade_pedidos_pendentes = df[df['status pedido'] == 'entrega pendente']['numeropedido'].nunique()
    return qunatidade_total_pedidos, valor_total_pedidos, quantidade_total_itens, quantidade_pedidos_entregues, quantidade_pedidos_pendentes

def card_style(metric_name, value, color="#FFFFFF", bg_color="#262730"):
    return f"""
    <div style="
        padding: 3px;
        border-radius: 5px;
        background-color: {bg_color};
        color: {color};
        text-align: center;
        box-shadow: 1px px 5px rgba(0,0,0,0.2);
    ">
        <h4 style="margin: 0; font-size: 22px;">{metric_name}</h4>
        <h2 style="margin: 5px 0; font-size: 22px;">{value}</h2>
    </div>
    """

# Calcular as métricas COM O DATAFRAME FILTRADO
qtd_total_pedidos, valor_total, qtd_total_itens, qtd_entregues, qtd_pendentes = calcular_metricas(df_filtrado)

col1_metricas, col2_metricas, col3_metricas, col4_metricas, col5_metricas = st.columns([1, 1, 1, 1, 1])

with col1_metricas:
    st.markdown(card_style("QTD Pedidos", qtd_total_pedidos), unsafe_allow_html=True)

with col2_metricas:
    st.markdown(card_style("Valor Total", formatar_moeda(valor_total)), unsafe_allow_html=True)

with col3_metricas:
    st.markdown(card_style("QTD Itens", qtd_total_itens), unsafe_allow_html=True)

with col4_metricas:
    st.markdown(card_style("Pedidos Recebidos", qtd_entregues), unsafe_allow_html=True)

with col5_metricas:
    st.markdown(card_style("Pedidos Pendentes", qtd_pendentes), unsafe_allow_html=True)

st.markdown("---")

# --- GRÁFICOS ---

# Gráfico de Distribuição de Status dos Pedidos
status_counts = df_filtrado['status pedido'].value_counts().reset_index()
status_counts.columns = ['status pedido', 'quantidade']
fig_status = px.pie(status_counts, names='status pedido', values='quantidade',
                        title='<b>Distribuição de Status dos Pedidos</b>')
st.plotly_chart(fig_status, use_container_width=True)


# Gráfico de Valor Total dos Pedidos por Mês (Filtrado)
if not df_filtrado.empty:
    valor_por_mes = df_filtrado.groupby(['ano', 'mes'])['valor liquido item'].sum().reset_index()
    valor_por_mes['data_ref'] = pd.to_datetime(valor_por_mes['ano'].astype(str) + '-' + valor_por_mes['mes'].astype(str) + '-01')
    valor_por_mes = valor_por_mes.sort_values(by='data_ref')
    valor_por_mes['mes_nome'] = valor_por_mes['data_ref'].dt.strftime('%B')
    valor_por_mes['mes_nome'] = valor_por_mes['mes_nome'].str[0].str.upper() + valor_por_mes['mes_nome'].str[1:]
    # Formatar os valores para exibição no gráfico e no hover
    valor_por_mes['valor_formatado'] = valor_por_mes['valor liquido item'].apply(formatar_moeda)
    fig_valor_mes = px.bar(valor_por_mes, x='mes_nome', y='valor liquido item',
                            labels={'valor liquido item': 'Valor Total', 'mes_nome': 'Mês'},
                            title='<b>Valor Total dos Pedidos por Mês (Filtrado)</b>',
                            text='valor_formatado', # Exibir o valor formatado nas barras
                            hover_data={'valor liquido item': ':.2f', 'mes_nome': True},
                            height=700, width=1100)
    fig_valor_mes.update_traces(textposition='outside', textfont_size=28)
    st.plotly_chart(fig_valor_mes, use_container_width=True)
else:
    st.info("Não há dados para exibir o gráfico de valor por mês com os filtros aplicados.")

st.markdown("---")

# Gráfico de Top 10 Fornecedores por Valor Total
top_10_fornecedores_graf = df_filtrado.groupby('fornecedor')['valor liquido item'].sum().nlargest(10).reset_index()
top_10_fornecedores_graf['valor_formatado'] = top_10_fornecedores_graf['valor liquido item'].apply(formatar_moeda)
fig_top_fornecedores = px.bar(top_10_fornecedores_graf, x='fornecedor', y='valor liquido item',
                               labels={'valor liquido item': 'Valor Total', 'fornecedor': 'Fornecedor'},
                               title='<b>Top 10 Fornecedores por Valor Total</b>',
                               text='valor_formatado', 
                               hover_data={'valor liquido item': ':.2f', 'fornecedor': True}, 
                               height=900, width=1100) 
fig_top_fornecedores.update_traces(textposition='outside', textfont_size=28)
st.plotly_chart(fig_top_fornecedores, use_container_width=True)


# Gráfico de Comparativo de Produtos Comprados entre Meses
if not df.empty:
    ano_atual = df['ano'].max()
    mes_atual = df[df['ano'] == ano_atual]['mes'].max()

    ano_anterior = ano_atual
    mes_anterior = mes_atual - 1
    if mes_anterior < 1:
        mes_anterior = 12
        ano_anterior -= 1

    df_atual_prod = df[(df['ano'] == ano_atual) & (df['mes'] == mes_atual)].groupby('descricao produto')['total itens'].sum().reset_index()
    df_atual_prod['Mês/Ano'] = f'{mes_atual}/{ano_atual}'
    df_anterior_prod = df[(df['ano'] == ano_anterior) & (df['mes'] == mes_anterior)].groupby('descricao produto')['total itens'].sum().reset_index()
    df_anterior_prod['Mês/Ano'] = f'{mes_anterior}/{ano_anterior}'

    df_comparativo_graf = pd.concat([df_atual_prod, df_anterior_prod])

    # Truncar os nomes dos produtos para um máximo de 15 caracteres (ajuste conforme necessário)
    max_chars = 15
    df_comparativo_graf['produto_truncado'] = df_comparativo_graf['descricao produto'].apply(lambda x: (x[:max_chars] + '...') if len(x) > max_chars else x)

    fig_comparativo_prod = px.bar(df_comparativo_graf, x='produto_truncado', y='total itens', color='Mês/Ano',
                                 barmode='group', labels={'total itens': 'Quantidade', 'produto_truncado': 'Produto'},
                                 title=f'<b>Comparativo de Produtos ({mes_anterior}/{ano_anterior} vs {mes_atual}/{ano_atual})</b>',
                                 height=700, width=1100) 
    fig_comparativo_prod.update_layout(
        xaxis=dict(
            tickangle=-45,
            automargin=True
        )
    )
    st.plotly_chart(fig_comparativo_prod, use_container_width=True)
else:
    st.info("Não há dados para exibir o comparativo de produtos entre meses.")

st.markdown("---")


# --- ALERTA DE PEDIDOS ATRASADOS ---
hoje = datetime.now().date()
pedidos_atrasados = df_filtrado[
    (df_filtrado['data entrega prevista'].dt.date < hoje) & (df_filtrado['data entrada'].isna())
]['numeropedido'].unique() 

if len(pedidos_atrasados) > 0:
    st.warning(f"⚠️ Atenção! {len(pedidos_atrasados)} pedidos estão atrasados:")
    # Filtrar o DataFrame original para exibir informações dos pedidos atrasados únicos
    df_pedidos_atrasados_unicos = df_filtrado[df_filtrado['numeropedido'].isin(pedidos_atrasados)][['numeropedido', 'data entrega prevista', 'fornecedor', 'usuario']].drop_duplicates(subset=['numeropedido'])
    # Formatar a coluna de data para o formato brasileiro
    df_pedidos_atrasados_unicos['data entrega prevista'] = df_pedidos_atrasados_unicos['data entrega prevista'].dt.strftime('%d/%m/%Y')
    st.dataframe(df_pedidos_atrasados_unicos)
    st.markdown("---")
# --- FIM DO ALERTA ---



def lista_pedidos(df):
    st.subheader(f"Lista de Pedidos")
    colunas_exibir = ['numeropedido', 'data emissao', 'data entrega prevista', 'fornecedor', 'usuario', 'descricao produto',
                        'prazo', 'tipo produto', 'status pedido']
    df_exibir = df[colunas_exibir].copy() 
    # Formatar as colunas de data
    for col in ['data emissao', 'data entrega prevista']:
        if col in df_exibir.columns:
            df_exibir[col] = df_exibir[col].dt.strftime('%d/%m/%Y')
    st.dataframe(df_exibir)

lista_pedidos(df_filtrado)

def listar_pedidos_pendentes_detalhado(df):
    pedidos_pendentes = df[df['status pedido'] == 'entrega pendente'].copy()
    if not pedidos_pendentes.empty:
        st.subheader("Pedidos Pendentes")
        colunas_exibir = ['numeropedido', 'data emissao', 'data entrega prevista', 'fornecedor', 'total itens', 'valor liquido item']
        pedidos_pendentes_exibir = pedidos_pendentes[colunas_exibir].copy() # Crie uma cópia
        # Formatar as colunas de data
        for col in ['data emissao', 'data entrega prevista']:
            if col in pedidos_pendentes_exibir.columns:
                pedidos_pendentes_exibir[col] = pedidos_pendentes_exibir[col].dt.strftime('%d/%m/%Y')
        pedidos_pendentes_exibir['valor liquido item'] = pedidos_pendentes_exibir['valor liquido item'].apply(lambda x: f'R$ {x:,.2f}'.replace(",", "X").replace(".", ",").replace("X", "."))
        st.dataframe(pedidos_pendentes_exibir)
    else:
        st.info("Não há pedidos com entrega pendente.")

# Usar o DATAFRAME FILTRADO na função
listar_pedidos_pendentes_detalhado(df_filtrado)

def listar_top_10_fornecedores(df):
    df.columns.tolist()


    if df.empty:
        st.info("O DataFrame filtrado está vazio, não é possível listar os top 10 fornecedores.")
        return

    if 'fornecedor' not in df.columns or 'valor liquido item' not in df.columns:
        st.error("Colunas 'fornecedor' ou 'valor liquido item' não encontradas no DataFrame filtrado.")
        return

    total_por_fornecedor = df.groupby('fornecedor')['valor liquido item'].sum()

    if total_por_fornecedor.empty:
        st.info("Não há dados de valor total por fornecedor após o agrupamento com o filtro aplicado.")
        return

    top_10_fornecedores = total_por_fornecedor.sort_values(ascending=False).head(10)

    if not top_10_fornecedores.empty:
        st.subheader("Top 10 Maiores Fornecedores (por Valor Total dos Pedidos)")
        top_10_df = pd.DataFrame({'Fornecedor': top_10_fornecedores.index,
                                    'Valor Total dos Pedidos': top_10_fornecedores.values})
        top_10_df['Valor Total dos Pedidos'] = top_10_df['Valor Total dos Pedidos'].apply(lambda x: f'R$ {x:,.2f}'.replace(",", "X").replace(".", ",").replace("X", "."))
        st.dataframe(top_10_df)
    else:
        st.info("Não há dados suficientes para listar os top 10 fornecedores com o filtro aplicado.")

# Usar o DATAFRAME FILTRADO na função
listar_top_10_fornecedores(df_filtrado)




# Determinar o mês e ano atual e anterior com base nos dados filtrados
if not df.empty:
    ano_atual = df['ano'].max()
    mes_atual = df[df['ano'] == ano_atual]['mes'].max()

    ano_anterior = ano_atual
    mes_anterior = mes_atual - 1
    if mes_anterior < 1:
        mes_anterior = 12
        ano_anterior -= 1

    df_atual = df[(df['ano'] == ano_atual) & (df['mes'] == mes_atual)]
    df_anterior = df[(df['ano'] == ano_anterior) & (df['mes'] == mes_anterior)]

    # Agrupar e contar a quantidade de cada produto no mês anterior
    quantidade_anterior = df_anterior.groupby('descricao produto')['total itens'].sum().reset_index()
    quantidade_anterior.rename(columns={'total itens': f'Quantidade {mes_anterior}/{ano_anterior}'}, inplace=True)

    # Agrupar e contar a quantidade de cada produto no mês atual
    quantidade_atual = df_atual.groupby('descricao produto')['total itens'].sum().reset_index()
    quantidade_atual.rename(columns={'total itens': f'Quantidade {mes_atual}/{ano_atual}'}, inplace=True)

    # Merge dos DataFrames para ter a quantidade dos dois meses lado a lado
    df_comparativo = pd.merge(quantidade_anterior, quantidade_atual, on='descricao produto', how='left').fillna(0)

    st.subheader(f"Comparativo de Produtos Comprados em {mes_anterior}/{ano_anterior} vs {mes_atual}/{ano_atual}:")
    st.dataframe(df_comparativo)

else:
    st.info("Não há dados para análise de produtos com os filtros aplicados.")