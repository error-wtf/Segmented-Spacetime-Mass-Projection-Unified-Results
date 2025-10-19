package com.lino.sss;

import java.util.*;

/**
 * Geodätische Icosphere-Mesh-Generierung für segmentierte Raumzeit-Visualisierung.
 * Erstellt ein gleichmäßiges trianguliertes Sphären-Mesh durch rekursive Subdivision
 * eines Ikosaeders.
 */
public final class Icosphere {
    public final Vec3[] verts;
    public final int[][] faces;

    private Icosphere(Vec3[] vertices, int[][] triangles) { 
        this.verts = vertices; 
        this.faces = triangles; 
    }

    /**
     * Erstellt eine Icosphere mit gegebenem Radius und Subdivision-Level.
     * 
     * @param radius Radius der Sphäre in AU
     * @param subdivisions Anzahl der Subdivision-Schritte (0-8 empfohlen)
     * @return Icosphere-Objekt mit Vertices und Faces
     */
    public static Icosphere build(double radius, int subdivisions) {
        Vec3[] vertices = baseVertices();
        int[][] triangles = baseTriangles();
        
        // Rekursive Subdivision
        for (int s = 0; s < subdivisions; s++) {
            Map<Long, Integer> midpointCache = new HashMap<>();
            List<Vec3> newVertices = new ArrayList<>(Arrays.asList(vertices));
            List<int[]> newTriangles = new ArrayList<>();
            
            for (int[] triangle : triangles) {
                int a = triangle[0], b = triangle[1], c = triangle[2];
                
                // Mittelpunkte der Kanten finden/erstellen
                int ab = getMidpoint(a, b, newVertices, midpointCache);
                int bc = getMidpoint(b, c, newVertices, midpointCache);
                int ca = getMidpoint(c, a, newVertices, midpointCache);
                
                // 4 neue Dreiecke erstellen
                newTriangles.add(new int[]{a, ab, ca});
                newTriangles.add(new int[]{b, bc, ab});
                newTriangles.add(new int[]{c, ca, bc});
                newTriangles.add(new int[]{ab, bc, ca});
            }
            
            vertices = newVertices.toArray(new Vec3[0]);
            triangles = newTriangles.toArray(new int[0][]);
        }
        
        // Normalisierung auf Einheitssphäre und Skalierung
        for (Vec3 vertex : vertices) { 
            vertex.nor().mul(radius); 
        }
        
        return new Icosphere(vertices, triangles);
    }

    /**
     * Findet oder erstellt Mittelpunkt zwischen zwei Vertices.
     */
    private static int getMidpoint(int i, int j, List<Vec3> vertices, Map<Long, Integer> cache) {
        // Eindeutiger Schlüssel für Kantenpaar (kleinerer Index zuerst)
        long key = (((long) Math.min(i, j)) << 32) | (long) Math.max(i, j);
        
        Integer existingIndex = cache.get(key);
        if (existingIndex != null) {
            return existingIndex;
        }
        
        // Neuen Mittelpunkt erstellen
        Vec3 a = vertices.get(i);
        Vec3 b = vertices.get(j);
        Vec3 midpoint = new Vec3(
            (a.x + b.x) / 2.0,
            (a.y + b.y) / 2.0,
            (a.z + b.z) / 2.0
        );
        
        int newIndex = vertices.size();
        vertices.add(midpoint);
        cache.put(key, newIndex);
        
        return newIndex;
    }

    /**
     * Basis-Ikosaeder Vertices (12 Punkte).
     * Verwendet den goldenen Schnitt φ = (1+√5)/2.
     */
    private static Vec3[] baseVertices() {
        double phi = (1.0 + Math.sqrt(5.0)) / 2.0; // Goldener Schnitt φ
        
        return new Vec3[]{
            // X-Y Ebene mit ±1, ±φ
            new Vec3(-1,  phi, 0), new Vec3( 1,  phi, 0),
            new Vec3(-1, -phi, 0), new Vec3( 1, -phi, 0),
            
            // Y-Z Ebene mit ±1, ±φ  
            new Vec3( 0, -1,  phi), new Vec3( 0,  1,  phi),
            new Vec3( 0, -1, -phi), new Vec3( 0,  1, -phi),
            
            // Z-X Ebene mit ±1, ±φ
            new Vec3( phi,  0, -1), new Vec3( phi,  0,  1),
            new Vec3(-phi,  0, -1), new Vec3(-phi,  0,  1)
        };
    }

    /**
     * Basis-Ikosaeder Dreiecke (20 Faces).
     * Definiert die Topologie des regulären Ikosaeders.
     */
    private static int[][] baseTriangles() {
        return new int[][]{
            // Obere Kappe (um Vertex 0)
            {0, 11, 5}, {0, 5, 1}, {0, 1, 7}, {0, 7, 10}, {0, 10, 11},
            
            // Oberer Gürtel
            {1, 5, 9}, {5, 11, 4}, {11, 10, 2}, {10, 7, 6}, {7, 1, 8},
            
            // Unterer Gürtel  
            {3, 9, 4}, {3, 4, 2}, {3, 2, 6}, {3, 6, 8}, {3, 8, 9},
            
            // Untere Kappe (um Vertex 3)
            {4, 9, 5}, {2, 4, 11}, {6, 2, 10}, {8, 6, 7}, {9, 8, 1}
        };
    }
    
    /**
     * Berechnet Mesh-Statistiken.
     */
    public String getStats() {
        double minRadius = Double.MAX_VALUE;
        double maxRadius = Double.MIN_VALUE;
        double avgRadius = 0.0;
        
        for (Vec3 v : verts) {
            double r = v.len();
            minRadius = Math.min(minRadius, r);
            maxRadius = Math.max(maxRadius, r);
            avgRadius += r;
        }
        avgRadius /= verts.length;
        
        return String.format(
            "Icosphere: %d vertices, %d faces | Radius: %.3f-%.3f AU (avg: %.3f)",
            verts.length, faces.length, minRadius, maxRadius, avgRadius
        );
    }
}
