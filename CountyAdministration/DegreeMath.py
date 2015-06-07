##############################Explanation Start

# Author: Dirk
# Created: 2013-10-14
# Updated: 2015-06-06

# Create a command line user interface that starts like this:
# ---------------------------------------------------------------
# Degree math options:
# 1) Difference; finds the difference between two entered angles.
# 2) Minus; subtracts the second entered angle from the first.
# 3) Plus; adds the second entered angle to the first.
# Enter 1, 2, or 3 to make a selection.
# ---------------------------------------------------------------

# Use a switch statement for these values
# case default -- return to screen and explain that you need to enter
# a one, two, or three.

# Needs to use a simple base of 60 for minutes and seconds.
# Degress will use a base of 90 as they are in quadrants.


#*****************Start************************#
def print_menu():
    print "---------------------------------------------------------------"
    print "Degree Math options:"
    print "1) Difference. Finds the difference between two angles."
    print "2) Subtraction. Subtracts the second angle from the first."
    print "3) Addition. Adds the second angle to the first."
    print "0) Exit. Exits the program."
    print "Note:"
    print "Addition goes clockwise, Subtraction goes counterclockwise."
    print "Please type 0, 1, 2, or 3 and hit ENTER to make a selection."
    print "---------------------------------------------------------------"

def menuLogic(selection = 0):
    if selection == 1:
        difference_prompts()
    elif selection == 2:
        addSubtractPrompts(1)
    elif selection == 3:
        addSubtractPrompts(0)
    elif selection == 0:
        print "Exiting...."
    else :
        print "Please enter a digit between 0 and 3."

class angleObject(object):
    def __init__(totalDegrees, minutes, seconds, preDirection = "N", \
                 postDirection = "W"):
        preDirection = preDirection
        totalDegrees = totalDegrees
        degrees = totalDegrees
        minutes = minutes
        seconds = seconds
        postDirection = postDirection

def normalize(passedAngle):
    normalizeValue = 0
    while normalizeValue != 2:
      if passedAngle.seconds < 0:
          passedAngle.seconds += 60
          passedAngle.minutes -= 1
      if passedAngle.seconds >= 60:
          passedAngle.seconds -= 60
          passedAngle.minutes += 1
      if passedAngle.minutes < 0:
          passedAngle.minutes += 60
          passedAngle.degrees -= 1
      if passedAngle.minutes >= 60:
          passedAngle.minutes -= 60
          passedAngle.degrees += 1
      if passedAngle.degrees >= 360:
          passedAngle.degrees -= 360
      if passedAngle.degrees < 0:
          passedAngle.degrees += 360
      if (passedAngle.seconds >= 0 and passedAngle.seconds < 60 and passedAngle.minutes >= 0 and passedAngle.minutes < 60 and 
          passedAngle.degrees >= 0 and passedAngle.degrees < 360):
          normalizeValue = 2
      
def difference_prompts():
    print "Difference of angles."
    print "Please enter the following information for angle one."
    angle1.preDirection = str(raw_input("Predirection (N or S):"))
    while angle1.preDirection != "N" and angle1.preDirection != "S" \
    and angle1.preDirection != "n" and angle1.preDirection != "s":
        print "Predirection is not north or south!"
        angle1.preDirection = str(raw_input("Predirection (N or S):"))
        
    validate1 = 0
    while validate1 != 2:
        angle1.degrees = raw_input("Degrees:")
        try :
            testVar = int(angle1.degrees)
            if testVar >= 0 and testVar <= 90:
                validate1 = 2
            else :
                print "Please enter an integer between 0 and 90."
                validate1 = 0
        except (TypeError, ValueError):
            print "Input not valid."
            print "Please enter an integer between 0 and 90."
            validate1 = 0
    angle1.degrees = int(angle1.degrees)
    
    validate1 = 0
    while validate1 != 2:
        angle1.minutes = raw_input("Minutes:")
        try :
            testVar = int(angle1.minutes)
            if testVar >= 0 and testVar <= 59:
                validate1 = 2
            else :
                print "Please enter an integer between 0 and 59."
                validate1 = 0
        except (TypeError, ValueError):
            print "Input not valid."
            print "Please enter an integer between 0 and 59."
            validate1 = 0
        angle1.minutes = int(angle1.minutes)
            
    validate1 = 0
    while validate1 != 2:
        angle1.seconds = raw_input("Seconds:")
        try :
            testVar = int(angle1.seconds)
            if testVar >= 0 and testVar <= 59:
                validate1 = 2
            else :
                print "Please enter an integer between 0 and 59."
                validate1 = 0
        except (TypeError, ValueError):
            print "Input not valid."
            print "Please enter an integer between 0 and 59."
            validate1 = 0
    angle1.seconds = int(angle1.seconds)
    
    angle1.postDirection = str(raw_input("Postdirection (E or W):"))
    while angle1.postDirection != "E" and angle1.postDirection != "W" \
    and angle1.postDirection != "e" and angle1.postDirection != "w":
        print "Postdirection is not E or W!"
        angle1.postDirection = str(raw_input("Postdirection (E or W):"))

    #****************Start of Angle Two**************************#
    
    print "Please enter the following information for angle one."
    angle2.preDirection = str(raw_input("Predirection (N or S):"))
    while angle2.preDirection != "N" and angle2.preDirection != "S" \
    and angle2.preDirection != "n" and angle2.preDirection != "s":
        print "Predirection is not north or south!"
        angle2.preDirection = str(raw_input("Predirection (N or S):"))
        
    validate1 = 0
    while validate1 != 2:
        angle2.degrees = raw_input("Degrees:")
        try :
            testVar = int(angle2.degrees)
            if testVar >= 0 and testVar <= 90:
                validate1 = 2
            else :
                print "Please enter an integer between 0 and 90."
                validate1 = 0
        except (TypeError, ValueError):
            print "Input not valid."
            print "Please enter an integer between 0 and 90."
            validate1 = 0
    angle2.degrees = int(angle2.degrees)
    
    validate1 = 0
    while validate1 != 2:
        angle2.minutes = raw_input("Minutes:")
        try :
            testVar = int(angle2.minutes)
            if testVar >= 0 and testVar <= 59:
                validate1 = 2
            else :
                print "Please enter an integer between 0 and 59."
                validate1 = 0
        except (TypeError, ValueError):
            print "Input not valid."
            print "Please enter an integer between 0 and 59."
            validate1 = 0
        angle2.minutes = int(angle2.minutes)
            
    validate1 = 0
    while validate1 != 2:
        angle2.seconds = raw_input("Seconds:")
        try :
            testVar = int(angle2.seconds)
            if testVar >= 0 and testVar <= 59:
                validate1 = 2
            else :
                print "Please enter an integer between 0 and 59."
                validate1 = 0
        except (TypeError, ValueError):
            print "Input not valid."
            print "Please enter an integer between 0 and 59."
            validate1 = 0
    angle2.seconds = int(angle2.seconds)
    
    angle2.postDirection = str(raw_input("Postdirection (E or W):"))
    while angle2.postDirection != "E" and angle2.postDirection != "W" \
    and angle2.postDirection != "e" and angle2.postDirection != "w":
        print "Postdirection is not E or W!"
        angle2.postDirection = str(raw_input("Postdirection (E or W):"))

    #****************End of Angle Two*************************#

    print "Finding the difference."
    # All three need to normalize to the Northeast quarter prior
    # to calculations.
    
    # Start angle one adjustments
    if angle1.preDirection == "N" or angle1.preDirection == "n":
        if angle1.postDirection == "E" or angle1.postDirection == "e":
            #Already in the NE quadrant. No need to change anything.
            pass
        elif angle1.postDirection == "W" or angle1.postDirection == "w":
            # Now in the NW quadrant. The degrees from northwest start
            # is 0 is 270. But, the angle starts at 270 with N 90 W.
            # It then counts down to 360 being N 0 W.
            # How do I map that?
            # N 89 59 59 W = Global 270 00 01.
            # 90 0 0 - N 89 59 59 W = 0 0 1
            # 0 0 1 + 270 0 0 = 270 00 01
            angle1.seconds = 0 - angle1.seconds
            angle1.minutes = 0 - angle1.minutes
            angle1.degrees = 90 - angle1.degrees
            normalize(angle1)
            angle1.degrees += 270
    elif angle1.preDirection == "S" or angle1.preDirection == "s":
        if angle1.postDirection == "E" or angle1.postDirection == "e":
            # Now in the SE quadrant. The degrees from north is 0 is 90
            # plus the angle's degrees.
            angle1.seconds = 0 - angle1.seconds
            angle1.minutes = 0 - angle1.minutes
            angle1.degrees = 90 - angle1.degrees
            normalize(angle1)
            angle1.degrees += 90
        elif angle1.postDirection == "W" or angle1.postDirection == "w":
            # Now in the SW quadrant. The true degrees from 0 is 180
            # plus the angle's degrees.
            angle1.degrees += 180
            
    #**********************Adjustment Break****************************#
    # Start angle two adjustments
    if angle2.preDirection == "N" or angle2.preDirection == "n":
        if angle2.postDirection == "E" or angle2.postDirection == "e":
            #Already in the NE quadrant. No need to change anything.
            pass
        elif angle2.postDirection == "W" or angle2.postDirection == "w":
            # Now in the NW quadrant. The degrees from northwest start
            # is 0 is 270. But, the angle starts at 270 with N 90 W.
            # It then counts down to 360 being N 0 W.
            # N 89 59 59 W = Global 270 00 01.
            # 90 0 0 - N 89 59 59 W = 0 0 1
            # 0 0 1 + 270 0 0 = 270 00 01
            angle2.seconds = 0 - angle2.seconds
            angle2.minutes = 0 - angle2.minutes
            angle2.degrees = 90 - angle2.degrees
            normalize(angle2)
            angle2.degrees += 270
    elif angle2.preDirection == "S" or angle2.preDirection == "s":
        if angle2.postDirection == "E" or angle2.postDirection == "e":
            # Now in the SE quadrant. The degrees from north is 0 is 90
            # plus the angle's degrees.
            angle2.seconds = 0 - angle2.seconds
            angle2.minutes = 0 - angle2.minutes
            angle2.degrees = 90 - angle2.degrees
            normalize(angle2)
            angle2.degrees += 90
        elif angle2.postDirection == "W" or angle2.postDirection == "w":
            # Now in the SW quadrant. The true degrees from 0 is 180
            # plus the angle's degrees.
            angle2.degrees += 180
            
    angle3.seconds = angle1.seconds - angle2.seconds
    angle3.minutes = angle1.minutes - angle2.minutes
    angle3.degrees = angle1.degrees - angle2.degrees
    
    normalize(angle3)
    
    if angle3.degrees > 360:
        angle3.degrees = angle3.degrees % 360
    elif angle3.degrees < 0:
        angle3.degrees = angle3.degrees + 360
    if angle3.degrees > 180:
        angle3.seconds = 0 - angle3.seconds
        angle3.minutes = 0 - angle3.minutes
        angle3.degrees = 360 - angle3.degrees
        normalize(angle3)
        
    # At this point, I need to check to output whether or not
    # going from angle 1 to angle 2 is additive or subtractive.
        
    print "The difference between the two angles is:"
    calcOutputOne = str(angle3.degrees) + str(degreeSymbol) + ","
    calcOutputTwo = str(angle3.minutes) + str(minutesSymbol) + ","
    calcOutputThree = str(angle3.seconds) + str(secondsSymbol)
    print calcOutputOne, calcOutputTwo, calcOutputThree

def addSubtractPrompts(subtractVar):
    if subtractVar == 1:
        print "Angle Subtraction."
    else :
        print "Angle Addition."
    
    print "Please enter the following information for angle one."
    angle1.preDirection = str(raw_input("Predirection (N or S):"))
    while angle1.preDirection != "N" and angle1.preDirection != "S" \
    and angle1.preDirection != "n" and angle1.preDirection != "s":
        print "Predirection is not north or south!"
        angle1.preDirection = str(raw_input("Predirection (N or S):"))
        
    validate1 = 0
    while validate1 != 2:
        angle1.degrees = raw_input("Degrees:")
        try :
            testVar = int(angle1.degrees)
            if testVar >= 0 and testVar <= 90:
                validate1 = 2
            else :
                print "Please enter an integer between 0 and 90."
                validate1 = 0
        except (TypeError, ValueError):
            print "Input not valid."
            print "Please enter an integer between 0 and 90."
            validate1 = 0
    angle1.degrees = int(angle1.degrees)
    
    validate1 = 0
    while validate1 != 2:
        angle1.minutes = raw_input("Minutes:")
        try :
            testVar = int(angle1.minutes)
            if testVar >= 0 and testVar <= 59:
                validate1 = 2
            else :
                print "Please enter an integer between 0 and 59."
                validate1 = 0
        except (TypeError, ValueError):
            print "Input not valid."
            print "Please enter an integer between 0 and 59."
            validate1 = 0
        angle1.minutes = int(angle1.minutes)
            
    validate1 = 0
    while validate1 != 2:
        angle1.seconds = raw_input("Seconds:")
        try :
            testVar = int(angle1.seconds)
            if testVar >= 0 and testVar <= 59:
                validate1 = 2
            else :
                print "Please enter an integer between 0 and 59."
                validate1 = 0
        except (TypeError, ValueError):
            print "Input not valid."
            print "Please enter an integer between 0 and 59."
            validate1 = 0
    angle1.seconds = int(angle1.seconds)
    
    angle1.postDirection = str(raw_input("Postdirection (E or W):"))
    while angle1.postDirection != "E" and angle1.postDirection != "W" \
    and angle1.postDirection != "e" and angle1.postDirection != "w":
        print "Postdirection is not E or W!"
        angle1.postDirection = str(raw_input("Postdirection (E or W):"))

    #****************Start of Angle Two**************************#
    
    print "Please enter the following information for angle two."

    validate1 = 0
    while validate1 != 2:
        angle2.degrees = raw_input("Degrees:")
        try :
            testVar = int(angle2.degrees)
            if testVar >= -359 and testVar <= 359:
                validate1 = 2
            else :
                print "Please enter an integer between -359 and 359."
                validate1 = 0
        except (TypeError, ValueError):
            print "Input not valid."
            print "Please enter an integer between -359 and 359."
            validate1 = 0
    angle2.degrees = int(angle2.degrees)
    
    validate1 = 0
    while validate1 != 2:
        angle2.minutes = raw_input("Minutes:")
        try :
            testVar = int(angle2.minutes)
            if testVar >= 0 and testVar <= 59:
                validate1 = 2
            else :
                print "Please enter an integer between 0 and 59."
                validate1 = 0
        except (TypeError, ValueError):
            print "Input not valid."
            print "Please enter an integer between 0 and 59."
            validate1 = 0
        angle2.minutes = int(angle2.minutes)
            
    validate1 = 0
    while validate1 != 2:
        angle2.seconds = raw_input("Seconds:")
        try :
            testVar = int(angle2.seconds)
            if testVar >= 0 and testVar <= 59:
                validate1 = 2
            else :
                print "Please enter an integer between 0 and 59."
                validate1 = 0
        except (TypeError, ValueError):
            print "Input not valid."
            print "Please enter an integer between 0 and 59."
            validate1 = 0
    angle2.seconds = int(angle2.seconds)

    #****************End of Angle Two*************************#
    
    # Start angle one adjustments

    if angle1.preDirection == "N" or angle1.preDirection == "n":
        if angle1.postDirection == "E" or angle1.postDirection == "e":
            #Already in the NE quadrant. No need to change anything.
            pass
        elif angle1.postDirection == "W" or angle1.postDirection == "w":
            # Now in the NW quadrant. The degrees from northwest start
            # is 0 is 270. But, the angle starts at 270 with N 90 W.
            # It then counts down to 360 being N 0 W.
            # N 89 59 59 W = Global 270 00 01.
            # 90 0 0 - N 89 59 59 W = 0 0 1
            # 0 0 1 + 270 0 0 = 270 00 01
            angle1.seconds = 0 - angle1.seconds
            angle1.minutes = 0 - angle1.minutes
            angle1.degrees = 90 - angle1.degrees
            normalize(angle1)
            angle1.degrees += 270
    elif angle1.preDirection == "S" or angle1.preDirection == "s":
        if angle1.postDirection == "E" or angle1.postDirection == "e":
            # Now in the SE quadrant. The degrees from north is 0 is 90
            # plus the angle's degrees.
            angle1.seconds = 0 - angle1.seconds
            angle1.minutes = 0 - angle1.minutes
            angle1.degrees = 90 - angle1.degrees
            normalize(angle1)
            angle1.degrees += 90
        elif angle1.postDirection == "W" or angle1.postDirection == "w":
            # Now in the SW quadrant. The true degrees from 0 is 180
            # plus the angle's degrees.
            angle1.degrees += 180
            
    #**********************Visual Break****************************#

    if subtractVar == 1:
        print "Subtracting..."
        angle3.seconds = angle1.seconds - angle2.seconds
        angle3.minutes = angle1.minutes - angle2.minutes
        angle3.degrees = angle1.degrees - angle2.degrees
    else :
        print "Adding..."
        angle3.seconds = angle1.seconds + angle2.seconds
        angle3.minutes = angle1.minutes + angle2.minutes
        angle3.degrees = angle1.degrees + angle2.degrees

    normalize(angle3)

    if (angle3.degrees >= 0 and (angle3.degrees < 90 or (angle3.degrees == 90 and angle3.minutes == 0 and angle3.seconds == 0))) \
        or (angle3.degrees == 360 and (angle3.minutes > 0 or angle3.seconds > 0)):
        angle3.preDirection = "N"
        angle3.postDirection = "E"
    elif (angle3.degrees > 90 and (angle3.degrees < 180 or (angle3.degrees == 180 and angle3.minutes == 0 and angle3.seconds == 0))) \
        or (angle3.degrees == 90 and (angle3.minutes > 0 or angle3.seconds > 0)):
        angle3.seconds = 0 - angle3.seconds
        angle3.minutes = 0 - angle3.minutes
        angle3.degrees = 180 - angle3.degrees
        angle3.preDirection = "S"
        angle3.postDirection = "E"
    elif (angle3.degrees > 180 and (angle3.degrees < 270 or (angle3.degrees == 270 and angle3.minutes == 0 and angle3.seconds == 0))) \
        or (angle3.degrees == 180 and (angle3.minutes > 0 or angle3.seconds > 0)):
        #angle3.seconds = angle3.seconds - 0
        #angle3.minutes = angle3.minutes - 0
        angle3.degrees = angle3.degrees - 180
        angle3.preDirection = "S"
        angle3.postDirection = "W"
    elif (angle3.degrees > 270 and angle3.degrees < 360) or (angle3.degrees == 270 and (angle3.minutes > 0 or angle3.seconds > 0)):
        angle3.seconds = 0 - angle3.seconds
        angle3.minutes = 0 - angle3.minutes
        angle3.degrees = 360 - angle3.degrees
        angle3.preDirection = "N"
        angle3.postDirection = "W"
    else :
        print "Error assigning quadrant."
        
    normalize(angle3)
    
    print "The calculated angle is:"
    calc_output_one = str(angle3.degrees) + str(degreeSymbol) + ","
    calc_output_two = str(angle3.minutes) + str(minutesSymbol) + ","
    calc_output_three = str(angle3.seconds) + str(secondsSymbol)
    print angle3.preDirection, calc_output_one, calc_output_two, \
          calc_output_three, angle3.postDirection

angle1 = angleObject(0, 0, 0)
angle2 = angleObject(0, 0, 0)
angle3 = angleObject(0, 0, 0)

angle1.preDirection = "N"
angle1.degrees = 0
angle1.minutes = 0
angle1.seconds = 0
angle1.postDirection = "E"

angle2.preDirection = "N"
angle2.degrees = 0
angle2.minutes = 0
angle2.seconds = 0
angle2.postDirection = "E"

angle3.preDirection = "N"
angle3.degrees = 0
angle3.minutes = 0
angle3.seconds = 0
angle3.postDirection = "E"

menuInput = 1

menuThank = ""

degreeSymbol = unichr(176).encode("latin-1")
angleWithDegree = ""

minutesSymbol = "'"
secondsSymbol = '"'

validate1 = 0
validate2 = 0
validate3 = 0

testVar = 0

calcOutputOne = ""
calcOutputTwo = ""
calcOutputThree = ""


#***************************Main Program Start*************#
print "Welcome to the Degree Math program."

while menuInput != 0:
    validate2 = 0
    while validate2 != 2:
        print_menu()
        menuInput = raw_input("")
        try :
            testVar = int(menuInput)
            if testVar >= 0 and testVar <= 3:
                validate2 = 2
            else :
                print "Please enter an integer between 0 and 3."
                validate2 = 0
        except (TypeError, ValueError):
            print "Input not valid."
            print "Please enter an integer between 0 and 3."
            validate2 = 0
    menuInput = int(menuInput)
    print menuThank
    menuLogic(menuInput)
exit