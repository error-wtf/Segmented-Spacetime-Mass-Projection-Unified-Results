package com.lino.sss;

/**
 * Segmented Spacetime Field Calculator nach Casu & Wrede Framework.
 * 
 * Implementiert:
 * - Segment Density Field: N(x) = Σ_i γ_i · K_i(||x - x_i||)
 * - Time Dilation: τ(x) = φ^(-α·N(x)) 
 * - Refractive Index: n(x) = 1 + κ·N(x)
 * - Natural Boundary Saturation via logistische Funktion
 */
public final class Field {
    
    /** Goldener Schnitt φ = (1+√5)/2 */
    public static final double PHI = (1.0 + Math.sqrt(5.0)) / 2.0;
    
    /** π-Konstante für metrische Invarianz */
    public static final double PI = Math.PI;

    /**
     * Logistische Sättigungsfunktion für Natural Boundary.
     * σ(x) = 1/(1 + e^(-x))
     * 
     * @param x Eingabewert
     * @return Sättigungswert zwischen 0 und 1
     */
    public static double logistic(double x) { 
        return 1.0 / (1.0 + Math.exp(-x)); 
    }

    /**
     * Soft-Power-Kernel mit Natural Boundary Saturation.
     * K_i(r) = (M_i / (r + r0)^p) · σ((r_nb - r)/δ)
     * 
     * @param r Abstand vom Körper
     * @param massScale Skalierte Masse M_i
     * @param r0 Softening-Radius
     * @param powerIndex Power-Law Index p
     * @param naturalBoundary Natural Boundary Radius r_nb
     * @param boundaryWidth Übergangsbreite δ
     * @return Kernel-Wert
     */
    public static double kernel(double r, double massScale, double r0, 
                               double powerIndex, double naturalBoundary, double boundaryWidth) {
        // Power-Law Komponente mit Softening
        double powerTerm = massScale / Math.pow(r + r0, powerIndex);
        
        // Natural Boundary Saturation
        double boundaryArg = (naturalBoundary - r) / boundaryWidth;
        double saturation = logistic(boundaryArg);
        
        return powerTerm * saturation;
    }

    /**
     * Berechnet Segment Density N(x) an gegebener Position.
     * N(x) = N_bg + Σ_i γ_i · K_i(||x - x_i||)
     * 
     * @param position Raumpunkt x
     * @param bodies Array von gravitierenden Körpern
     * @param params Feld-Parameter
     * @return Segment Density N(x), begrenzt auf [0, N_max]
     */
    public static double segmentDensity(Vec3 position, Body[] bodies, Params params) {
        double density = params.backgroundDensity;
        
        for (Body body : bodies) {
            double distance = Vec3.dist(position, body.position);
            double kernelValue = kernel(
                distance, 
                body.massScale, 
                body.softeningRadius,
                params.powerIndex, 
                body.naturalBoundary, 
                body.boundaryWidth
            );
            density += body.couplingStrength * kernelValue;
        }
        
        // Begrenzung auf physikalisch sinnvolle Werte
        return Math.max(0.0, Math.min(params.maxDensity, density));
    }

    /**
     * Berechnet Zeitdilatation τ(x) aus Segment Density.
     * τ(x) = φ^(-α · N(x))
     * 
     * @param segmentDensity N(x)
     * @param alpha Kopplungsparameter α
     * @return Zeitdilatationsfaktor τ(x) ≤ 1
     */
    public static double timeDilation(double segmentDensity, double alpha) { 
        return Math.pow(PHI, -alpha * segmentDensity); 
    }

    /**
     * Berechnet effektiven Brechungsindex n(x) aus Segment Density.
     * n(x) = 1 + κ · N(x)
     * 
     * @param segmentDensity N(x)
     * @param kappa Kopplungsparameter κ
     * @return Brechungsindex n(x) ≥ 1
     */
    public static double refractiveIndex(double segmentDensity, double kappa) { 
        return 1.0 + kappa * segmentDensity; 
    }
    
    /**
     * Berechnet φ-Spiral Parameter für temporale Uhren.
     * Spiral-Frequenz ∝ 1/τ(x) für lokale Zeitbeschleunigung.
     * 
     * @param localTimeDilation τ(x) am Körper
     * @return Spiral-Frequenz-Faktor
     */
    public static double phiSpiralFrequency(double localTimeDilation) {
        return PHI / localTimeDilation; // Schneller bei τ < 1
    }

    /**
     * Gravitierender Körper mit segmented spacetime Parametern.
     */
    public static final class Body {
        public final String name;
        public final Vec3 position;
        public final double massScale;           // M_i in dimensionslosen Einheiten
        public final double couplingStrength;    // γ_i Kopplungsstärke
        public final double softeningRadius;     // r0 Softening-Radius
        public final double naturalBoundary;     // r_nb Natural Boundary Radius
        public final double boundaryWidth;       // δ Übergangsbreite

        public Body(String name, Vec3 position, double massScale, 
                   double couplingStrength, double softeningRadius, 
                   double naturalBoundary, double boundaryWidth) {
            this.name = name;
            this.position = position;
            this.massScale = massScale;
            this.couplingStrength = couplingStrength;
            this.softeningRadius = softeningRadius;
            this.naturalBoundary = naturalBoundary;
            this.boundaryWidth = boundaryWidth;
        }
        
        @Override
        public String toString() {
            return String.format("%s @ %s (M=%.6f, γ=%.3f)", 
                name, position, massScale, couplingStrength);
        }
    }

    /**
     * Segmented Spacetime Feld-Parameter.
     */
    public static final class Params {
        public double powerIndex = 2.0;           // p: Power-Law Index
        public double backgroundDensity = 0.0;    // N_bg: Hintergrund-Dichte
        public double maxDensity = 5.0;           // N_max: Maximale Dichte
        public double alpha = 1.0;                // α: Zeitdilatations-Kopplung
        public double kappa = 0.015;              // κ: Brechungsindex-Kopplung

        public Params set(double powerIndex, double backgroundDensity, 
                         double maxDensity, double alpha, double kappa) {
            this.powerIndex = powerIndex;
            this.backgroundDensity = backgroundDensity;
            this.maxDensity = maxDensity;
            this.alpha = alpha;
            this.kappa = kappa;
            return this;
        }
        
        @Override
        public String toString() {
            return String.format(
                "Params(p=%.1f, N_bg=%.3f, N_max=%.1f, α=%.2f, κ=%.3f)",
                powerIndex, backgroundDensity, maxDensity, alpha, kappa
            );
        }
    }
    
    /**
     * Erstellt Standard-Sonnensystem für Demo.
     */
    public static Body[] createSolarSystem() {
        return new Body[] {
            // Sonne (Zentrum, dominante Masse)
            new Body("Sun", new Vec3(0, 0, 0), 
                    1.0,        // M_scale = 1 (Referenz)
                    1.0,        // γ = 1 (volle Kopplung)
                    0.00465,    // r0 ≈ Sonnenradius in AU
                    0.025,      // r_nb ≈ 5x Sonnenradius
                    0.005),     // δ ≈ Sonnenradius
            
            // Jupiter (größter Planet)
            new Body("Jupiter", new Vec3(5.2, 0, 0),
                    0.000954,   // M_scale ≈ M_Jupiter/M_Sun
                    1.0,        // γ = 1
                    0.000477,   // r0 ≈ Jupiter-Radius in AU
                    0.003,      // r_nb ≈ 6x Jupiter-Radius
                    0.0006),    // δ ≈ Jupiter-Radius
            
            // Saturn
            new Body("Saturn", new Vec3(9.5, 0, 0),
                    0.000286,   // M_scale ≈ M_Saturn/M_Sun
                    1.0,        // γ = 1
                    0.000403,   // r0 ≈ Saturn-Radius in AU
                    0.0025,     // r_nb
                    0.0005),    // δ
            
            // Erde (für Referenz)
            new Body("Earth", new Vec3(1.0, 0, 0),
                    0.000003,   // M_scale ≈ M_Earth/M_Sun
                    1.0,        // γ = 1
                    0.0000426,  // r0 ≈ Erd-Radius in AU
                    0.0002,     // r_nb
                    0.00004)    // δ
        };
    }
}
