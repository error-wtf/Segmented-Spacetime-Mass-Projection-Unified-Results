# SSZ Suite — Papers Integration Complete

## ✅ Status: DEPLOYMENT-READY

Alle Validation Papers und theoretischen Dokumente sind jetzt im Repository gebundelt.

---

## 📁 Struktur

### Validation Papers (`papers/validation/`)

**10 Dateien, ~593 KB** - Observational papers zur Validierung

- G79.29+0.46 Papers (4 papers + dataset description)
- Cygnus X Papers (2 papers + dataset description)
- SSZ Application (1 paper)
- Combined manifest + README

### Theory Papers (`docs/theory/`)

**20 Dateien, ~380 KB** - SSZ theoretical foundation

- Core Framework (3 papers)
- Mathematical Foundations (4 papers)
- Physical Implications (3 papers)
- Advanced Topics (3 papers)
- Temporal Analysis (3 papers)
- Implementation & Verification (3 papers)
- Reference (1 paper) + README

---

## 🔧 Configuration - Automatic Path Resolution

```python
from SSZ.segwave import load_sources_config

config = load_sources_config()
# Returns: {'base_dir': '/path/to/repo/papers/validation', 
#           'exists': True, 'source': 'repo_bundled'}
```

### Priority Order

1. `SSZ_SOURCES_DIR` environment variable (highest)
2. `papers/validation/` (bundled in repo) ← **DEFAULT**
3. External Windows path (fallback)
4. External Linux/WSL path (fallback)

---

## 🚀 Deployment Benefits

✅ **Self-Contained** - No external dependencies  
✅ **Offline-Capable** - All papers included  
✅ **Version-Controlled** - Git-tracked references  
✅ **Reproducible** - Complete research environment  
✅ **Cross-Platform** - Works on Windows/Linux/WSL

---

## 📚 Usage

Papers are automatically discoverable after installation:

```bash
# Install
.\install.ps1  # Windows
./install.sh   # Linux

# Papers location auto-resolved
python -c "from SSZ.segwave import load_sources_config; print(load_sources_config())"
```

See `papers/validation/README.md` and `docs/theory/README.md` for details.

---

**Total Size:** ~973 KB scientific literature  
**Files:** 30 papers + 5 README/manifests  
**License:** ANTI-CAPITALIST SOFTWARE LICENSE v1.4

**Copyright © 2025**  
Carmen Wrede und Lino Casu
