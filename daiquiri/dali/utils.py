def make_query_dict_upper_case(input_dict):
    output_dict = input_dict.copy()

    for key in output_dict.keys():
        if key.upper() != key:
            values = output_dict.getlist(key)

            if key.upper() in output_dict:
                output_dict.appendlist(key.upper(), values)
            else:
                output_dict.setlist(key.upper(), values)

            output_dict.pop(key)

    return output_dict
