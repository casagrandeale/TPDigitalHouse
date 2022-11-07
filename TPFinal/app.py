import streamlit as st
import streamlit.components.v1 as components
import joblib
import shap
import pandas as pd

loaded_model = None
datatemplate = None
filename = "model.sav"

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
        model = joblib.load(filename)
        data = pd.read_csv('datatemplate.csv')
        data.drop(['Unnamed: 0','price'],axis=1,inplace=True)
        return model,data    

def st_shap(plot, height=None):
    print(type(shap))
    print(dir(shap))
    js=shap.getjs()
    shap_html = f"<head>{js}</head><body>{plot.html()}</body>"
    components.html(shap_html, height=height)

def predict(tipo,bathroomType,tipoRoom,bathrooms,rooms,beds,people,minimum_nights,maximum_nights,cabletv,barrio,host_is_superhost,number_of_reviews,host_identity_verified,
    review_scores_rating,air_conditioning,outdoor,pool,parking,pet_friendly,internet,white_goods,gym,kitchen,refrigerator,dishes_silverware,essentials,grill,email_verification,
    host_days_active,long_term_stays_allowed,heating,elevator,instant_bookable,freezer,phone_verification,tv):
   
   with st.spinner('Prediciendo...'):
        datatemplate.drop(datatemplate.index, inplace=True)
        df = datatemplate.append({'property_type_House': 1 if tipo == 'Casa' else 0, 'bathroomtype_shared': 1 if bathroomType == 'Compartido' else 0,
            'room_type_Private room': 1 if tipoRoom == 'Hab. Privada' else 0, 'room_type_Shared room': 1 if tipoRoom == 'Hab. compartida' else 0, 
            'bathrooms':bathrooms,'bedrooms':rooms,'beds':beds,'accommodates':people,'minimum_nights':minimum_nights,'maximum_nights':maximum_nights,
            'cable':1 if cabletv else 0,'host_is_superhost': 1 if host_is_superhost else 0,
            'host_identity_verified':1 if host_identity_verified else 0,'number_of_reviews':number_of_reviews,'review_scores_rating':review_scores_rating, 
            'air_conditioning':1 if air_conditioning else 0,'outdoor':1 if outdoor else 0,'pool':1 if pool else 0,
            'parking':1 if parking else 0,'tv':1 if tv else 0,'internet':1 if internet else 0,'white_goods':1 if white_goods else 0,'gym':1 if gym else 0,
            'pet_friendly':1 if pet_friendly else 0,'dishes_silverware':1 if dishes_silverware else 0,'essentials':1 if essentials else 0,'grill':1 if grill else 0,
            'kitchen':1 if kitchen else 0,'long_term_stays_allowed':1 if long_term_stays_allowed else 0,'heating':1 if heating else 0,'elevator':1 if elevator else 0,
            'refrigerator':1 if refrigerator else 0,'freezer':1 if freezer else 0,'phone_verification':1 if phone_verification else 0,'email_verification':1 if email_verification else 0,
            'instant_bookable':1 if instant_bookable else 0,'host_days_active':host_days_active
            }, ignore_index=True)

        df = df.fillna(0)
        df['neighbourhood_cleansed_'+barrio] = 1
        df = df.astype(int, copy=False)
        df['review_scores_rating'] = df['review_scores_rating'].astype(float)
        df['review_scores_rating'] = review_scores_rating 

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
            beds= st.slider('¿Cantidad de camas?', 1, 10, 1)

        ##acommodates hay que sacarla
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
            minimum_nights= st.slider('¿Cantidad de noches minimas?', 0, 1000, 1)

        c = cols[1]
        with c:
            maximum_nights= st.slider('¿Cantidad de noches máximas?', 0, 1000, 1)


        with st.expander(label='Seleccione caraterísticas del inmueble:', expanded=True):
            cols = st.columns(2)
            c = cols[0]
            with c:
                    tv = st.checkbox('TV')
                    cabletv = st.checkbox('TV por Cable')
                    internet = st.checkbox('Internet')
                    grill = st.checkbox('Parrilla')
                    parking = st.checkbox('Parking')
                    pool = st.checkbox('Piscina')
                    elevator = st.checkbox('Ascensor')
                    pet_friendly = st.checkbox('Pet Friendly')
                    gym = st.checkbox('Gimnasio')
                    outdoor = st.checkbox('Exteriores (Jardin/Parque/Balcón)')
                    air_conditioning = st.checkbox('Aire acondicionado')
                    refrigerator = st.checkbox('Heladera')
                    freezer = st.checkbox('Freezer')
            c = cols[1]
            with c:        
                    heating = st.checkbox('Calefacción')
                    essentials = st.checkbox('Escenciales')
                    kitchen = st.checkbox('Cocina')
                    white_goods = st.checkbox('Electr. línea blanca')
                    dishes_silverware = st.checkbox('Vajilla')
                    instant_bookable = st.checkbox('Reserva instantánea')
                    long_term_stays_allowed = st.checkbox('Largas estadias')

        with st.expander(label='Sobre el host:', expanded=True):
            cols = st.columns(2)
            c = cols[0]
            with c:
                host_is_superhost = st.checkbox('Super host')
                host_days_active = st.slider('¿Cantidad de meses activo?', 0, 120, 1)    
                number_of_reviews= st.slider('¿Cantidad reseñas?', 0, 10000, 1)        
                review_scores_rating= st.slider('¿Puntuación?', 0.0, 5.0, 0.1)        
            c = cols[1]
            with c:   
                host_identity_verified = st.checkbox('Identidad verificada')
                phone_verification = st.checkbox('Teléfono verificado')
                email_verification = st.checkbox('Email verificado')
    submitted = form.form_submit_button("Estimar")
    if submitted:
        predict(tipo,bathroomType,tipoRoom,bathrooms,rooms,beds,people,minimum_nights,maximum_nights,cabletv,barrio,host_is_superhost,number_of_reviews,host_identity_verified,
    review_scores_rating,air_conditioning,outdoor,pool,parking,pet_friendly,internet,white_goods,gym,kitchen,refrigerator,dishes_silverware,essentials,grill,email_verification,
    host_days_active * 30,long_term_stays_allowed,heating,elevator,instant_bookable,freezer,phone_verification,tv)

# aca empieza la 'pagina'
st.title("Estimador de precios de alquiler por noche CABA")

loaded_model,datatemplate =  loadModel()

maincontainer = st.empty()

createStart()





