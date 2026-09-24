#!/usr/bin/env python3
"""Generate the text-based USD maze submitted with the Go2 teleop task."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Wall:
    name: str
    position: tuple[float, float, float]
    size: tuple[float, float, float]


WALL_HEIGHT = 0.65
WALL_THICKNESS = 0.16

MAZE_WALLS = (
    Wall("south", (0.0, -4.0, WALL_HEIGHT / 2), (10.0, WALL_THICKNESS, WALL_HEIGHT)),
    Wall("north", (0.0, 4.0, WALL_HEIGHT / 2), (10.0, WALL_THICKNESS, WALL_HEIGHT)),
    Wall("west", (-5.0, 0.0, WALL_HEIGHT / 2), (WALL_THICKNESS, 8.0, WALL_HEIGHT)),
    Wall("east", (5.0, 0.0, WALL_HEIGHT / 2), (WALL_THICKNESS, 8.0, WALL_HEIGHT)),
    Wall("inner_00", (-1.75, -1.70, WALL_HEIGHT / 2), (6.50, WALL_THICKNESS, WALL_HEIGHT)),
    Wall("inner_01", (1.75, 0.55, WALL_HEIGHT / 2), (6.50, WALL_THICKNESS, WALL_HEIGHT)),
    Wall("inner_02", (-1.60, 2.80, WALL_HEIGHT / 2), (6.80, WALL_THICKNESS, WALL_HEIGHT)),
)


def _vec(values: tuple[float, float, float]) -> str:
    return ", ".join(f"{value:.6g}" for value in values)


def make_usda() -> str:
    walls = []
    for wall in MAZE_WALLS:
        walls.append(f'''    def Cube "{wall.name}" (
        prepend apiSchemas = ["PhysicsCollisionAPI"]
    )
    {{
        uniform bool physics:collisionEnabled = 1
        double size = 1
        float3 xformOp:scale = ({_vec(wall.size)})
        double3 xformOp:translate = ({_vec(wall.position)})
        uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:scale"]
    }}''')
    body = "\n\n".join(walls)
    return f'''#usda 1.0
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


def main() -> None:
    output = Path(__file__).resolve().parent / "assets" / "go2_maze.usda"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(make_usda(), encoding="utf-8")
    print(f"Wrote {output} ({len(MAZE_WALLS)} walls)")


if __name__ == "__main__":
    main()
