package com.lino.sss;

import org.teavm.jso.browser.Window;
import org.teavm.jso.dom.html.*;

/**
 * UI-Hilfsfunktionen für DOM-Zugriff via TeaVM.
 * Vereinfacht den Zugriff auf HTML-Elemente und deren Werte.
 */
public final class UI {
    
    private static HTMLDocument doc() { 
        return Window.current().getDocument(); 
    }

    /**
     * Holt ein Slider-Element (input[type="range"]) nach ID.
     */
    public static HTMLInputElement slider(String id) { 
        return (HTMLInputElement) doc().getElementById(id); 
    }
    
    /**
     * Holt ein Checkbox-Element (input[type="checkbox"]) nach ID.
     */
    public static HTMLInputElement checkbox(String id) { 
        return (HTMLInputElement) doc().getElementById(id); 
    }
    
    /**
     * Holt ein beliebiges HTML-Element nach ID.
     */
    public static HTMLElement span(String id) { 
        return (HTMLElement) doc().getElementById(id); 
    }
    
    /**
     * Alias für span() - holt beliebiges Element nach ID.
     */
    public static HTMLElement byId(String id) { 
        return (HTMLElement) doc().getElementById(id); 
    }

    /**
     * Liest den numerischen Wert eines Sliders aus.
     * 
     * @param id Element-ID des Sliders
     * @return Slider-Wert als double, oder 0.0 bei Fehler
     */
    public static double sliderVal(String id) {
        HTMLInputElement element = slider(id);
        if (element == null) return 0.0;
        
        try { 
            return Double.parseDouble(element.getValue()); 
        } catch (Exception e) { 
            return 0.0; 
        }
    }
    
    /**
     * Setzt den Text-Inhalt eines Elements.
     * 
     * @param id Element-ID
     * @param text Neuer Text-Inhalt
     */
    public static void setText(String id, String text) { 
        HTMLElement element = span(id);
        if (element != null) {
            element.setInnerHTML(text); 
        }
    }

    /**
     * Prüft, ob eine Checkbox aktiviert ist.
     * 
     * @param id Checkbox-ID
     * @return true wenn aktiviert, false sonst
     */
    public static boolean isChecked(String id) { 
        HTMLInputElement element = checkbox(id);
        return element != null && element.isChecked(); 
    }

    /**
     * Holt alle Body-Toggle-Checkboxen (class="bodyToggle").
     * 
     * @return HTMLCollection der Body-Toggle-Elemente
     */
    public static HTMLCollection bodyToggles() {
        HTMLElement controlsElement = (HTMLElement) doc().getElementById("controls");
        if (controlsElement != null) {
            return controlsElement.getElementsByClassName("bodyToggle");
        }
        return null;
    }
    
    /**
     * Setzt den Wert eines Sliders programmatisch.
     * 
     * @param id Slider-ID
     * @param value Neuer Wert
     */
    public static void setSliderValue(String id, double value) {
        HTMLInputElement element = slider(id);
        if (element != null) {
            element.setValue(String.valueOf(value));
        }
    }
    
    /**
     * Aktiviert/deaktiviert eine Checkbox programmatisch.
     * 
     * @param id Checkbox-ID
     * @param checked Neuer Zustand
     */
    public static void setChecked(String id, boolean checked) {
        HTMLInputElement element = checkbox(id);
        if (element != null) {
            element.setChecked(checked);
        }
    }
    
    /**
     * Prüft, ob ein Radio-Button aktiviert ist.
     * 
     * @param id Radio-Button-ID
     * @return true wenn aktiviert
     */
    public static boolean isRadioSelected(String id) {
        HTMLInputElement element = (HTMLInputElement) byId(id);
        return element != null && element.isChecked();
    }
    
    /**
     * Holt den Wert eines Text-Input-Elements.
     * 
     * @param id Input-ID
     * @return Text-Wert oder leerer String
     */
    public static String getInputValue(String id) {
        HTMLInputElement element = (HTMLInputElement) byId(id);
        return element != null ? element.getValue() : "";
    }
    
    /**
     * Holt ein Select-Element nach ID.
     * 
     * @param id Select-Element-ID
     * @return HTMLSelectElement oder null
     */
    public static HTMLSelectElement select(String id) { 
        return (HTMLSelectElement) byId(id); 
    }
    
    /**
     * Holt den ausgewählten Wert eines Select-Elements.
     * 
     * @param id Select-Element-ID
     * @return Ausgewählter Wert oder leerer String
     */
    public static String selectVal(String id) {
        HTMLSelectElement s = select(id);
        return s != null ? s.getValue() : "";
    }
}
