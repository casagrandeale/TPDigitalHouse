import streamlit as st
import streamlit.components.v1 as components

@st.cache
def buildBarrios():
    barrios = ['Palermo','Recoleta','San Nicolas','Retiro','Belgrano','Almagro','Monserrat','Balvanera','Villa Crespo','Nuñez','San Telmo',
    'Colegiales','Caballito','Puerto Madero','Chacarita','Constitucion','Villa Urquiza','Saavedra','Barracas','San Cristobal',
    'Flores','Boedo','Boca','Villa Devoto','Villa Ortuzar','Coghlan','Villa Pueyrredon','Parque Chacabuco','Villa Del Parque','Parque Patricios',
    'Paternal','Villa Santa Rita','Floresta','Parque Chas','Agronomia','Villa Luro','Villa Gral. Mitre','Velez Sarsfield','Mataderos','Nueva Pompeya','Liniers','Monte Castro',
    'Villa Real','Parque Avellaneda','Versalles','Villa Lugano','Villa Soldati','Villa Riachuelo']
    barrios.sort()
    return (barrios)

# aca empieza la 'pagina'
st.title("Estimador de precios de alquiler por noche CABA")

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
        host_has_profile_pic = st.checkbox('Foto de perfil')
        host_days_active = st.slider('¿Cantidad de meses activo?', 0, 120, 1)        
    c = cols[1]
    with c:   
        host_identity_verified = st.checkbox('Identidad verificada')
        phone_verification = st.checkbox('Teléfono verificado')
        email_verification = st.checkbox('Email verificado')
 

##https://github.com/carabedo/properatti/blob/main/app.py


if st.button('Estimar'):
    st.write('Camas: '+str(rooms)) 




