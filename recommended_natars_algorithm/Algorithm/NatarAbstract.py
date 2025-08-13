from itertools import combinations
import sys
import math

class abstract_natar(object):

    # ---------------- Constructor ---------------------------#

    def __init__(self, natar_id, lat_cord, long_cord, max_capacity, is_recommended, is_open):

        self.natar_id = natar_id
        self.type = None
        self.lat_cord = lat_cord
        self.long_cord = long_cord
        self.max_capacity = max_capacity
        self.possible_groups_for_evacuation = []
        self.all_combinations = []
        self.combinations_obj_function = {}
        self.received_groups_of_casualties = []
        self.current_capacity = 0
        self.is_recommended = is_recommended
        self.is_open = is_open

    def clear_received_groups_of_casualties(self):

        self.received_groups_of_casualties.clear()

    # ---------------- Getters and Setters ---------------------------#

    def get_is_open(self):

        return self.is_open

    def get_lat(self):

        return self.lat_cord

    def get_long(self):

        return self.long_cord

    def get_natar_id(self):

        return self.natar_id

    def get_coordinates(self):

        return self.lat_cord, self.long_cord

    def get_location(self):

        return self.location

    def get_max_capacity(self):

        return self.max_capacity

    def get_combinations(self):

        return self.all_combinations

    def get_is_recommended(self):

        return self.is_recommended

    def get_received_groups_of_casualties(self):

        return self.received_groups_of_casualties

    def is_main_natar(self):

        if self.type == "Main_Natar":

            return True

        else:

            return False

    def create_all_combinations(self):

        list_combinations = []

        list_of_ids = self.generate_casualties_groups_number_ids()

        for n in range(len(list_of_ids)+1):

            list_combinations += list(combinations(list_of_ids, n))

        self.all_combinations = list_combinations

    def generate_casualties_groups_number_ids(self):

        number_ids = []

        for casualty_group in self.possible_groups_for_evacuation:

            casualty_group_id = casualty_group.casualty_group_id

            number_ids.append(casualty_group_id)

        return number_ids

    def update_natar_combinations_obj_function(self, combination, objective_function_results):

        self.combinations_obj_function.update({combination: objective_function_results})

    def update_only_received_casualties(self, number_of_casualties_to_add):

        self.current_capacity = self.current_capacity + number_of_casualties_to_add


    def receive_disaster_site(self, disaster_site_id, disaster_site_number_of_casualties):

        self.received_groups_of_casualties.append([disaster_site_id, disaster_site_number_of_casualties])
        number_of_casualties_to_add = disaster_site_number_of_casualties
        self.current_capacity = self.current_capacity + number_of_casualties_to_add

    def partly_receive_hit_polygon(self, polygon_hit, polygon_hit_number_of_casualties):

        self.received_groups_of_casualties.append([polygon_hit, polygon_hit_number_of_casualties])
        number_of_casualties_able_to_receive = self.max_capacity - self.current_capacity
        number_of_casualties_left = polygon_hit_number_of_casualties - number_of_casualties_able_to_receive
        number_of_casualties_to_add = number_of_casualties_able_to_receive
        self.current_capacity = self.current_capacity + number_of_casualties_to_add
        return number_of_casualties_to_add, number_of_casualties_left


    def change_natar_to_recommended(self):

        self.is_recommended = True

    def remove_group_of_casualties(self, group_of_casualties):

        self.received_groups_of_casualties.remove(group_of_casualties)
        number_of_casualties_to_add = group_of_casualties.get_number_of_casualties()
        self.current_capacity = self.current_capacity - number_of_casualties_to_add

    def get_current_capacity_left(self):

        capacity_left = self.max_capacity - self.current_capacity

        return capacity_left

    def choose_smallest_group_of_casualties(self):

        max_gain = sys.maxsize
        group_to_remove = None

        for group_of_casualties in self.received_groups_of_casualties:

            number_of_casualties = group_of_casualties.get_number_of_casualties()

            current_capacity = self.get_current_capacity_left()

            updated_capacity = current_capacity + number_of_casualties

            if updated_capacity >= 0:

                if number_of_casualties < max_gain:

                    max_gain = number_of_casualties

                    group_to_remove = group_of_casualties

        #todo - add also the number of casualties as a criterion.

        return group_to_remove

    def get_received_groups_of_casualties(self):

        return self.received_groups_of_casualties

    def get_type(self):

        return self.type

    def get_current_capacity(self):

        return self.current_capacity



