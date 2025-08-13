from .NatarAbstract import abstract_natar

"""
This is the Main Natar Class. 
"""

class main_natar(abstract_natar):

    # ---------------- Constructor ---------------------------#

    def __init__(self, natar_id, lat_cord, long_cord, max_capacity, is_recommended, is_open):

        abstract_natar.__init__(self, natar_id=natar_id, lat_cord=lat_cord, long_cord=long_cord, max_capacity=max_capacity, is_recommended=is_recommended, is_open=is_open)
        self.sub_natars = []
        self.type = "Main_Natar"
        self.received_sub_natars = []

    # ---------------- Assign New Sub Natars Methods -------------------------#

    def assign_new_sub_natar_to_sub_natars_list(self, sub_natar_obj):

        self.sub_natars.append(sub_natar_obj)

    def receive_new_sub_natar_to_received_sub_natars(self, sub_natar):

        if sub_natar.get_attached_to_main_natar() is False:

            self.received_sub_natars.append(sub_natar)
            self.receive_sub_natar(sub_natar=sub_natar)
            sub_natar.change_attached_to_main_natar_to_true()
    def receive_sub_natar(self, sub_natar):

        number_of_casualties_to_add = sub_natar.get_current_capacity()
        self.current_capacity = self.current_capacity + number_of_casualties_to_add

    # ---------------- Check for Overall Capacity ---------------------------#

    def check_if_capacity_left(self):

        overall_capacity = 0

        for natar in self.sub_natars:

            natar_capacity = natar.get_max_capacity()

            overall_capacity = overall_capacity + natar_capacity

        if overall_capacity < self.max_capacity:

            return True

        else:

            return False

    def how_much_capacity_left(self):

        overall_capacity = 0

        for natar in self.sub_natars:

            natar_capacity = natar.get_max_capacity()

            overall_capacity = overall_capacity + natar_capacity

        capacity_left = self.max_capacity - overall_capacity

        return capacity_left

    # ---------------- Getters and Setters ---------------------------#

    def set_sub_natars(self, sub_natars):

        self.sub_natars = sub_natars

    def get_sub_natars(self):

        return self.sub_natars

