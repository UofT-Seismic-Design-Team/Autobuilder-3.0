from MainMenu import *
from Model import *

# TESTING only
def main():

    elevations = [0, 6, 9, 12, 15, 18, 21, 27, 33, 39, 45, 51, 57, 60]
    tower = Tower(elevations)

    floorPlan = FloorPlan()

    member1 = Member(Node(0,0), Node(2,0))
    member2 = Member(Node(2,0), Node(6,8))
    member3 = Member(Node(6,8), Node(6,12))
    member4 = Member(Node(6,12), Node(0,12))
    member5 = Member(Node(0,12), Node(0,0))

    floorPlan.addMember(member1)
    floorPlan.addMember(member2)
    floorPlan.addMember(member3)
    floorPlan.addMember(member4)
    floorPlan.addMember(member5)

    floorPlan2 = FloorPlan()

    member21 = Member(Node(0,0), Node(2,0))
    member22 = Member(Node(2,0), Node(2,8))
    member23 = Member(Node(2,8), Node(6,8))
    member24 = Member(Node(6,8), Node(6,12))
    member25 = Member(Node(6,12), Node(0,12))
    member26 = Member(Node(0,12), Node(0,0))

    floorPlan2.addMember(member21)
    floorPlan2.addMember(member22)
    floorPlan2.addMember(member23)
    floorPlan2.addMember(member24)
    floorPlan2.addMember(member25)
    floorPlan2.addMember(member26)

    for elev in elevations[5:]:
        floorPlan.addElevation(elev)
    
    for elev in elevations[5:]:
        tower.floors[elev].addFloorPlan(floorPlan)

    for elev in elevations[:6]:
        floorPlan2.addElevation(elev)

    for elev in elevations[:6]:
        tower.floors[elev].addFloorPlan(floorPlan2)

    tower.generateFacesByFloorPlan(floorPlan)
    tower.generateFacesByFloorPlan(floorPlan2)

    tower.generatePanelsByFace()
    tower.addPanelsToFloors()
    
    tower.generateColumnsByFace()

    app = QApplication(sys.argv)

    main = MainWindow()
    main.setTower(tower)

    main.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()