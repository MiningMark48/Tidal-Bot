class ValueHelper:

    @staticmethod
    def list_tuple_value(tuple_list: list):
        if not len(tuple_list) > 0:
            return None
        return tuple_list[0][2]
