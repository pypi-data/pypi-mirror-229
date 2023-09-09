import math

x = 0
y = 0


def _init():
    x = 0
    y = 0


def angle():
    return math.atan2(y, x)


def from_angle(p_angle):
    import gdsbin.vector2 as vector2

    vector2.x = math.sin(p_angle)
    vector2.y = math.cos(p_angle)
    return vector2


def vec_length():
    return math.sqrt(x * x + y * y)


def length_squared():
    return x * x + y * y


def normalized():
    import gdsbin.vector2 as vector2

    l = x * x + y * y
    if l != 0:
        l = math.sqrt(l)
        vector2.x = x / l
        vector2.y = y / l
        return vector2
    vector2.x = x
    vector2.y = y
    return vector2


def is_normalized():
    return math_is_equal_approx(length_squared(), 1)


def distance_to(p_vector2):
    return math.sqrt(
        (x - p_vector2.x) * (x - p_vector2.x) + (y - p_vector2.y) * (y - p_vector2.y)
    )


def distance_squared_to(p_vector2):
    return (x - p_vector2.x) * (x - p_vector2.x) + (y - p_vector2.y) * (y - p_vector2.y)


def angle_to(vector2, p_vector2):
    return math.atan2(cross(vector2, p_vector2), dot(vector2, p_vector2))


def angle_to_point(vector2, p_vector2):
    return (sub(vector2, p_vector2)).angle()


def dot(vector2, p_other):
    return vector2.x * p_other.x + vector2.y * p_other.y


def cross(vector2, p_other):
    return vector2.x * p_other.y - vector2.y * p_other.x


def sign():
    sign = self
    sign.x = sign(x)
    sign.y = sign(y)
    return sign


def floor():
    floor = self
    floor.x = floor(x)
    floor.y = floor(y)
    return floor


def ceil():
    ceil = self
    ceil.x = ceil(x)
    ceil.y = ceil(y)
    return ceil


def round():
    round = self
    round.x = round(x)
    round.y = round(y)
    return round


def rotated(vec2, p_by):
    sine = math.sin(p_by)
    cosi = math.cos(p_by)
    import gdsbin.vector2 as vector2

    vector2.x = vec2.x * cosi - vec2.y * sine
    vector2.y = vec2.x * sine + vec2.y * cosi
    return vector2


def posmod(vec2, p_mod):
    import gdsbin.vector2 as vector2

    vector2.x = fposmod(vec2.x, p_mod)
    vector2.y = fposmod(vec2.y, p_mod)
    return vector2


def posmodv(vec2, p_modv):
    import gdsbin.vector2 as vector2

    vector2.x = fposmod(vec2.x, p_modv.x)
    vector2.y = fposmod(vec2.y, p_modv.y)
    return vector2


def project(vector2, p_to):
    return mul(p_to, dot(vector2, p_to) / p_to.length_squared())


def clamped(vec2, p_min, p_max):
    import gdsbin.vector2 as vector2

    vector2.x = clamp(vec2.x, p_min.x, p_max.x)
    vector2.y = clamp(vec2.y, p_min.y, p_max.y)
    return vector2


def snapped(vec2, p_step):
    import gdsbin.vector2 as vector2

    vector2.x = snapped(vec2.x, p_step.x)
    vector2.y = snapped(vec2.y, p_step.y)
    return vector2


def limit_length(vec2, p_len):
    l = vec_length()
    v = vec2
    if l > 0 and p_len < l:
        return mul(div(v, l), p_len)
    return v


def move_toward(vec2, p_to, p_delta):
    v = vec2
    vd = p_to.sub(v)
    len = vd.vec_length()
    if len <= p_delta:
        return p_to
    else:
        return add(v, mul(vd.div(len), p_delta))


def slide(vector2, p_normal):
    return sub(vector2, mul(p_normal, dot(vector2, p_normal)))


def bounce(vector2, p_normal):
    return inv(reflect(vector2, p_normal))


def reflect(vector2, p_normal):
    return sub(mul(mul(p_normal, 2.0), dot(vector2, p_normal)), vector2)


def vec_is_equal_approx(p_v):
    return math_is_equal_approx(x, p_v.x) and math_is_equal_approx(y, p_v.y)


def is_zero_approx():
    return is_zero_approx(x) and is_zero_approx(y)


def is_finite():
    return is_finite(x) and is_finite(y)


def sub(vec1, vec2):
    import gdsbin.vector2 as vector2

    vector2.x = vec1.x - vec2.x
    vector2.y = vec1.y - vec2.y
    return vector2


def add(vec1, vec2):
    import gdsbin.vector2 as vector2

    vector2.x = vec1.x + vec2.x
    vector2.y = vec1.y + vec2.y
    return vector2


def mul(vec, p_by):
    import gdsbin.vector2 as vector2

    vector2.x = vec.x * p_by
    vector2.y = vec.y * p_by
    return vector2


def inv(vec):
    import gdsbin.vector2 as vector2

    vector2.x = -vec.x
    vector2.y = -vec.y
    return vector2


def div(vec, p_by):
    import gdsbin.vector2 as vector2

    vector2.x = vec.x / p_by
    vector2.y = vec.y / p_by
    return vector2


def math_is_equal_approx(a, b):
    # Check for exact equality first, required to handle "infinity"values.
    if a == b:
        return True
    CMP_EPSILON = 0.00001
    tolerance = CMP_EPSILON * abs(a)
    if tolerance < CMP_EPSILON:
        tolerance = CMP_EPSILON
    return abs(a - b) < tolerance


if __name__ == "__main__":
    _init()
