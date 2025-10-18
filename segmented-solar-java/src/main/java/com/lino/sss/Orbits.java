package com.lino.sss;

/**
 * Orbital mechanics utilities für Segmented Spacetime Visualization.
 * Generiert Orbit-Trajektorien und φ-basierte Spiral-Strukturen.
 */
public final class Orbits {
    
    /**
     * Erstellt einfache Kreisbahn im ekliptischen Plane (Platzhalter für Kepler-Orbits).
     * 
     * @param radiusAU Bahnradius in AU
     * @param numPoints Anzahl der Punkte entlang der Bahn
     * @return Array von 3D-Punkten der Kreisbahn
     */
    public static Vec3[] circle(double radiusAU, int numPoints) {
        Vec3[] points = new Vec3[numPoints];
        
        for (int i = 0; i < numPoints; i++) {
            double angle = 2.0 * Math.PI * i / (numPoints - 1);
            double x = radiusAU * Math.cos(angle);
            double y = radiusAU * Math.sin(angle);
            double z = 0.0; // Ekliptische Ebene
            
            points[i] = new Vec3(x, y, z);
        }
        
        return points;
    }
    
    /**
     * Erstellt elliptische Bahn mit gegebenen Kepler-Elementen.
     * 
     * @param semiMajorAxis Große Halbachse a in AU
     * @param eccentricity Exzentrität e
     * @param inclination Inklination i in Grad
     * @param numPoints Anzahl der Bahnpunkte
     * @return Array von 3D-Punkten der elliptischen Bahn
     */
    public static Vec3[] ellipse(double semiMajorAxis, double eccentricity, 
                                double inclination, int numPoints) {
        Vec3[] points = new Vec3[numPoints];
        
        // Inklination in Radiant
        double incRad = Math.toRadians(inclination);
        
        for (int i = 0; i < numPoints; i++) {
            // Exzentrische Anomalie (vereinfacht als gleichmäßige Verteilung)
            double E = 2.0 * Math.PI * i / (numPoints - 1);
            
            // Wahre Anomalie aus exzentrischer Anomalie
            double nu = 2.0 * Math.atan2(
                Math.sqrt(1 + eccentricity) * Math.sin(E / 2),
                Math.sqrt(1 - eccentricity) * Math.cos(E / 2)
            );
            
            // Abstand vom Brennpunkt
            double r = semiMajorAxis * (1 - eccentricity * Math.cos(E));
            
            // Position in Bahnebene
            double xOrb = r * Math.cos(nu);
            double yOrb = r * Math.sin(nu);
            double zOrb = 0.0;
            
            // Rotation um Inklination (vereinfacht: nur um X-Achse)
            double x = xOrb;
            double y = yOrb * Math.cos(incRad) - zOrb * Math.sin(incRad);
            double z = yOrb * Math.sin(incRad) + zOrb * Math.cos(incRad);
            
            points[i] = new Vec3(x, y, z);
        }
        
        return points;
    }
    
    /**
     * Erstellt φ-basierte Spirale um einen Himmelskörper.
     * Repräsentiert die "Normaluhr"-Struktur der segmentierten Raumzeit.
     * 
     * @param center Zentrumsposition des Körpers
     * @param baseRadius Basis-Radius der Spirale in AU
     * @param timeDilation Lokaler Zeitdilatationsfaktor τ(x)
     * @param numTurns Anzahl der Spiral-Windungen
     * @param pointsPerTurn Punkte pro Windung
     * @return Array von 3D-Punkten der φ-Spirale
     */
    public static Vec3[] phiSpiral(Vec3 center, double baseRadius, 
                                  double timeDilation, double numTurns, 
                                  int pointsPerTurn) {
        int totalPoints = (int) (numTurns * pointsPerTurn);
        Vec3[] points = new Vec3[totalPoints];
        
        // Goldener Schnitt φ
        double phi = Field.PHI;
        
        for (int i = 0; i < totalPoints; i++) {
            // Parameter entlang der Spirale
            double t = (double) i / (totalPoints - 1);
            double angle = numTurns * 2.0 * Math.PI * t;
            
            // φ-basierte logarithmische Spirale
            // r(θ) = r₀ * φ^(θ/π) moduliert durch Zeitdilatation
            double spiralRadius = baseRadius * Math.pow(phi, angle / Math.PI) * timeDilation;
            
            // Spirale in lokaler X-Y Ebene
            double x = spiralRadius * Math.cos(angle);
            double y = spiralRadius * Math.sin(angle);
            double z = 0.0;
            
            // Translation zum Körper-Zentrum
            points[i] = new Vec3(
                center.x + x,
                center.y + y, 
                center.z + z
            );
        }
        
        return points;
    }
    
    /**
     * Berechnet Orbital-Geschwindigkeit für Kreisbahn (vereinfacht).
     * 
     * @param radiusAU Bahnradius in AU
     * @param centralMass Zentralmasse in Sonnenmassen
     * @return Orbital-Geschwindigkeit in km/s
     */
    public static double orbitalVelocity(double radiusAU, double centralMass) {
        // Vereinfachte Formel: v = √(GM/r)
        // G = 6.674e-11 m³/(kg·s²), M_sun = 1.989e30 kg, 1 AU = 1.496e11 m
        double GM_sun = 1.327e20; // m³/s² für Sonnenmasse
        double radiusM = radiusAU * 1.496e11; // AU zu Meter
        
        double velocity = Math.sqrt(GM_sun * centralMass / radiusM);
        return velocity / 1000.0; // m/s zu km/s
    }
    
    /**
     * Berechnet Orbital-Periode für Kreisbahn (Kepler's 3. Gesetz).
     * 
     * @param radiusAU Bahnradius in AU
     * @param centralMass Zentralmasse in Sonnenmassen
     * @return Orbital-Periode in Tagen
     */
    public static double orbitalPeriod(double radiusAU, double centralMass) {
        // Kepler's 3. Gesetz: P² = (4π²/GM) * a³
        // Für Sonnenmasse und AU: P² = a³ (P in Jahren, a in AU)
        double periodYears = Math.pow(radiusAU, 1.5) / Math.sqrt(centralMass);
        return periodYears * 365.25; // Jahre zu Tage
    }
    
    /**
     * Erstellt Orbit-Punkte für alle Planeten des Sonnensystems.
     * 
     * @return Array von Orbit-Arrays für jeden Planeten
     */
    public static Vec3[][] createSolarSystemOrbits() {
        // Planetendaten: [a_AU, e, i_deg]
        double[][] planetData = {
            {0.387, 0.206, 7.0},   // Mercury
            {0.723, 0.007, 3.4},   // Venus  
            {1.000, 0.017, 0.0},   // Earth
            {1.524, 0.093, 1.9},   // Mars
            {5.204, 0.049, 1.3},   // Jupiter
            {9.582, 0.056, 2.5}    // Saturn
        };
        
        Vec3[][] orbits = new Vec3[planetData.length][];
        
        for (int i = 0; i < planetData.length; i++) {
            double a = planetData[i][0];
            double e = planetData[i][1]; 
            double inc = planetData[i][2];
            
            // Mehr Punkte für äußere Planeten
            int numPoints = (int) (200 + a * 20);
            
            if (e < 0.05) {
                // Nahezu kreisförmige Bahnen
                orbits[i] = circle(a, numPoints);
            } else {
                // Elliptische Bahnen
                orbits[i] = ellipse(a, e, inc, numPoints);
            }
        }
        
        return orbits;
    }
}
