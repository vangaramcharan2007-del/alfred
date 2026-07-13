import os

class CADEngine:
    def __init__(self, export_dir: str = "C:\\Users\\vanga\\Documents\\Jarvis_Vault\\CAD_Exports"):
        self.export_dir = export_dir
        
    def generate_base_enclosure(self, width: float, length: float, height: float, wall_thickness: float = 2.0):
        os.makedirs(self.export_dir, exist_ok=True)
        filename = os.path.join(self.export_dir, "enclosure.scad")
        
        # OpenSCAD script for a hollow rectangular box
        scad_script = f"""// Auto-generated Enclosure
width = {width};
length = {length};
height = {height};
wall = {wall_thickness};

difference() {{
    // Outer shell
    cube([width, length, height]);
    
    // Inner hollow
    translate([wall, wall, wall])
        cube([width - 2*wall, length - 2*wall, height]);
}}
"""
        with open(filename, "w", encoding="utf-8") as f:
            f.write(scad_script)
            
        return filename
