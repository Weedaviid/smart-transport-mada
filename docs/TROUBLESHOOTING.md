# 🔧 Guide de dépannage - TransMad

Guide complet pour résoudre les problèmes courants du projet TransMad.

---

## 📋 Table des matières

1. [Erreur: `_build_segments` not defined](#erreur-_build_segments-not-defined)
2. [Le serveur ne démarre pas](#le-serveur-ne-démarre-pas)
3. [La carte ne s'affiche pas](#la-carte-ne-saffiche-pas)
4. [Les présets ne fonctionnent pas](#les-présets-ne-fonctionnent-pas)
5. [Erreur 500 sur /api/find-route](#erreur-500-sur-apifind-route)
6. [CSS non chargé](#css-non-chargé)
7. [JavaScript non exécuté](#javascript-non-exécuté)

---

## 🐛 Problèmes courants

### Erreur: `_build_segments` not defined

**Symptômes:**
```
NameError: name '_build_segments' is not defined
File "E:\project\source\app.py", line 129
```

**Cause:**
La fonction `_build_segments()` était appelée mais pas déclarée avec `def`.

**Solution:** ✅ **CORRIGÉ dans la version actuelle**

Le problème était à la ligne ~453 de `app.py`:

❌ **AVANT:**
```python
    return jsonify(journey)


    segments = []  # Pas de "def" !
    for i in range(len(path) - 1):
        # ...
```

✅ **APRÈS (corrigé):**
```python
    return jsonify(journey)


def _build_segments(path):
    """
    Construit les segments d'un trajet à partir d'un chemin
    """
    segments = []
    for i in range(len(path) - 1):
        # ...
```

**Vérification:**
```powershell
# Tester l'API
$body = @{ start = "Analakely"; end = "Ivandry"; optimization = "distance" } | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:5000/api/find-route" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
# Devrait retourner JSON avec "segments": [...]
```

---

### Le serveur ne démarre pas

**Symptômes:**
- Message "Python was not found"
- Erreur "No module named 'flask'"
- Port déjà utilisé

**Solutions:**

#### Problème 1: Python non trouvé

```powershell
# Vérifier Python
py --version

# Si erreur, installer Python 3.7+
# https://www.python.org/downloads/
```

#### Problème 2: Flask non installé

```powershell
# Installer les dépendances
pip install flask flask-cors

# Ou utiliser requirements.txt
pip install -r requirements.txt
```

#### Problème 3: Port 5000 déjà utilisé

```powershell
# Arrêter les processus Python existants
Get-Process -Name python, py -ErrorAction SilentlyContinue | Stop-Process -Force

# Attendre 2 secondes
Start-Sleep -Seconds 2

# Relancer le serveur
py source/app.py
```

**Vérification:**
```
✓ Serving Flask app 'app'
✓ Debug mode: on
✓ Running on http://127.0.0.1:5000
```

---

### La carte ne s'affiche pas

**Symptômes:**
- Zone blanche/grise à la place de la carte
- Message "Leaflet is not defined" dans la console (F12)

**Solutions:**

#### Vérifier Leaflet chargé

1. Ouvrir **F12** → Onglet **Console**
2. Chercher erreur: `Uncaught ReferenceError: L is not defined`

**Solution:** Vérifier dans `templates/index.html`:

```html
<!-- Leaflet CSS -->
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />

<!-- Leaflet JS (AVANT app.js) -->
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<!-- App.js -->
<script src="{{ url_for('static', filename='js/app.js') }}"></script>
```

⚠️ **Important:** Leaflet doit être chargé **AVANT** `app.js`

#### Vérifier la connexion internet

Leaflet est chargé depuis un CDN (unpkg.com). Sans internet, la carte ne s'affiche pas.

**Solution offline:** Télécharger Leaflet localement:
```powershell
# Créer dossier
New-Item -Path "static/libs/leaflet" -ItemType Directory -Force

# Télécharger et extraire Leaflet 1.9.4
# https://leafletjs.com/download.html
```

Modifier `index.html`:
```html
<link rel="stylesheet" href="{{ url_for('static', filename='libs/leaflet/leaflet.css') }}" />
<script src="{{ url_for('static', filename='libs/leaflet/leaflet.js') }}"></script>
```

---

### Les présets ne fonctionnent pas

**Symptômes:**
- Cliquer un preset ne fait rien
- Les champs ne se remplissent pas

**Solutions:**

#### Vérifier la console JavaScript

1. **F12** → **Console**
2. Chercher: `Uncaught TypeError: Cannot read property 'dataset' of null`

**Cause:** Événements non attachés

**Solution:** Dans `static/js/app.js`, vérifier:

```javascript
// Les présets doivent être définis
const PRESETS = {
  'analakely-ivandry': { start: 'Analakely', end: 'Ivandry' },
  // ...
};

// Les listeners doivent être attachés
function attachEventListeners() {
  // ...
  
  // Présets
  document.querySelectorAll('.preset-btn').forEach(btn => {
    btn.addEventListener('click', selectPreset);
  });
}
```

#### Vérifier les boutons HTML

Dans `templates/index.html`:
```html
<button class="preset-btn" data-preset="analakely-ivandry">
  🔄 Analakely → Ivandry
</button>
```

⚠️ Attribut `data-preset` doit correspondre aux clés dans `PRESETS`

---

### Erreur 500 sur /api/find-route

**Symptômes:**
```
127.0.0.1 - - [Date] "POST /api/find-route HTTP/1.1" 500 -
```

**Causes possibles:**

#### 1. Fonction manquante (comme `_build_segments`)

**Vérifier les logs Flask** dans le terminal:
```
NameError: name 'some_function' is not defined
```

**Solution:** Déclarer la fonction manquante

#### 2. Localité inexistante

**Erreur:**
```python
AttributeError: 'NoneType' object has no attribute 'name'
```

**Cause:** `graph.get_node(name)` retourne `None`

**Solution:** Vérifier les noms de localités dans `database.py`:
```python
LOCALITIES = {
    'Analakely': {'latitude': -18.8829, 'longitude': 47.5241},
    'Ivandry': {'latitude': -18.8769, 'longitude': 47.5544},
    # ... 8 autres localités
}
```

**Noms exacts (sensibles à la casse):**
- Analakely
- Ivandry
- Plateau Haute-Ville
- Andohalo
- Ambohiditra
- Anjary
- Anosibe
- Tsimahafotsy
- Betongitra
- Antsorohavola

#### 3. JSON mal formé

**Erreur:**
```
400 Bad Request: The browser (or proxy) sent a request that this server could not understand.
```

**Solution:** Vérifier le format JSON:
```javascript
// Correct
fetch('/api/find-route', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    start: 'Analakely',
    end: 'Ivandry',
    optimization: 'distance'
  })
});
```

---

### CSS non chargé

**Symptômes:**
- Page sans style (texte brut)
- Boutons non colorés

**Solutions:**

#### Vérifier le chemin CSS

**F12** → **Network** → Chercher `style.css`

Status:
- **200**: ✅ Fichier chargé
- **404**: ❌ Fichier non trouvé

**Solution pour 404:**

Vérifier dans `index.html`:
```html
<!-- CORRECT -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">

<!-- INCORRECT -->
<link rel="stylesheet" href="E:\project\static\css\style.css">
<link rel="stylesheet" href="/css/style.css">
```

#### Vérifier la structure des dossiers

```
E:\project\
├── static\
│   └── css\
│       └── style.css  ← Doit exister ici
└── templates\
    └── index.html
```

#### Forcer le rechargement

Navigateur peut avoir mis en cache un ancien CSS:

**Solution:** 
- **Ctrl+F5** (Windows) ou **Cmd+Shift+R** (Mac)
- Ou vider le cache: **F12** → **Application** → **Clear storage**

---

### JavaScript non exécuté

**Symptômes:**
- Boutons ne réagissent pas
- Console vide (pas de logs)

**Solutions:**

#### Vérifier les erreurs de syntaxe

**F12** → **Console** → Chercher:
```
Uncaught SyntaxError: Unexpected token
```

**Causes courantes:**
- Virgule manquante dans objet JSON
- Parenthèse/accolade non fermée
- Guillemets non échappés

#### Vérifier le chargement

**F12** → **Network** → Chercher `app.js`

**Status 404:** Le fichier n'est pas trouvé

**Solution:**
```html
<!-- Correct -->
<script src="{{ url_for('static', filename='js/app.js') }}"></script>

<!-- Ordre important: Leaflet AVANT app.js -->
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="{{ url_for('static', filename='js/app.js') }}"></script>
```

#### Vérifier l'initialisation

Dans `app.js`, vérifier que l'initialisation se fait au chargement:

```javascript
// À la fin du fichier
document.addEventListener('DOMContentLoaded', () => {
  loadLocalities();
  attachEventListeners();
});
```

---

## 🔍 Outils de diagnostic

### 1. Console navigateur (F12)

**Onglets importants:**
- **Console**: Erreurs JavaScript
- **Network**: Fichiers chargés (CSS/JS/API)
- **Elements**: HTML généré

### 2. Logs Flask

Terminal où tourne `py source/app.py`:
```
127.0.0.1 - - [09/Mar/2026 13:36:07] "POST /api/find-route HTTP/1.1" 500 -
Traceback (most recent call last):
  File "app.py", line 129
    NameError: name '_build_segments' is not defined
```

### 3. Tester API manuellement

```powershell
# Health check
Invoke-WebRequest -Uri "http://localhost:5000/api/health" -UseBasicParsing

# Liste des localités
Invoke-WebRequest -Uri "http://localhost:5000/api/localities" -UseBasicParsing

# Trajet
$body = @{ start = "Analakely"; end = "Ivandry"; optimization = "distance" } | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:5000/api/find-route" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
```

---

## 📝 Checklist de vérification

Avant de signaler un bug, vérifier:

- [ ] Python 3.7+ installé (`py --version`)
- [ ] Flask installé (`pip list | Select-String flask`)
- [ ] Serveur lancé (`py source/app.py`)
- [ ] Message "Running on http://127.0.0.1:5000" visible
- [ ] API health répond: `http://localhost:5000/api/health`
- [ ] Aucune erreur dans console (F12)
- [ ] CSS chargé (F12 → Network → style.css → Status 200)
- [ ] JS chargé (F12 → Network → app.js → Status 200)
- [ ] Leaflet chargé (F12 → Console → taper `L` → doit afficher objet)

---

## 🚀 Redémarrage complet

Si tout échoue, procédure complète:

```powershell
# 1. Aller dans le dossier
cd E:\project

# 2. Arrêter tous les serveurs
Get-Process -Name python, py -ErrorAction SilentlyContinue | Stop-Process -Force

# 3. Vérifier les dépendances
pip install -r requirements.txt

# 4. Vider cache navigateur
# Ouvrir navigateur → Ctrl+Shift+Del → Tout supprimer

# 5. Relancer serveur
py source/app.py

# 6. Attendre le message
# ✓ Running on http://127.0.0.1:5000

# 7. Ouvrir dans navigateur
start http://localhost:5000

# 8. F5 pour rafraîchir (forcer: Ctrl+F5)
```

---

## 📞 Support

Si le problème persiste:

1. **Copier les logs d'erreur** du terminal Flask
2. **Copier les erreurs de console** (F12 → Console)
3. **Vérifier la version Python**: `py --version`
4. **Vérifier les dépendances**: `pip list`

---

**TransMad Troubleshooting Guide** - Résolvez tous vos problèmes! 🔧
