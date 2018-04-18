from leasing.enums import IndexType


def int_floor(value, precision):
    return value // precision * precision


def calculate_index_adjusted_value_type_1_2_3_4(value, index_value, precision, base):
    return int_floor(value, precision) / base * index_value


def calculate_index_adjusted_value_type_5_7(value, index_value, base):
    return value / base * index_value


def calculate_index_adjusted_value_type_6_v2(value, index_value):
    return int_floor(value, 10) * index_value


def calculate_index_adjusted_value(value, index_value, index_type=IndexType.TYPE_7, precision=None, **extra):
    if index_value.__class__ and index_value.__class__.__name__ == 'Index':
        index_value = index_value.number

    if index_type == IndexType.TYPE_1:
        assert precision
        return calculate_index_adjusted_value_type_1_2_3_4(value, index_value, precision, 50620)

    elif index_type == IndexType.TYPE_2:
        assert precision
        return calculate_index_adjusted_value_type_1_2_3_4(value, index_value, precision, 4661)

    elif index_type == IndexType.TYPE_3:
        return calculate_index_adjusted_value_type_1_2_3_4(value, index_value, 10, 418)

    elif index_type == IndexType.TYPE_4:
        return calculate_index_adjusted_value_type_1_2_3_4(value, index_value, 20, 418)

    elif index_type == IndexType.TYPE_5:
        return calculate_index_adjusted_value_type_5_7(value, index_value, 392)

    elif index_type == IndexType.TYPE_6 and extra:
        raise NotImplementedError('Cannot calculate index adjusted value for index type 6 version 1')

    elif index_type == IndexType.TYPE_6 and not extra:
        return calculate_index_adjusted_value_type_6_v2(value, index_value)

    elif index_type == IndexType.TYPE_7:
        return calculate_index_adjusted_value_type_5_7(value, index_value, 100)

    else:
        raise NotImplementedError('Cannot calculate index adjusted value for index type {}'.format(index_type))
