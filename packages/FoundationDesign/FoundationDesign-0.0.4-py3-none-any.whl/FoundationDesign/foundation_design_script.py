from FoundationDesign import padFoundationDesign, PadFoundation


def pad_foundation_analyse(request):
    post_data = json.loads(request.body.decode("utf-8"))

    soil_profile = post_data["soil_profile"]
    soils = json.loads(soil_profile)

    pad_soil_depth = post_data["pad_soil_depth"]
    pad_foundation_depth = post_data["pad_foundation_depth"]
    pad_foundation_width = post_data["pad_foundation_width"]
    pad_foundation_length = post_data["pad_foundation_length"]
    pad_bearing_capacity = post_data[
        "pad_bearing_capacity"
    ]  # bearing capacity of the foundation in kN/m2
    pad_soil_unit_weight = post_data[
        "pad_soil_unit_weight"
    ]  # soil unit weight in kN/m3
    pad_concrete_unit_weight = post_data[
        "pad_concrete_unit_weight"
    ]  # concrete unit weight in kN/m3

    pad_concrete_cover = post_data["pad_concrete_cover"]  # concrete cover in mm

    pad_column_width = post_data["pad_column_width"]
    pad_column_length = post_data["pad_column_length"]
    pad_column_x = post_data["pad_column_x"]
    pad_column_y = post_data["pad_column_y"]

    pad_reinforcement_size = post_data["pad_reinforcement_size"]
    pad_reinforcement_spacing = post_data["pad_reinforcement_spacing"]

    pad_concrete_strength = post_data["pad_concrete_strength"]
    pad_steel_strength = post_data["pad_steel_strength"]

    pad_horizontal_x_permanent = post_data["pad_horizontal_x_permanent"]
    pad_horizontal_y_permanent = post_data["pad_horizontal_y_permanent"]
    pad_axial_permanent = post_data["pad_axial_permanent"]
    pad_bending_x_permanent = post_data["pad_bending_x_permanent"]
    pad_bending_y_permanent = post_data["pad_bending_y_permanent"]

    pad_horizontal_x_variable = post_data["pad_horizontal_x_variable"]
    pad_horizontal_y_variable = post_data["pad_horizontal_y_variable"]
    pad_axial_variable = post_data["pad_axial_variable"]
    pad_bending_x_variable = post_data["pad_bending_x_variable"]
    pad_bending_y_variable = post_data["pad_bending_y_variable"]

    # Retrieving wind axial, horizontal and moments in x and y direction
    pad_horizontal_x_wind = post_data["pad_horizontal_x_wind"]
    pad_horizontal_y_wind = post_data["pad_horizontal_y_wind"]
    pad_axial_wind = post_data["pad_axial_wind"]
    pad_bending_x_wind = post_data["pad_bending_x_wind"]
    pad_bending_y_wind = post_data["pad_bending_y_wind"]

    # SETTINGS
    pad_shear_stress_factor = post_data[
        "pad_shear_stress_factor"
    ]  # dropped down list with this values 1.5, 1.4, 1.15
    pad_uls_strength_factor_imp = post_data["pad_uls_strength_factor_imp"]
    pad_uls_strength_factor_perm = post_data[
        "pad_uls_strength_factor_perm"
    ]  # default is 1.35 but user can also enter 1.25,

    fdn = PadFoundation(
        foundation_length=pad_foundation_length,
        foundation_width=pad_foundation_width,
        column_length=pad_column_length,
        column_width=pad_column_width,
        col_pos_xdir=pad_column_x,
        col_pos_ydir=pad_column_y,
        soil_bearing_capacity=pad_bearing_capacity,
    )
    self_weights = fdn.foundation_loads(
        foundation_thickness=pad_foundation_depth,
        soil_depth_abv_foundation=pad_soil_depth,
        soil_unit_weight=pad_soil_unit_weight,
        concrete_unit_weight=pad_concrete_unit_weight,
    )

    fdn.column_axial_loads(
        permanent_axial_load=pad_axial_permanent,
        imposed_axial_load=pad_axial_variable,
        wind_axial_load=pad_axial_wind,
    )
    fdn.column_horizontal_loads_xdir(
        permanent_horizontal_load_xdir=pad_horizontal_x_permanent,
        imposed_horizontal_load_xdir=pad_horizontal_x_variable,
        wind_horizontal_load_xdir=pad_horizontal_x_wind,
    )
    fdn.column_horizontal_loads_ydir(
        permanent_horizontal_load_ydir=pad_horizontal_y_permanent,
        imposed_horizontal_load_ydir=pad_horizontal_y_variable,
        wind_horizontal_load_ydir=pad_horizontal_y_wind,
    )
    fdn.column_moments_xdir(
        permanent_moment_xdir=pad_bending_x_permanent,
        imposed_moment_xdir=pad_bending_x_variable,
        wind_moments_xdir=pad_bending_x_wind,
    )
    fdn.column_moments_ydir(
        self,
        permanent_moment_ydir=pad_bending_y_permanent,
        imposed_moment_ydir=pad_bending_y_variable,
        wind_moments_ydir=pad_bending_y_wind,
    )

    fdn.uls_strength_factor_permanent = pad_uls_strength_factor_perm
    fdn.uls_strength_factor_imposed = pad_uls_strength_factor_imp
    total_force_x_dir_sls = fdn.total_force_X_dir_sls()
    total_force_y_dir_sls = fdn.total_force_Y_dir_sls()
    total_force_z_dir_sls = fdn.total_force_Z_dir_sls()
    total_force_x_dir_uls = fdn.total_force_X_dir_uls()
    total_force_y_dir_uls = fdn.total_force_Y_dir_uls()
    total_force_z_dir_uls = fdn.total_force_Z_dir_uls()
    total_moments_x_direction_sls = fdn.total_moments_X_direction_sls()
    total_moments_y_direction_sls = fdn.total_moments_Y_direction_sls()
    eccentricity_x_dir_sls = fdn.eccentricity_X_direction_sls()
    eccentricity_x_dir_uls = fdn.eccentricity_X_direction_uls()
    eccentricity_y_dir_sls = fdn.eccentricity_Y_direction_sls()
    eccentricity_y_dir_uls = fdn.eccentricity_Y_direction_uls()
    pressure_result_sls = fdn.pad_base_pressures_sls()
    pressure_result_uls = fdn.pad_base_pressures_uls()
    minimum_area_required = fdn.minimum_area_required()

    fdn_design = padFoundationDesign(
        fdn,
        fck=pad_concrete_strength,
        fyk=pad_steel_strength,
        concrete_cover=pad_concrete_cover,
        bar_diameterX=pad_reinforcement_size,
        bar_diameterY=pad_reinforcement_size,
    )
    fdn_design.update_punching_shear_stress_factor(beta=pad_shear_stress_factor)

    plot_foundation_loading_X = fdn_design.plot_foundation_loading_X()
    plot_foundation_loading_Y = fdn_design.plot_foundation_loading_Y()
    plot_bending_moment_X = fdn_design.plot_bending_moment_X()
    plot_bending_moment_Y = fdn_design.plot_bending_moment_Y()
    plot_shear_force_X = fdn_design.plot_shear_force_X()
    plot_shear_force_Y = fdn_design.plot_shear_force_Y()
    plot_foundation_loading_x = fdn_design.plot_foundation_loading_X()
    plot_foundation_loading_y = fdn_design.plot_foundation_loading_Y()
    design_moment_xdir = fdn_design.get_design_moment_X()
    design_moment_ydir = fdn_design.get_design_moment_Y()
    design_shear_force_x = fdn_design.get_design_shear_force_X()
    design_shear_force_y = fdn_design.get_design_shear_force_Y()

    area_of_steel_reqd_X_dir = fdn_design.area_of_steel_reqd_X_dir()
    area_of_steel_reqd_Y_dir = fdn_design.area_of_steel_reqd_Y_dir()

    reinforcement_provision_flexure_X_dir = (
        fdn_design.reinforcement_provision_flexure_X_dir()
    )
    reinforcement_provision_flexure_Y_dir = (
        fdn_design.reinforcement_provision_flexure_Y_dir()
    )
    tranverse_shear_check_Xdir = fdn_design.tranverse_shear_check_Xdir()
    tranverse_shear_check_Ydir = fdn_design.tranverse_shear_check_Ydir()

    punching_shear_column_face = fdn_design.punching_shear_column_face()
    punching_shear_check_1d = fdn_design.punching_shear_check_1d()
    punching_shear_check_2d = fdn_design.punching_shear_check_2d()

    sliding_resistance_check = fdn_design.sliding_resistance_check()

    return JsonResponse({"test": "working"}, safe=False)
