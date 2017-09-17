#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

Essai de mesure de l'inconfort de conduite d'une voiture en
affichant les variations d'accélérations par unité de temps
inconfort = dacc/dt

(c) metra 2017
joseph.metrailler@bluewin.ch

"""

# importation des modules externes
from sense_hat import SenseHat
import time
from datetime import datetime
from math import *


# constantes pour les couleurs
c_black = [0, 0, 0]
c_green = [0, 255, 0]
c_red = [255, 0, 0]
c_blue = [0, 0, 255]
c_white = [255, 255, 255]
c_yellow = [255, 255, 0]

# dimensions de l'écran
x_pix = 8
y_pix = 8

# User Settings
debug = False
deepDebug = False
light_dim = False

print("confortmetre version 0.1")
print("------------------------")
print("debug = %s" % debug)
print("deepDebug = %s" % deepDebug)
print("light dim = %s" % light_dim)
print("------------------------")
print("Runing")

#initialisation du Sensehat
sense = SenseHat()  
sense.clear()

# paramètre de l'application
nbrePasses = 120
csteFiltrage = 5. # filtrage sur 10 secondes
gainFactor = 1
passes_thresh = 1
over_time_limit = 5
nMilliSec = int(csteFiltrage/nbrePasses*1000)

# initialisation variables
i=0
mx=[]
my=[]
mz=[]
mt=[]

# mise à zero des vecteurs 
while i < nbrePasses:
    mx.append(0)
    my.append(0)
    mz.append(0)
    mt.append(0)
    i += 1

# setting des valeurs initiales des variables de mesure de l'accélération
x1 = 0
y1 = 0
z1 = 0

x2 = 0
y2 = 0
z2 = 0

totmx = 0
totmy = 0
totmz = 0
totmt = 0

cptPasses = 0
listIndex = 0
oldTime = 0 
overTimeCount = 0

# initialisation des variables 
newTime = int(round(time.time()*1000)) # new time en ms
vTime = newTime - oldTime # delta t en ms

#try:
while True:
    while True:
        
        # index dans la liste
        listIndex = cptPasses % (nbrePasses - 1)

        # on récupère les valeurs de la passe précédente
        x1 = x2
        y1 = y2
        z1 = z2
        
        # on lit les nouvelles valeurs
        x2, y2, z2 = sense.get_accelerometer_raw().values()
        
        # on calcule les différences dacc/dt
        dx = abs(x2-x1)*1000/vTime
        dy = abs(y2-y1)*1000/vTime
        dz = abs(z2-z1)*1000/vTime
        # et la somme quadratique
        dt = sqrt(dx*dx+dy*dy+dz*dz)/3

        if deepDebug :
            print
            print x2, x1, vTime, dx
            print y2, y1, vTime, dy
            print z2, z1, vTime, dz
            print dt
            print

        # totaux pour les moyennes, seule la dernière valeur lue est actualisée
        totmx = totmx - mx[listIndex] + dx
        totmy = totmy - my[listIndex] + dy
        totmz = totmz - mz[listIndex] + dz
        totmt = totmt - mt[listIndex] + dt

        # et la liste des valeurs est mise à jour pour la valeur actuelle
        mx[listIndex] = dx
        my[listIndex] = dy
        mz[listIndex] = dz
        mt[listIndex] = dt

        # calcul des valeurs moyennes sur les nombre de passes
        # et multiplication par le gainFactor pour correspondre à l'étendue de l'affichage
        meanmx = min(int(totmx / nbrePasses * gainFactor),8)
        meanmy = min(int(totmy / nbrePasses * gainFactor),8)
        meanmz = min(int(totmz / nbrePasses * gainFactor),8)
        meanmt = min(int(totmt / nbrePasses * gainFactor),8)

        # affichage des mesures
        sense.clear()

        # dacc/dt pour l'axe des x
        i = 0
        while i < meanmx:
            sense.set_pixel(i,0,c_green)
            i += 1

        # dacc/dt pour l'axe des y
        i = 0
        while i < meanmy:
            sense.set_pixel(i,1,c_red)
            i += 1

        i = 0
        while i < meanmz:
            sense.set_pixel(i,2,c_blue)
            i += 1

        # dacc/dt pour l'axe des z
        i = 0
        while i < meanmt:
            sense.set_pixel(i,4,c_yellow)
            sense.set_pixel(i,5,c_yellow)
            sense.set_pixel(i,6,c_yellow)
            sense.set_pixel(i,7,c_yellow)
            i += 1

        # mise à jour du compteur de passes et de l'index des listes
        cptPasses += 1
        listIndex = cptPasses % (nbrePasses )

        # on attend le nbre de ms prévu
        
        while vTime < nMilliSec:
            newTime = int(round(time.time()*1000))
            vTime = newTime - oldTime

        # prêt pour l prochaine passe
        oldTime = newTime

        # algorithme adaptation du nombre de passes
        # la constante de temps de moyennage n'est pas modifiée, seuls le nombre de passes
        # et l'intervalle entre deux mesures sont adaptés
        # 
        # reduction du nombre de passes si le programme utilise plus de temps qu'attribué

        if vTime > nMilliSec :
            
            overTimeCount += 1
            if debug : print "." ,overTimeCount
            newTime = min(int(round(time.time()*1000)),1)
            vTime = newTime - oldTime

        if overTimeCount > over_time_limit:
            nbrePasses -= passes_thresh
            nMilliSec = int(csteFiltrage/nbrePasses*1000)
            overTimeCount = 0
            if deepDebug :
                print
                print "+", nbrePasses, cptPasses, " / " , nMilliSec, vTime, " / " , datetime.now()

        if listIndex == 0 :
            if debug :
                print nbrePasses, cptPasses, nMilliSec, vTime , " - ",
            cptPasses = 1
        
##except:
##    print
##    print "------------------------------------------------------------------------------------------------------"
##    print
##    print vTime, nMilliSec, " - ", meanmx, meanmy, meanmz, meantot
##    print "... bye ..."
##    print "------------------------------------------------------------------------------------------------------"
