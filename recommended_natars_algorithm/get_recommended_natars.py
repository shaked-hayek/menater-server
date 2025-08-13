from .Algorithm.Algorithm import run_algorithm


def get_recommended_natars(sites_data, natars_data):
    recommended_natars_list, unallocated_disaster_sites_list = run_algorithm(disaster_site_data=sites_data, natars_data=natars_data)
    return recommended_natars_list
