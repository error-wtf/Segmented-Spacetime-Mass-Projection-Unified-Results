package com.lino.sss;

import org.teavm.jso.browser.Window;
import org.teavm.jso.dom.html.*;
import org.teavm.jso.canvas.*;

/**
 * Interaktive Segmented Spacetime Solar System Visualisierung.
 * 
 * Erweiterte Version mit UI-Kontrollen, Orbits, Planetenkugeln,
 * Live-Neuberechnung und JSON-Ephemeriden-Support.
 */
public final class Main {

    // Kamera / Projektion
    static double camZ = 400.0, scale = 800.0, rotY = 0.0, rotX = 0.2;
    static boolean autoRotate = true;
    static String mode = "wire"; // "wire" | "points"

    // Mesh
    static Icosphere ico;
    static double[] N, TAU, NIDX;
    static double Nmin, Nmax, TAUmin, TAUmax, NIDXmin, NIDXmax;
    
    // Color mode & palette
    static String colorMode = "N"; // "N" | "TAU" | "NIDX"
    static String palette = "Turbo"; // "Turbo" | "Viridis" | "Plasma" | "Greys"
    
    // LUT-basierte Farbverwaltung für Performance
    static int[][] lutTurbo, lutViridis, lutPlasma, lutGreys;

    // UI cached
    static HTMLCanvasElement canvas, legend;
    static CanvasRenderingContext2D g, gLegend;
    static int W, H;

    // Bodies (Demo initial)
    static Field.Body[] baseBodies;
    static boolean showOrbits = true;

    // Params
    static Field.Params P = new Field.Params();

    // Orbits cache
    static Vec3[][] orbitPts;

    public static void main(String[] args) {
        HTMLDocument doc = Window.current().getDocument();
        canvas = (HTMLCanvasElement) doc.getElementById("canvas");
        legend = (HTMLCanvasElement) doc.getElementById("legendCanvas");
        g = (CanvasRenderingContext2D) canvas.getContext("2d");
        gLegend = (CanvasRenderingContext2D) legend.getContext("2d");
        W = canvas.getWidth(); 
        H = canvas.getHeight();

        System.out.println("🌌 Interactive Segmented Spacetime Solar System");
        System.out.println("📐 Canvas: " + W + "x" + H);

        // Mesh
        ico = Icosphere.build(120.0, 5);
        System.out.println("🔺 " + ico.getStats());

        // Bodies (Sun + Planets rough AU positions; placeholders)
        baseBodies = new Field.Body[]{
            new Field.Body("Sun",     new Vec3(0,0,0),    1.0,      1.0, 0.005, 0.025, 0.005),
            new Field.Body("Mercury", new Vec3(0.39,0,0), 1.65e-7,  1.0, 0.0002,0.001, 0.0002),
            new Field.Body("Venus",   new Vec3(0.72,0,0), 2.45e-6,  1.0, 0.0006,0.002, 0.0004),
            new Field.Body("Earth",   new Vec3(1.00,0,0), 3.00e-6,  1.0, 0.0006,0.002, 0.0004),
            new Field.Body("Mars",    new Vec3(1.52,0,0), 3.23e-7,  1.0, 0.0004,0.0015,0.0003),
            new Field.Body("Jupiter", new Vec3(5.20,0,0), 9.54e-4,  1.0, 0.0005,0.003, 0.0006),
            new Field.Body("Saturn",  new Vec3(9.58,0,0), 2.86e-4,  1.0, 0.0005,0.003, 0.0006)
        };

        // Orbits (simple circles)
        orbitPts = new Vec3[][]{
            Orbits.circle(0.39, 240), Orbits.circle(0.72, 240), Orbits.circle(1.00, 240),
            Orbits.circle(1.52, 240), Orbits.circle(5.20, 240), Orbits.circle(9.58, 240)
        };

        System.out.println("🪐 Solar System: " + baseBodies.length + " bodies");

        // UI init values
        syncParamsFromUI();
        computeField();

        // Initialize LUTs for performance
        initLUTs();

        // Handlers
        attachUIHandlers();

        // Start loop
        Window.requestAnimationFrame(ts -> tick());
        
        System.out.println("✅ Interactive system ready with LUT optimization!");
    }

    static void syncParamsFromUI() {
        P.alpha = UI.sliderVal("alpha");
        P.kappa = UI.sliderVal("kappa");
        P.powerIndex = UI.sliderVal("p");
        P.maxDensity = UI.sliderVal("nmax");
        
        UI.setText("alphaVal", String.format("%.2f", P.alpha));
        UI.setText("kappaVal", String.format("%.3f", P.kappa));
        UI.setText("pVal",     String.format("%.2f", P.powerIndex));
        UI.setText("nmaxVal",  String.format("%.1f", P.maxDensity));
        
        autoRotate = UI.isChecked("rot");
        showOrbits = UI.isChecked("showOrbits");
        mode = UI.isRadioSelected("points") ? "points" : "wire";
        
        // Color mode
        boolean cmTau = UI.isRadioSelected("cmTau");
        boolean cmn = UI.isRadioSelected("cmn");
        colorMode = cmTau ? "TAU" : (cmn ? "NIDX" : "N");
        
        // Palette
        palette = UI.selectVal("palette");
        
        updateCmapInfo();
    }

    static Field.Body[] filteredBodies() {
        HTMLCollection c = UI.bodyToggles();
        if (c == null) return baseBodies;
        
        boolean sunOn=true, merc=true, ven=true, ear=true, mar=true, jup=true, sat=true;
        
        for (int i = 0; i < c.getLength(); i++) {
            HTMLElement el = (HTMLElement) c.item(i);
            String name = el.getAttribute("data-body");
            boolean on = ((HTMLInputElement) el).isChecked();
            
            if ("Sun".equals(name)) sunOn = on;
            if ("Mercury".equals(name)) merc = on;
            if ("Venus".equals(name)) ven = on;
            if ("Earth".equals(name)) ear = on;
            if ("Mars".equals(name)) mar = on;
            if ("Jupiter".equals(name)) jup = on;
            if ("Saturn".equals(name)) sat = on;
        }
        
        java.util.ArrayList<Field.Body> list = new java.util.ArrayList<>();
        for (Field.Body b : baseBodies) {
            if (("Sun".equals(b.name) && sunOn)
             || ("Mercury".equals(b.name) && merc)
             || ("Venus".equals(b.name) && ven)
             || ("Earth".equals(b.name) && ear)
             || ("Mars".equals(b.name) && mar)
             || ("Jupiter".equals(b.name) && jup)
             || ("Saturn".equals(b.name) && sat)) {
                list.add(b);
            }
        }
        return list.toArray(new Field.Body[0]);
    }

    static void computeField() {
        Field.Body[] bodies = filteredBodies();
        UI.setText("status", "Computing fields...");
        
        double[] Ntmp = new double[ico.verts.length];
        double[] Ttmp = new double[ico.verts.length];
        double[] Itmp = new double[ico.verts.length];

        double nmin = Double.POSITIVE_INFINITY, nmax = Double.NEGATIVE_INFINITY;
        double tmin = Double.POSITIVE_INFINITY, tmax = Double.NEGATIVE_INFINITY;
        double imin = Double.POSITIVE_INFINITY, imax = Double.NEGATIVE_INFINITY;

        for (int i = 0; i < ico.verts.length; i++) {
            double Nv = Field.segmentDensity(ico.verts[i], bodies, P);
            Ntmp[i] = Nv;
            if (Nv < nmin) nmin = Nv; 
            if (Nv > nmax) nmax = Nv;

            double Tv = Field.timeDilation(Nv, P.alpha);
            Ttmp[i] = Tv;
            if (Tv < tmin) tmin = Tv; 
            if (Tv > tmax) tmax = Tv;

            double Iv = Field.refractiveIndex(Nv, P.kappa);
            Itmp[i] = Iv;
            if (Iv < imin) imin = Iv; 
            if (Iv > imax) imax = Iv;
        }
        
        N = Ntmp; Nmin = nmin; Nmax = nmax;
        TAU = Ttmp; TAUmin = tmin; TAUmax = tmax;
        NIDX = Itmp; NIDXmin = imin; NIDXmax = imax;

        UI.setText("status", "Ready ✓");
        drawLegend();
        updateCmapInfo();
        
        System.out.printf("📊 Fields: N(%.6f-%.3f) τ(%.6f-%.3f) n(%.6f-%.3f)%n", 
            Nmin, Nmax, TAUmin, TAUmax, NIDXmin, NIDXmax);
    }
    
    static void updateCmapInfo() {
        if ("N".equals(colorMode)) {
            UI.setText("cmapInfo", String.format("N: min=%.3f max=%.3f", Nmin, Nmax));
        } else if ("TAU".equals(colorMode)) {
            UI.setText("cmapInfo", String.format("τ: min=%.3f max=%.3f", TAUmin, TAUmax));
        } else {
            UI.setText("cmapInfo", String.format("n: min=%.3f max=%.3f", NIDXmin, NIDXmax));
        }
    }

    static void attachUIHandlers() {
        // Slider handlers
        UI.slider("alpha").setOninput(ev -> { syncParamsFromUI(); computeField(); });
        UI.slider("kappa").setOninput(ev -> { syncParamsFromUI(); computeField(); });
        UI.slider("p").setOninput(ev -> { syncParamsFromUI(); computeField(); });
        UI.slider("nmax").setOninput(ev -> { syncParamsFromUI(); computeField(); });
        
        // Checkbox handlers
        UI.checkbox("rot").setOnchange(ev -> { syncParamsFromUI(); });
        UI.byId("showOrbits").setOnclick(ev -> { syncParamsFromUI(); });
        
        // Radio button handlers
        ((HTMLInputElement) UI.byId("wire")).setOnchange(ev -> { syncParamsFromUI(); });
        ((HTMLInputElement) UI.byId("points")).setOnchange(ev -> { syncParamsFromUI(); });
        
        // Color mode handlers
        ((HTMLInputElement) UI.byId("cmN")).setOnchange(ev -> { syncParamsFromUI(); drawLegend(); });
        ((HTMLInputElement) UI.byId("cmTau")).setOnchange(ev -> { syncParamsFromUI(); drawLegend(); });
        ((HTMLInputElement) UI.byId("cmn")).setOnchange(ev -> { syncParamsFromUI(); drawLegend(); });
        
        // Palette & Screenshot handlers
        UI.select("palette").setOnchange(ev -> { syncParamsFromUI(); initLUTs(); drawLegend(); });
        UI.byId("savePng").setOnclick(ev -> savePNG());
        UI.byId("exportLuts").setOnclick(ev -> exportLUTs());
        
        // Button handlers
        UI.byId("recompute").setOnclick(ev -> { 
            syncParamsFromUI(); 
            computeField(); 
        });
        
        // Bodies toggles
        HTMLCollection c = UI.bodyToggles();
        if (c != null) {
            for (int i = 0; i < c.getLength(); i++) {
                ((HTMLInputElement) c.item(i)).setOnchange(ev -> { computeField(); });
            }
        }
        
        // Ephemeriden laden (JSON)
        UI.byId("loadEphem").setOnclick(ev -> {
            UI.setText("status", "Loading ephemerides.json ...");
            NetUtil.loadJSON("ephemerides.json", new NetUtil.JsonCallback() {
                public void onLoad(String txt) {
                    Field.Body[] ext = NetUtil.parseBodies(txt);
                    if (ext != null && ext.length > 0) {
                        baseBodies = ext; 
                        computeField();
                        UI.setText("status", "Loaded ephemerides ✓ (" + ext.length + " bodies)");
                        System.out.println("📡 Loaded " + ext.length + " bodies from JSON");
                    } else {
                        UI.setText("status", "Invalid JSON");
                    }
                }
                public void onError(String msg) { 
                    UI.setText("status", "Error: " + msg); 
                    System.err.println("❌ Ephemerides load error: " + msg);
                }
            });
        });
    }

    static void tick() {
        clear();
        if (autoRotate) rotY += 0.006;

        // draw mesh
        if ("wire".equals(mode)) drawWire();
        else drawPoints();

        // draw bodies & orbits
        if (showOrbits) drawOrbits();
        drawBodies();

        Window.requestAnimationFrame(ts -> tick());
    }

    static void clear() {
        g.setFillStyle("rgb(10,10,12)");
        g.fillRect(0, 0, W, H);
        g.setLineWidth(0.6);
    }

    static void drawLegend() {
        for (int x = 0; x < legend.getWidth(); x++) {
            double t = x / (double) (legend.getWidth() - 1);
            String col = colormap(t);
            gLegend.setFillStyle(col);
            gLegend.fillRect(x, 0, 1, legend.getHeight());
        }
    }

    static void drawWire() {
        for (int[] tri : ico.faces) {
            int a = tri[0], b = tri[1], c = tri[2];
            drawEdgeWithIndices(a, b);
            drawEdgeWithIndices(b, c);
            drawEdgeWithIndices(c, a);
        }
    }
    
    static void drawEdgeWithIndices(int idx0, int idx1) {
        Vec3 p0 = ico.verts[idx0];
        Vec3 p1 = ico.verts[idx1];
        
        double v0 = "N".equals(colorMode) ? N[idx0] : ("TAU".equals(colorMode) ? TAU[idx0] : NIDX[idx0]);
        double v1 = "N".equals(colorMode) ? N[idx1] : ("TAU".equals(colorMode) ? TAU[idx1] : NIDX[idx1]);
        double valueAvg = 0.5 * (v0 + v1);

        double[] s0 = project(rotate(p0.cpy(), rotX, rotY));
        double[] s1 = project(rotate(p1.cpy(), rotX, rotY));
        if (s0 == null || s1 == null) return;
        
        double t = normScalar(valueAvg);
        g.setStrokeStyle(colormap(t));
        g.beginPath();
        g.moveTo(W * 0.5 + s0[0], H * 0.5 - s0[1]);
        g.lineTo(W * 0.5 + s1[0], H * 0.5 - s1[1]);
        g.stroke();
    }
    
    static void drawPoints() {
        for (int i = 0; i < ico.verts.length; i++) {
            Vec3 p = rotate(ico.verts[i].cpy(), rotX, rotY);
            double[] s = project(p);
            if (s == null) continue;
            
            double value = "N".equals(colorMode) ? N[i] : ("TAU".equals(colorMode) ? TAU[i] : NIDX[i]);
            double t = normScalar(value);
            g.setFillStyle(colormap(t));
            g.fillRect(W * 0.5 + s[0], H * 0.5 - s[1], 1.2, 1.2);
        }
    }

    // Mapping helper: normalisiert value anhand aktuell selektiertem Feld
    static double normScalar(double value) {
        if ("N".equals(colorMode)) {
            return (value - Nmin) / Math.max(1e-9, (Nmax - Nmin));
        } else if ("TAU".equals(colorMode)) {
            return (value - TAUmin) / Math.max(1e-9, (TAUmax - TAUmin));
        } else {
            return (value - NIDXmin) / Math.max(1e-9, (NIDXmax - NIDXmin));
        }
    }

    static void drawBodies() {
        Field.Body[] bodies = filteredBodies();
        for (Field.Body b : bodies) {
            Vec3 p = rotate(b.position.cpy(), rotX, rotY);
            double[] s = project(p);
            if (s == null) continue;
            int px = (int) Math.round(W * 0.5 + s[0]);
            int py = (int) Math.round(H * 0.5 - s[1]);
            
            // planet dot size by log mass scale
            double size = 4 + 12 * clamp01(Math.log10(b.massScale + 1e-9) + 6); // crude
            g.setFillStyle("rgb(245,240,210)");
            if ("Sun".equals(b.name)) g.setFillStyle("rgb(255,220,120)");
            
            g.beginPath();
            g.arc(px, py, size, 0, Math.PI * 2);
            g.fill();
        }
    }

    static void drawOrbits() {
        // Sun at center; draw circles for planets (skip Sun)
        for (int k = 0; k < orbitPts.length; k++) {
            Vec3[] pts = orbitPts[k];
            for (int i = 0; i < pts.length - 1; i++) {
                drawOrbitSegment(pts[i], pts[i + 1]);
            }
        }
    }

    static void drawOrbitSegment(Vec3 a, Vec3 b) {
        double[] s0 = project(rotate(a.cpy(), rotX, rotY));
        double[] s1 = project(rotate(b.cpy(), rotX, rotY));
        if (s0 == null || s1 == null) return;
        g.setStrokeStyle("rgba(180,180,200,0.5)");
        g.beginPath();
        g.moveTo(W * 0.5 + s0[0], H * 0.5 - s0[1]);
        g.lineTo(W * 0.5 + s1[0], H * 0.5 - s1[1]);
        g.stroke();
    }

    // --- Helpers ---
    static Vec3 rotate(Vec3 v, double rx, double ry) {
        double cy = Math.cos(rx), sy = Math.sin(rx);
        double y = v.y * cy - v.z * sy, z = v.y * sy + v.z * cy;
        v.y = y; v.z = z;
        double cx = Math.cos(ry), sx = Math.sin(ry);
        double x = v.x * cx + v.z * sx; z = -v.x * sx + v.z * cx;
        v.x = x; v.z = z;
        return v;
    }
    
    static double[] project(Vec3 v) {
        double z = camZ - v.z;
        if (z <= 1.0) return null;
        double f = scale / z;
        return new double[]{ v.x * f, v.y * f };
    }
    
    static String colormap(double t) {
        t = clamp01(t);
        int idx = (int) Math.floor(t * 255.0);
        if (idx > 255) idx = 255; // Safety clamp
        
        int[] rgb;
        switch (palette) {
            case "Viridis": rgb = lutViridis[idx]; break;
            case "Plasma":  rgb = lutPlasma[idx]; break;
            case "Greys":   rgb = lutGreys[idx]; break;
            default:        rgb = lutTurbo[idx];
        }
        return "rgb(" + rgb[0] + "," + rgb[1] + "," + rgb[2] + ")";
    }
    
    static double clamp01(double v) { 
        return v < 0 ? 0 : v > 1 ? 1 : v; 
    }
    
    // === LUT INITIALIZATION ===
    
    static void initLUTs() {
        long startTime = System.currentTimeMillis();
        
        lutTurbo = buildLUT("Turbo");
        lutViridis = buildLUT("Viridis");
        lutPlasma = buildLUT("Plasma");
        lutGreys = buildLUT("Greys");
        
        long endTime = System.currentTimeMillis();
        System.out.printf("🎨 LUTs initialized in %d ms%n", endTime - startTime);
    }
    
    static int[][] buildLUT(String name) {
        int[][] tab = new int[256][3];
        for (int i = 0; i < 256; i++) {
            double t = i / 255.0;
            int[] rgb;
            switch (name) {
                case "Viridis": rgb = cmapViridis(t); break;
                case "Plasma":  rgb = cmapPlasma(t); break;
                case "Greys":   rgb = cmapGreys(t); break;
                default:        rgb = cmapTurbo(t);
            }
            tab[i] = rgb;
        }
        return tab;
    }
    
    // === COLOR PALETTES ===
    
    static int[] cmapGreys(double t) {
        int v = (int) Math.round(255 * t);
        return new int[]{v, v, v};
    }
    
    static int[] cmapTurbo(double t) {
        // Approximation von Google Turbo – leichtgewichtige Näherung
        // Quelle: vereinfachte Poly-Fit; kompakt und flott
        double r = 34.61 + t * (1172.33 + t * (-10793.56 + t * (33300.12 + t * (-38394.49 + t * 15054.07))));
        double g = 23.31 + t * (557.33 + t * (1225.33 + t * (-3574.69 + t * (4772.99 + t * (-2110.90)))));
        double b = 27.2 + t * (321.89 + t * (1517.40 + t * (-4642.37 + t * (5930.97 + t * (-2586.66)))));
        int R = clamp255(r / 255.0), G = clamp255(g / 255.0), B = clamp255(b / 255.0);
        return new int[]{R, G, B};
    }
    
    static int[] cmapViridis(double t) {
        // Kompakte Interpolation nach viridis (annäherungsweise)
        // Anchor-Stützstellen (t, R,G,B) – minimalistisch
        double[][] A = {
            {0.0, 68, 1, 84}, {0.25, 58, 82, 139}, {0.5, 32, 144, 140},
            {0.75, 94, 201, 97}, {1.0, 253, 231, 37}
        };
        return lerpStops(A, t);
    }
    
    static int[] cmapPlasma(double t) {
        double[][] A = {
            {0.0, 13, 8, 135}, {0.25, 126, 3, 168}, {0.5, 203, 71, 119},
            {0.75, 248, 149, 64}, {1.0, 240, 249, 33}
        };
        return lerpStops(A, t);
    }
    
    static int[] lerpStops(double[][] stops, double t) {
        if (t <= 0) return new int[]{(int) stops[0][1], (int) stops[0][2], (int) stops[0][3]};
        if (t >= 1) return new int[]{(int) stops[stops.length - 1][1], (int) stops[stops.length - 1][2], (int) stops[stops.length - 1][3]};
        
        for (int i = 0; i < stops.length - 1; i++) {
            double t0 = stops[i][0], t1 = stops[i + 1][0];
            if (t >= t0 && t <= t1) {
                double u = (t - t0) / (t1 - t0);
                int r = (int) Math.round(stops[i][1] + u * (stops[i + 1][1] - stops[i][1]));
                int g = (int) Math.round(stops[i][2] + u * (stops[i + 1][2] - stops[i][2]));
                int b = (int) Math.round(stops[i][3] + u * (stops[i + 1][3] - stops[i][3]));
                return new int[]{r, g, b};
            }
        }
        return new int[]{255, 255, 255};
    }
    
    static int clamp255(double x) {
        int v = (int) Math.round(255.0 * x);
        return v < 0 ? 0 : (v > 255 ? 255 : v);
    }
    
    // === SCREENSHOT FUNCTIONALITY ===
    
    static void savePNG() {
        try {
            // HTMLCanvasElement.toDataURL() ist im TeaVM CanvasContext verfügbar
            String dataURL = canvas.toDataURL("image/png");
            
            // "künstlicher" Download-Link
            HTMLDocument doc = Window.current().getDocument();
            HTMLAnchorElement a = (HTMLAnchorElement) doc.createElement("a");
            a.setAttribute("href", dataURL);
            a.setAttribute("download", "segmented_solar_mesh.png");
            a.setStyle("display", "none");
            
            doc.getBody().appendChild(a);
            a.click();
            a.remove();
            
            System.out.println("📸 Screenshot saved: segmented_solar_mesh.png");
        } catch (Exception e) {
            System.err.println("❌ Screenshot failed: " + e.getMessage());
        }
    }
    
    // === LUT EXPORT FUNCTIONALITY ===
    
    static void exportLUTs() {
        try {
            StringBuilder json = new StringBuilder();
            json.append("{\n");
            json.append("  \"metadata\": {\n");
            json.append("    \"generator\": \"Segmented Spacetime Solar System\",\n");
            json.append("    \"version\": \"1.0\",\n");
            json.append("    \"size\": 256,\n");
            json.append("    \"format\": \"RGB\"\n");
            json.append("  },\n");
            
            // Export all palettes
            json.append("  \"palettes\": {\n");
            json.append("    \"turbo\": ").append(lutToJSON(lutTurbo)).append(",\n");
            json.append("    \"viridis\": ").append(lutToJSON(lutViridis)).append(",\n");
            json.append("    \"plasma\": ").append(lutToJSON(lutPlasma)).append(",\n");
            json.append("    \"greys\": ").append(lutToJSON(lutGreys)).append("\n");
            json.append("  }\n");
            json.append("}");
            
            // Create download
            String dataURL = "data:application/json;charset=utf-8," + 
                           Window.current().encodeURIComponent(json.toString());
            
            HTMLDocument doc = Window.current().getDocument();
            HTMLAnchorElement a = (HTMLAnchorElement) doc.createElement("a");
            a.setAttribute("href", dataURL);
            a.setAttribute("download", "segmented_spacetime_luts.json");
            a.setStyle("display", "none");
            
            doc.getBody().appendChild(a);
            a.click();
            a.remove();
            
            System.out.println("📊 LUTs exported: segmented_spacetime_luts.json");
        } catch (Exception e) {
            System.err.println("❌ LUT export failed: " + e.getMessage());
        }
    }
    
    static String lutToJSON(int[][] lut) {
        StringBuilder sb = new StringBuilder();
        sb.append("[");
        for (int i = 0; i < lut.length; i++) {
            if (i > 0) sb.append(",");
            sb.append("[").append(lut[i][0]).append(",").append(lut[i][1]).append(",").append(lut[i][2]).append("]");
        }
        sb.append("]");
        return sb.toString();
    }
}
