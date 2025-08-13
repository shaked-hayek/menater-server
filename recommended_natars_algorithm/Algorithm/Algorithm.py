from pulp import LpMinimize, LpProblem, LpVariable, lpSum, LpStatus, PULP_CBC_CMD
from .HitPolygon import hit_polygon
from .MainNatar import main_natar
from .SubNatar import sub_natar
from .GeneralMethods import *


###-------------------------------------------- Data Preparation ----------------------------------------------------###

def create_disaster_sites_and_natars_objects_lists(disaster_site_data, natars_data):

    disaster_site_object_list = create_disaster_sites_object_list(disaster_site_data=disaster_site_data)

    natars_object_list, main_natar_object_list, sub_natar_object_list = create_natars_object_list(natars_data=natars_data)

    return disaster_site_object_list, natars_object_list, main_natar_object_list, sub_natar_object_list

def create_disaster_sites_object_list(disaster_site_data):

    disaster_sites_object_list = []

    for data_row in disaster_site_data:

        new_disaster_site = hit_polygon(polygon_data=data_row)

        disaster_sites_object_list.append(new_disaster_site)

    return disaster_sites_object_list

def create_natars_object_list(natars_data):

    natars_object_list = []
    main_natar_object_list = []
    sub_natar_object_list = []

    for data_row in natars_data:

        if data_row[4] == 1:

            new_natar = main_natar(natar_id=data_row[0], lat_cord=data_row[1], long_cord=data_row[2], max_capacity=data_row[3], is_recommended=data_row[6], is_open=data_row[7])
            main_natar_object_list.append(new_natar)

        else:

            new_natar = sub_natar(natar_id=data_row[0], lat_cord=data_row[1], long_cord=data_row[2], max_capacity=data_row[3], main_natar=data_row[5], is_recommended=data_row[6], is_open=data_row[7])
            sub_natar_object_list.append(new_natar)

        natars_object_list.append(new_natar)

    return natars_object_list, main_natar_object_list, sub_natar_object_list

###-------------------------------------------- MILP Methods --------------------------------------------------------###


def generate_K_disaster_sites_id_list(sorted_disaster_sites):

    K_list = []

    for disaster_site in sorted_disaster_sites:

        disaster_site_id = disaster_site.get_id()

        K_list.append(disaster_site_id)

    return K_list

def generate_J_main_natars_id_list(main_natar_object_list):

    J_list = []

    for main_natar in main_natar_object_list:

        main_natar_id = main_natar.get_natar_id()

        J_list.append(main_natar_id)

    return J_list

def generate_Ck_casualties_for_each_disaster_site_dict(sorted_disaster_sites):

    Ck_dict = {}

    for disaster_site in sorted_disaster_sites:

        disaster_site_id = disaster_site.get_id()

        number_of_casualties_upon_disaster = disaster_site.get_casualties_upon_disaster()

        Ck_dict.update({disaster_site_id: number_of_casualties_upon_disaster})

    return Ck_dict

def generate_distances_k_j_dict(sorted_disaster_sites, main_natar_object_list):

    distance_k_j_dict = {}

    for disaster_site in sorted_disaster_sites:

        disaster_site_id = disaster_site.get_id()

        ds_lat_cord, ds_long_cord = disaster_site.get_coordinates()

        for main_natar in main_natar_object_list:

            main_natar_id = main_natar.get_natar_id()

            mn_lat_cord, mn_long_cord = main_natar.get_coordinates()

            distance = haversine(lon1=ds_long_cord, lat1=ds_lat_cord, lon2=mn_long_cord, lat2=mn_lat_cord)

            key = (disaster_site_id, main_natar_id)

            distance_k_j_dict.update({key: round(distance, 2)})

    return distance_k_j_dict

def generate_max_capacity_for_main_natarsdict(main_natar_object_list):

    MS_dict = {}

    for main_natar in main_natar_object_list:

        main_natar_id = main_natar.get_natar_id()

        max_capacity_of_natar = main_natar.get_max_capacity()

        MS_dict.update({main_natar_id: max_capacity_of_natar})

    return MS_dict

def generate_max_capacity_for_sub_natars_dict(sub_natar_object_list):

    MN_dict = {}

    for sub_natar in sub_natar_object_list:

        sub_natar_id = sub_natar.get_natar_id()

        max_capacity_of_natar = sub_natar.get_max_capacity()

        MN_dict.update({sub_natar_id: max_capacity_of_natar})

    return MN_dict

def generate_TC(Ck_dict):

    TC = sum(Ck_dict.values())

    return TC


###-------------------------------------------- Print Methods -------------------------------------------------------###

def print_problem(polygons_object_list):

    for disaster_site in polygons_object_list:

        disaster_site_id = disaster_site.get_id()

        disaster_site_casualties = disaster_site.get_casualties_upon_disaster()

        print(f"Disaster Site {disaster_site_id} with {disaster_site_casualties} casualties")

def print_all_allocations(natars_object_list):

    for natar in natars_object_list:

        is_recommended = natar.get_is_recommended()

        if is_recommended:

            natar_id = natar.get_natar_id()
            number_of_casualties = natar.get_current_capacity()
            received_groups_of_casualties = natar.get_received_groups_of_casualties()
            natar_type = natar.get_type()
            if natar_type == "Main_Natar":
                print(
                    f"Natar {natar_id} from type {natar_type} will be open and will receive {number_of_casualties} casualties with groups {received_groups_of_casualties}.")
            else:

                main_natar_id = natar.get_main_natar_id()
                print(
                    f"Natar {natar_id} from type {natar_type} with main natar id {main_natar_id} will be open and will receive {number_of_casualties} casualties with groups {received_groups_of_casualties}.")

###-------------------------------------------- Second Phase Methods ------------------------------------------------###

def is_second_phase_run(natars_data):

    for data_row in natars_data:

        if data_row[6] is True or data_row[7] is True:

            return True

    return False


def create_disaster_site_natars_distance_dict(disaster_site, natars_object_list):

    distance_dict = {}

    for natar in natars_object_list:

        natar_id = natar.get_natar_id()

        disaster_site_lat = disaster_site.get_lat()
        disaster_site_long = disaster_site.get_long()
        natar_lat = natar.get_lat()
        natar_long = natar.get_long()

        distance_km = haversine(lon1=disaster_site_long, lat1=disaster_site_lat, lon2=natar_long, lat2=natar_lat)

        distance_dict.update({natar_id: distance_km})

    return distance_dict

def check_if_natar_is_recommended(natar_id, Y_dict, natars_object_list):

        is_recommended = False

        is_recommended_in_Y = check_if_natar_is_recommended_in_Y(natar_id=natar_id, Y_dict=Y_dict)  # Check if recommended at y - if Yes Return True

        if is_recommended_in_Y:

            is_recommended = True

            return is_recommended

        elif check_if_natar_is_recommended_in_object(natar_id=natar_id, natars_object_list=natars_object_list):  # Check if recommended as object - Return True

            is_recommended = True

            return is_recommended

        else:

            return is_recommended

def check_if_natar_is_recommended_in_Y(natar_id, Y_dict):

    is_recommended = False

    for y_natar_id in Y_dict:

        if natar_id == y_natar_id:

            is_recommended = Y_dict.get(y_natar_id)

            if is_recommended == 0:

                return is_recommended

            else:

                is_recommended = True

                return is_recommended

    return is_recommended


def check_if_natar_is_recommended_in_object(natar_id, natars_object_list):

    is_recommended = False

    natar_object = find_natar_as_object(natar_id=natar_id, natars_object_list=natars_object_list)

    is_recommended_in_object = natar_object.get_is_recommended()

    if is_recommended_in_object:

        is_recommended = True

        return is_recommended

    else:

        return is_recommended


def find_natar_as_object(natar_id, natars_object_list):

    for natar in natars_object_list:

        natar_object_id = natar.get_natar_id()

        if natar_object_id == natar_id:

            return natar

    print(f"Bug - Did not found {natar_id} in the natars_object_list.")


def check_for_required_coverage(disaster_site, natar, natar_coverage):

    is_there_coverage = False

    disaster_site_casualties = disaster_site.get_casualties_upon_disaster()

    natar_capacity_left = natar.get_current_capacity_left()

    natar_capability_coverage = natar_capacity_left * natar_coverage

    if natar_capability_coverage >= disaster_site_casualties:

        is_there_coverage = True

        return is_there_coverage

    else:

        return is_there_coverage


def operate_case_one_and_two(disaster_site, natar_object, natar_coverage):

    found_allocation = False

    is_there_coverage = check_for_required_coverage(disaster_site=disaster_site, natar=natar_object,  natar_coverage=natar_coverage)

    if is_there_coverage:

        disaster_site_id = disaster_site.get_id()

        disaster_site_number_of_casualties = disaster_site.get_casualties_upon_disaster()

        natar_object.change_natar_to_recommended()  # Update the natar object that is recommended.

        natar_object.receive_disaster_site(disaster_site_id=disaster_site_id, disaster_site_number_of_casualties=disaster_site_number_of_casualties)  # Update the number of casualties in the main natar.

        disaster_site.update_the_number_of_casualties( number_of_casualties_assigned_to_natar=disaster_site_number_of_casualties)  # Update the number of casualties and the disaster site.

        found_allocation = True

        return found_allocation

    else:

        return found_allocation


def operate_case_three(disaster_site, natar_object, natar_coverage, natars_object_list):

    found_allocation = False

    is_there_coverage = check_for_required_coverage(disaster_site=disaster_site, natar=natar_object, natar_coverage=natar_coverage)

    if is_there_coverage:

        disaster_site_id = disaster_site.get_id()

        disaster_site_number_of_casualties = disaster_site.get_casualties_upon_disaster()

        natar_object.change_natar_to_recommended()  # Update the sub natar object that is recommended.

        natar_object.receive_disaster_site(disaster_site_id=disaster_site_id, disaster_site_number_of_casualties=disaster_site_number_of_casualties)  # Update the number of casualties in the main natar.

        disaster_site.update_the_number_of_casualties(number_of_casualties_assigned_to_natar=disaster_site_number_of_casualties)  # Update the number of casualties and the disaster site.

        main_natar_id = natar_object.get_main_natar_id()

        main_natar_object = find_natar_as_object(natar_id=main_natar_id, natars_object_list=natars_object_list)

        main_natar_object.change_natar_to_recommended()

        main_natar_object.update_only_received_casualties(number_of_casualties_to_add=disaster_site_number_of_casualties)  # Update the number of casualties at the main natar.

        found_allocation = True

        return found_allocation

    else:

        return found_allocation


def operate_case_four(disaster_site, natar_object, natar_coverage, natars_object_list):

    found_allocation = False

    is_there_coverage = check_for_required_coverage(disaster_site=disaster_site, natar=natar_object, natar_coverage=natar_coverage)

    if is_there_coverage:

        disaster_site_id = disaster_site.get_id()

        disaster_site_number_of_casualties = disaster_site.get_casualties_upon_disaster()

        natar_object.change_natar_to_recommended()  # Update the sub natar object that is recommended.

        natar_object.receive_disaster_site(disaster_site_id=disaster_site_id, disaster_site_number_of_casualties=disaster_site_number_of_casualties)  # Update the number of casualties in the main natar.

        disaster_site.update_the_number_of_casualties(number_of_casualties_assigned_to_natar=disaster_site_number_of_casualties)  # Update the number of casualties and the disaster site.

        main_natar_id = natar_object.get_main_natar_id()

        main_natar_object = find_natar_as_object(natar_id=main_natar_id, natars_object_list=natars_object_list)

        main_natar_object.change_natar_to_recommended()

        main_natar_object.update_only_received_casualties(number_of_casualties_to_add=disaster_site_number_of_casualties)  # Update the number of casualties at the main natar.

        found_allocation = True

        return found_allocation

    else:

        return found_allocation


def create_recommended_natars_list(natars_object_list):

    returned_list = []

    for natar in natars_object_list:

        is_recommended = natar.get_is_recommended()

        if is_recommended:

            natar_id = natar.get_natar_id()

            returned_list.append(natar_id)

    return returned_list

def create_recommended_natars_dict(natars_object_list):

    natars_dict = {}

    for natar in natars_object_list:

        is_recommended = natar.get_is_recommended()

        if is_recommended:

            natar_id = natar.get_natar_id()

            received_groups_of_casualties = natar.get_received_groups_of_casualties()

            natars_dict.update({natar_id: received_groups_of_casualties})

    return natars_dict

def create_unallocated_disaster_sites_list(polygons_object_list):

    returned_list = []

    for disaster_site in polygons_object_list:

        is_fully_allocated = disaster_site.get_fully_allocated()

        if is_fully_allocated == False:

            disaster_site_id = disaster_site.get_id()

            returned_list.append(disaster_site_id)

    return returned_list

def algorithm_solutions(natars_object_list, polygons_object_list):

    recommended_natars_dict = create_recommended_natars_dict(natars_object_list=natars_object_list)

    unallocated_disaster_sites_list = create_unallocated_disaster_sites_list(polygons_object_list=polygons_object_list)

    return recommended_natars_dict, unallocated_disaster_sites_list

###-------------------------------------------- Input Section -------------------------------------------------------###

print_debug = False

PS = 5  # The maximum number of natars.

f = 100  # Penalty per untreated casualties.

M = 100000  # NEW: Big-M constant.

epsilon = 1  # NEW: Small epsilon for strict inequality.

natar_coverage = 0.8  # Coverage required for allocation.

###-------------------------------------------- Full Algorithm ------------------------------------------------------###

def run_full_milp_and_second_phase(disaster_site_data, natars_data):

###-------------------------------------------- Object Creation -----------------------------------------------------###

    polygons_object_list, natars_object_list, main_natar_object_list, sub_natar_object_list = create_disaster_sites_and_natars_objects_lists(disaster_site_data=disaster_site_data, natars_data=natars_data) # Second Phase - This phase including the generation of polygons and natars as objects.

###-------------------------------------------- Variable Creation ---------------------------------------------------###

    K_list = generate_K_disaster_sites_id_list(sorted_disaster_sites=polygons_object_list)  # Disaster Site ID List.

    J_list = generate_J_main_natars_id_list(main_natar_object_list=main_natar_object_list)  # Main Natar ID List.

    C = generate_Ck_casualties_for_each_disaster_site_dict(sorted_disaster_sites=polygons_object_list)  # Dict With Main Natar ID as Key and the Number of Casualties as Values

    ds = generate_distances_k_j_dict(sorted_disaster_sites=polygons_object_list, main_natar_object_list=main_natar_object_list)  # Dict with key (Main Natar ID, Disaster Site ID) and the Value is Distance as KM.

    MS = generate_max_capacity_for_main_natarsdict(main_natar_object_list=main_natar_object_list)  # Dict With Main Natar ID as Key and Max Casualties as Values

    MN = generate_max_capacity_for_sub_natars_dict(sub_natar_object_list=sub_natar_object_list)  # Dict With Sub Natar ID as Key and Max Casualties as Values

    TC = generate_TC(Ck_dict=C)  # The Total Number of Casualties in C

###-------------------------------------------- Decision Variables --------------------------------------------------###

    Y = {j: LpVariable(name=f"Y_{j}", cat='Binary') for j in J_list}  # Will receive 1 if open and 0 if closed.

    S_k_j = {(k, j): LpVariable(f"S_{k}_{j}", cat='Binary') for k in K_list for j in J_list}  # Will receive 1 if disaster site K is assigned to natar J.

    UR = {j: LpVariable(name=f"UR_{j}", lowBound=0, cat='Integer') for j in J_list}  # Under Capacity for Natar j.

    OR = {j: LpVariable(name=f"OR_{j}", lowBound=0, cat='Integer') for j in J_list}  # Over Capacity for Natar j.

    O_Total = LpVariable(name="O_Total", lowBound=0)  # The total Over Capacity.

    U_Total = LpVariable(name="U_Total", lowBound=0)  # The total Under Capacity.

    B = {j: LpVariable(name=f"B_{j}", cat='Binary') for j in J_list}  # XOR control variable

    z1 = {j: LpVariable(name=f"z1_{j}", cat='Binary') for j in J_list}  # >>> NEW

    z2 = {j: LpVariable(name=f"z2_{j}", cat='Binary') for j in J_list}  # >>> NEW

###-------------------------------------------- Objective Function --------------------------------------------------###

    model = LpProblem("Natar_MILP", LpMinimize)

    model += (lpSum(S_k_j[(k, j)] * ds[k][j] * C[k] for k in K_list if k in ds and k in C for j in J_list if j in ds[k]) + f * U_Total) # "Minimize_Total_Cost"

###-------------------------------------------- Constraints Section -------------------------------------------------###

    model += lpSum(Y[j] for j in J_list) <= PS  # Constraint 1 - Number of Main Natar cannot exceed PS.

    for k in K_list:  # Constraint 2 - The Connection Between Disaster Site and Natar will Be 0 or 1.

        for j in J_list:

            model += S_k_j[(k,j)] <= Y[j]

    for k in K_list:  # Constraint 3 - The Sum of Connections Between Disaster Site and Natar will be 1.

        model += lpSum(S_k_j[(k,j)] for j in J_list) == 1

    model += lpSum(C[k] for k in K_list) == TC  # Constraint 4 -The Sum of Casualties in C will be Equal to TC.

    for j in J_list:

        model += lpSum(S_k_j[(k,j)] * C[k] for k in K_list) - MS[j] * Y[j] <= UR[j]  # Constraint 5a - ???

        model += (MS[j] * Y[j] - lpSum(S_k_j[(k, j)] * C[k] for k in K_list)) <= OR[j]  # Constraint 5b -???

        model += U_Total <= MS[j] * B[j]  # Constraint 5c - ???

        model += O_Total <= TC * (1-B[j])  # Constraint 5d - ???

        # >>> NEW: Additional XOR constraints
        model += MS[j] - UR[j] >= -M * (1 - z1[j])         # Constraint 5e >>> NEW

        model += OR[j] - MS[j] >= epsilon - M * (1 - z2[j])  # Constraint 5f >>> NEW

        model += z1[j] + z2[j] == 1                         # Constraint 5g >>> NEW

    model += U_Total == lpSum(UR[j] for j in J_list)  # Constraint 6.

    model += O_Total == lpSum(OR[j] for j in J_list)  # Constraint 7.

    model += lpSum(S_k_j[(k, j)] * C[k] for k in K_list for j in J_list) + U_Total - O_Total == TC  # Constraint 8.

    model.solve(PULP_CBC_CMD(msg=1, mip=True))

    if print_debug:

        print("Status:", LpStatus[model.status])

        for var in model.variables():

            print(f"{var.name} = {var.varValue}")

        print("Objective:", model.objective.value())

    Y_dict = {j: Y[j].varValue for j in J_list}

    S_k_j_dict = {(k, j): S_k_j[(k, j)].varValue for k in K_list for j in J_list}

    UR_dict = {j: UR[j].varValue for j in J_list}

    OR_dict = {j: OR[j].varValue for j in J_list}

    B_dict = {j: B[j].varValue for j in J_list}

    U_Total_val = U_Total.varValue

    O_Total_val = O_Total.varValue

###-------------------------------------------- Second Phase Algorithm-----------------------------------------------###

    if print_debug:

        print_problem(polygons_object_list)

    for disaster_site in polygons_object_list:

        distance_dict = create_disaster_site_natars_distance_dict(disaster_site=disaster_site, natars_object_list=natars_object_list)  # Create the distance dict.

        distance_dict = dict(sorted(distance_dict.items(), key=lambda item: item[1]))  # Sort the distance dict by disatnce ascending.

        for natar_id in distance_dict:

            is_recommended = check_if_natar_is_recommended(natar_id=natar_id, Y_dict=Y_dict, natars_object_list=natars_object_list)

            natar_object = find_natar_as_object(natar_id=natar_id, natars_object_list=natars_object_list)

            is_natar_main_natar = natar_object.is_main_natar()

            if is_natar_main_natar is False:

                main_natar_id = natar_object.get_main_natar_id()

                is_main_natar_recommended = check_if_natar_is_recommended(natar_id=main_natar_id, Y_dict=Y_dict, natars_object_list=natars_object_list)

            # Case 1 - The natar is main natar and recommended

            if is_natar_main_natar is True and is_recommended is True:

                found_allocation = operate_case_one_and_two(disaster_site=disaster_site, natar_object=natar_object, natar_coverage=natar_coverage)

                if found_allocation:

                    break

            # Case 2 - The natar is main natar and not recommended

            elif is_natar_main_natar is True and is_recommended is False:

                found_allocation = operate_case_one_and_two(disaster_site=disaster_site, natar_object=natar_object, natar_coverage=natar_coverage)

                if found_allocation:

                    break

            # Case 3 - The natar is not main natar and main natar is recommended

            elif is_natar_main_natar is False and is_main_natar_recommended is True:

                found_allocation = operate_case_three(disaster_site=disaster_site, natar_object=natar_object, natar_coverage=natar_coverage, natars_object_list=natars_object_list)

                if found_allocation:

                    break

            # Case 4 - The natar is not main natar and main natar is not recommended

            elif is_natar_main_natar is False and is_main_natar_recommended is False:

                found_allocation = operate_case_four(disaster_site=disaster_site, natar_object=natar_object, natar_coverage=natar_coverage, natars_object_list=natars_object_list)

                if found_allocation:

                    break

        fully_allocated = disaster_site.get_fully_allocated()

        if print_debug:

            if fully_allocated == False:

                print(f"Did not found allocation for disaster site {disaster_site.get_id()}")

    if print_debug:

        print_all_allocations(natars_object_list=natars_object_list)

    recommended_natars_dict, unallocated_disaster_sites_list = algorithm_solutions(natars_object_list=natars_object_list, polygons_object_list=polygons_object_list)

    return recommended_natars_dict, unallocated_disaster_sites_list

###-------------------------------------------- Only Second Phase Algorithm -----------------------------------------###

def run_only_second_phase(disaster_site_data, natars_data):

    print("This is the dynamic Run")

    ###-------------------------------------------- Object Creation -----------------------------------------------------###

    polygons_object_list, natars_object_list, main_natar_object_list, sub_natar_object_list = create_disaster_sites_and_natars_objects_lists(disaster_site_data=disaster_site_data, natars_data=natars_data)  # Second Phase - This phase including the generation of polygons and natars as objects.

    for disaster_site in polygons_object_list:

        distance_dict = create_disaster_site_natars_distance_dict(disaster_site=disaster_site, natars_object_list=natars_object_list)  # Create the distance dict.

        distance_dict = dict(sorted(distance_dict.items(), key=lambda item: item[1]))  # Sort the distance dict by disatnce ascending.

        for natar_id in distance_dict:

            natar_object = find_natar_as_object(natar_id=natar_id, natars_object_list=natars_object_list)

            is_open = natar_object.get_is_open()

            is_natar_main_natar = natar_object.is_main_natar()

            if is_natar_main_natar is False:

                main_natar_id = natar_object.get_main_natar_id()

                main_natar_object = find_natar_as_object(natar_id=main_natar_id, natars_object_list=natars_object_list)

                is_main_natar_open = main_natar_object.get_is_open()

        # Case 1 - The natar is main natar and open

            if is_natar_main_natar is True and is_open is True:     # Case 1 - Main natar which in opened.

                found_allocation = operate_case_one_and_two(disaster_site=disaster_site, natar_object=natar_object, natar_coverage=natar_coverage)

                if found_allocation:

                    break

            # Case 2 - The natar is main natar and not open

            elif is_natar_main_natar is True and is_open is False:

                found_allocation = operate_case_one_and_two(disaster_site=disaster_site, natar_object=natar_object, natar_coverage=natar_coverage)

                if found_allocation:

                    break

            # Case 3 - The natar is not main natar and main natar is open

            elif is_natar_main_natar is False and is_main_natar_open is True:

                found_allocation = operate_case_three(disaster_site=disaster_site, natar_object=natar_object, natar_coverage=natar_coverage, natars_object_list=natars_object_list)

                if found_allocation:

                    break

            # Case 4 - The natar is not main natar and main natar is not open

            elif is_natar_main_natar is False and is_main_natar_open is False:

                found_allocation = operate_case_four(disaster_site=disaster_site, natar_object=natar_object, natar_coverage=natar_coverage, natars_object_list=natars_object_list)

                if found_allocation:

                    break

        fully_allocated = disaster_site.get_fully_allocated()

        if print_debug:

            if fully_allocated == False:

                print(f"Did not found allocation for disaster site {disaster_site.get_id()}")

    if print_debug:

        print_all_allocations(natars_object_list=natars_object_list)

    recommended_natars_dict, unallocated_disaster_sites_list = algorithm_solutions(natars_object_list=natars_object_list, polygons_object_list=polygons_object_list)

    return recommended_natars_dict, unallocated_disaster_sites_list

###-------------------------------------------- Main Method----------------------------------------------------------###

def run_algorithm(disaster_site_data, natars_data):

    second_phase_run = is_second_phase_run(natars_data=natars_data)

    if second_phase_run:

        recommended_natars_dict, unallocated_disaster_sites_list = run_only_second_phase(disaster_site_data=disaster_site_data, natars_data=natars_data)

    else:

        recommended_natars_dict, unallocated_disaster_sites_list = run_full_milp_and_second_phase(disaster_site_data=disaster_site_data, natars_data=natars_data)

    return recommended_natars_dict, unallocated_disaster_sites_list

