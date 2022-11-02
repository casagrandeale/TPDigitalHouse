
import numpy as np
import pandas as pd
import regex as re
from datetime import datetime
from sklearn.base import BaseEstimator, TransformerMixin

class AirbnbCABATransformer(BaseEstimator, TransformerMixin):

    def fit(self,X,y=None):
        return self

    def transform(self, X, y=None):
        data = X

        data = self._dropNotUsedColumns(data)
        data = self._processBathRooms(data)
        data = self._processBedRooms(data)
        data = self._convertToBoolean(data)
        data = self._processPrice(data)
        data = self._processPropertyType(data)
        data = self._processOutLiers(data)
        data = self._processHostDaysActive(data)
        data = self._processAmenities(data)
        data = self._processVerifications(data)
                
        data = data.fillna(0)

        data = self._processNeighbourhood(data)
        data = self._dropTextColumns(data)
        data = self._processGetdummies(data)
        data = self._convertToInt(data)
        
        return data

    def _dropNotUsedColumns(self,data):
        
        data = data.drop(['id'], axis=1)
        data = data.drop(['source'], axis=1)
        data = data.drop(['availability_30','availability_60','availability_90','availability_365','listing_url','scrape_id','last_scraped','picture_url','host_id','host_url','host_name'], axis=1)
        data = data.drop(['host_location','host_neighbourhood','reviews_per_month','neighborhood_overview','neighbourhood','neighbourhood_group_cleansed'], axis=1)
        data = data.drop(['host_response_rate','host_thumbnail_url','host_about','host_response_time','host_response_rate','host_acceptance_rate','host_thumbnail_url'], axis=1)
        data = data.drop(['host_picture_url','host_listings_count', 'minimum_minimum_nights','maximum_minimum_nights','minimum_maximum_nights','maximum_maximum_nights'], axis=1)
        data = data.drop(['minimum_nights_avg_ntm','maximum_nights_avg_ntm','calendar_updated', 'calendar_last_scraped','has_availability','host_total_listings_count'], axis=1)
        data = data.drop(['number_of_reviews','number_of_reviews_ltm','number_of_reviews_l30d','first_review','last_review'], axis=1)
        data = data.drop(['review_scores_rating','review_scores_location','review_scores_accuracy','review_scores_cleanliness'], axis=1)
        data = data.drop(['review_scores_checkin','review_scores_communication','review_scores_value','license','calculated_host_listings_count','calculated_host_listings_count_entire_homes'], axis=1)
        data = data.drop(['calculated_host_listings_count_private_rooms','calculated_host_listings_count_shared_rooms'], axis=1)
        return data

    def _extractBathRoomType(self,row):  
        if ("shared" in row["bathrooms_text"].lower()):
            return "shared"
        return "private"

    def _extractBathQuantity(self,row):  
        f = re.findall('\d*\.?\d+',row["bathrooms_text"])
        if (len(f)>0):
            return f[0]
        return "1"
    
    def _processBathRooms(self,data):
        data["bathrooms_text"] = data["bathrooms_text"].astype(str)
        data["bathroomtype"] = data.apply(lambda x:self._extractBathRoomType(x),axis =1)   
        data["bathrooms"] = data.apply(lambda x:self._extractBathQuantity(x),axis =1)   

        data["bathrooms"] = data["bathrooms"].astype(float)
        data["bathrooms"] = data["bathrooms"].apply(np.ceil)
        data["bathrooms"] = data["bathrooms"].astype(int)
        data = data.drop(['bathrooms_text'], axis=1)
        return data

    _numbers_es = ["mono","un","dos","tres","cuatro","cinco","seis"]
    _numbers_en = ["single","one","two","three","four","five","six"]

    _patron = '((?P<numero>\d|mono|un|dos|tres|cuatro|cinco|seis|single|one|two|three|four|five|six|1|2|3|4|5|6)\s*((?P<ambiente>amb)|(?P<bedroom>hab|bedroom|bdr)))'
    _patron_regex = re.compile(_patron,flags = re.IGNORECASE)

    def _extractBedRoom(self,row):
        try:
            resultado=None
            ambientes=0
            if (row['description'] and isinstance(row['description'],str)):
                resultado = self._patron_regex.search(row['description'])
            if ((resultado is None) and row['name'] and isinstance(row['name'],str)):
                resultado = self._patron_regex.search(row['name'])
            if (resultado is not None):
                qty = 1
                if (resultado.group("numero") in self._numbers_es):
                    qty = self._numbers_es.index(resultado.group("numero"))
                    if (qty == 0):
                        qty = 1
                elif(resultado.group("numero") in self._numbers_en):
                    qty = self._numbers_en.index(resultado.group("numero"))
                    if (qty == 0):
                        qty = 1
                elif(resultado.group("numero").isnumeric()):
                    qty = int(resultado.group("numero"))
                if (resultado.group("ambiente")):
                    if (qty > 1):
                        qty = qty - 1
                return qty    
        
        except:
            return np.nan


    def _processBedRooms(self,data):
        #Relleno con patron regex según la palabra ambiente
        data.loc[data.bedrooms.isnull(),'bedrooms'] = data.loc[data.bedrooms.isnull()].apply(self._extractBedRoom,axis=1)

        data.loc[data.bedrooms.isnull(),'bedrooms'] = 1
        data.loc[data.beds.isnull(),'beds'] = 1

        return data
    
    def _convertToBoolean(self,data):
        data.replace({'f': 0, 't': 1}, inplace=True)
        return data
    
    def _processPrice(self,data):
        data.price = data.price.str[1:-3]
        data.price = data.price.str.replace(",", "")
        data.price = data.price.astype('int64')
        return data
    
    def _processPropertyType(self,data):
        data.loc[data["property_type"].str.contains("Entire cottage|Ranch|Shared room in guest suite|house|casa|villa|home|townhouse|chalet|Entire place|Entire cabin",case=False,na=False),"property_type"] = "House"
        data.loc[data["property_type"].str.contains("Cave|Shared room in ryokan|loft|apartment|dept|condo|floor|rental unit|Entire in-law|Entire guest suite|Private room in guest suite|Private room",case=False,na=False),"property_type"] = "Apartment"
        data.loc[data["property_type"].str.contains("Pension|hostel|hotel|bed and breakfast|resort",case=False,na=False),"property_type"] = "Hotel"
        data.loc[~data.property_type.isin(['House', 'Apartment','Hotel']), 'property_type'] = 'Other'
        return data
    
    def _findOutliers(self,df, column, limit=4):
        """
        Devuelve outliers para una columna arriba del limite máximo
        Se puede ajustar el limite corriendo el 75%
        """
        q25, q50, q75 = df[column].quantile(q=[0.25, 0.5, 0.75])
        iqr = q75 - q25
        # max limits to be considered an outlier
        max_ = q75 + limit * iqr
        # identify the points
        outlier_mask = [True if x > max_ else False for x in df[column]]
        print('{} outliers found out of {} data points, {}% of the data. {} is the max'.format(
            sum(outlier_mask), len(df[column]),
            100 * (sum(outlier_mask) / len(df[column])),max_))
        return outlier_mask

    def _processOutLiers(self,data):
        # quitar outliers de precios
        data = data[np.logical_not(self._findOutliers(data, 'price',limit=8))]
        # quitar outliers de baños
        data = data[np.logical_not(self._findOutliers(data, 'bathrooms',limit=6))]

        # quitamos outliers de camas
        data = data[np.logical_not(self._findOutliers(data, 'beds',limit=6))]

        # quitamos outliers de noches minimas
        data = data[np.logical_not(self._findOutliers(data, 'minimum_nights',limit=14))]

        return data
    
    def _processHostDaysActive(self,data):
        #convertimos a dias la fecha desde que el host se encuentra activo
        data.host_since = pd.to_datetime(data.host_since) 

        # Calculating the number of days
        data['host_days_active'] = (datetime.now() - data.host_since).astype('timedelta64[D]')

        # Replacing null values with the median
        data.host_days_active.fillna(data.host_days_active.median(), inplace=True)
        return data

    def _processAmenities(self,data):
        amenities = data.amenities.str.replace("[{}]", "").str.replace('"', "").str.replace('\\\\u2013', '-').str.replace('\\\\u2019','´').str.replace('\\\\u00f3','ó').str.replace('\\\\u00e9','é').str.replace('\\\\u00ed','í').str.replace('\\\\u00e1','á').str.replace('\\\\u00b4','').str.replace('\\\\u00f1','ñ').str.replace('\\\\u00a0','').str.replace('{', '').str.replace('}', ',').str.replace('[', '').str.replace(']', ',').str.replace('"', '')
        dict = [{"feature":"cable","values":["cable tv","TV with standard cable","cable"]}
       ,{"feature":"air_conditioning","values":["AC - split type ductless system","Air conditioning","aire acondicionado"]}
       ,{"feature":"outdoor","values":["Outdoor dining area","Patio or balcony","patio","balcony","jardin","Backyard","Garden","Outdoor","Sun loungers","Terrace"]}
       ,{"feature":"pool","values":["Shared pool","pool","pileta","piscina"]}
       ,{"feature":"parking","values":["Paid parking on premises","Paid parking lot off premises","Paid parking off premises","private parking","estacionamiento","cochera"]}
       ,{"feature":"tv","values":["tv","HDTV","Smart TV"]}
       ,{"feature":"internet","values":["Wifi","High speed cable","internet","Ethernet connection"]}
       ,{"feature":"white_goods","values":["Dryer","Free washer - In unit","Dishwasher","lavaplatos","washer","secarropas","lavavajilla"]}
       ,{"feature":"gym","values":["Exercise equipment","Gym","gimnasio"]}
       ,{"feature":"pet_friendly","values":["pet","pets","mascotas","mascota","Cat(s)","Dog(s)","perros","gatos"]}
       ,{"feature":"dishes_silverware","values":["Dishes and silverware","cubiertos","platos","vajilla","dishes","silverware"]} 
       ,{"feature":"essentials","values":["Essentials","Body Soap","soap","shampoo","jabon","Shower gel","Conditioner"]} 
       ,{"feature":"grill","values":["BBQ grill","parrilla","grill","BBQ","asador"]} 
       ,{"feature":"kitchen","values":["Kitchen","Cocina","Cooking basics","Oven"]} 
       ,{"feature":"long_term_stays_allowed","values":["Long term stays allowed"]}  
       ,{"feature":"heating","values":["Heating"]}
       ,{"feature":"elevator","values":["Elevator","Ascensor","elevador"]}  
       ,{"feature":"refrigerator","values":["Refrigerator"]}
       ,{"feature":"freezer","values":["Freezer"]} 
       ] 
            
        for feat in dict:
            for x in feat["values"]:
                data.loc[data.amenities.str.contains(x,case=False,na=False),feat["feature"]] = 1 
        return data

    def _processVerifications(self,data):
        data.loc[data.host_verifications.str.contains('phone',case=False,na=False),'phone_verification'] = 1 
        data.loc[data.host_verifications.str.contains('work_email',case=False,na=False),'email_verification'] = 1 
        data.loc[data.host_verifications.str.contains('email',case=False,na=False),'email_verification'] = 1        
        return data

    def _processNeighbourhood(self,data):
        data.loc[data.neighbourhood_cleansed == "Dique 1","neighbourhood_cleansed"] = "Puerto Madero"
        data.loc[data.neighbourhood_cleansed == "Dique 4","neighbourhood_cleansed"] = "Puerto Madero"
        data.loc[data.neighbourhood_cleansed == "Dique 3","neighbourhood_cleansed"] = "Puerto Madero"
        data.loc[data.neighbourhood_cleansed == "Dique 2","neighbourhood_cleansed"] = "Puerto Madero"
        return data
    
    def _dropTextColumns(self,data):
        data = data.drop(['name','description','amenities','host_since','host_verifications','latitude','longitude'], axis=1)
        return data
    
    def _convertToInt(self,data):
        data['bathrooms'] = data['bathrooms'].astype(int)
        data['bedrooms'] = data['bedrooms'].astype(int)
        data['host_days_active'] = data['host_days_active'].astype(int)
        data['air_conditioning'] = data['air_conditioning'].astype(int)
        data['beds'] = data['beds'].astype(int)
        data['cable'] = data['cable'].astype(int)
        data['outdoor'] = data['outdoor'].astype(int)
        data['pool'] = data['pool'].astype(int)
        data['parking'] = data['parking'].astype(int)
        data['tv'] = data['tv'].astype(int)
        data['parking'] = data['parking'].astype(int)
        data['internet'] = data['internet'].astype(int)
        data['white_goods'] = data['white_goods'].astype(int)
        data['gym'] = data['gym'].astype(int)
        data['pet_friendly'] = data['pet_friendly'].astype(int)
        data['dishes_silverware'] = data['dishes_silverware'].astype(int)
        data['essentials'] = data['essentials'].astype(int)
        data['pet_friendly'] = data['pet_friendly'].astype(int)
        data['kitchen'] = data['kitchen'].astype(int)
        data['grill'] = data['grill'].astype(int)
        data['long_term_stays_allowed'] = data['long_term_stays_allowed'].astype(int)
        data['heating'] = data['heating'].astype(int)
        data['elevator'] = data['elevator'].astype(int)
        data['refrigerator'] = data['refrigerator'].astype(int)
        data['freezer'] = data['freezer'].astype(int)
        data['phone_verification'] = data['phone_verification'].astype(int)
        data['email_verification'] = data['email_verification'].astype(int)
        return data

    def _processGetdummies(self,data):
        data = pd.get_dummies(data)
        return data

        









