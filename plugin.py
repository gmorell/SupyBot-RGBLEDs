###
# Copyright (c) 2013, Gabriel Morell-Pacheco
# All rights reserved.
#
#
###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

import time
import random
import os
import threading

PIN_RED = 0
PIN_GRE = 1
PIN_BLU = 2
CTL_CMD = 'echo "%i=%.2f" > /dev/pi-blaster'

#some helper functions
def randRGB():
    r = random.randint(0,255)
    g = random.randint(0,255)
    b = random.randint(0,255)
    return [r,g,b]

def stepTo(pres,dest,stepsize=4):
    if abs(pres-dest) > stepsize:
        if pres > dest:
            pres -=stepsize
        elif pres < dest:
            pres +=stepsize
        else:
            pass
    else:
        pres = dest
    return pres

def split_every_n(sequence,n):
    while sequence:
        yield sequence[:n]
        sequence = sequence[n:]

def clean_rgb_message(msg):
    return [int(a) for a in msg.split(' ') if 255 >= int(a) >= 0]

class RGBLEDs(callbacks.Plugin):
    """Add the help for "@plugin help RGBLEDs" here
    This should describe *how* to use this plugin."""
    threaded = True
    def __init__(self,irc):
        self.__parent = super(RGBLEDs,self)
        self.__parent.__init__(irc)
        self.e = threading.Event()
        self.RGB = [255,255,255]
        self.steptime = 1
        self.steptime_fast = 0.05
        self.stepsize = 4

    def write_value(self,pin,value):
        os.popen(CTL_CMD % (pin,value))

    def write_rgb(self):
        #print CTL_CMD % (PIN_RED, float(self.RGB[0])/255.)
        #print self.RGB
        os.popen(CTL_CMD % (PIN_RED, self.RGB[0]/255.))
        os.popen(CTL_CMD % (PIN_GRE, self.RGB[1]/255.))
        os.popen(CTL_CMD % (PIN_BLU, self.RGB[2]/255.))

    #here begins self,irc
    def _stahp(self,irc):
        irc.reply('Stopping Current Action')
        self.e.set()
        
    def stahp(self,irc,msg,args):
        irc.reply('Stopping Current Action')
        self.e.set()
        
    stop = wrap(stahp)

    def setcolour(self,irc,msg,args,text):
        """
            sets a colour
        """
        self._stahp(irc)
        colors = list(split_every_n(clean_rgb_message(text),3))[0]
        if len(colors) == 3:
            self.RGB[0] = colors[0]
            self.RGB[1] = colors[1]
            self.RGB[2] = colors[2]
            self.write_rgb()
            irc.reply("Set Colours to %s" % self.RGB)
        else:
            irc.reply("Colour Message Too Short")
    setcolour = wrap(setcolour, ['text'])
        
    def _randomstep(self,irc):
        #self.RGB = randRGB()
        while not self.e.isSet():
            newRGB = randRGB()
            while self.RGB != newRGB:
                self.RGB[0] = stepTo(self.RGB[0],newRGB[0],self.stepsize)
                self.RGB[1] = stepTo(self.RGB[1],newRGB[1],self.stepsize)
                self.RGB[2] = stepTo(self.RGB[2],newRGB[2],self.stepsize)
                
                self.write_rgb()
                
                time.sleep(self.steptime)
                
    def randomstep(self,irc,msg,args):
        """
            steps between random rgb values
        """
        self._stahp(irc)

        irc.reply("RandomSteps Engaged w/ %i seconds between steps" % self.steptime )
        self.e.clear()
        t = threading.Thread(target=self._randomstep, kwargs={'irc':irc})
        t.start()

    rand = wrap(randomstep)

    def _bounce(self,irc,colorlist):
        while not self.e.isSet():
            for col in colorlist:
                target = col
                while self.RGB != target:
                    self.RGB[0] = stepTo(self.RGB[0],target[0],self.stepsize)
                    self.RGB[1] = stepTo(self.RGB[1],target[1],self.stepsize)
                    self.RGB[2] = stepTo(self.RGB[2],target[2],self.stepsize)
                
                    self.write_rgb()
                
                    time.sleep(self.steptime)

    def bounce(self,irc,msg,args,text):
        """
            fady bounce between n colourpairs
            msg looks like 0 0 0 33 33 33 255 255 255
        """
        self._stahp(irc)
        
        colours = list(split_every_n(clean_rgb_message(text),3))
        rightlen = []
        for c in colours:
            if len(c) == 3:
                rightlen.append(c)
            
        irc.reply("Bouncing Engaged w/ %s colours" % len(rightlen) )
        self.e.clear()
        t = threading.Thread(target=self._bounce, kwargs={'irc':irc,'colorlist':rightlen})
        t.start()
        
    bounce = wrap(bounce,['text'])

    def _sieze(self,irc):
        while not self.e.isSet():
            self.RGB = randRGB()
            self.write_rgb()
            time.sleep(self.steptime_fast)

    def sieze(self,irc,msg,args):
        """
            steps between random rgb values. no fading max fast. final destination
        """
        self._stahp(irc)

        irc.reply("Siezure Mode Engaged w/ %s seconds between steps" % self.steptime_fast )
        self.e.clear()
        t = threading.Thread(target=self._sieze, kwargs={'irc':irc})
        t.start()

Class = RGBLEDs


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
