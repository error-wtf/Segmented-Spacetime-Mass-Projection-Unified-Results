"""
Icosphere mesh generation for segmented spacetime visualization.
Creates geodesic spheres with triangular faces for representing the spacetime mesh.
"""

import numpy as np
from typing import Tuple

def normalize(v: np.ndarray) -> np.ndarray:
    """Normalize vectors to unit length."""
    return v / np.linalg.norm(v, axis=1, keepdims=True)

def icosahedron() -> Tuple[np.ndarray, np.ndarray]:
    """Generate base icosahedron vertices and faces."""
    t = (1.0 + np.sqrt(5.0)) / 2.0  # Golden ratio φ
    
    # 12 vertices of icosahedron
    verts = np.array([
        [-1,  t, 0], [ 1,  t, 0], [-1, -t, 0], [ 1, -t, 0],
        [ 0, -1,  t], [ 0,  1,  t], [ 0, -1, -t], [ 0,  1, -t],
        [ t,  0, -1], [ t,  0,  1], [-t,  0, -1], [-t,  0,  1]
    ], dtype=float)
    
    # 20 triangular faces
    faces = np.array([
        [0,11,5], [0,5,1], [0,1,7], [0,7,10], [0,10,11],
        [1,5,9], [5,11,4], [11,10,2], [10,7,6], [7,1,8],
        [3,9,4], [3,4,2], [3,2,6], [3,6,8], [3,8,9],
        [4,9,5], [2,4,11], [6,2,10], [8,6,7], [9,8,1]
    ], dtype=int)
    
    return verts, faces

def subdivide(verts: np.ndarray, faces: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Subdivide each triangle into 4 smaller triangles."""
    mid_cache = {}
    
    def midpoint(a: int, b: int) -> Tuple[int, np.ndarray]:
        """Get midpoint vertex index, creating if needed."""
        key = tuple(sorted((a, b)))
        if key in mid_cache:
            return mid_cache[key], None
        
        # Create new midpoint vertex
        m = (np.array(verts[a]) + np.array(verts[b])) * 0.5
        mid_cache[key] = len(verts)
        return mid_cache[key], m

    verts = verts.tolist()
    new_faces = []
    
    for f in faces:
        a, b, c = f
        
        # Get midpoint indices and vertices
        ia, ma = midpoint(a, b)
        ib, mb = midpoint(b, c) 
        ic, mc = midpoint(c, a)
        
        # Add new vertices if created
        if ma is not None: verts.append(ma.tolist())
        if mb is not None: verts.append(mb.tolist())
        if mc is not None: verts.append(mc.tolist())
        
        # Create 4 new triangular faces
        new_faces.extend([
            [a, ia, ic],    # Corner triangle at a
            [b, ib, ia],    # Corner triangle at b
            [c, ic, ib],    # Corner triangle at c
            [ia, ib, ic]    # Central triangle
        ])
    
    return np.array(verts, float), np.array(new_faces, int)

def build_icosphere(radius: float = 1.0, subdivisions: int = 4) -> Tuple[np.ndarray, np.ndarray]:
    """
    Build geodesic icosphere mesh.
    
    Parameters:
    -----------
    radius : float
        Radius of the sphere in desired units (e.g., AU for solar system)
    subdivisions : int
        Number of subdivision iterations (higher = more detailed mesh)
        
    Returns:
    --------
    vertices : np.ndarray, shape (N, 3)
        Vertex positions
    faces : np.ndarray, shape (M, 3)
        Triangle face indices
    """
    v, f = icosahedron()
    
    # Subdivide mesh
    for _ in range(subdivisions):
        v, f = subdivide(v, f)
    
    # Normalize to unit sphere and scale to desired radius
    v = normalize(v) * radius
    
    return v, f

def mesh_info(vertices: np.ndarray, faces: np.ndarray) -> dict:
    """Get mesh statistics."""
    return {
        'num_vertices': len(vertices),
        'num_faces': len(faces),
        'radius_min': np.min(np.linalg.norm(vertices, axis=1)),
        'radius_max': np.max(np.linalg.norm(vertices, axis=1)),
        'radius_mean': np.mean(np.linalg.norm(vertices, axis=1))
    }

if __name__ == "__main__":
    # Test mesh generation
    print("Testing icosphere generation...")
    
    for subdiv in range(3, 7):
        v, f = build_icosphere(radius=100.0, subdivisions=subdiv)
        info = mesh_info(v, f)
        print(f"Subdivision {subdiv}: {info['num_vertices']} vertices, {info['num_faces']} faces")
    
    print("Icosphere generation test complete!")
