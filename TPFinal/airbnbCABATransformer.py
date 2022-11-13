
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
       
        data = self._processAmenities(data)
                
        data = data.fillna(0)

        data = self._processNeighbourhood(data)
        data = self._dropTextColumns(data)
        data = self._processGetdummies(data)
        data = self._convertToInt(data)
        
        data.columns = data.columns.str.replace('neighbourhood_cleansed_', '')
        data.columns = data.columns.str.replace('property_type_Apartment', 'Apartment')
        data.columns = data.columns.str.replace('property_type_House', 'House')
        data.columns = data.columns.str.replace('room_type_Private room', 'Private room')
        data.columns = data.columns.str.replace('room_type_Shared room', 'Shared room')
        data.columns = data.columns.str.replace('room_type_Entire home/apt', 'Entire home/apt')
        
        datatemplate = data.iloc[1:2]
        datatemplate.to_pickle("datatemplate.pkl", protocol=2)
        datatemplate.to_csv("datatemplate.csv")

        return data

    def _dropNotUsedColumns(self,data):        
        data = data.drop(['id','source','availability_30','availability_60','availability_90','availability_365','listing_url','beds','scrape_id','last_scraped','picture_url','host_id','host_url','host_name',
            'host_location','host_neighbourhood','neighborhood_overview','neighbourhood','neighbourhood_group','neighbourhood_group_cleansed',
            'host_thumbnail_url','host_about','host_response_time','host_has_profile_pic',
            'host_acceptance_rate','host_thumbnail_url','host_picture_url','host_listings_count',
            'minimum_minimum_nights','maximum_minimum_nights','minimum_maximum_nights','maximum_maximum_nights',
            'minimum_nights_avg_ntm','maximum_nights_avg_ntm','calendar_updated', 'calendar_last_scraped',
            'has_availability','host_response_time','host_total_listings_count','reviews_per_month',
            'number_of_reviews_ltm','number_of_reviews_l30d','first_review','last_review','instant_bookable',
            'review_scores_location','review_scores_accuracy','review_scores_cleanliness','host_response_rate',
                        'review_scores_checkin','review_scores_communication','review_scores_value',
                        'license','calculated_host_listings_count','calculated_host_listings_count_entire_homes',
            'calculated_host_listings_count_private_rooms','calculated_host_listings_count_shared_rooms'
            ], axis=1)
        data = data.reset_index()
        data = data.drop(['index'],axis=1)
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
        return data
    
    def _convertToBoolean(self,data):
        data.replace({'f': 0, 't': 1}, inplace=True)
        return data
    
    def _processPrice(self,data):
        data['price'] = data['price'].astype('string').str.replace(',', '').str.replace('\$', '').astype('float64').astype('int64')
        return data
    
    def _processPropertyType(self,data):
        data.loc[data["property_type"].str.contains("Entire cottage|Ranch|house|casa|villa|home|townhouse|chalet|Entire place|Entire cabin",case=False,na=False),"property_type"] = "House"
        data.loc[data["property_type"].str.contains("Cave|Shared room in ryokan|Shared room in guest suite|loft|apartment|dept|condo|floor|rental unit|Entire in-law|Entire guest suite|Private room in guest suite|Private room",case=False,na=False),"property_type"] = "Apartment"
        data.loc[data["property_type"].str.contains("Pension|hostel|hotel|bed and breakfast|resort",case=False,na=False),"property_type"] = "Hotel"
        data.loc[~data.property_type.isin(['House', 'Apartment','Hotel']), 'property_type'] = 'Other'
        data = data.loc[data.property_type != "Hotel"]
        data = data.loc[data.property_type != "Other"]
        data = data.loc[data.room_type != "Hotel room"]
        return data
    
    def _processOutLiers(self,data):
        # quitar outliers de precios
        data = data.loc[ data['price'] <  200000 ]
        data = data.loc[ data['price'] >  1000 ]
        data = data.loc[ data['price']< (data['price'].mean() + 3*data['price'].std())]
        
        # data = data[np.logical_not(self._findOutliers(data, 'price',limit=3))]
        # quitar outliers de baños
        data = data[data.bathrooms < 6]        
        # quitamos outliers de habitaciones
        data = data[data.bedrooms < 10]
        #data = data[np.logical_not(self._findOutliers(data, 'minimum_nights',limit=15))]

        return data
    
    def _processAmenities(self,data):
        amenities = data.amenities.str.replace("[{}]", "").str.replace('"', "").str.replace('\\\\u2013', '-').str.replace('\\\\u2019','´').str.replace('\\\\u00f3','ó').str.replace('\\\\u00e9','é').str.replace('\\\\u00ed','í').str.replace('\\\\u00e1','á').str.replace('\\\\u00b4','').str.replace('\\\\u00f1','ñ').str.replace('\\\\u00a0','').str.replace('{', '').str.replace('}', ',').str.replace('[', '').str.replace(']', ',').str.replace('"', '')
        dict = [
        {"feature":"air_conditioning","values":["AC - split type ductless system","Air conditioning","aire acondicionado","Window AC unit"]}
       ,{"feature":"pool","values":["Shared pool","pool","pileta","piscina"]}
       ,{"feature":"parking","values":["Paid parking on premises","Paid parking lot off premises","Paid parking off premises","private parking","estacionamiento","cochera"]}
       ,{"feature":"tv","values":["tv","HDTV","Smart TV","cable tv","TV with standard cable","cable","standard cable","Netflix"]}
       ,{"feature":"internet","values":["Wifi","High speed cable","internet","Ethernet connection"]}
       ,{"feature":"gym","values":["Exercise equipment","Gym","gimnasio"]}
       ,{"feature":"pet_friendly","values":["pet","pets","mascotas","mascota","Cat(s)","Dog(s)","perros","gatos"]}       
       ,{"feature":"grill","values":["BBQ grill","parrilla","grill","BBQ","asador"]} 
       ,{"feature":"elevator","values":["Elevator","Ascensor","elevador"]}
       ] 
            
        for feat in dict:
            for x in feat["values"]:
                data.loc[data.amenities.str.contains(x,case=False,na=False),feat["feature"]] = 1 
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
        data['air_conditioning'] = data['air_conditioning'].astype(int)
        data['pool'] = data['pool'].astype(int)
        data['parking'] = data['parking'].astype(int)
        data['tv'] = data['tv'].astype(int)
        data['parking'] = data['parking'].astype(int)
        data['internet'] = data['internet'].astype(int)
        data['gym'] = data['gym'].astype(int)
        data['pet_friendly'] = data['pet_friendly'].astype(int)
        data['pet_friendly'] = data['pet_friendly'].astype(int)
        data['grill'] = data['grill'].astype(int)
        data['elevator'] = data['elevator'].astype(int)
        data['host_identity_verified'] = data['host_identity_verified'].astype(int)
        data['accommodates'] = data['accommodates'].astype(int)
        data['maximum_nights'] = data['maximum_nights'].astype(int)
        data['review_scores_rating'] = data['review_scores_rating'].astype("float32")
        return data

    def _processGetdummies(self,data):
        data = pd.get_dummies(data)
        return data