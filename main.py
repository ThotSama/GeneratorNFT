from dataclasses import dataclass
from openpyxl import Workbook, load_workbook
import PIL
import sqlite3
import os
import glob
from random import randint
import sqlite3


@dataclass
class Image:
    name: str
    filters: list
    matrixOfPixels: list
    

@dataclass
class Collection:
    name: str
    imageSize: int
    listOfImages: list
    listOfCategories: list
    categoriesOptional: list #0 = optionnel, 1 = obligatoire
    numberMaxOfImages: int



#-----BASE DE DONNEES------#

def majFiltresDB():
    
    #ATTENTION, avant de lancer cette fonction, veuillez supprimer tout enregistrement dans la base de données actuelle
    
    #nb de filtres par categories
    tailleNbFiltre = [12,4,4,6]
    #nom de chaque filtre
    nomFiltres = [["fond1","fond2","fond3","fond4","fond5","fond6",
                   "fond7","fond8","fond9","fond10","fond11","fond12"],
                  ["body1","body2","body3","body4"],
                  ["smile1","smile2","smile3","smile4"],
                  ["eyes1","eyes2","eyes3","eyes4","eyes5","eyes6"]]
    #id_filtre
    compteurID = 1
    #pour chaque categorie
    for i in range(len(tailleNbFiltre)):
        #pour chaque filtre dans la categorie i
        for j in range(tailleNbFiltre[i]):
            #creation de l'insert correspondant au filtre j
            sql = "INSERT INTO Filtre VALUES ('"+str(compteurID)+"', '"+nomFiltres[i][j]+"', '"+str(i+1)+"');"
            #insertion dans la BDD
            insertInDB(sql)
            #id_filtre +1
            compteurID += 1
            

def openDB(nameDB):
    connexion = sqlite3.connect('stockageNFT.db')
    cursor = connexion.cursor()
    return connexion, cursor
    
def insertInDB(strCommand):
    global connexion, cursor
    cursor.execute(strCommand)
    connexion.commit()

def selectInDB(strCommand):
    global connexion, cursor
    cursor.execute(strCommand)
    connexion.commit()
    rows = cursor.fetchall()
    return rows

def afficheSelect(resultSelect):
    for line in resultSelect:
        print(line)

def closeDB(connexion):
    connexion.close()
#--------------------------#


def recupCategories(nameCollection):
    
    listOfCategories = [i.split('/')[-1] for i in os.listdir('./Collections/'+nameCollection+'/Filtres/')]
    return listOfCategories
    
def createCollection(name, size, nbMaxImages) -> Collection:
    listOfCategories = recupCategories(name)
    return Collection(name, size, [],listOfCategories,[], nbMaxImages)

def addImageInCollection(collection, image):
    return collection.listOfImages.append(image)


def allFiltersForCategorie(collection, nameCategorie):
    
    file_list = [i.split('/')[-1] for i in glob.glob('./Collections/collectionTest/Filtres/'+nameCategorie+'/*png')]
    for i in range(len(file_list)):
        file_list[i] = file_list[i].replace(nameCategorie+"\\",'')
    return file_list

def chooseFilter(listAllFilters):
    filtersChosen = []
    randNumber = 0
    for i in range(len(listAllFilters)):
        filtersChosen.append(listAllFilters[i][randint(0, len(listAllFilters[i])-1)])
    return filtersChosen


def getPixelOfImage(pathImage, collection, categorie, boolFilter):
    if boolFilter:
        img = PIL.Image.open("Collections/"+collection.name+"/Filtres/"+categorie+"/"+pathImage).convert('RGBA')
        
    else:
        img = pathImage
    largeur, hauteur = img.size
    listOfPixels = []
    for x in range(largeur):
        lineOfPixels = []
        for y in range(hauteur):
            # récupére les valeurs du pixel
                
            lineOfPixels.append((img.getpixel((x,y))[0], img.getpixel((x,y))[1], img.getpixel((x,y))[2], img.getpixel((x,y))[3]))
        listOfPixels.append(lineOfPixels)

    return listOfPixels

def applyFilter(filterMatrice, imageFinale):
    for x in range(len(filterMatrice)):
        for y in range(len(filterMatrice[0])):
            
            pixelFilter = filterMatrice[x][y]
            if pixelFilter[3] != 0 :
                imageFinale.putpixel((x,y), (int(pixelFilter[0]),int(pixelFilter[1]),int(pixelFilter[2])))
    return imageFinale

def createImage(collection, nameImage):

    listAllFilters = []
    for i in range (len(collection.listOfCategories)):
        listAllFilters.append(allFiltersForCategorie(collection, collection.listOfCategories[i]))
    filtersChosen = chooseFilter(listAllFilters)
    
    imgTotale = PIL.Image.new('RGBA', (collection.imageSize, collection.imageSize))
    imgTotale.putalpha(0)
    for i in range(len(filtersChosen)):
        
        pixelOfOneFilter = getPixelOfImage(filtersChosen[i], collection, collection.listOfCategories[i], True)
        
        imgTotale = applyFilter(pixelOfOneFilter, imgTotale)

    #sauvegarde dans la bdd
    sqlCommand = "SELECT * FROM IMAGE;"
    rows = selectInDB(sqlCommand)
    
        #insert into image
    id_image = str(len(rows)+1)
    sqlCommand = "INSERT INTO IMAGE(id_image, name_image, id_collection) VALUES('"+id_image+"', '"+str(nameImage.replace(".png",""))+"', '0');"
    insertInDB(sqlCommand)
    
        #insert into filtreAppliques
    for i in range(len(filtersChosen)):
        idFiltre = selectInDB("select id_filtre from filtre where name_filtre = '"+str(filtersChosen[i].replace(".png","")+"';"))
        idFiltre = str(str(str(idFiltre).replace("[('","")).replace("',)]",""))
        sqlCommand = "INSERT INTO FILTRESAPPLIQUES VALUES('"+str(len(rows)+1)+"', '"+str(idFiltre)+"');"
        insertInDB(sqlCommand)


    #sauvegarde de l'image    
    imgTotale.save('./Collections/'+collection.name+'/Images/'+nameImage)

    
    return imgTotale


def createXImages(collection, nbImage):
    allImages = []
    for i in range(nbImage):
        newImage = createImage(collectionTest, "nft"+str(i+1)+".png")
        print("Image n°"+str(i+1)+" / "+str(nbImage))
    
    return allImages

#-------------TESTS--------------#
nameDB = 'stockageNFT.db'
connexion, cursor = openDB(nameDB)


collectionTest = createCollection("collectionTest", 64, 1152)
#createXImages(collectionTest, 100)
for i in range(100):
    print("Image "+str(i+1)+" / 100")
    afficheSelect(selectInDB("select name_filtre from filtre inner join filtresAppliques on filtre.id_filtre = filtresAppliques.id_filtre where id_image = '"+str(i+1)+"';"))
    print("\n")

       
closeDB(connexion)


