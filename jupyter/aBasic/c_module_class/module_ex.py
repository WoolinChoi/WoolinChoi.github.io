import fah_converter as fah
print ("Enter a celsius value: ")
celsius = float(input())
fahrenheit = fah.covert_c_to_f(celsius)
print ("That's ", fahrenheit, " degrees Fahrenheit")