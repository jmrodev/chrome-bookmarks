# 🔖 Chrome Bookmarks Dashboard & Organizer

Un organizador, limpiador y panel interactivo para marcadores de Google Chrome, Brave, Edge y navegadores basados en Chromium.

[![Format: Netscape Bookmark](https://img.shields.io/badge/Format-Netscape_Bookmark_HTML-blue.svg)](https://en.wikipedia.org/wiki/Netscape_Bookmark_File_Format)
[![Tests: 10/10 Passing](https://img.shields.io/badge/Tests-10%2F10_Passing-brightgreen.svg)](test_bookmarks.py)
[![Bookmarks: 501 Active](https://img.shields.io/badge/Active_Bookmarks-501-success.svg)](bookmarks_ordenados.html)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

---

## ✨ Características Principales

1. **Cumplimiento Estricto del Estándar Netscape Bookmark**:
   - Totalmente compatible con la herramienta nativa de importación de Chrome (`Ctrl + Shift + O`).
   - Conserva los favicons embebidos en base64 (`ICON`), timestamps (`ADD_DATE`), y referencias exactas.
   - Pila balanceada de contenedores `<DL><p>` y carpetas `<DT><H3>`.

2. **Organización Granular en 3 Niveles Jerárquicos**:
   - **🌐 Personal y Hobbies**: Mecánica & Automotriz (ECU Peugeot), Radioafición & Telecomunicaciones (Radio Club LU4DQ), Gaming & Consolas (PS2 Homebrew), Ciencias Exactas (Matemáticas & Álgebra), Streaming y Cine.
   - **🎓 Formación y Cursos**: Alura Oracle ONE, Argentina Programa, TUDAI / TECDA (ISFD 166), Plataformas de Aprendizaje y Cursos Cloud/Datos.
   - **🤖 Inteligencia Artificial**: Asistentes y Copilotos, Utilidades y Automatización, Modelos Open, Generación Visual y Text-to-Speech.
   - **💻 Desarrollo Web & Programación**: Arquitectura & CS, Backend & Datos (Bases de Datos SQL, APIs, Node.js/JS), Frontend (React, CSS/Layouts), Retos de Código y Documentación.
   - **🛠️ Herramientas & Entornos**: Terminal, Editores (Neovim/VSCode), Git & GitHub, Redes/Túneles, Diseño & UI, Productividad.
   - **💼 Empleo y Portafolio**: Bolsas de Trabajo Tech & Remoto, Plataformas Freelance, Consultoras y Portafolio.
   - **🐧 Sistemas y Servidores**: Distribuciones Linux (Arch/Manjaro), Servidores Locales (Webmin/SSH), Ciberseguridad & Hacking Ético.
   - **👥 Creadores y Comunidad**: MiduDev, MoureDev, TodoCode, Carlos Azaustre, etc.

3. **🧹 Auditoría y Limpieza Automática de Enlaces Caídos**:
   - Detección de fallos DNS, dominios caducados, servicios discontinuados y errores HTTP 404 / 521.
   - Redirección automática de forks de GitHub eliminados a sus repositorios canónicos activos (ej. *Coding Interview University*, *JavaScript30*).
   - Consulta el informe detallado en [ENLACES_ELIMINADOS.md](ENLACES_ELIMINADOS.md).

4. **⚡ Dashboard Web Interactivo Integrado**:
   - El archivo `index.html` (o `bookmarks_ordenados.html`) se puede abrir directamente en cualquier navegador como una página web.
   - **Dark Mode Moderno**: Paleta de colores slate/azul oscura optimizada para lectura.
   - **Búsqueda Instantánea**: Filtrado reactivo en tiempo real por palabra clave o URL.
   - **Carpetas Colapsables / Acordeón**: Navegación ágil haciendo clic en cualquier categoría.

5. **🧪 Suite Automatizada de Pruebas Unitarias**:
   - 10 reglas de validación en Python (`test_bookmarks.py`) que aseguran que el archivo nunca se corrompa ni contenga enlaces caídos.

---

## 🚀 Cómo Usarlo

### 1. Importar a Google Chrome / Chromium / Brave / Edge

1. Abre tu navegador y presiona `Ctrl + Shift + O` (o navega a `chrome://bookmarks/`).
2. En la esquina superior derecha, haz clic en el menú de tres puntos (`⋮`).
3. Selecciona **Importar marcadores**.
4. Elige el archivo `bookmarks_ordenados.html`.
5. ¡Listo! Todas las carpetas y subcarpetas aparecerán organizadas en tu **Barra de Marcadores**.

### 2. Abrir como Dashboard Web Local

Simplemente haz doble clic en `bookmarks_ordenados.html` o `index.html`, o ejecútalo desde la terminal:
```bash
xdg-open bookmarks_ordenados.html
# o abre con Google Chrome:
google-chrome bookmarks_ordenados.html
```

### 3. Ejecutar las Pruebas de Validación

Para verificar la integridad del formato, balance de etiquetas y ausencia de enlaces caídos:
```bash
python3 test_bookmarks.py
```
Salida esperada:
```
test_01_header_and_doctype (__main__.TestChromeBookmarkFormat) ... ok
test_02_personal_toolbar_folder (__main__.TestChromeBookmarkFormat) ... ok
test_03_tag_balance (__main__.TestChromeBookmarkFormat) ... ok
test_04_folder_definitions (__main__.TestChromeBookmarkFormat) ... ok
test_05_no_empty_folders (__main__.TestChromeBookmarkFormat) ... ok
test_06_purged_dead_links_removed (__main__.TestChromeBookmarkFormat) ... ok
test_07_canonical_redirects_applied (__main__.TestChromeBookmarkFormat) ... ok
test_08_no_duplicate_urls (__main__.TestChromeBookmarkFormat) ... ok
test_09_url_validity (__main__.TestChromeBookmarkFormat) ... ok
test_10_attribute_integrity (__main__.TestChromeBookmarkFormat) ... ok

----------------------------------------------------------------------
Ran 10 tests in 0.046s

OK
```

### 4. Regenerar o Personalizar Marcadores

Si deseas modificar las reglas de clasificación o agregar nuevas exclusiones:
1. Edita `generate_bookmarks.py`.
2. Ejecuta:
```bash
python3 generate_bookmarks.py
```

---

## 📁 Estructura del Repositorio

```
chrome-bookmarks/
├── bookmarks_ordenados.html  # Archivo Netscape HTML listo para importar en Chrome
├── index.html                # Versión interactiva para Dashboard Web / GitHub Pages
├── generate_bookmarks.py     # Script generador, clasificador y limpiador
├── test_bookmarks.py         # Suite de pruebas unitarias (10 validaciones)
├── ENLACES_ELIMINADOS.md     # Informe detallado de los 49 enlaces caídos auditados
├── .github/
│   └── workflows/
│       └── test.yml          # GitHub Actions CI para validación continua
├── .gitignore
└── README.md
```

---

## 🛡️ Auditoría y Seguridad

- Las URLs de redes locales (`192.168.x.x`) y paneles de administración privada se conservan y se mantienen aisladas bajo la categoría de *Sistemas y Servidores*.
- Todos los marcadores han sido verificados contra inyecciones de código y desbalance de tags.
