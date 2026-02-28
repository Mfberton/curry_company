import streamlit as st
from PIL import Image

st.set_page_config(
  page_title='Home',
  page_icon='🏠',
  layout='wide'
)

image = Image.open( 'logo.png' )
st.sidebar.image( image, width=120)

st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )

st.sidebar.markdown( """---""" )

st.write( "# Curry Company Growth Dashboard")

st.markdown(
  """
  Growth Dashboard foi construído para acompanhar as métricas de crescimento dos entregadores e restaurantes.
  ### Como urilizar esse Gouth Dashboard?
  - Visão Empresa:
    - Visão Gerencial: Métricas gerais de comportamento.
    - Visão Tática: Indicadores semanais de crescimento.
    - Visão Geográfica: Insigths de geolocalização.
  - Visão Entregadores:
    - Acompanhamento de indicadores semanais de crescimento.
  - Visão Restaurantes:
    - Indicadores semanais de crescimento dos restaurantes.
  ### Ask for Help
  - Time de Data Science no Discord
    - @mauriciofortesberton
  """
)
