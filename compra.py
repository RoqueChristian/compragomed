import pandas as pd
import numpy as np
import streamlit as st

st.set_page_config(page_title="Go MED SAÚDE", page_icon=":bar_chart:", layout="wide")

df = pd.read_csv('df_compra.csv')

def formatar_moeda(valor, simbolo_moeda="R$"):
    if pd.isna(valor):
        return ''
    return f"{simbolo_moeda} {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def aplicar_filtros(df, ano='todos', mes='todos'):
    df_filtrado = df.copy()
    if ano != 'todos':
        df_filtrado = df_filtrado[df_filtrado['ano'] == ano]
    if mes != 'todos':
        df_filtrado = df_filtrado[df_filtrado['mes'] == mes]
    
    return df_filtrado

col1, col2 = st.columns(2)
with col1:
    ano = st.selectbox("Ano", ['todos'] + sorted(list(df['ano'].unique())))
with col2:
    mes = st.selectbox("Mês", ['todos'] + sorted(list(df['mes'].unique())))
    

    df_filtrado = aplicar_filtros(df, ano, mes)

def calcular_metricas(df):
    qunatidade_total_pedidos = df['numeropedido'].nunique()
    valor_total_pedidos = df['valor bruto total itens'].sum()
    quantidade_total_itens = df['total itens'].sum()
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

col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])

with col1:
    st.markdown(card_style("QTD Pedidos", qtd_total_pedidos), unsafe_allow_html=True)

with col2:
    st.markdown(card_style("Valor Total", formatar_moeda(valor_total)), unsafe_allow_html=True)

with col3:
    st.markdown(card_style("QTD Itens", qtd_total_itens), unsafe_allow_html=True)

with col4:
    st.markdown(card_style("Pedidos Recebidos", qtd_entregues), unsafe_allow_html=True)

with col5:
    st.markdown(card_style("Pedidos Pendentes", qtd_pendentes), unsafe_allow_html=True)



st.subheader(f"Lista de Pedodos")
st.dataframe(df)

def listar_pedidos_pendentes_detalhado(df):
    pedidos_pendentes = df[df['status pedido'] == 'entrega pendente'].copy()
    if not pedidos_pendentes.empty:
        st.subheader("Pedidos Pendentes")
        colunas_exibir = ['numeropedido', 'data emissao', 'data entrega prevista', 'fornecedor', 'total itens', 'valor bruto total itens']
        pedidos_pendentes_exibir = pedidos_pendentes[colunas_exibir]
        pedidos_pendentes_exibir['valor bruto total itens'] = pedidos_pendentes_exibir['valor bruto total itens'].apply(lambda x: f'R$ {x:,.2f}'.replace(",", "X").replace(".", ",").replace("X", "."))
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

    if 'fornecedor' not in df.columns or 'valor bruto total itens' not in df.columns:
        st.error("Colunas 'fornecedor' ou 'valor bruto total itens' não encontradas no DataFrame filtrado.")
        return

    total_por_fornecedor = df.groupby('fornecedor')['valor bruto total itens'].sum()

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
if not df_filtrado.empty:
        ano_atual_filtrado = df_filtrado['ano'].max()
        mes_atual_filtrado = df_filtrado[df_filtrado['ano'] == ano_atual_filtrado]['mes'].max()

        ano_anterior_filtrado = ano_atual_filtrado
        mes_anterior_filtrado = mes_atual_filtrado - 1
        if mes_anterior_filtrado < 1:
            mes_anterior_filtrado = 12
            ano_anterior_filtrado -= 1

        df_atual_filtrado = df_filtrado[(df_filtrado['ano'] == ano_atual_filtrado) & (df_filtrado['mes'] == mes_atual_filtrado)]
        df_anterior_filtrado = df_filtrado[(df_filtrado['ano'] == ano_anterior_filtrado) & (df_filtrado['mes'] == mes_anterior_filtrado)]

        # Agrupar e contar a quantidade de cada produto no mês anterior
        quantidade_anterior = df_anterior_filtrado.groupby('descricao produto')['total itens'].sum().reset_index()
        quantidade_anterior.rename(columns={'total itens': f'Quantidade {mes_anterior_filtrado}/{ano_anterior_filtrado}'}, inplace=True)

        # Agrupar e contar a quantidade de cada produto no mês atual
        quantidade_atual = df_atual_filtrado.groupby('descricao produto')['total itens'].sum().reset_index()
        quantidade_atual.rename(columns={'total itens': f'Quantidade {mes_atual_filtrado}/{ano_atual_filtrado}'}, inplace=True)

        # Merge dos DataFrames para ter a quantidade dos dois meses lado a lado
        df_comparativo = pd.merge(quantidade_anterior, quantidade_atual, on='descricao produto', how='left').fillna(0)

        st.subheader(f"Comparativo de Produtos Comprados em {mes_anterior_filtrado}/{ano_anterior_filtrado} vs {mes_atual_filtrado}/{ano_atual_filtrado} (Filtro Aplicado):")
        st.dataframe(df_comparativo)

else:
    st.info("Não há dados para análise de produtos com os filtros aplicados.")