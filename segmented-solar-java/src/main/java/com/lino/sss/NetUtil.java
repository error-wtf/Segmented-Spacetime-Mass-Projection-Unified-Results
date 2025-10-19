package com.lino.sss;

import org.teavm.jso.ajax.XMLHttpRequest;
import org.teavm.jso.core.JSArray;
import org.teavm.jso.core.JSObject;
import org.teavm.jso.core.JSObjects;

/**
 * Netzwerk-Utilities für JSON-Laden via TeaVM XMLHttpRequest.
 * Ermöglicht das Laden externer Ephemeriden-Daten zur Laufzeit.
 */
public final class NetUtil {
    
    /**
     * Callback-Interface für asynchrone JSON-Requests.
     */
    public interface JsonCallback { 
        /**
         * Wird aufgerufen bei erfolgreichem Laden der JSON-Daten.
         * 
         * @param jsonText Der geladene JSON-String
         */
        void onLoad(String jsonText); 
        
        /**
         * Wird aufgerufen bei Fehlern beim Laden.
         * 
         * @param errorMessage Fehlerbeschreibung
         */
        void onError(String errorMessage); 
    }

    /**
     * Lädt JSON-Daten von einer URL asynchron.
     * 
     * @param url URL der JSON-Datei
     * @param callback Callback für Erfolg/Fehler
     */
    public static void loadJSON(String url, JsonCallback callback) {
        XMLHttpRequest xhr = XMLHttpRequest.create();
        
        xhr.open("GET", url);
        xhr.setOnreadystatechange(() -> {
            if (xhr.getReadyState() == 4) { // DONE
                if (xhr.getStatus() == 200) {
                    callback.onLoad(xhr.getResponseText());
                } else {
                    callback.onError("HTTP " + xhr.getStatus() + ": " + xhr.getStatusText());
                }
            }
        });
        
        // Timeout setzen (10 Sekunden)
        xhr.setTimeout(10000);
        xhr.setOntimeout(() -> {
            callback.onError("Request timeout");
        });
        
        xhr.setOnerror(() -> {
            callback.onError("Network error");
        });
        
        try {
            xhr.send();
        } catch (Exception e) {
            callback.onError("Failed to send request: " + e.getMessage());
        }
    }

    /**
     * Parst JSON-Array von Himmelskörpern zu Field.Body Array.
     * 
     * Erwartetes JSON-Format:
     * [
     *   {
     *     "name": "Earth",
     *     "x": 1.0, "y": 0.0, "z": 0.0,
     *     "Mscale": 0.000003,
     *     "r0": 0.0000426,
     *     "rNb": 0.0002,
     *     "delta": 0.00004
     *   },
     *   ...
     * ]
     * 
     * @param jsonText JSON-String
     * @return Array von Field.Body Objekten, oder null bei Fehler
     */
    public static Field.Body[] parseBodies(String jsonText) {
        try {
            JSObject parsed = JSObjects.parse(jsonText);
            
            if (!(parsed instanceof JSArray)) {
                System.err.println("JSON is not an array");
                return null;
            }
            
            JSArray<?> jsonArray = (JSArray<?>) parsed;
            int length = jsonArray.getLength();
            Field.Body[] bodies = new Field.Body[length];
            
            for (int i = 0; i < length; i++) {
                JSObject bodyObj = (JSObject) jsonArray.get(i);
                
                // Pflichtfelder
                String name = getStringProperty(bodyObj, "name", "Unknown");
                double x = getNumberProperty(bodyObj, "x", 0.0);
                double y = getNumberProperty(bodyObj, "y", 0.0);
                double z = getNumberProperty(bodyObj, "z", 0.0);
                double massScale = getNumberProperty(bodyObj, "Mscale", 0.000001);
                
                // Optionale Felder mit Defaults
                double gamma = getNumberProperty(bodyObj, "gamma", 1.0);
                double r0 = getNumberProperty(bodyObj, "r0", 0.001);
                double rNb = getNumberProperty(bodyObj, "rNb", 0.01);
                double delta = getNumberProperty(bodyObj, "delta", 0.002);
                
                bodies[i] = new Field.Body(
                    name,
                    new Vec3(x, y, z),
                    massScale,
                    gamma,
                    r0,
                    rNb,
                    delta
                );
            }
            
            return bodies;
            
        } catch (Exception e) {
            System.err.println("Error parsing JSON: " + e.getMessage());
            return null;
        }
    }
    
    /**
     * Hilfsfunktion: Holt String-Property aus JSObject.
     */
    private static String getStringProperty(JSObject obj, String key, String defaultValue) {
        try {
            JSObject prop = JSObjects.get(obj, key);
            return prop != null ? prop.stringValue() : defaultValue;
        } catch (Exception e) {
            return defaultValue;
        }
    }
    
    /**
     * Hilfsfunktion: Holt Number-Property aus JSObject.
     */
    private static double getNumberProperty(JSObject obj, String key, double defaultValue) {
        try {
            JSObject prop = JSObjects.get(obj, key);
            return prop != null ? prop.asNumber() : defaultValue;
        } catch (Exception e) {
            return defaultValue;
        }
    }
    
    /**
     * Erstellt Beispiel-JSON für Ephemeriden (Demo-Zwecke).
     * 
     * @return JSON-String mit Beispiel-Himmelskörpern
     */
    public static String createSampleEphemerides() {
        return "[\n" +
               "  {\n" +
               "    \"name\": \"Sun\",\n" +
               "    \"x\": 0.0, \"y\": 0.0, \"z\": 0.0,\n" +
               "    \"Mscale\": 1.0,\n" +
               "    \"gamma\": 1.0,\n" +
               "    \"r0\": 0.00465,\n" +
               "    \"rNb\": 0.025,\n" +
               "    \"delta\": 0.005\n" +
               "  },\n" +
               "  {\n" +
               "    \"name\": \"Earth\",\n" +
               "    \"x\": 0.96, \"y\": 0.28, \"z\": 0.00,\n" +
               "    \"Mscale\": 0.000003,\n" +
               "    \"gamma\": 1.0,\n" +
               "    \"r0\": 0.0000426,\n" +
               "    \"rNb\": 0.0002,\n" +
               "    \"delta\": 0.00004\n" +
               "  },\n" +
               "  {\n" +
               "    \"name\": \"Jupiter\",\n" +
               "    \"x\": 5.12, \"y\": 0.88, \"z\": -0.03,\n" +
               "    \"Mscale\": 0.000954,\n" +
               "    \"gamma\": 1.0,\n" +
               "    \"r0\": 0.000477,\n" +
               "    \"rNb\": 0.003,\n" +
               "    \"delta\": 0.0006\n" +
               "  }\n" +
               "]";
    }
    
    /**
     * Lädt Ephemeriden-Daten und führt Callback mit geparsten Bodies aus.
     * 
     * @param url URL der Ephemeriden-JSON-Datei
     * @param callback Callback für erfolgreiche Body-Erstellung
     * @param errorCallback Callback für Fehler
     */
    public static void loadEphemerides(String url, 
                                     EphemeridesCallback callback,
                                     JsonCallback errorCallback) {
        loadJSON(url, new JsonCallback() {
            @Override
            public void onLoad(String jsonText) {
                Field.Body[] bodies = parseBodies(jsonText);
                if (bodies != null && bodies.length > 0) {
                    callback.onBodiesLoaded(bodies);
                } else {
                    errorCallback.onError("Failed to parse ephemerides JSON");
                }
            }
            
            @Override
            public void onError(String errorMessage) {
                errorCallback.onError(errorMessage);
            }
        });
    }
    
    /**
     * Callback-Interface für erfolgreich geladene Ephemeriden.
     */
    public interface EphemeridesCallback {
        /**
         * Wird aufgerufen wenn Himmelskörper erfolgreich geladen wurden.
         * 
         * @param bodies Array der geladenen Himmelskörper
         */
        void onBodiesLoaded(Field.Body[] bodies);
    }
}
