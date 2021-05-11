#!/bin/env python
# -*- coding: utf-8 -*-
#======================== IMPORTS ====================================

import os,sys,time
import argparse
import csv
import numpy as np
import geopandas as gpd
import pandas as pd


from osgeo import gdal, ogr

#======================== PARSER =====================================


parser = argparse.ArgumentParser(description='To create summarize from image , shapefile')
parser.add_argument('-inImg','--inputImage',required=True,help='Input image path (.tif)')
parser.add_argument('-inSHP','--inputSHP',required=True, help='input shapefile path (.shp)')
parser.add_argument('-NAME','--inputNAME',required=True, help='column name of class ("XXX")')
parser.add_argument('-CODE','--inputCODE',required=True, help='column code ("XXX")')
parser.add_argument('-out', '--outputFile',type=str,help='path where would you like create .csv')
parser.add_argument('-Nomenclature', '--outNom',type=str, nargs='?', help ='name off each class')

params=vars(parser.parse_args())

image_data_path = params['inputImage']
vector_data_path = params['inputSHP']
csvfile_path = params['outputFile']
Nomenclature_path = params['outNom']
NAME=params['inputNAME']
CODE=params['inputCODE']

startTime = time.time()

#===================== TRAITEMENT ====================================

print ('----- Processing -----')

#============== LECTURE DU SHP ==================================
data=gpd.GeoDataFrame.from_file(vector_data_path) #lecture du shape file


# ============ ETABLISSEMENT DE LECTURE DE CSV SANS INFO ========

poly_area=[]
for index, row in data.iterrows():
	poly_area.append(row['geometry'].area) # récupération manuelle de la surface
	#print('Polygon area at index {index} is : {area:.3f}'.format(index=index, area=poly_area)) 

surface_par_poly=np.array(poly_area[:])



if NAME in data:
	Nom_de_classe=data['LIBEL_V3']

	
taille_initiale=Nom_de_classe.shape[0]	
		
if CODE in data:
	code_v3=data['CODE_V3']
else:
	code_v3=[]



	
#=============== RECUPERATION DE RESOLUTION =====================

image = gdal.Open(image_data_path) # lecture de l'image
_,xres,_,_,_,yres=image.GetGeoTransform() #extraction de la résolution


#============== FILTRE DE DONNEES ===============================

unique_name=[]	# vecteur de noms unqiues
unique_name,reference=np.unique(Nom_de_classe, return_index=True) # remplissage du vecteur et ajout d'un index
idc=[] # vecteur d'indice des doublons
surface=[]
nbr_polygone=[]
Nbr_pixel=[]
for i in unique_name:
	idc=np.where(Nom_de_classe == i)[0] #récupération des coordonnées des doublons
	surface.append(sum(surface_par_poly[idc])) # pushback des données (sommes des polygnes de même nom)
	#surface.append(sum(surface_par_poly[idc]/xres))
	nbr_polygone.append(idc.shape[0])

#============== ECRITURE DU CSV ==================================

if len(code_v3)==0:
	entete={'Nom de classe':unique_name,'nbr polygone':nbr_polygone,'surface (m2)':surface}
else:
	entete={'Nom de classe':unique_name,'nbr polygone':nbr_polygone,'CODE_V3':code_v3[reference],'surface (m2)':surface} #forme du tableau
out_file=pd.DataFrame(entete)
out_file.to_csv(csvfile_path)

print('------------. SUMMARISE DONE .--------------')
#print(out_file)

#============== ECRITURE NOMENCLATURE ================
if Nomenclature_path is not None:
	print('---------. NOMENCLATURE DONE .----------')
	scalaire=str(range(1,len(unique_name)))
	with open(Nomenclature_path, 'w') as fic:
	    fic.write('\n'.join([str(nom) + ": " + str(i) for (nom, i) in zip(unique_name,range(1,len(unique_name)))]))
	fic.close()
else:
	print('---------. NO NOMENCLATURE .-----------')

#============ AFFICHAGE TPS EXECUTION ==============================

endTime = time.time()
print('----- complete -----')
print ('The script took ' + str(endTime - startTime)+ ' seconds')
 
