import streamlit as st
import streamlit.components.v1 as components
import joblib
import shap
import pandas as pd
from io import BytesIO
import requests

loaded_model = None
datatemplate = None
filename = "https://raw.githubusercontent.com/casagrandeale/TPDigitalHouse/main/TPFinal/model.sav"
#filename = "model.sav"

@st.cache
def buildBarrios():
    barrios = ['Palermo','Recoleta','San Nicolas','Retiro','Belgrano','Almagro','Monserrat','Balvanera','Villa Crespo','Nuñez','San Telmo',
    'Colegiales','Caballito','Puerto Madero','Chacarita','Constitucion','Villa Urquiza','Saavedra','Barracas','San Cristobal',
    'Flores','Boedo','Boca','Villa Devoto','Villa Ortuzar','Coghlan','Villa Pueyrredon','Parque Chacabuco','Villa Del Parque','Parque Patricios',
    'Paternal','Villa Santa Rita','Floresta','Parque Chas','Agronomia','Villa Luro','Villa Gral. Mitre','Velez Sarsfield','Mataderos','Nueva Pompeya','Liniers','Monte Castro',
    'Villa Real','Parque Avellaneda','Versalles','Villa Lugano','Villa Soldati','Villa Riachuelo']
    barrios.sort()
    return (barrios)


def loadModel():
    with st.spinner('Cargando modelo...'):
        mfile = BytesIO(requests.get(filename).content)
        model = joblib.load(mfile)
        #model = joblib.load(filename)
        #data = pd.read_csv('https://raw.githubusercontent.com/casagrandeale/TPDigitalHouse/main/TPFinal/datatemplate.csv')
        #data = pd.read_csv('datatemplate.csv')
        data = pd.read_pickle("https://raw.githubusercontent.com/casagrandeale/TPDigitalHouse/main/TPFinal/datatemplate.pkl")
        data.drop(['price'],axis=1,inplace=True)
        return model,data    

def st_shap(plot, height=None):
    print(type(shap))
    print(dir(shap))
    js=shap.getjs()
    shap_html = f"<head>{js}</head><body>{plot.html()}</body>"
    components.html(shap_html, height=height)

def predict(tipo,bathroomType,tipoRoom,bathrooms,rooms,people,minimum_nights,maximum_nights,barrio,host_identity_verified,
    review_scores_rating,air_conditioning,pool,parking,pet_friendly,internet,gym,grill,
    elevator,tv):
   
   with st.spinner('Prediciendo...'):
        datatemplate.drop(datatemplate.index, inplace=True)
        df = datatemplate.append({'House': 1 if tipo == 'Casa' else 0, 'Apartment': 1 if tipo == 'Departamento' else 0, 
            'bathroomtype_shared': 1 if bathroomType == 'Compartido' else 0,'bathroomtype_private':1 if bathroomType == 'Privado' else 0,
            'Entire home/apt':1 if tipoRoom == 'Toda la propiedad' else 0,
            'Private room': 1 if tipoRoom == 'Hab. Privada' else 0, 
            'Shared room': 1 if tipoRoom == 'Hab. compartida' else 0, 
            'bathrooms':bathrooms,'bedrooms':rooms,'accommodates':people,'minimum_nights':minimum_nights,'maximum_nights':maximum_nights,            
            'host_identity_verified':1 if host_identity_verified else 0,
            'review_scores_rating':review_scores_rating, 
            'air_conditioning':1 if air_conditioning else 0,
            'pool':1 if pool else 0,
            'parking':1 if parking else 0,'tv':1 if tv else 0,'internet':1 if internet else 0,'gym':1 if gym else 0,
            'pet_friendly':1 if pet_friendly else 0,
            'grill':1 if grill else 0,            
            'elevator':1 if elevator else 0
            }, ignore_index=True)

        df[barrio] = 1
        df = df.fillna(0).astype(int)
        
        # Get the model's prediction
        pred = loaded_model.predict(df)

        # Calculate shap values
        explainer = shap.TreeExplainer(loaded_model)
        shap_values = explainer.shap_values(df)

        # Get series with shap values, feature names, & feature values
        feature_names = df.columns
        feature_values = df.values[0]
        shaps = pd.Series(shap_values[0], zip(feature_names, feature_values))

        # Print results
        result = f'${pred[0]:,.0f} Precio estimado. \n\n'            
        
        st.subheader(result)

        # Show shapley values force plot
        shap.initjs()
        # printeamos el grafico
        st.subheader('Analizando la prediccion:')
        st_shap(shap.force_plot(base_value=explainer.expected_value, shap_values=shap_values,  features=df))       
        if st.button('Volver'):            
            createStart()
    
def createStart():
  with maincontainer.container():
    form = st.form("my_form")
    with form:
        st.header('Ingrese las características de la propiedad:')

        cols = st.columns(2)
        c = cols[0]
        with c:
            tipo = st.selectbox('¿Tipo de inmueble?',['Casa','Departamento'])

        c = cols[1]
        with c:
            tipoRoom = st.selectbox('¿Tipo de alquiler?',['Toda la propiedad','Hab. Privada','Hab. compartida'])

        barrio = st.selectbox('Barrio',buildBarrios())

        cols = st.columns(2)
        c = cols[0]
        with c:
            rooms= st.slider('¿Cantidad de habitaciones?', 0, 10, 1)

        c = cols[1]
        with c:
             people = st.slider('¿Cuantas personas?', 1, 10, 1)

        cols = st.columns(2)
        c = cols[0]
        with c:
            bathrooms= st.slider('¿Cantidad de baños?', 0, 10, 1)

        c = cols[1]
        with c:
            bathroomType = st.selectbox('Tipo de baño',['Privado','Compartido'])

        cols = st.columns(2)
        c = cols[0]
        with c:
            minimum_nights= st.number_input(label='Noches minimas',min_value=1,max_value=200, value=1, step=1) 

        c = cols[1]
        with c:
            maximum_nights= st.number_input(label='Noches máximas',min_value=1,max_value=500, value=1, step=1) 


        with st.expander(label='Seleccione caraterísticas del inmueble:', expanded=True):
            cols = st.columns(2)
            c = cols[0]
            with c:
                    tv = st.checkbox('TV')                    
                    internet = st.checkbox('Internet')
                    grill = st.checkbox('Parrilla')
                    parking = st.checkbox('Parking')
                    pool = st.checkbox('Piscina')
                    
            c = cols[1]
            with c:        
                    air_conditioning = st.checkbox('Aire acondicionado')
                    elevator = st.checkbox('Ascensor')
                    pet_friendly = st.checkbox('Pet Friendly')
                    gym = st.checkbox('Gimnasio')                    

        with st.expander(label='Sobre el host:', expanded=True):
            cols = st.columns(2)
            c = cols[0]
            with c:
                host_identity_verified = st.checkbox('Identidad verificada')
            c = cols[1]
            with c:   
                review_scores_rating= st.slider('¿Puntuación?', 0.0, 5.0, 0.1)        
    submitted = form.form_submit_button("Estimar")
    if submitted:
        predict(tipo,bathroomType,tipoRoom,bathrooms,rooms,people,minimum_nights,maximum_nights,barrio,host_identity_verified,
    review_scores_rating,air_conditioning,pool,parking,pet_friendly,internet,gym,grill,    
    elevator,tv)

st.set_page_config(layout="wide")

# aca empieza la 'pagina'
st.title("Estimador de precios de alquiler por noche CABA")

loaded_model,datatemplate =  loadModel()

maincontainer = st.empty()

createStart()





