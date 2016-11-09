# Paul Flaten
# 10/7/2016

from copy import deepcopy
from math import sqrt, pi, radians, sin, cos

import Draft


Doc = FreeCAD.ActiveDocument

V = FreeCAD.Vector
Rotation = FreeCAD.Rotation
Placement = FreeCAD.Placement

XL_GEAR_TOOTHPRINT = [V(-1.525411,-1),V(-1.525411,0),V(-1.41777,0.015495),V(-1.320712,0.059664),V(-1.239661,0.129034),V(-1.180042,0.220133),V(-0.793044,1.050219),V(-0.733574,1.141021),V(-0.652507,1.210425),V(-0.555366,1.254759),V(-0.447675,1.270353),V(0.447675,1.270353),V(0.555366,1.254759),V(0.652507,1.210425),V(0.733574,1.141021),V(0.793044,1.050219),V(1.180042,0.220133),V(1.239711,0.129034),V(1.320844,0.059664),V(1.417919,0.015495),V(1.525411,0),V(1.525411,-1)]
MXL_GEAR_TOOTHPRINT = [V(-0.660421,-0.5),V(-0.660421,0),V(-0.621898,0.006033),V(-0.587714,0.023037),V(-0.560056,0.049424),V(-0.541182,0.083609),V(-0.417357,0.424392),V(-0.398413,0.458752),V(-0.370649,0.48514),V(-0.336324,0.502074),V(-0.297744,0.508035),V(0.297744,0.508035),V(0.336268,0.502074),V(0.370452,0.48514),V(0.39811,0.458752),V(0.416983,0.424392),V(0.540808,0.083609),V(0.559752,0.049424),V(0.587516,0.023037),V(0.621841,0.006033),V(0.660421,0),[0.660421,-0.5]]


XL_GEAR_TOOTH_PROFILE = [["NAME", "XL"], ["TOOTHPRINT", XL_GEAR_TOOTHPRINT], ["STD_TOOTH_WIDTH", 3.051], ["STD_TOOTH_DEPTH", 1.27], ["STD_TOOTH_PITCH", 5.08], ["STD_PITCH_LINE_OFFSET", 0.254]]
#More Profiles to come...

def Remove_Object(Object_Name, Doc_Name = ""):
    if Doc_Name == "":
        Doc.removeObject(Object_Name)
    else:
        FreeCAD.getDocument(Doc_Name).removeObject(Object_Name)
    return

def Make_a_Polygon_Sketch(Name = "Unnamed_Polygon", Nodes = [V(0,0,0)], Closed = False, Placement = Placement(V(0,0,0), Rotation(0,0,0))):
    New_Polygon = Doc.addObject("Part::Polygon", Name)
    New_Polygon.Nodes = Nodes
    New_Polygon.Close = Closed
    New_Polygon.Placement = Placement
    Doc.recompute()
    return New_Polygon

def Make_a_Circle_Sketch(Name = "Unnamed_Circle", Radius = 1, Angle0 = 0.0, Angle1 = 0.0, Placement = Placement(V(0,0,0), Rotation(0,0,0))):
    New_Circle = Doc.addObject("Part::Circle", Name)
    New_Circle.Radius = Radius
    New_Circle.Angle0 = Angle0
    New_Circle.Angle1 = Angle1
    New_Circle.Placement = Placement
    Doc.recompute()
    return New_Circle

def Make_an_Extrusion(Target_Sketch_Name, Extrusion_Name = "Unnamed_Extrusion", Extrusion_Array = (0,0,0), Placement = Placement(V(0,0,0), Rotation(0,0,0)), Solid = (False), TaperAngle = (0)):
    Current_Extrusion = Doc.addObject("Part::Extrusion", Extrusion_Name)
    Current_Extrusion.Base = Doc.getObjectsByLabel(Target_Sketch_Name)[0]
    Current_Extrusion.Dir = Extrusion_Array
    Current_Extrusion.Solid = Solid
    Current_Extrusion.TaperAngle = TaperAngle
    Current_Extrusion.Placement = Placement
    Doc.getObject(Target_Sketch_Name).ViewObject.Visibility = False
    Doc.recompute()
    return Current_Extrusion

def Make_a_Cut(Base_Object_Name, Tool_Object_Name, Cut_Name = "Unnamed_Cut"):
    Base = Doc.getObjectsByLabel(Base_Object_Name)[0]
    Tool = Doc.getObjectsByLabel(Tool_Object_Name)[0]
    New_Cut = Doc.addObject("Part::Cut", Cut_Name)
    New_Cut.Base = Base
    New_Cut.Tool = Tool
    Base.ViewObject.Visibility = False
    Tool.ViewObject.Visibility = False
    New_Cut.ViewObject.ShapeColor = Base.ViewObject.ShapeColor
    New_Cut.ViewObject.DisplayMode = Base.ViewObject.DisplayMode
    Doc.recompute()
    return New_Cut

class Gear:
    """Base class for building a gear."""

    Tooth_profile_name     = ""
    Toothprint             = []
    Tooth_Width         = 0
    Tooth_Depth         = 0
    Tooth_Pitch         = 0
    Pitch_Line_Offset     = 0

    Sketches             = []
    Extrusions             = []
    Cuts                 = []

    def __init__(self,
                 teeth=6,
                 width=1,
                 Additional_Tooth_Width=0,
                 Additional_Tooth_Depth=0):
        self.Number_of_Teeth = teeth
        self.Gear_Width = width
        self.Tooth_Width += Additional_Tooth_Width
        self.Tooth_Depth += Additional_Tooth_Depth


    def Ready_for_Computation(self):
        if self.Toothprint == []:
            return False
        elif self.Tooth_Pitch < 0:
            print("ERROR! Value Tooth_Pitch must be greatter than 0")
            return False
        elif self.Pitch_Line_Offset < 0:
            print("ERROR! Value Pitch_Line_Offset must be greatter than 0")
            return False
        elif self.Number_of_Teeth <= 2:
            print("ERROR! Value Number_of_Teeth must be greatter than or equal to 2")
            return False
        elif self.Gear_Width < 0:
            print("ERROR! Value Gear_Width must be greatter than 0")
            return False
        else:
            return True


    def Draw_Gear(self):
        if not self.Ready_for_Computation():
            # better to raise an exception here
            print("There are invalid values present. The Gear is not ready to be drawn.")
            return

        pulley_radius = self.Get_Tooth_Spacing()

        tooth_width_scale = self.Tooth_Width / self.Tooth_Width
        tooth_depth_scale = self.Tooth_Depth / self.Tooth_Depth
        Temporary_Toothprint = self.Toothprint

        #REMOVE##REMOVE##REMOVE##REMOVE##REMOVE##REMOVE##REMOVE##REMOVE##REMOVE##REMOVE##REMOVE##REMOVE##REMOVE#
        print("######################################################################################")
        print("Tooth width scale: " + str(tooth_width_scale))
        print("Tooth depth scale: " + str(tooth_depth_scale))
        print("Tooth width:    " + str(self.Tooth_Width))
        print("Tooth depth: " + str(self.Tooth_Depth))
        print("Temporary Toothprint: " + str(Temporary_Toothprint))
        print("######################################################################################")
        #REMOVE##REMOVE##REMOVE##REMOVE##REMOVE##REMOVE##REMOVE##REMOVE##REMOVE##REMOVE##REMOVE##REMOVE##REMOVE#

        Gear_Radius  = sqrt(pulley_radius**2 - (self.Tooth_Width / 2)**2)   # DJW: what is this about?

        self.Sketches.append(["Main_Gear_Body", Make_a_Circle_Sketch(Name = "Sketch_Main_Gear_Body", Radius = Gear_Radius)])
        self.Extrusions.append(["Main_Gear_Body", Make_an_Extrusion("Sketch_Main_Gear_Body", Extrusion_Name = "Extrusion_Main_Gear_Body", Extrusion_Array = (0,0,self.Gear_Width), Solid = (True))])

        #Temporary_Toothprint = deepcopy(self.Toothprint)
        #Temporary_Toothprint = self.Toothprint

        for vector in Temporary_Toothprint:
            vector.scale(tooth_width_scale, tooth_depth_scale, 1)

        current_tooth_number = 1

        for current_gear in range(0,self.Number_of_Teeth):
            current_rotation = 0 + (360 / self.Number_of_Teeth) * current_gear
            current_position_x = Gear_Radius * cos(radians(current_rotation - 90 ))
            current_position_y = Gear_Radius * sin(radians(current_rotation - 90))

            self.Sketches.append(["Tooth" + str(current_tooth_number), Make_a_Polygon_Sketch(Name = "Sketch_Tooth" + str(current_tooth_number), Nodes = Temporary_Toothprint, Closed = True, Placement = Placement(V(current_position_x, current_position_y, 0), Rotation(current_rotation, 0, 0)))])
            self.Extrusions.append(["Tooth" + str(current_tooth_number), Make_an_Extrusion("Sketch_Tooth" + str(current_tooth_number), Extrusion_Name = "Extrusion_Tooth" + str(current_tooth_number), Extrusion_Array = (0,0,self.Gear_Width), Solid = (True))])

            if current_tooth_number == 1:
                self.Cuts.append(["Tooth" + str(current_tooth_number), Make_a_Cut("Extrusion_Main_Gear_Body" , "Extrusion_Tooth" + str(current_tooth_number), Cut_Name = "Cut_Tooth" + str(current_tooth_number))])
            else:
                self.Cuts.append(["Tooth" + str(current_tooth_number), Make_a_Cut("Cut_Tooth" + str(current_tooth_number - 1), "Extrusion_Tooth" + str(current_tooth_number), Cut_Name = "Cut_Tooth" + str(current_tooth_number))])

            current_tooth_number = current_tooth_number + 1


    def Get_Tooth_Spacing(self):
        return ((self.Number_of_Teeth * self.Tooth_Pitch) / (pi * 2) - self.Pitch_Line_Offset)


    def Remove_Cuts(self):
        for Cut in reversed(self.Cuts):
            Doc.removeObject(Cut[1].Label)
        self.Cuts = []
        Doc.recompute()


    def Remove_Extrusions(self):
        for Extrusion in reversed(self.Extrusions):
            Doc.removeObject(Extrusion[1].Label)
        self.Extrusions = []
        Doc.recompute()


    def Remove_Sketches(self):
        for Sketch in reversed(self.Sketches):
            Doc.removeObject(Sketch[1].Label)
        self.Sketches = []
        Doc.recompute()


    def Remove_Gear(self):
        self.Remove_Cuts()
        self.Remove_Extrusions()
        self.Remove_Sketches()



class XLGear(Gear):
    Tooth_profile_name = "XL"
    Toothprint = XL_GEAR_TOOTHPRINT
    Tooth_Width = 3.051
    Tooth_Depth = 1.27
    Tooth_Pitch = 5.08
    Pitch_Line_Offset = 0.254



##Test Code. This is not a part of the program!
#New_Gear = Gear(XL_GEAR_TOOTH_PROFILE, 15, Gear_Width_OVR = 3)                # Will make a gear with radius 11.77520211936695 mm
#New_Gear.Draw_Gear()

g = XLGear(15, 5)
g.Draw_Gear()

