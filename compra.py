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

df['data entrega prevista'] = pd.to_datetime(df['data entrega prevista'], errors='coerce')
df['data entrada'] = pd.to_datetime(df['data entrada'], errors='coerce')
df['data emissao'] = pd.to_datetime(df['data emissao'], format='%d/%m/%Y', errors='coerce')

def formatar_moeda(valor, simbolo_moeda='R$'):
    try:
        valor = float(valor)
        return f"{simbolo_moeda} {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return f"{simbolo_moeda} 0,00"

def aplicar_filtros(df, ano='todos', mes='todos', usuario='todos', situacao='todos', tipo_fornecedor='todos'):
    df_filtrado = df.copy()
    ano_atual = datetime.now().year
    meses_abreviados_num_para_abv = {
        1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
        7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
    }
    meses_abreviados_abv_para_num = {v: k for k, v in meses_abreviados_num_para_abv.items()}

    if ano == 'todos':
        df_filtrado = df_filtrado[df_filtrado['ano'] == ano_atual]
    elif ano != 'todos':
        df_filtrado = df_filtrado[df_filtrado['ano'] == int(ano)]

    if mes == 'todos':
        df_filtrado['mes_nome'] = df_filtrado['mes'].map(meses_abreviados_num_para_abv)
    elif mes != 'todos':
        if mes in meses_abreviados_abv_para_num:
            df_filtrado = df_filtrado[df_filtrado['mes'] == meses_abreviados_abv_para_num[mes]]
            df_filtrado['mes_nome'] = mes
        elif isinstance(mes, int):
            df_filtrado = df_filtrado[df_filtrado['mes'] == mes]
            df_filtrado['mes_nome'] = meses_abreviados_num_para_abv.get(mes)
        else:
            df_filtrado['mes_nome'] = None  

    if usuario != 'todos':
        df_filtrado = df_filtrado[df_filtrado['usuario'] == usuario]

    if situacao != 'todos':
        df_filtrado = df_filtrado[df_filtrado['situacao pedido'] == situacao]

    if tipo_fornecedor != 'todos':
        df_filtrado = df_filtrado[df_filtrado['tipo fornecedor'] == tipo_fornecedor]

    return df_filtrado

ano_atual = datetime.now().year
meses_abreviados_num_para_abv = {
    1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
    7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
}
meses_ano_atual_numericos = sorted(list(df[df['ano'] == ano_atual]['mes'].unique()))
meses_ano_atual_nomes = ['todos'] + [meses_abreviados_num_para_abv[mes] for mes in meses_ano_atual_numericos]

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    anos_unicos = ['todos'] + sorted(list(df['ano'].unique()))
    index_ano_atual = anos_unicos.index(ano_atual) if ano_atual in anos_unicos else 0
    ano = st.selectbox("Ano", anos_unicos, index=index_ano_atual)
with col2:
    mes = st.selectbox("Mês", meses_ano_atual_nomes)
with col3:
    usuario = st.selectbox("Usuário", ['todos'] + sorted(list(df['usuario'].unique())))
with col4:
    situacao = st.selectbox("Situação", ['todos'] + sorted(list(df['situacao pedido'].unique())))
with col5:
    tipo_fornecedor = st.selectbox("Tipo de Fornecedor", ['todos'] + sorted(list(df['tipo fornecedor'].unique())))

df_filtrado = aplicar_filtros(df, ano, mes, usuario, situacao, tipo_fornecedor)

def calcular_metricas(df):
    qunatidade_total_pedidos = df['numeropedido'].nunique()
    valor_total_pedidos = df['valor liquido item'].sum()
    quantidade_total_itens = df['qtd pedido item'].sum()
    quantidade_pedidos_entregues = df[df['situacao pedido'] == 'fechado pedido chegou']['numeropedido'].nunique()
    quantidade_pedidos_pendentes = df[df['situacao pedido'] == 'pendente']['numeropedido'].nunique()
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

# Gráfico de Valor Total dos Pedidos por Mês 
if not df_filtrado.empty:
    valor_por_mes = df_filtrado.groupby(['ano', 'mes_nome'])['valor liquido item'].sum().reset_index()
    valor_por_mes.rename(columns={'mes_nome': 'mes'}, inplace=True) 
    meses_ordenados = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    valor_por_mes['mes_ordenado'] = pd.Categorical(valor_por_mes['mes'], categories=meses_ordenados, ordered=True)
    valor_por_mes = valor_por_mes.sort_values('mes_ordenado')
    valor_por_mes['valor_formatado'] = valor_por_mes['valor liquido item'].apply(formatar_moeda)
    fig_valor_mes = px.bar(valor_por_mes, x='mes', y='valor liquido item',
                            labels={'valor liquido item': 'Valor Total', 'mes': 'Mês'},
                            title='<b>Valor Total dos Pedidos por Mês (Filtrado)</b>',
                            text='valor_formatado',
                            hover_data={'valor liquido item': ':.2f', 'mes': True},
                            height=900, width=1100)
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

st.markdown("---")


def listar_pedidos_pendentes_detalhado(df):
    pedidos_pendentes = df[df['situacao pedido'] == 'pendente'].copy()
    pedidos_unicos = pedidos_pendentes['numeropedido'].nunique()
    if pedidos_unicos > 0:
        st.warning(f"⚠️ Atenção! {pedidos_unicos} pedidos estão com entrega pendente:")
    if not pedidos_pendentes.empty:
        st.subheader("Pedidos Pendentes")
        colunas_exibir_originais = ['numeropedido', 'status pedido', 'data emissao', 'data entrega prevista', 'data entrada', 'fornecedor', 'descricao produto', 'total itens', 'valor liquido item']
        pedidos_pendentes_exibir = pedidos_pendentes[colunas_exibir_originais].copy()

        # Converter as colunas de data para datetime
        for col in ['data emissao', 'data entrega prevista']:
            if col in pedidos_pendentes_exibir.columns:
                pedidos_pendentes_exibir[col] = pd.to_datetime(pedidos_pendentes_exibir[col], format='%d/%m/%Y', errors='coerce')
                nao_datetime = pedidos_pendentes_exibir[pd.isna(pedidos_pendentes_exibir[col])]
                if not nao_datetime.empty:
                    st.warning(f"⚠️ Atenção! Alguns valores na coluna '{col}' não puderam ser convertidos para data. Verifique os dados.")
                    st.dataframe(nao_datetime[[col]])

        # Calcular o prazo de entrega em dias
        if 'data emissao' in pedidos_pendentes_exibir.columns and 'data entrega prevista' in pedidos_pendentes_exibir.columns:
            pedidos_pendentes_exibir['prazo entrega (dias)'] = (pedidos_pendentes_exibir['data entrega prevista'] - pedidos_pendentes_exibir['data emissao']).dt.days
            colunas_exibir = colunas_exibir_originais + ['prazo entrega (dias)']
        else:
            st.error("Erro: As colunas de data não foram convertidas corretamente. O cálculo do prazo de entrega não será realizado.")
            colunas_exibir = colunas_exibir_originais

        # 👉 Calcular o total antes de formatar os valores
        total_valor_liquido = pedidos_pendentes_exibir['valor liquido item'].sum()

        # Formatar colunas para exibição
        pedidos_pendentes_exibir_formatado = pedidos_pendentes_exibir[colunas_exibir].copy()
        for col in ['data emissao', 'data entrega prevista']:
            if col in pedidos_pendentes_exibir_formatado.columns and pd.api.types.is_datetime64_any_dtype(pedidos_pendentes_exibir_formatado[col]):
                pedidos_pendentes_exibir_formatado[col] = pedidos_pendentes_exibir_formatado[col].dt.strftime('%d/%m/%Y')

        pedidos_pendentes_exibir_formatado['valor liquido item'] = pedidos_pendentes_exibir_formatado['valor liquido item'].apply(
            lambda x: f'R$ {x:,.2f}'.replace(",", "X").replace(".", ",").replace("X", ".")
        )

        st.dataframe(pedidos_pendentes_exibir_formatado)

        # Exibir total formatado
        st.info(f"Valor Total dos Pedidos Pendentes: {formatar_moeda(total_valor_liquido)}")

    else:
        st.info("Não há pedidos com entrega pendente.")

listar_pedidos_pendentes_detalhado(df)



def calcular_variacao_percentual(row, preco_anterior_col, preco_atual_col):
    preco_anterior = row[preco_anterior_col]
    preco_atual = row[preco_atual_col]
    if preco_anterior == 0 or preco_atual == 0:
        return 0.0
    return ((preco_atual - preco_anterior) / preco_anterior) * 100

def aplicar_cor(val):
    if isinstance(val, (int, float)):
        if val < 0:
            color = 'green'
        elif val > 0:
            color = 'red'
        else:
            color = 'white'
        return f'color: {color}'
    return ''

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

    # Agrupar e obter a média do preço unitário e a soma da quantidade de cada produto no mês anterior
    preco_anterior = df_anterior.groupby('descricao produto')['preco unitario liquido item'].mean().reset_index()
    preco_anterior.rename(columns={'preco unitario liquido item': f'Preço Unitário {mes_anterior}/{ano_anterior}'}, inplace=True)
    quantidade_anterior = df_anterior.groupby('descricao produto')['qtd pedido item'].sum().reset_index()
    quantidade_anterior.rename(columns={'qtd pedido item': f'Quantidade {mes_anterior}/{ano_anterior}'}, inplace=True)

    # Agrupar e obter a média do preço unitário e a soma da quantidade de cada produto no mês atual
    preco_atual = df_atual.groupby('descricao produto')['preco unitario liquido item'].mean().reset_index()
    preco_atual.rename(columns={'preco unitario liquido item': f'Preço Unitário {mes_atual}/{ano_atual}'}, inplace=True)
    quantidade_atual = df_atual.groupby('descricao produto')['qtd pedido item'].sum().reset_index()
    quantidade_atual.rename(columns={'qtd pedido item': f'Quantidade {mes_atual}/{ano_atual}'}, inplace=True)

    # Merge dos DataFrames para ter a quantidade e o preço dos dois meses lado a lado
    df_comparativo = pd.merge(quantidade_anterior, quantidade_atual, on='descricao produto', how='outer').fillna(0)
    df_comparativo = pd.merge(df_comparativo, preco_anterior, on='descricao produto', how='left').fillna(0)
    df_comparativo = pd.merge(df_comparativo, preco_atual, on='descricao produto', how='left').fillna(0)

    # Calcular a variação percentual
    coluna_preco_anterior = f'Preço Unitário {mes_anterior}/{ano_anterior}'
    coluna_preco_atual = f'Preço Unitário {mes_atual}/{ano_atual}'

    if coluna_preco_anterior in df_comparativo.columns and coluna_preco_atual in df_comparativo.columns:
        df_comparativo['Variação Preço Unitário (%)'] = df_comparativo.apply(
            lambda row: calcular_variacao_percentual(row, coluna_preco_anterior, coluna_preco_atual),
            axis=1
        )

        # Formatar as colunas de preço
        df_comparativo[coluna_preco_anterior] = df_comparativo[coluna_preco_anterior].apply(formatar_moeda)
        df_comparativo[coluna_preco_atual] = df_comparativo[coluna_preco_atual].apply(formatar_moeda)

        # Criar o filtro de variação percentual
        filtro_percentual = st.radio(
            "Filtrar Variação de Preço:",
            ["Todos", "Positivos", "Negativos"],
            horizontal=True
        )

        df_filtrado = df_comparativo.copy()
        if filtro_percentual == "Negativos":
            df_filtrado = df_filtrado[df_filtrado['Variação Preço Unitário (%)'] > 0]
        elif filtro_percentual == "Positivos":
            df_filtrado = df_filtrado[df_filtrado['Variação Preço Unitário (%)'] < 0]

        # Aplicar formatação para remover casas decimais nas colunas de quantidade
        coluna_quantidade_anterior = f'Quantidade {mes_anterior}/{ano_anterior}'
        coluna_quantidade_atual = f'Quantidade {mes_atual}/{ano_atual}'
        if coluna_quantidade_anterior in df_filtrado.columns:
            df_filtrado[coluna_quantidade_anterior] = df_filtrado[coluna_quantidade_anterior].astype(int)
        if coluna_quantidade_atual in df_filtrado.columns:
            df_filtrado[coluna_quantidade_atual] = df_filtrado[coluna_quantidade_atual].astype(int)

        # Aplicar estilo para colorir a coluna de variação NO DATAFRAME FILTRADO (ANTES da formatação para string)
        df_styled = df_filtrado.style.applymap(aplicar_cor, subset=['Variação Preço Unitário (%)'])

        # Formatar a coluna de variação percentual para exibição (DEPOIS da aplicação do estilo)
        df_styled = df_styled.format({'Variação Preço Unitário (%)': '{:.2f}%'})

        st.subheader(f"Comparativo de Produtos Comprados em {mes_anterior}/{ano_anterior} vs {mes_atual}/{ano_atual}:")
        st.dataframe(df_styled)
    else:
        st.warning("Não foi possível encontrar as colunas de preço para comparação.")

else:
    st.info("Não há dados para análise de produtos com os filtros aplicados.")