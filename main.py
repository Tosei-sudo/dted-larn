
from dted import DTED2
from dummy import File
import time

with open("s55_w069.dt2", "rb") as file:
    dted_file = File(file.read())

start = time.time()

dted = DTED2()
dted.read(dted_file)
# print dted.get_elevetion( -70.997984, 41.998259)
# print dted.get_elevetion( -70.7421, 41.1079)
# print dted.get_elevetion( -70.5899, 41.9258)
print dted.get_elevetion( -68.71331, -54.31950)
print dted.get_elevetion( -68.8599941, -54.8835870)

print "Time:" + str(time.time() - start)