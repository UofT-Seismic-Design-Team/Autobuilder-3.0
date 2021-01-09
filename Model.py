from Definition import *    # for constants
import math as m

# Module description: 
# - Stores classes that define the geometry of the tower and its components

# -------------------------------------------------------------------------
# Wrapper class for all the data
class Tower:

    def __init__(self, elevations = []):
        # Geometry
        self.elevations = elevations
        self.floors = {}
        self.columns = {}
        self.floorPlans = {}
        self.panels = {}
        self.bracings = {}
        self.faces = []

        # Section properties
        self.sections = {}

        # Groups and assignments
        self.bracingGroups = {}
        self.sectionGroups = {}
        self.assignments = {}
        
        # Input table
        self.member_ids = {} # Member id from SAP2000 model (key: member_id; value: sectionGroup)
        self.inputTable = {}

    def setElevations(self, elevs):
        self.elevations = elevs

    def setSections(self, sects):
        self.sections = sects

    def reset(self):
        ''' clear all data '''
        self.elevations.clear()
        self.floors.clear()
        self.columns.clear()
        self.floorPlans.clear()
        self.panels.clear()
        self.sections.clear()
        self.bracings.clear()
        self.bracingGroups.clear()
        self.sectionGroups.clear()
        self.assignments.clear()
        self.faces.clear()
        self.member_ids.clear()
        self.inputTable.clear()

    def build(self):
        ''' build tower (assume all tower components are saved in tower)'''
        self.defineFloors()

        self.addFloorPlansToFloors()
        self.addPanelsToFloors()

        for name in self.floorPlans:
            self.generateFacesByFloorPlan(self.floorPlans[name])
        self.generateColumnsByFace()     

    def defineFloors(self):
        ''' Add Floor objects to the member variables based on the elevations '''
        for elev in self.elevations:
            # Create new floor if needed
            if not (elev in self.floors):
                self.floors[elev] = Floor(elev)

        # Delete redundant floors
        for elev in self.floors:
            if not (elev in self.elevations):
                del self.floors[elev]

    def addFace(self, face):
        ''' Add face object to faces '''
        self.faces.append(face)

    def addFloorPlan(self, floorPlan):
        ''' Add floor plan object to floorPlans '''
        self.floorPlans[floorPlan.name] = floorPlan

    def addPanel(self, panel):
        ''' Add panel object to panels '''
        self.panels[panel.name] = panel

    def addBracing(self, bracing):
        ''' Add bracing object to bracings '''
        self.bracings[bracing.name] = bracing

    def addBracingGroup(self, group):
        ''' Add bracing group object to bracing groups '''
        self.bracingGroups[group.name] = group

    def addSectionGroup(self, group):
        ''' Add section group object to section groups '''
        self.sectionGroups[group.name] = group

    def addAssignment(self, assignment):
        ''' Add bracing assignment objects to bracing assignments '''
        self.assignments[assignment.name] = assignment

    def addFloorPlansToFloors(self):
        ''' Add floor plans to floors based on the elevation '''
        for floorPlan in self.floorPlans.values():
            for elev in floorPlan.elevations:
                if elev in self.floors:
                    self.floors[elev].addFloorPlan(floorPlan)

    def clearFloor(self):
        '''Clears the floor plan prior to updating them'''
        for elev in self.elevations:
            if elev in self.floors:
                self.floors[elev].floorPlans.clear()
                self.floors[elev].panels.clear()

    def addPanelsToFloors(self):
        ''' Add panels to floors based on the elevation '''
        for panel_id in self.panels:
            panel = self.panels[panel_id]
            elevation = panel.lowerLeft.z
            
            floor = self.floors[elevation]

            floor.addPanel(panel)

    def generatePanels_addToFloors(self):
        self.generatePanelsByFace()
        self.addPanelsToFloors()

    def generateFacesByFloorPlan(self, floorPlan):
        ''' Generate face objects by floor plan '''

        for member in floorPlan.members:
            face = Face()
            for elev in floorPlan.elevations:

                memberStart = member.start_node
                memberEnd = member.end_node

                # Add elevation to member
                start = Node()
                start.setLocation(memberStart.x, memberStart.y, elev)
                end = Node()
                end.setLocation(memberEnd.x, memberEnd.y, elev)

                member = Member()
                member.setNodes(start, end)

                face.addMember(elev, member)

            self.faces.append(face)

    def generatePanelsByFace(self):
        ''' Generate panel objects by faces '''
        for face in self.faces:
            # Step 1: sort the keys out (elevation)
            elevations = list(face.members.keys())
            elevations.sort()
            # Step 2: use members to form panels
            for i in range (len(elevations)-1):
                bottomMember = face.members[elevations[i]]
                topMember = face.members[elevations[i+1]]
                # Step 3: form panel
                panel = Panel()
                panel.definePanelWithMembers(topMember, bottomMember)
                # Step 4: add panel to panels
                self.panels[panel.name] = panel

    def generateColumnsByFace(self):
        ''' Add column objects by face '''
        for face in self.faces:
            # Step 1: sort the keys out (elevation)
            elevations = list(face.members.keys())
            elevations.sort()
            # Step 2: use members to generate columns
            for i in range (len(elevations)-1):
                bottomMember = face.members[elevations[i]]
                topMember = face.members[elevations[i+1]]

                leftColumn = Member()
                leftColumn.setNodes(bottomMember.start_node, topMember.start_node)

                rightColumn = Member()
                rightColumn.setNodes(bottomMember.end_node, topMember.end_node)

                self.columns[leftColumn.name] = leftColumn
                self.columns[rightColumn.name] = rightColumn

    def updateInputTable(self,inputTable):
        self.inputTable = inputTable

# -------------------------------------------------------------------------
class Floor:
    def __init__(self, elevation):
        self.elevation = elevation
        self.nodes = []
        self.floorPlans = {}
        self.panels = []
    
    def addPanel(self, panel):
        self.panels.append(panel)

    def addNode(self, node):
        self.nodes.append(node)

    def addFloorPlan(self, floorPlan):
        self.floorPlans[floorPlan.name] = floorPlan

    def __str__(self):
        return "Floor elevation: " + str(self.elevation)

# -------------------------------------------------------------------------
class FloorPlan:

     # static variable for id
    id = 1

    def __init__(self, name=None):
        self.name = name    # name is in string form
        if not name:
            self.name = str(FloorPlan.id)
            FloorPlan.id += 1

        self.nodes = []
        self.members = []
        self.elevations = []

    def addNode(self, node):
        self.nodes.append(node)

    def addMember(self, member):
        self.members.append(member)

    def generateMembersfromNodes(self):
        self.members.clear()
        numNodes = len(self.nodes)
        for i in range(numNodes-1):
            member = Member(self.nodes[i], self.nodes[i+1])
            self.addMember(member)
        member = Member(self.nodes[numNodes-1], self.nodes[0])
        self.addMember(member)

    def addElevation(self, elevation):
        self.elevations.append(elevation)

    def __str__(self):
        return "Floor Plan " + str(self.name)

# -------------------------------------------------------------------------
class Face:

    # static variable for id
    id = 1

    def __init__(self, name=None):

        # Use id as name if name is not provided
        self.name = name
        if not name:
            self.name = str(Face.id)
            Face.id += 1

        # contains horizontal members/beams on the face
        # key: elevation; element: member
        self.members = {}

    def addMember(self, elevation, member):
        self.members[elevation] = member

# -------------------------------------------------------------------------
class Panel:

    # static variable for id
    id = 1

    def __init__(self, name=None):

        # Use id as name if name is not provided
        self.name = name
        if not name:
            self.name = str(Panel.id)
            Panel.id += 1

        # Nodes that define a panel object
        self.lowerLeft = Node()
        self.upperLeft = Node()
        self.upperRight = Node()
        self.lowerRight = Node()

        # Bracing that is assigned to a panel object
        self.bracingGroup = ''

    def definePanelWithNodes(self, lowerLeft, upperLeft, upperRight, lowerRight):
        ''' Define panel with nodes '''
        self.lowerLeft = lowerLeft
        self.upperLeft = upperLeft
        self.upperRight = upperRight
        self.lowerRight = lowerRight

    def definePanelWithMembers(self, topMember, bottomMember):
        ''' Define panel with top and bottom members in the same orientation '''
        self.lowerLeft = bottomMember.start_node
        self.lowerRight = bottomMember.end_node
        self.upperLeft = topMember.start_node
        self.upperRight = topMember.end_node

    def addBracingAssignment(self, bGroup):
        self.bracingGroup = bGroup

    def __str__(self):
        return "Panel " + str(self.name)

# -------------------------------------------------------------------------
class Node:

    # static variable for id
    id = 1

    def __init__(self, x = 0, y = 0, z = 0, name = None):

        # Use id if name is not provided
        self.name = name
        if not name:
            self.name = str(Node.id)
            Node.id +=  1

        self.x = x
        self.y = y
        self.z = z

    def setLocation(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        
    def __str__(self):
        return str(self.name) + " (" + str(self.x) + "," + str(self.y) + "," + str(self.z) + ")"

# -------------------------------------------------------------------------
class Member:

    # static variable for id
    id = 1

    def __init__(self, start_node=Node(), end_node=Node(), name=None):

        # Use id if name is not provided
        self.name = name
        if not name:
            self.name = str(Member.id)
            Member.id +=  1

        self.start_node = start_node
        self.end_node = end_node

        self.material = None

    def addMaterial(self, mat):
        self.material = mat

    def setNodes(self, start, end):
        ''' set start and end nodes '''
        self.start_node = start
        self.end_node = end

    def angle(self):
        ''' Find angle between the member and the x axis --> in radians '''
        start = self.start_node
        end = self.end_node

        slope = (end.y - start.y) / (end.x - start.x + Algebra.EPSILON) # tolerance to avoid divison by zero
        
        orientationX = end.x - start.x
        orientationY = end.y - start.y

        angle = abs(m.atan(slope))
        
        # First quadrant
        if orientationX >= 0 and orientationY >= 0:
            angle = angle
        # Second quadrant
        elif orientationX < 0 and orientationY > 0:
            angle = m.pi - angle
        # Third quadrant
        elif orientationX <= 0 and orientationY <= 0:
            angle += m.pi
        # Fourth quardant
        elif orientationX > 0 and orientationY < 0:
            angle = m.pi*2 - angle

        return angle
# --------------------------------------------------------------------------
class Bracing:

    # static variable for id
    id = 1

    def __init__(self, name=None):
        self.name = name    # name is in string form
        if not name:
            self.name = str(Bracing.id)
            Bracing.id += 1

        self.nodePairs = []
        self.members = []
        self.materials = []

    def addNodes(self, node1, node2):
        self.nodePairs.append([node1,node2])

    def addMember(self, member):
        self.members.append(member)

    def addMat(self, mat):
        self.materials.append(mat)

    def generateMembersfromNodes(self):
        numNodePairs = len(self.nodePairs)
        for i in range(numNodePairs):
            member = Member(self.nodePairs[i][0], self.nodePairs[i][1])
            member.addMaterial(self.materials[i])
            self.addMember(member)

    def __str__(self):
        return "Bracing " + str(self.name)

# --------------------------------------------------------------------------     

class BracingGroup:
    # static variable for id
    id = 1

    def __init__(self, name=None):
        self.name = name    # name is in string form
        if not name:
            self.name = str(BracingGroup.id)
            BracingGroup.id += 1

        self.bracings = []
        self.panelAssignments = []
    
    def addBracing(self, bracing):
        self.bracings.append(bracing)

    def addPanel(self, panel):
        self.panelAssignments.append(panel)

class SectionGroup:
    # static variable for id
    id = 1

    def __init__(self, name=None):
        self.name = name    # name is in string form
        if not name:
            self.name = str(SectionGroup.id)
            SectionGroup.id += 1

        self.sections = []
        self.memberIdAssignments = []
    
    def addSection(self, section):
        self.sections.append(section)

    def addMemberId(self, member_id):
        self.memberIdAssignments.append(member_id)

# --------------------------------------------------------------------------
class Assignment:

     # static variable for id
    id = 1

    def __init__(self, name=None):
        self.name = name    # name is in string form
        if not name:
            self.name = str(assignment.id)
            assingment.id += 1

        self.bracingGroup = None

    def addBracingGroup(self, group):
        self.bracingGroup = group

    def __str__(self):
        return "Assignment" + str(self.name)


'''ADD function to go back to bottom floor once top is reached'''

class Section:

    def __init__(self, name, rank):
        self.name = name
        self.rank = rank

    def setName(self, name):
        self.name = name

    def setRank(self, rank):
        self.rank = rank