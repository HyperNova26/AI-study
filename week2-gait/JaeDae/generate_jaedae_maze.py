#!/usr/bin/env python3
"""Generate JaeDae's maze as a portable USDA asset.
"""

from pathlib import Path

HEIGHT = 0.65
THICKNESS = 0.16

# name, centre (x, y), dimensions (x, y).  The alternating openings form a
# own 11 x 9 m maze, distinct from the provided sample and prior submission.
WALLS = (
    ("boundary_south", (0.0, -4.5), (11.0, THICKNESS)),
    ("boundary_north", (0.0, 4.5), (11.0, THICKNESS)),
    ("boundary_west", (-5.5, 0.0), (THICKNESS, 9.0)),
    ("boundary_east", (5.5, 0.0), (THICKNESS, 9.0)),
    ("divider", (-1.5, 0.0), (8.0, THICKNESS)),
)


def wall_usda(name: str, centre: tuple[float, float], size: tuple[float, float]) -> str:
    """Return one collidable cube, scaled in metres from USD's unit cube."""
    return f'''    def Cube "{name}" (
        prepend apiSchemas = ["PhysicsCollisionAPI"]
    )
    {{
        uniform bool physics:collisionEnabled = 1
        double size = 1
        float3 xformOp:scale = ({size[0]:g}, {size[1]:g}, {HEIGHT:g})
        double3 xformOp:translate = ({centre[0]:g}, {centre[1]:g}, {HEIGHT / 2:g})
        uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:scale"]
    }}'''


def main() -> None:
    walls = "\n\n".join(wall_usda(*wall) for wall in WALLS)
    usda = f'''#usda 1.0
(
    defaultPrim = "JaeDaeMaze"
    metersPerUnit = 1
    upAxis = "Z"
)

def Xform "JaeDaeMaze"
{{
{walls}
}}
'''
    output = Path(__file__).resolve().parent / "assets" / "jaedae_maze.usda"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(usda, encoding="utf-8", newline="\n")
    print(f"Wrote {output} ({len(WALLS)} static collision walls)")


if __name__ == "__main__":
    main()
