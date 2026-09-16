"""Distinct hand-drawn footballer faces; smooth cel contours in editable meshes."""
import bpy
import messi_floating as art


def smooth(points,steps=6):
    result=[]
    for i in range(len(points)):
        a,b,c,d=(points[(i+j)%len(points)] for j in (-1,0,1,2))
        for n in range(steps):
            t=n/steps
            result.append(tuple(.5*((2*b[k])+(-a[k]+c[k])*t+(2*a[k]-5*b[k]+4*c[k]-d[k])*t*t+(-a[k]+3*b[k]-3*c[k]+d[k])*t*t*t) for k in (0,1)))
    return result


def redraw(root,ronaldo=False):
    prefixes=('Face','Hair','Beard','Moustache','Left ear','Right ear','Eye','Iris','Brow','Nose','Mouth','Lower lip','Ronaldo jaw','Ronaldo smile')
    for obj in list(root.children):
        if obj.name.startswith(prefixes):bpy.data.objects.remove(obj,do_unlink=True)
    for name,color in {'complexion':'#edbb96','facelight':'#ffdab4','contour':'#b77d62','lip':'#ae705e','darkbeard':'#593c2e','beardlit':'#81563d','iris':'#56482c'}.items():art.material(name,color)
    def p(name,pts,c,y=-.45,soft=True):return art.shape(name,smooth(pts) if soft else pts,c,y,root,width=.011)
    def l(name,pts,c='ink',y=-.56,w=.01):return art.ink(name,pts,y,w,c,root)
    def e(name,x,z,rx,rz,c,y=-.53):return art.oval(name,x,z,rx,rz,c,y,root,False)
    for side in (-1,1):
        e('Portrait ear',side*.405,5.93,.105,.165,'complexion',-.41)
        l('Ear contour',[(side*.43,6.01),(side*.47,5.95),(side*.43,5.84)],'contour',-.44)
    if ronaldo:
        p('CR face',[(-.36,6.29),(-.18,6.41),(.17,6.41),(.35,6.27),(.38,5.95),(.30,5.63),(.18,5.44),(-.10,5.42),(-.29,5.58),(-.38,5.91)],'complexion')
        p('CR cheek shadow',[(.29,6.25),(.37,6.03),(.32,5.78),(.22,5.54),(.04,5.48),(.12,5.75),(.21,5.87)],'contour',-.465)
        p('CR hair',[(-.37,5.98),(-.43,6.32),(-.36,6.5),(-.12,6.56),(.18,6.63),(.39,6.5),(.42,6.28),(.35,5.99),(.29,6.29),(.03,6.37),(-.20,6.31),(-.28,6.28)],'hair',-.49)
        for i in range(5):
            l('CR swept hair',[(-.30+i*.08,6.39),(-.12+i*.08,6.49),(.08+i*.065,6.51)],'hairlight',-.54,.008)
        for side in (-1,1):
            x=side*.18
            p('CR almond eye',[(x-.092,6.026),(x-.016,6.067),(x+.086,6.035),(x+.022,5.997)],'white',-.515)
            e('CR iris',x+.004,6.029,.030,.038,'iris',-.535)
            e('CR pupil',x+.004,6.029,.014,.031,'ink',-.545)
            e('CR catchlight',x-.005,6.043,.008,.009,'white',-.555)
            l('CR eyebrow',[(x-.09,6.126),(x-.02,6.145),(x+.09,6.11)],'hair',-.56,.018)
            l('CR cheekbone',[(side*.28,5.91),(side*.19,5.82)],'contour',-.54,.008)
        l('CR nose bridge',[(.025,6.08),(.032,5.96),(.078,5.88),(.053,5.846)],'contour')
        l('CR nostrils',[(-.072,5.855),(-.036,5.831),(.015,5.846),(.07,5.837)],'beard',w=.009)
        p('CR lips',[(-.14,5.706),(-.055,5.728),(.006,5.714),(.066,5.723),(.143,5.738),(.092,5.667),(-.037,5.65)],'lip',-.53)
        l('CR mouth line',[(-.13,5.705),(-.01,5.695),(.13,5.724)],'beard',-.56,.008)
        l('CR chin crease',[(-.064,5.545),(.04,5.526),(.115,5.554)],'contour',-.54,.007)
    else:
        p('Leo face',[(-.34,6.31),(-.12,6.44),(.17,6.40),(.35,6.21),(.36,5.94),(.30,5.62),(.13,5.42),(-.14,5.41),(-.34,5.62),(-.4,5.99)],'complexion')
        p('Leo temple shadow',[(.27,6.27),(.35,6.15),(.35,5.93),(.24,5.67),(.10,5.65),(.17,5.97)],'contour',-.46)
        p('Leo beard',[(-.37,5.99),(-.27,5.77),(-.15,5.75),(-.04,5.80),(.12,5.78),(.27,5.80),(.35,6.00),(.31,5.59),(.18,5.38),(-.02,5.32),(-.21,5.4),(-.34,5.6)],'darkbeard',-.48)
        p('Leo beard light',[(-.26,5.72),(-.11,5.64),(.13,5.67),(.23,5.56),(.09,5.40),(-.08,5.39),(-.22,5.49)],'beardlit',-.49)
        p('Leo hair',[(-.38,5.99),(-.44,6.28),(-.37,6.48),(-.23,6.55),(-.09,6.59),(.09,6.56),(.26,6.53),(.38,6.4),(.37,6.14),(.31,5.99),(.27,6.26),(.15,6.32),(-.01,6.30),(-.23,6.34),(-.30,6.18)],'hair',-.50)
        for i in range(5):l('Leo hair strands',[(-.3+i*.09,6.41),(-.22+i*.09,6.49),(-.13+i*.08,6.47)],'hairlight',-.54,.011)
        for side in (-1,1):
            x=side*.18
            p('Leo eye',[(x-.095,6.023),(x-.02,6.058),(x+.079,6.029),(x+.015,6.005)],'white',-.515)
            e('Leo iris',x+.011,6.027,.029,.031,'iris',-.535)
            e('Leo pupil',x+.011,6.027,.014,.027,'ink',-.545)
            e('Leo eye light',x+.002,6.04,.007,.008,'white',-.555)
            l('Leo brow',[(x-.10,6.123),(x-.018,6.135),(x+.083,6.103)],'hair',-.56,.02)
            l('Leo under eye',[(x-.074,5.974),(x+.033,5.965)],'contour',-.54,.007)
        l('Leo nose',[(.00,6.09),(-.012,5.975),(.043,5.87),(.01,5.83),(-.081,5.85)],'beard',w=.011)
        p('Leo moustache',[(-.17,5.76),(-.045,5.803),(.018,5.776),(.112,5.788),(.19,5.723),(.10,5.693),(.015,5.72),(-.10,5.70)],'darkbeard',-.55)
        l('Leo mouth',[(-.11,5.675),(.014,5.661),(.12,5.68)],'ink',-.57,.01)
        l('Leo lip highlight',[(-.045,5.629),(.047,5.622)],'complexion',-.56,.009)
        for i in range(9):
            x=-.22+i*.055;l('Leo beard strand',[(x,5.57-abs(x)*.2),(x+.01,5.48-abs(x)*.1)],'darkbeard',-.555,.006)
