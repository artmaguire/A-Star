__global_tags__ = [100, 106, 107, 108, 109, 110, 111, 112, 113, 115, 116, 123, 124, 125, 301, 302, 303, 304, 305, 401]

__map_config__ = {
    'car': __global_tags__ + [101, 102, 103, 104, 105],
    'cycle': __global_tags__ + [114, 117, 118, 119, 120, 121, 122, 201, 202, 203, 204],
    'foot': __global_tags__ + [114, 117, 118, 119, 120, 121, 122, 301, 302, 303, 304, 305]
}

def get_tag_tuple(tag):
    if type(tag) is not str or tag not in __map_config__:
        return None

    return tuple(__map_config__[tag])
