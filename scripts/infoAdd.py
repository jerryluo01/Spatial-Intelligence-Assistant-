from pymxs import runtime as rt

for obj in rt.objects:
    name = obj.name.lower()

    if "solar" in name:
        subsystem = "Power"
        weight = 50.0
    elif "antenna" in name:
        subsystem = "Communications"
        weight = 10.0
    elif "thruster" in name or "engine" in name:
        subsystem = "Propulsion"
        weight = 35.0
    else:
        subsystem = "Unknown"
        weight = 0.0

    rt.setUserProp(obj, "Subsystem", subsystem)
    rt.setUserProp(obj, "Weight", str(weight))

print("successful")