import pymxs
import json
import requests

rt = pymxs.runtime

EXPORT_PATH = r"C:\Users\jerry\Desktop\Spatial-Intelligence-Assistant\scene_export.json"
API_URL = "http://localhost:8000/ingest_json"


# --- Utility getters ----------------------------------------------------------

def safe_get_mat_name(obj):
    try:
        if obj.material:
            return str(obj.material.name)
    except:
        pass
    return ""


def safe_get_parent(obj):
    try:
        return str(obj.parent.name)
    except:
        return ""


def get_userprop_via_maxscript(obj, prop):
    """Reads a user property reliably through MaxScript execution."""
    try:
        val = rt.execute(f'getUserProp ${obj.name} "{prop}"')
        return str(val) if val else ""
    except:
        return ""


def set_userprop_if_missing(obj, prop, value):
    """Assigns the property only if it doesn't already exist."""
    existing = get_userprop_via_maxscript(obj, prop)
    if not existing:
        try:
            rt.execute(f'setUserProp ${obj.name} "{prop}" "{value}"')
        except Exception as e:
            print(f"Could not set {prop} on {obj.name}: {e}")


# --- Auto-assignment logic ----------------------------------------------------

def auto_assign_subsystem_and_weight(obj):
    """Heuristics to fill missing Subsystem/Weight based on object name."""
    name = obj.name.lower()

    if "solar" in name:
        subsystem, weight = "Power", 50.0
    elif "antenna" in name or "dish" in name:
        subsystem, weight = "Communications", 10.0
    elif "thruster" in name or "engine" in name or "propulsion" in name:
        subsystem, weight = "Propulsion", 35.0
    elif "panel" in name or "radiator" in name:
        subsystem, weight = "Thermal", 20.0
    elif "camera" in name or "sensor" in name:
        subsystem, weight = "Payload", 15.0
    else:
        subsystem, weight = "Unknown", 0.0

    set_userprop_if_missing(obj, "Subsystem", subsystem)
    set_userprop_if_missing(obj, "Weight", weight)


# --- Class detection ----------------------------------------------------------

def node_class(obj):
    cls = str(rt.classof(obj))
    if "Geometry" in cls:
        return "Geometry"
    if "Helper" in cls:
        return "Helper"
    if "Light" in cls:
        return "Light"
    if "Camera" in cls:
        return "Camera"
    return cls


# --- Main extraction ----------------------------------------------------------

nodes = []
for obj in rt.objects:
    if not rt.isValidNode(obj):
        continue

    # Assign missing user properties automatically
    auto_assign_subsystem_and_weight(obj)

    subsystem = get_userprop_via_maxscript(obj, "Subsystem")
    weight = get_userprop_via_maxscript(obj, "Weight")

    entry = {
        "name": obj.name,
        "parent": safe_get_parent(obj),
        "class_": node_class(obj),
        "material": safe_get_mat_name(obj),
        "user_props": {
            "Subsystem": subsystem,
            "Weight": weight
        }
    }

    print(f"{obj.name} → Subsystem: {subsystem}, Weight: {weight}")
    nodes.append(entry)


data = {"nodes": nodes}

with open(EXPORT_PATH, "w") as f:
    json.dump(data, f, indent=2)

print(f"Exported {len(nodes)} nodes to {EXPORT_PATH}")

# Optional server upload
# try:
#     r = requests.post(API_URL, json=data)
#     print(f"Server response: {r.status_code} - {r.text}")
# except Exception as e:
#     print(f"Could not send to backend: {e}")

# rt.messageBox(f"Export complete. {len(nodes)} nodes extracted.")
