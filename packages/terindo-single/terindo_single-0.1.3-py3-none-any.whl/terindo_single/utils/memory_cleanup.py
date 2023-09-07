import atexit
import gc

def clean_up_objects(objects_to_clean):
    """
    Cleans up a list of objects by printing each object to be cleaned up and then
    deleting all references to the objects.

    :param objects_to_clean: A list of objects to be cleaned up.
    :type objects_to_clean: list
    """
    for obj in objects_to_clean:
        print(f"Cleaning up: {obj}")
    del objects_to_clean[:]  # Clear the list, removing all references
    gc.collect()
    
def register_cleanup(objects_to_clean):
    atexit.register(clean_up_objects, objects_to_clean)
