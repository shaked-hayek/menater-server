
"""
This is the Hit Polygon Class that represents a destruction site.
"""


class hit_polygon(object):

    # ---------------- Constructor ---------------------------#

    def __init__(self, polygon_data):

        self.hit_polygon_id = polygon_data[0]
        self.lat_cord = polygon_data[1]
        self.long_cord = polygon_data[2]
        self.casualties_upon_disaster = polygon_data[3]
        self.number_of_casualties = polygon_data[3]
        self.fully_allocated = False
        self.print_debug = True

    ### ----------------------- Supporting Methods -------------- ###

    def update_the_number_of_casualties(self, number_of_casualties_assigned_to_natar):

        self.number_of_casualties = self.number_of_casualties - number_of_casualties_assigned_to_natar

        if self.number_of_casualties == 0:

            self.fully_allocated = True

            if self.print_debug:

                print(f"Disaster Site {self.hit_polygon_id} was fully allocated.")

    ### ----------------------- Getters ------------------------ ###

    def get_id(self):

        return self.hit_polygon_id

    def get_number_of_casualties(self):

        return self.number_of_casualties

    def get_hit_polygon_id(self):

        return self.hit_polygon_id

    def get_coordinates(self):

        return self.lat_cord, self.long_cord

    def get_casualties_upon_disaster(self):

        return self.casualties_upon_disaster

    def get_lat(self):

        return self.lat_cord

    def get_long(self):

        return self.long_cord

    def get_fully_allocated(self):

        return self.fully_allocated