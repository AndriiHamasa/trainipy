def params_to_ints(qs):
    return [int(str_id.strip()) for str_id in qs.split(",")]