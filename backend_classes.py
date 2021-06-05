class Tower:
    def __init__(self, panel_bracing_schemes, member_sections):
        self.panel_bracing_schemes = panel_bracing_schemes
        self.member_sections = member_sections

class BracingScheme:
    def __init__(self, elements, section_props):
        self.elements = elements
        self.section_props = section_props

class Panel:
    def __init__(self, lower_left, upper_left, upper_right, lower_right, memberIDs_contained=["UNKNOWN"]):
        self.lower_left = lower_left
        self.upper_left = upper_left
        self.upper_right = upper_right
        self.lower_right = lower_right
        self.memberIDs_contained = memberIDs_contained
    def clear_panel(self, SapModel):
        # Deletes all members that are in the panel
        if self.memberIDs_contained == ["UNKNOWN"]:
            # Check if there are any members contained within the panel
            vec1_x = self.point1[0] - self.point2[0]
            vec1_y = self.point1[1] - self.point2[1]
            vec1_z = self.point1[2] - self.point2[2]
            vec2_x = self.point1[0] - self.point3[0]
            vec2_y = self.point1[1] - self.point3[1]
            vec2_z = self.point1[2] - self.point3[2]
            vec1 = [vec1_x, vec1_y, vec1_z]
            vec2 = [vec2_x, vec2_y, vec2_z]
            norm_vec = numpy.cross(numpy.array(vec1), numpy.array(vec2))

            [number_members, all_member_names, ret] = SapModel.FrameObj.GetNameList()
            # Loop through all members in model
            for member_name in all_member_names:
                # Get member coordinates
                [member_pt1_name, member_pt2_name, ret] = SapModel.FrameObj.GetPoints(member_name)
                if ret != 0:
                    print('ERROR checking member ' + member_name)
                [member_pt1_x, member_pt1_y, member_pt1_z, ret] = SapModel.PointObj.GetCoordCartesian(member_pt1_name)
                if ret != 0:
                    print('ERROR getting coordinate of point ' + member_pt1_name)
                [member_pt2_x, member_pt2_y, member_pt2_z, ret] = SapModel.PointObj.GetCoordCartesian(member_pt2_name)
                if ret != 0:
                    print('ERROR getting coordinate of point ' + member_pt2_name)

                # Round the member coordinates
                max_decimal_places = 6
                member_pt1_x = round(member_pt1_x, max_decimal_places)
                member_pt1_y = round(member_pt1_y, max_decimal_places)
                member_pt1_z = round(member_pt1_z, max_decimal_places)
                member_pt2_x = round(member_pt2_x, max_decimal_places)
                member_pt2_y = round(member_pt2_y, max_decimal_places)
                member_pt2_z = round(member_pt2_z, max_decimal_places)

                # Check if the member is within the elevation of the panel
                panel_max_z = max(self.point1[2], self.point2[2], self.point3[2], self.point4[2])
                panel_min_z = min(self.point1[2], self.point2[2], self.point3[2], self.point4[2])
                if member_pt1_z <= panel_max_z and member_pt1_z >= panel_min_z and member_pt2_z <= panel_max_z and member_pt2_z >= panel_min_z:
                    member_vec_x = member_pt2_x - member_pt1_x
                    member_vec_y = member_pt2_y - member_pt1_y
                    member_vec_z = member_pt2_z - member_pt1_z
                    member_vec = [member_vec_x, member_vec_y, member_vec_z]

                    # Check if member is in the same plane as the panel
                    if numpy.dot(member_vec, norm_vec) == 0:
                        # To do this, check if the vector between a member point and a plane point is parallel to plane
                        test_vec = [member_pt1_x - self.point1[0], member_pt1_y - self.point1[1],
                                    member_pt1_z - self.point1[2]]
                        if numpy.dot(test_vec, norm_vec) == 0:
                            # Check if the member lies within the limits of the panel
                            # First, transform the frame of reference since Shapely only works in 2D
                            # Create unit vectors
                            ref_vec_1 = vec1
                            ref_vec_2 = numpy.cross(ref_vec_1, norm_vec)
                            # Project each point defining the panel onto each reference vector
                            panel_pt1_trans_1 = numpy.dot(self.point1, ref_vec_1) / numpy.linalg.norm(ref_vec_1)
                            panel_pt1_trans_2 = numpy.dot(self.point1, ref_vec_2) / numpy.linalg.norm(ref_vec_2)
                            panel_pt2_trans_1 = numpy.dot(self.point2, ref_vec_1) / numpy.linalg.norm(ref_vec_1)
                            panel_pt2_trans_2 = numpy.dot(self.point2, ref_vec_2) / numpy.linalg.norm(ref_vec_2)
                            panel_pt3_trans_1 = numpy.dot(self.point3, ref_vec_1) / numpy.linalg.norm(ref_vec_1)
                            panel_pt3_trans_2 = numpy.dot(self.point3, ref_vec_2) / numpy.linalg.norm(ref_vec_2)
                            panel_pt4_trans_1 = numpy.dot(self.point4, ref_vec_1) / numpy.linalg.norm(ref_vec_1)
                            panel_pt4_trans_2 = numpy.dot(self.point4, ref_vec_2) / numpy.linalg.norm(ref_vec_2)
                            # Project each point defining the member onto the reference vector
                            member_pt1 = [member_pt1_x, member_pt1_y, member_pt1_z]
                            member_pt2 = [member_pt2_x, member_pt2_y, member_pt2_z]
                            member_pt1_trans_1 = numpy.dot(member_pt1, ref_vec_1) / numpy.linalg.norm(ref_vec_1)
                            member_pt1_trans_2 = numpy.dot(member_pt1, ref_vec_2) / numpy.linalg.norm(ref_vec_2)
                            member_pt2_trans_1 = numpy.dot(member_pt2, ref_vec_1) / numpy.linalg.norm(ref_vec_1)
                            member_pt2_trans_2 = numpy.dot(member_pt2, ref_vec_2) / numpy.linalg.norm(ref_vec_2)
                            # Create shapely geometries to check if member is in the panel
                            poly_coords = [(panel_pt1_trans_1, panel_pt1_trans_2),
                                           (panel_pt2_trans_1, panel_pt2_trans_2),
                                           (panel_pt3_trans_1, panel_pt3_trans_2),
                                           (panel_pt4_trans_1, panel_pt4_trans_2)]
                            member_coords = [(member_pt1_trans_1, member_pt1_trans_2),
                                             (member_pt2_trans_1, member_pt2_trans_2)]
                            panel_shapely = shapely.geometry.Polygon(poly_coords)
                            member_shapely = shapely.geometry.LineString(member_coords)
                            # Delete member if it is inside the panel
                            if member_shapely.intersects(panel_shapely) == True and member_shapely.touches(
                                    panel_shapely) == False:
                                ret = SapModel.FrameObj.Delete(member_name, 0)
            self.memberIDs_contained = []

        else:
            # Delete members that are contained in the panel
            for memberID in self.memberIDs_contained:
                ret = SapModel.FrameObj.Delete(memberID, 0)
                if ret != 0:
                    print('ERROR deleting member ' + memberID)
            self.memberIDs_contained = []

    def build_bracing_scheme(self, SapModel, bracing_scheme):
        if self.memberIDs_contained == ["UNKNOWN"]:
            self.clear_panel(SapModel)
        for element_num in bracing_scheme.elements.keys():
            nodes = bracing_scheme.elements[element_num]
            node_1_name = nodes[0]
            node_2_name = nodes[1]
            node_1_coords = bracing_scheme.nodes[node_1_name]
            node_2_coords = bracing_scheme.nodes[node_2_name]
            section_prop = bracing_scheme.section_props[element_num]
            # Scale the member start and end points to fit the panel location and dimensions
            # Get unit vectors to define the panel
            panel_vec_horiz_x = self.point4[0] - self.point1[0]
            panel_vec_horiz_y = self.point4[1] - self.point1[1]
            panel_vec_horiz_z = self.point4[2] - self.point1[2]
            panel_vec_vert_x = self.point2[0] - self.point1[0]
            panel_vec_vert_y = self.point2[1] - self.point1[1]
            panel_vec_vert_z = self.point2[2] - self.point1[2]
            panel_vec_horiz = [panel_vec_horiz_x, panel_vec_horiz_y, panel_vec_horiz_z]
            panel_vec_vert = [panel_vec_vert_x, panel_vec_vert_y, panel_vec_vert_z]
            # Get the scaled start and end coordinates for the member
            # Translate point "horizontally" and "vertically"
            start_node_x = self.point1[0] + node_1_coords[0] * panel_vec_horiz[0] + node_1_coords[1] * panel_vec_vert[0]
            start_node_y = self.point1[1] + node_1_coords[0] * panel_vec_horiz[1] + node_1_coords[1] * panel_vec_vert[1]
            start_node_z = self.point1[2] + node_1_coords[0] * panel_vec_horiz[2] + node_1_coords[1] * panel_vec_vert[2]
            end_node_x = self.point1[0] + node_2_coords[0] * panel_vec_horiz[0] + node_2_coords[1] * panel_vec_vert[0]
            end_node_y = self.point1[1] + node_2_coords[0] * panel_vec_horiz[1] + node_2_coords[1] * panel_vec_vert[1]
            end_node_z = self.point1[2] + node_2_coords[0] * panel_vec_horiz[2] + node_2_coords[1] * panel_vec_vert[2]
            # Create the member
            [member_name, ret] = SapModel.FrameObj.AddByCoord(start_node_x, start_node_y, start_node_z, end_node_x,
                                                              end_node_y, end_node_z, PropName=section_prop)
            if ret != 0:
                print('ERROR building member in panel')
            self.memberIDs_contained.append(member_name)

class Results:
    period = None
    th_load_cases = None
    th_acc = None
    th_disp = None
    
    th_base_shear = None
    cr_elevs = None
    cr_x = None
    cr_y = None

    def get_th_results(self, SapModel, th_load_combos = [], cr = False, period = False, ):
        # period
    def get_cr_results(self, SapModel, cr_elevs):

    def get_fabi(self, ):
