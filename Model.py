# Module description: 
# - Stores classes that define the geometry of the tower and its components

# -------------------------------------------------------------------------
class Tower:

    def __init__(self, elevations = []):
        self.elevations = elevations
        self.floorsPlan = []
        self.floors = {}
        self.nodes = {}
        self.columns = {}
        self.panels = {}
        self.faces = []

        self.defineFloors()

    def defineFloors(self):
        ''' Add Floor objects to the member variables based on the elevations '''
        for elev in self.elevations:
            self.floors[elev] = Floor(elev)

    def addNodesToFloors(self):
        ''' Add nodes to the floors they are on based on the elevation '''
        for node in self.nodes.values():
            if node.z in self.elevations:
                floor_at_z = self.floors[node.z]
                floor_at_z.addNode(node)

    def addFace(self, face):
        ''' Add face object to faces '''
        self.faces.append(face)

    def generateFacesByFloorPlan(self, floorPlan):
        ''' Generate face objects by floor plan '''

        for member in floorPlan.members:
            face = Face()
            for elev in floorPlan.elevations:

                memberStart = member.start_node
                memberEnd = member.end_node

                # Add elevation to memeber
                start = Node()
                start.setLocation(memberStart.x, memberStart.y, elev)
                end = Node()
                end.setLocation(memberEnd.x, memberEnd.y, elev)

                member = Member()
                member.setNodes(start, end)

                face.addMember(elev, member)

            self.faces.append(face)

    def addPanelsToFloors(self):
        ''' Add panels to floors based on the elevation '''
        for panel_id in self.panels:
            panel = self.panels[panel_id]
            elevation = panel.lowerLeft.z
            
            floor  = self.floors[elevation]

            floor.addPanel(panel)

    def generatePanelsByFace(self):
        ''' Generate panel objects by faces '''
        for face in self.faces:
            # Step 1: sort the keys out (by elevation)
            elevations = list(face.members.keys())
            elevations.sort()
            # Step 2: use members to form panels
            for i in range (len(elevations)-1):
                bottomMember = face.members[elevations[i]]
                topMember = face.members[elevations[i+1]]
                # Step 3: form panel
                panel = Panel()
                panel.definePanel(topMember, bottomMember)
                # Step 4: add panel to panels
                self.panels[panel.name] = panel

    def generateColumnsByFace(self):
        ''' Add column objects by face '''
        for face in self.faces:
            # Step 1: sort the keys out (by elevation)
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
        self.name = name
        if not name:
            self.name = FloorPlan.id
            FloorPlan.id += 1

        self.members = []
        self.elevations = []

    def addMember(self, member):
        self.members.append(member)

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
            self.name = Face.id
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
            self.name = Panel.id
            Panel.id += 1

        # Nodes that define a panel object
        self.lowerLeft = Node()
        self.upperLeft = Node()
        self.upperRight = Node()
        self.lowerRight = Node()

    def definePanel(self, topMember, bottomMember):
        ''' Define panel with top and bottom members with same orientation '''
        self.lowerLeft = bottomMember.start_node
        self.lowerRight = bottomMember.end_node
        self.upperRight = bottomMember.start_node
        self.upperLeft = bottomMember.end_node

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
            self.name = Node.id
            Node.id +=  1

        self.x = x
        self.y = y
        self.z = z
        self.xy_members = [] # stores the members connected on the x-y plane
        self.z_members = [] # stores the members on the z axis
        self.other_members = []

    def setLocation(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def addMemberOnXYPlane(self, member):
        self.xy_members.append(member)

    def addMemberOnZAxis(self, member):
        self.z_members.append(member)

    def addOtherMember(self, member):
        self.other_members.append(member)
        
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
            self.name = Member.id
            Member.id +=  1

        self.start_node = start_node
        self.end_node = end_node

    def setNodes(self, start, end):
        ''' set the start and end nodes '''
        self.start_node = start
        self.end_node = end

# --------------------------------------------------------------------------
