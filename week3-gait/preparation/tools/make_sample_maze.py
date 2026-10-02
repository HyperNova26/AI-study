#!/usr/bin/env python3
"""Write assets/sample_maze.usda: a small S-shaped maze for trying a policy before using your own.

Same text USD layout as week2-gait/ChanwonJung/generate_maze_usda.py (static Cube walls with
PhysicsCollisionAPI). Students run their own week-2 maze with go2_policy_teleop.py --maze-usd.
"""

from pathlib import Path

HEIGHT = 0.6
THICKNESS = 0.15

# name, center (x, y), size (x, y). The outer box is 8 m x 6 m; two inner walls leave 2.5 m gaps
# at alternating ends, so the path is: south corridor east -> middle corridor west -> north corridor east.
WALLS = (
    ("south", (0.0, -3.0), (8.0, THICKNESS)),
    ("north", (0.0, 3.0), (8.0, THICKNESS)),
    ("west", (-4.0, 0.0), (THICKNESS, 6.0)),
    ("east", (4.0, 0.0), (THICKNESS, 6.0)),
    ("inner_south", (-1.25, -1.0), (5.5, THICKNESS)),
    ("inner_north", (1.25, 1.0), (5.5, THICKNESS)),
)


def wall_prim(name, center, size):
    return f'''    def Cube "{name}" (
        prepend apiSchemas = ["PhysicsCollisionAPI"]
    )
    {{
        uniform bool physics:collisionEnabled = 1
        double size = 1
        float3 xformOp:scale = ({size[0]:g}, {size[1]:g}, {HEIGHT:g})
        double3 xformOp:translate = ({center[0]:g}, {center[1]:g}, {HEIGHT / 2:g})
        uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:scale"]
    }}'''


def main():
    body = "\n\n".join(wall_prim(*wall) for wall in WALLS)
    text = f'''#usda 1.0
(
    defaultPrim = "Maze"
    metersPerUnit = 1
    upAxis = "Z"
)

def Xform "Maze"
{{
{body}
}}
'''
    output = Path(__file__).resolve().parents[1] / "assets" / "sample_maze.usda"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8", newline="\n")
    print(f"Wrote {output} ({len(WALLS)} walls)")


if __name__ == "__main__":
    main()
