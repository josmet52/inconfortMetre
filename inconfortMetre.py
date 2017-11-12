#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
inconfortMetre.py 
Version 1.0
19.9.2017

Mesure de l'inconfort de conduite d'une voiture en
affichant les variations d'accélérations par unité de temps
inconfort = dacc/dt

en vert = inconfort longitudinal
en rouge inconfort transversal
en bleu inconfort vertical
en moyenne quadratique des trois mesures

nMilliSec = (csteFiltrage / nbrePasses) * 1000
nMilliSec = temps entre deux mesures en fonction
            de la constante de temps de filtrage 
            et du nombre de mesures utilisées pour la moyenne

Le joystick permet :
 haut-bas de changer la sensibilité de l'affichage de l'inconfort
 gauche-droite de changer la durée du filtrage mobile en secondes
 centre de changer l'intensité des leds et si 5 pressions successives de quitter le programme

(c) josmet 2017
joseph.metrailler@bluewin.ch

"""

# importation des modules externes
from sense_hat import SenseHat
import os
import time
from datetime import datetime
from math import *
##import pygame
##from pygame.locals import *
import sys

#initialisation du Sensehat
sense = SenseHat()  
sense.clear()

#initialisation pygame
##pygame.init()
##pygame.display.init()
##dispaly=pygame.display.set_mode((80, 60))

# constantes pour les couleurs
dim_factor = 3
c_color_val = int(255 / dim_factor)
c_black = [0, 0, 0]
c_green = [0, c_color_val, 0]
c_red = [c_color_val, 0, 0]
c_blue = [0, 0, c_color_val]
c_white = [c_color_val, c_color_val, c_color_val]
c_yellow = [c_color_val, c_color_val, 0]

# dimensions de la amtrice sensehat
x_pix = 8
y_pix = 8

# User Settings
debug = False
deepDebug = False
lightDim = True

# pour changer un status, passer le mot "debug" ou  "deepDebug" en paramètre
for x in sys.argv: 
    if x == "debug":
        debug = True
    elif x == "deepDebug":
        deepDebug = True
    
if debug :
    print("confortmetre version 0.1")
    print("------------------------")
    print("debug = %s" % debug)
    print("deepDebug = %s" % deepDebug)
    print("lightDim = %s" % lightDim)
    print("------------------------")
    print("Runing")

# paramètre de l'application
nbrePasses = 100
csteFiltrage = 5. # filtrage sur 5 secondes
gainFactor = 5
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

# initialisation des variables de mesure de l'accélération x, y et z
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

# initialisation des variables compteurs
cptPasses = 0
listIndex = 0
oldTime = 0 
overTimeCount = 0

# initialisation des variables de duree
newTime = int(round(time.time()*1000)) # new time en ms
vTime = newTime - oldTime # delta t en ms

# et c'est parti
running = True
stopCount = 0
sense.set_rotation(90)
sense.show_message("go", text_colour = c_white)
sense.set_rotation(0)

#try:
    
while running:
    
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
        print (x2, x1, vTime, dx)
        print (y2, y1, vTime, dy)
        print (z2, z1, vTime, dz)
        print (dt)
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

    for event in sense.stick.get_events():
#        print("The joystick was {} {}".format(event.action, event.direction))
        if event.action == "pressed":
            if deepDebug : print("The joystick was {} {} {}".format(event.action, event.direction, str(stopCount)))
            if event.direction == "up" :
                stopCount = 0
                csteFiltrage -= 0.5
                sense.show_message("f" +str(csteFiltrage), text_colour = c_white)
                nMilliSec = int(csteFiltrage/nbrePasses*1000)
                if debug : print ("csteFiltrage = " + str(csteFiltrage) + " - nMilliSec = " + str(nMilliSec) + " - vTime = " + str(vTime) + " - nbrePasses = " + str(nbrePasses))
            elif event.direction == "down" :
                stopCount = 0
                csteFiltrage += 0.5
                sense.show_message("f" +str(csteFiltrage), text_colour = c_white)
                nMilliSec = int(csteFiltrage/nbrePasses*1000)
                if debug : print ("csteFiltrage = " + str(csteFiltrage) + " - nMilliSec = " + str(nMilliSec) + " - vTime = " + str(vTime) + " - nbrePasses = " + str(nbrePasses))
            elif event.direction == "left" :
                stopCount = 0
                gainFactor-= 1
                sense.show_message("g" +str(gainFactor), text_colour = c_white)
                if debug : print ("gainFactor = " + str(gainFactor))
            elif event.direction == "right" :
                stopCount = 0
                gainFactor += 1
                sense.show_message("g" +str(gainFactor), text_colour = c_white)
                if debug : print ("gainFactor = " + str(gainFactor))
            elif event.direction == "middle" :
                stopCount += 1
                #if debug : print ("k_enter " + str(stopCount))
                lightDim = not(lightDim)
                if lightDim:
                    c_color_val = int(c_color_val / dim_factor)
                else:
                    c_color_val = 255
                    
                c_black = [0, 0, 0]
                c_green = [0, c_color_val, 0]
                c_red = [c_color_val, 0, 0]
                c_blue = [0, 0, c_color_val]
                c_white = [c_color_val, c_color_val, c_color_val]
                c_yellow = [c_color_val, c_color_val, 0]
                
            sense.set_rotation(0)
            
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
        if deepDebug : print ("." + str(overTimeCount) + " " + str(nbrePasses))
        newTime = min(int(round(time.time()*1000)),1)
        vTime = newTime - oldTime

    if overTimeCount > over_time_limit:
        nbrePasses -= passes_thresh
        nMilliSec = int(csteFiltrage/nbrePasses*1000)
        overTimeCount = 0
        if deepDebug :
            print
            print ("+", nbrePasses, cptPasses, " / " , nMilliSec, vTime, " / " , datetime.now())

    if listIndex == 0 :
        cptPasses = 1
        if deepDebug :
            print (nbrePasses, cptPasses, nMilliSec, vTime , " - ",)

    if stopCount > 4 : running = False

# et oui bye bye
sense.set_rotation(90)
sense.show_message("... bye")
sense.set_rotation(0)
        
##except:
##    print
##    print "------------------------------------------------------------------------------------------------------"
##    print
##    print vTime, nMilliSec, " - ", meanmx, meanmy, meanmz, meantot
##    print "... bye ..."
##    print "------------------------------------------------------------------------------------------------------"
