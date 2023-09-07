from units_python.__init__ import v, sqrt, nsqrt
# from __init__ import v, sqrt, nsqrt

def run_tests():

    value = v("1000 dm^3")
    value1 = v("5 km")
    value2 = v("519 m")
    factor = value1 / value2
    factor.round(8)

    unit_test = [
        value.raw() == "1.0 m**3.0",
        (value1 + value2).raw() == "5519.0 m",
        (value1 - value2).raw() == "4481.0 m",
        (value1 * value2).raw() == f"2594999.9999999995 m**2.0",
        (value1 * 2).raw() == f"{float(5000 * 2)} m",
        (value1 * factor).raw() == f"{float(5000 * factor.raw_value())} m"
    ]
    print("basic value instance operations: ", unit_test)

    my_value = v("9 m^2")
    my_copied_value = my_value.copy()

    my_value = v("9 m**2")
    my_value_sqrt = sqrt(my_value)

    other_value = v("27 m^3")
    my_value_3sqrt = nsqrt(other_value, 3)

    third_value = v("3.1415926535 m")
    third_value.round(4)

    speed = v("90 mph")
    time = v("2 hours")
    distance = speed / time
    # print(distance) # outputs "0.0125 mph/s"
    distance = speed / 2
    distance.change_unit("miles")
    # print(distance)

    method_test = [
        my_copied_value.raw() == "9.0 m**2.0",
        my_value_sqrt.raw() == "3.0 m",
        my_value_3sqrt.raw() == "3.0 m",
        third_value.raw() == "3.1416 m",
    ]
    print("method test: ", method_test)

if __name__ == "__main__":

    # other_value = v("27 m^3")
    # my_value_3sqrt = nsqrt(other_value, 3)
    # print(my_value_3sqrt.raw())

    # a = v("5 m/s^2")
    # t = v("4 s")
    # v0 = v("0 m/s")
    # fart = v0 + a*t
    # print("fart: ", fart.raw())

    # speed_without_unit = 96 / 8
    # speed = v(f"{speed_without_unit} km/h")
    # print(speed.raw())

    # x0 = v("0 m")
    # a = v("8 m/s^2")
    # v0 = v("88 km/h") 
    # t = v0 / v("8 m/s^2")
    # print(t.raw())
    # x = x0 + v0*t + 1/2 * a * t**2
    # print(x.raw())

    # print(v("1 km/h").raw())
    # print(v("27.78 m/s").to("km/h"))

    # a = v("-8 m/s^2")
    # print(a.abs().raw())

    run_tests()