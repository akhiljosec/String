import gc

all_obj = gc.get_objects()

my_obj = [obj for obj in all_obj]

for i, obj in enumerate(my_obj):
    print(f"{i+1}. Object ID: {id(obj)}")