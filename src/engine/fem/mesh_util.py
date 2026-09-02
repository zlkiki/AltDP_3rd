"""
src/engine/fem/mesh_util.py
===========================
Pure Python 2D Mesh Generation Utilities for AltDP_3rd FEM Engine.
Replaces commercial CM2 MeshTools DLLs with zero dependencies.
"""

import numpy as np
from typing import List, Tuple, Dict, Any


def generate_structured_quad_mesh(
    length_x: float,
    length_y: float,
    nx: int,
    ny: int,
    origin_x: float = 0.0,
    origin_y: float = 0.0
) -> Tuple[np.ndarray, List[List[int]]]:
    """
    Generate regular structured quadrilateral mesh for a rectangular domain.
    
    Returns:
        nodes: (nx+1)*(ny+1) x 2 numpy array of coordinates
        elements: (nx*ny) x 4 list of element connectivity (CCW)
    """
    dx = float(length_x) / max(1, nx)
    dy = float(length_y) / max(1, ny)
    
    nodes = []
    node_grid = np.zeros((ny + 1, nx + 1), dtype=int)
    
    for j in range(ny + 1):
        y = origin_y + j * dy
        for i in range(nx + 1):
            x = origin_x + i * dx
            node_grid[j, i] = len(nodes)
            nodes.append([x, y])
            
    elements = []
    for j in range(ny):
        for i in range(nx):
            n1 = int(node_grid[j, i])
            n2 = int(node_grid[j, i + 1])
            n3 = int(node_grid[j + 1, i + 1])
            n4 = int(node_grid[j + 1, i])
            elements.append([n1, n2, n3, n4])
            
    return np.array(nodes), elements


def generate_structured_tri_mesh(
    length_x: float,
    length_y: float,
    nx: int,
    ny: int,
    origin_x: float = 0.0,
    origin_y: float = 0.0
) -> Tuple[np.ndarray, List[List[int]]]:
    """
    Generate structured triangular mesh by splitting each quad element into 2 triangles.
    """
    nodes, quad_elems = generate_structured_quad_mesh(length_x, length_y, nx, ny, origin_x, origin_y)
    tri_elements = []
    
    for q in quad_elems:
        # Split quad [n1, n2, n3, n4] into [n1, n2, n3] and [n1, n3, n4]
        tri_elements.append([q[0], q[1], q[2]])
        tri_elements.append([q[0], q[2], q[3]])
        
    return nodes, tri_elements
