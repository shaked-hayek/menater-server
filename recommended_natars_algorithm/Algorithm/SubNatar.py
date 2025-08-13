from .NatarAbstract import abstract_natar

"""
This is the Sub Natar Class. 
"""


class sub_natar(abstract_natar):

    # ---------------- Constructor ---------------------------#

    def __init__(self, natar_id, lat_cord, long_cord, max_capacity, main_natar, is_recommended, is_open):

        abstract_natar.__init__(self, natar_id=natar_id, lat_cord=lat_cord, long_cord=long_cord, max_capacity=max_capacity, is_recommended=is_recommended, is_open=is_open)
        self.main_natar = main_natar
        self.type = "Sub_Natar"
        self.attached_to_main_natar = False

    # ---------------- Attach to Main Natar Methods ------------------#

    def change_attached_to_main_natar_to_true(self):

        self.attached_to_main_natar = True

    # ---------------- Getters and Setters ---------------------------#

    def set_main_natar(self, main_natar):

        self.main_natar = main_natar

    def get_main_natar_id(self):

        return self.main_natar

    def get_attached_to_main_natar(self):

        return self.attached_to_main_natar



