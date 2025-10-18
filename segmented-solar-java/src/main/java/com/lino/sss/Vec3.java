package com.lino.sss;

/**
 * Einfache 3D-Vektor-Klasse für Segmented Spacetime Berechnungen.
 * Unterstützt grundlegende Vektoroperationen in kartesischen Koordinaten.
 */
public final class Vec3 {
    public double x, y, z;
    
    public Vec3() { 
        this(0.0, 0.0, 0.0); 
    }
    
    public Vec3(double x, double y, double z) { 
        this.x = x; 
        this.y = y; 
        this.z = z; 
    }
    
    public Vec3 set(double X, double Y, double Z) { 
        x = X; 
        y = Y; 
        z = Z; 
        return this; 
    }
    
    public Vec3 add(Vec3 other) { 
        x += other.x; 
        y += other.y; 
        z += other.z; 
        return this; 
    }
    
    public Vec3 sub(Vec3 other) { 
        x -= other.x; 
        y -= other.y; 
        z -= other.z; 
        return this; 
    }
    
    public Vec3 mul(double scalar) { 
        x *= scalar; 
        y *= scalar; 
        z *= scalar; 
        return this; 
    }
    
    public double len() { 
        return Math.sqrt(x*x + y*y + z*z); 
    }
    
    public Vec3 nor() { 
        double L = len(); 
        if (L > 0.0) {
            x /= L; 
            y /= L; 
            z /= L;
        } 
        return this; 
    }
    
    public Vec3 cpy() { 
        return new Vec3(x, y, z); 
    }
    
    public static double dist(Vec3 a, Vec3 b) {
        double dx = a.x - b.x;
        double dy = a.y - b.y; 
        double dz = a.z - b.z;
        return Math.sqrt(dx*dx + dy*dy + dz*dz);
    }
    
    public static Vec3 cross(Vec3 a, Vec3 b) {
        return new Vec3(
            a.y * b.z - a.z * b.y,
            a.z * b.x - a.x * b.z,
            a.x * b.y - a.y * b.x
        );
    }
    
    public static double dot(Vec3 a, Vec3 b) {
        return a.x * b.x + a.y * b.y + a.z * b.z;
    }
    
    @Override
    public String toString() {
        return String.format("Vec3(%.3f, %.3f, %.3f)", x, y, z);
    }
}
