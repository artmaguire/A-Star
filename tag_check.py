__global_tags__ = [1, 15, 16, 21, 22, 31, 32, 41, 42, 43, 51, 63]

__map_config__ = {
    'car':   __global_tags__ + [11, 12, 13, 14],
    'cycle': __global_tags__ + [62, 71, 72, 81, 91, 92],
    'foot':  __global_tags__ + [3, 62, 71, 72, 91, 92]
}


def get_tag_tuple(tag):
    if type(tag) is not str or tag not in __map_config__:
        return None

    return tuple(__map_config__[tag])
