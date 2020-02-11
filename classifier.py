import numpy as np 
import json
import pandas as pd
import re
from os import path, SEEK_END
from sklearn.neighbors import KNeighborsClassifier , KDTree
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from nltk.stem import WordNetLemmatizer
import nltk
import pickle
nltk.download('stopwords')
nltk.download('wordnet')
from nltk.corpus import stopwords

FoodTypes = {0 :"Drink", 1:"Dessert", 2:"Breakfast", 3:"Japanese", 4:"Mexican", 5:"Chinese", 6:"American",7:"Italian",8:"Indian",9:"Mediterranean",10:"Other"}
FoodTypesRev = {"Drink" : 0, "Dessert": 1, "Breakfast": 2, "Japanese": 3, "Mexican":4, "Chinese":5, "American":6, "Italian": 7, "Indian": 8, "Mediterranean": 9, "Other" : 10}

minVal, maxVal = 0, 10

def getMenuItem(path, index):
    with open(path, "r") as json_file:
        data = json.load(json_file)
        for i, item in enumerate(data):
            if i >= index:
                yield item

def saveIndex(path, index):
    with open(path, "w") as f:
        f.write(index)

def getIndex(path):
    index = 0
    with open(path, "r") as f:
        res = f.read()
    try:
        index = int(res)
    except ValueError:
        print("Value error: ", res, " cannot be cast to int.")
    return index

def appendClassified(path, item):
    with open(path, "rb+") as json_file:
        json_file.seek(-1, SEEK_END)
        json_file.truncate()

    with open(path, "a+") as json_file:
        json_file.write(",")
        json_file.write("\n")
        json.dump(item, json_file)
        json_file.write("]")
        
# def manualClassifyItem(item):
#     #Classify item
#     res = ""
#     while True:
#         print("-"*70)
#         print(item)
#         print(FoodTypes)
#         response = -1
#         try:
#             response = int(input("Select #: "))
#             if response >= minVal and response  <= maxVal:
#                 res = FoodTypes[response]
#                 break
#         except ValueError:
#             print("Error, invalid input")
#     return res
    
# def manualClassify():
#     index = getIndex("index.txt")
#     initialIndex = index
#     items = [x for x in getMenuItem("menu.json", index)]
#     done = False
#     print("Press q to stop.")
#     for item in items:
#         item["type"] = manualClassifyItem(item)
#         appendClassified("classified.json", item)
#         index += 1

#         #Allow user to stop after each item
#         start = time.time()
#         while start + 1 > time.time():
#             try:
#                 if keyboard.is_pressed('q'):
#                     print("Exiting, items classified: ", (index - initialIndex))
#                     done = True
#                     break
#             except:
#                 break
#         if done:
#             break
#     saveIndex("index.txt", str(index))

# def supervisedClassify(classifier, vectorizer, tfidfconverter):
#     index = getIndex("index.txt")
#     initialIndex = index
#     items = [x for x in getMenuItem("menu.json", index)]
#     df = getDataFrameFromJson(items)
#     normalized = normalizeItems(df["item_name"])
#     normalized = vectorizer.transform(normalized).toarray()
#     normalized = tfidfconverter.fit_transform(normalized).toarray()

#     done = False
#     print("Press q to stop.")
#     for i, item in enumerate(items):
#         invalid = True
#         single = np.reshape(normalized[i], (1,-1))
#         predict = classifier.predict(single)
#         while invalid:
#             ver = str(input(f"Is : {item} :  {predict} ?"))
#             if ver == "y" or ver == "Y":
#                 invalid = False
#             elif ver == "n" or ver == "N":
#                 break
        
#         #Manually classify item
#         if invalid:
#             item["type"] = manualClassifyItem(item)
#         else:
#             item["type"] = predict[0]
        
#         appendClassified("classified.json", item)
#         index += 1

#         #Allow user to stop after each item
#         start = time.time()
#         while start + 1 > time.time():
#             try:
#                 if keyboard.is_pressed('q'):
#                     print("Exiting, items classified: ", (index - initialIndex))
#                     done = True
#                     break
#             except:
#                 break
#         if done:
#             break
#     saveIndex("index.txt", str(index))

# def autoClassify(classifier, vectorizer, tfidfconverter):
#     index = getIndex("index.txt")
#     items = [x for x in getMenuItem("menu.json", index)]
#     df = getDataFrameFromJson(items)
#     normalized = normalizeItems(df["item_name"])
#     normalized = vectorizer.transform(normalized).toarray()
#     normalized = tfidfconverter.fit_transform(normalized).toarray()
    
#     predictions = classifier.predict(normalized)
#     for i, item in enumerate(items):
#         item["type"] = predictions[i]
    
#     with open("classified_test.json", "a+") as json_file:
#         json.dump(items, json_file)

def getDataFrameFromJson(jsonDict):
    columnNames = [key for key in jsonDict[0]]
    arr = np.empty(shape=(len(jsonDict), len(columnNames)), dtype="U50")
    for i, _ in enumerate(jsonDict):
        for j, col in enumerate(columnNames):
            arr[i][j] = str(jsonDict[i][col])
    df = pd.DataFrame(arr, columns=columnNames)
    return df

class Restaurant(object):
    def __init__(self, brandID, name, vector=None):
        self.brandId = brandID
        self.name = name
        self.menuCount = 0
        if vector is None:
            self.vector = np.zeros(shape=11, dtype=float)
        else:
            self.vector = np.array(vector)

    def normalize(self):
        total = sum(self.vector)
        for i in range(len(self.vector)):
            self.vector[i] = (self.vector[i] / total)
    
    def addItem(self, itemType):
        self.vector[FoodTypesRev[itemType]] += 1
    
    def __str__(self):            
        return json.dumps({"brand_id" : self.brandId, "restaurant": self.name, "vector": self.vector.tolist()})

class RestaurantManager(object):
    def __init__(self, restaurantPath=None):
        self.restaurantPath = restaurantPath
        self.restaurants = dict()
        if restaurantPath is not None and path.exists(restaurantPath):
            with open(self.restaurantPath, "r") as json_file:
                restData = json.load(json_file)
                for rest in restData:
                    self.restaurants[rest["brand_id"]] = Restaurant(rest["brand_id"], rest["restaurant"], rest["vector"])
        
    def hasRestaurant(self, brandID):
        return (str(brandID) in self.restaurants)
    
    def addRestaurant(self, brandID, name, vector=None, restaurant=None):
        if brandID not in self.restaurants:
            if restaurant is None:
                self.restaurants[brandID] = Restaurant(brandID, name, vector)
            else:
                self.restaurants[brandID] = restaurant

class Classifier(object):
    def __init__(self, itemsPath, modelPath=None):
        self.modelPath = modelPath
        self.itemsPath = itemsPath
        self.stemmer = WordNetLemmatizer()
        self.model = None
        self.vectorizer = None
        self.transformer = None
        self.__createModel()

    def __createModel(self):
        if self.modelPath is not None and path.exists(self.modelPath):
            self.model = pickle.load(open(self.modelPath, "rb"))
            self.transformer = TfidfTransformer()
            self.vectorizer = CountVectorizer(decode_error="replace",vocabulary=pickle.load(open("_tokens.pkl", "rb")))
        elif self.itemsPath is not None and path.exists(self.itemsPath):
            df = getDataFrameFromJson([x for x in getMenuItem(self.itemsPath, 0)])
            self.vectorizer = CountVectorizer(max_features=1500, min_df=5, max_df=0.7, stop_words=stopwords.words('english'))
            data = self.vectorizer.fit_transform(self.__normalizeItems(df["item_name"])).toarray()
            self.transformer = TfidfTransformer()
            data = self.transformer.fit_transform(data).toarray()
            self.model = RandomForestClassifier(n_estimators=1000, random_state=0)
            self.model.fit(data, df["type"])
            #Save model so it can be obtained more efficiently next time
            pickle.dump(self.model, open("model.sav", "wb"))
            pickle.dump(self.vectorizer.vocabulary_, open("_tokens.pkl", "wb"))
    
    def __normalizeItems(self, itemsList):
        normalizedItems = []
        for i in range(0, len(itemsList)):
            normalizedItems.append(self.__normalizeItem(itemsList[i]))
        return normalizedItems

    def __normalizeItem(self, item):
        nItem = re.sub(r'\W', ' ', str(item))
        nItem = re.sub(r'\s+[a-zA-Z]\s+', ' ', nItem)
        nItem = re.sub(r'\^[a-zA-Z]\s+', ' ', nItem) 
        nItem = re.sub(r'\s+', ' ', nItem, flags=re.I)
        nItem = re.sub(r'^b\s+', '', nItem)
        nItem = nItem.lower()
        nItem = nItem.split()
        nItem = [self.stemmer.lemmatize(word) for word in nItem]
        nItem = ' '.join(nItem)
        return nItem

    def predict(self, item):
        normalized = self.__normalizeItem(item["item_name"])
        normalized = self.vectorizer.transform([normalized]).toarray()
        normalized = self.transformer.fit_transform(normalized).toarray()
        prediction = self.model.predict(normalized)
        return prediction[0] 

    def predictList(self, itemsList):
        normalized = self.__normalizeItems([x["item_name"] for x in itemsList])
        normalized = self.vectorizer.transform(normalized).toarray()
        normalized = self.transformer.fit_transform(normalized).toarray()
        prediction = self.model.predict(normalized)
        return prediction

#if __name__== "__main__":
    #rm = RestaurantManager("r_features.json")
    # classifier = Classifier(itemsPath="classified.json", modelPath="model.sav")
    # item1 = {"restaurant": "Benihana", "item_name": "Dr Pepper", "calories": 70, "serving": "oz", "brand_id": "521b95434a56d006cae29803", "type": "Drink"}
    # item2 = {"restaurant": "Olive Garden", "item_name": "Five Cheese Ziti al Forno", "calories": 1220, "serving": "serving", "brand_id": "513fbc1283aa2dc80c000024", "type": "Italian"}
    # print(classifier.predict(item1))
    # print(classifier.predict(item2))

    # restaurants = dict() #brand_id -> Restaurant
    # indexMap = dict()    #Facilitate reverse lookup indicies -> brand_id
    # menuItems = [x for x in getMenuItem("classified_test.json", 0)]

    # rIndex = 0
    # for item in menuItems:
    #     if item["brand_id"] not in restaurants:
    #         restaurants[item["brand_id"]] = Restaurant(item["brand_id"], item["restaurant"], rIndex)
    #         indexMap[rIndex] = item["brand_id"]
    #         rIndex += 1
    #     restaurants[item["brand_id"]].addItem(item["type"])
    
    # for rest in restaurants.values():
    #     rest.normalize()
    
    # path = "r_features.json"
    # with open(path, "a+") as out:
    #     for rest in restaurants.values():
    #         out.write(str(rest))
    #         out.write(",\n")

    # tree = KDTree(np.array( [x.vector for x in restaurants.values()]))
    # user1 = np.array([0.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0]) #American = 1.0
    # dist, ind = tree.query(user1.reshape(1,-1), k=5, sort_results=True, return_distance=True)
    # print("*"*120,"\nAmerican = 1.0:  query v = ", user1)
    # for j, i in enumerate(ind[0]):
    #     print(str(i).rjust(5), ", ", restaurants[indexMap[i]].name.rjust(25), ", target v = ".rjust(10), str([round(x, 2) for x in restaurants[indexMap[i]].vector]).rjust(50), ", dist = ".rjust(7), str(dist[0][j]).rjust(15))


    
    


    




