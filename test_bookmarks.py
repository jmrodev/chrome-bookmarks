#!/usr/bin/env python3
"""
Test Suite for Chrome Netscape Bookmark Format & Health
Validates format compliance, tag balance, clean data integrity, and zero dead/private links.
"""

import os
import re
import sys
import html
import json
import unittest
from urllib.parse import urlparse
from html.parser import HTMLParser

ORIGINAL_FILE = "/home/jmro/Documents/bookmarks_9_7_26.html"
TARGET_FILE = "/home/jmro/Documents/bookmarks_ordenados.html"

URL_REDIRECTS = {
    "https://github.com/jmrodev/coding-interview-university": "https://github.com/jwasham/coding-interview-university",
    "https://github.com/jmrodev/JavaScript30": "https://github.com/wesbos/JavaScript30",
    "https://github.com/jmrodev/awesome-interview-questions": "https://github.com/DopplerHQ/awesome-interview-questions",
    "https://github.com/jmrodev/superbook-tech-interview-handbook": "https://github.com/yangshun/tech-interview-handbook",
    "https://tabler-icons.io/": "https://tabler.io/icons",
    "http://www.lu4dq.com.ar/revistas.html": "http://www.lu4dq.com.ar/",
    "https://annas-archive.org/": "https://annas-archive.li/"
}

PURGED_URLS = {
    # Seguridad / Claves privadas
    "http://jmro.duckdns.org:8088/cgi-bin/wake?key=jmro-wake-2026",
    # Privacidad / NSFW
    "https://huggingface.co/Heartsync/NSFW-Uncensored?not-for-all-audiences=true",
    "https://undressme.ai/video",
    # Dominios caídos / DNS / 404
    "https://constana.io/dashboard/home",
    "https://github.com/jmrodev/practicas-iniciales",
    "https://www.aluracursos.com/challenges/challenge-one-logica",
    "https://pornpen.ai/getpro",
    "https://llava.hliu.cc/",
    "https://www.useblackbox.io/pricing",
    "https://github.com/jmrodev/NvChad",
    "https://github.com/jmrodev/practice-python",
    "https://github.com/jmrodev/dataStructuresAndAlgos",
    "https://github.com/jmrodev/computer-science-flash-cards",
    "https://github.com/jmrodev/code-catalog-python",
    "https://github.com/jmrodev/freecodecamp",
    "https://github.com/jmrodev/front_end_interview_questions_flashcards",
    "https://www.useblackbox.io/pricing?ref=onboarding",
    "https://helpcenter.itmplatform.com/es/project/ejemplo-de-uso-de-api-con-html-javascript/",
    "https://juanmarcelorodriguez675198.invisionapp.com/freehand/ZNQYr1QcJ?blank=",
    "https://windbasics.com/?fbclid=IwAR0eySmcXjEF-A41xl9-ICY7Zrk4U2EN9-zD_6pD80pdPyQoxYpAvIq3Wkc",
    "https://mailgolem.com/",
    "https://wiki.manjaro.org/index.php/Build_Manjaro_ISOs_with_buildiso",
    "https://whitestack.com/es/empleos/",
    "https://remotive.com/salaries",
    "https://carlosazaustre.es/cursos/reactjs-gratis",
    "https://carlosazaustre.es/cursos/programacion-javascript",
    "https://carlosazaustre.es/cursos/nodejs-gratis",
    "https://carlosazaustre.es/cursos/vue-gratis",
    "https://cssbuttons.io/switches",
    "https://beta.tome.app/",
    "https://worldtimeapi.org/pages/examples",
    "https://www.useblackbox.io/",
    "https://stsewd.dev/es/posts/neovim-installation-configuration/",
    "https://www.evaferreira.com.ar/en/education.html",
    "https://labs.openai.com/",
    "https://aprendiendo.dev/react#lessons",
    "https://www.efset.org/ef-set-50/take-test/#set50-131/result",
    "https://www.webpagetest.org/learn/lightning-fast-web-performance/#toc",
    "https://canvas.instructure.com/courses/11637553/assignments/54036652?module_item_id=128274825",
    "https://carlcheo.com/compsci",
    "https://barbaritalara.com/oportunidad-para-estudiar-full-stack-%f0%9f%9a%80%f0%9f%94%a5/",
    "https://argentinaprograma.inti.gob.ar/",
    "https://trabajosremotos.es/",
    "https://trabajosremotos.es/trabajo/ingeniero-de-soporte-audible-trabajo-remoto-5838",
    "https://www.practice-sql.com/"
}

class BookmarkValidatorParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.dl_open = 0
        self.dl_close = 0
        self.folders = []
        self.current_stack = []
        self.bookmarks = []
        self.in_h3 = False
        self.in_a = False
        self.h3_buf = []
        self.a_buf = []
        self.a_attrs = {}
        self.folder_children = {}

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        if tag == "dl":
            self.dl_open += 1
        elif tag == "h3":
            self.in_h3 = True
            self.h3_buf = []
        elif tag == "a":
            self.in_a = True
            self.a_buf = []
            self.a_attrs = attr_dict

    def handle_endtag(self, tag):
        if tag == "dl":
            self.dl_close += 1
            if self.current_stack:
                self.current_stack.pop()
        elif tag == "h3":
            self.in_h3 = False
            fname = "".join(self.h3_buf).strip()
            self.current_stack.append(fname)
            fpath = " / ".join(self.current_stack)
            self.folders.append(fpath)
            self.folder_children.setdefault(fpath, 0)
            if len(self.current_stack) > 1:
                parent_path = " / ".join(self.current_stack[:-1])
                self.folder_children[parent_path] = self.folder_children.get(parent_path, 0) + 1
        elif tag == "a":
            self.in_a = False
            title = "".join(self.a_buf).strip()
            href = self.a_attrs.get("href", "").strip()
            fpath = " / ".join(self.current_stack)
            self.bookmarks.append({
                "url": href,
                "title": title,
                "path": fpath,
                "attrs": self.a_attrs
            })
            if fpath in self.folder_children:
                self.folder_children[fpath] += 1

    def handle_data(self, data):
        if self.in_h3:
            self.h3_buf.append(data)
        elif self.in_a:
            self.a_buf.append(data)


class TestChromeBookmarkFormat(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.orig_path = ORIGINAL_FILE
        if os.path.exists("bookmarks_ordenados.html"):
            cls.target_path = "bookmarks_ordenados.html"
        else:
            cls.target_path = TARGET_FILE
        
        self_assert = unittest.TestCase()
        self_assert.assertTrue(os.path.exists(cls.target_path), f"File {cls.target_path} does not exist.")
        
        with open(cls.target_path, "r", encoding="utf-8") as f:
            cls.content = f.read()

        cls.parser = BookmarkValidatorParser()
        cls.parser.feed(cls.content)

        if os.path.exists(cls.orig_path):
            with open(cls.orig_path, "r", encoding="utf-8", errors="ignore") as f:
                orig_content = f.read()
            raw_urls = re.findall(r'HREF="([^"]+)"', orig_content, re.IGNORECASE)
            cls.orig_urls = set(html.unescape(u.strip()) for u in raw_urls if u.strip())
        else:
            cls.orig_urls = set()

    def test_01_header_and_doctype(self):
        """Regla 1: Encabezado NETSCAPE y metadatos estándar de Chrome."""
        lines = [l.strip() for l in self.content.splitlines() if l.strip()]
        self.assertEqual(lines[0], "<!DOCTYPE NETSCAPE-Bookmark-file-1>", 
                         "Debe comenzar con el Doctype oficial de Netscape Bookmark.")
        self.assertIn('<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">', self.content,
                      "Debe definir la codificación UTF-8 en el META tag.")
        self.assertIn("<TITLE>Bookmarks</TITLE>", self.content, "Debe incluir <TITLE>Bookmarks</TITLE>.")
        self.assertIn("<H1>Bookmarks</H1>", self.content, "Debe incluir encabezado <H1>Bookmarks</H1>.")

    def test_02_personal_toolbar_folder(self):
        """Regla 2: La carpeta raíz debe estar marcada como barra de herramientas de marcadores."""
        match = re.search(r'<H3[^>]*PERSONAL_TOOLBAR_FOLDER="true"[^>]*>(.*?)</H3>', self.content, re.IGNORECASE)
        self.assertIsNotNone(match, "Debe tener una carpeta con atributo PERSONAL_TOOLBAR_FOLDER='true'.")
        self.assertTrue(len(match.group(1).strip()) > 0, "El nombre de la barra de marcadores no debe estar vacío.")

    def test_03_tag_balance(self):
        """Regla 3: Balance estricto de etiquetas <DL> y </DL>."""
        dl_open = len(re.findall(r"<DL>", self.content, re.IGNORECASE))
        dl_close = len(re.findall(r"</DL>", self.content, re.IGNORECASE))
        self.assertEqual(dl_open, dl_close, f"El número de etiquetas <DL> ({dl_open}) debe ser idéntico al de </DL> ({dl_close}).")
        self.assertEqual(self.parser.dl_open, self.parser.dl_close, "El parser reporta desbalance en la pila de etiquetas <DL>.")

    def test_04_folder_definitions(self):
        """Regla 4: Toda carpeta <H3> debe abrir inmediatamente un contenedor <DL>."""
        h3_count = len(re.findall(r"<H3[^>]*>", self.content, re.IGNORECASE))
        dl_count = len(re.findall(r"<DL>", self.content, re.IGNORECASE))
        self.assertEqual(dl_count, h3_count + 1, 
                         f"Cada <H3> ({h3_count}) debe corresponder a un sub-contenedor <DL> (total esperado {h3_count + 1}, obtenido {dl_count}).")

    def test_05_no_empty_folders(self):
        """Regla 5: Ninguna carpeta creada debe quedar vacía."""
        for fpath, count in self.parser.folder_children.items():
            self.assertGreater(count, 0, f"La carpeta '{fpath}' no tiene ningún marcador o subcarpeta.")

    def test_06_purged_links_removed(self):
        """Regla 6: Los 45 enlaces caídos o depurados deben haber sido eliminados."""
        target_urls = set(b["url"] for b in self.parser.bookmarks)
        found_dead = target_urls.intersection(PURGED_URLS)
        self.assertEqual(len(found_dead), 0, f"Se encontraron enlaces no depurados: {found_dead}")

    def test_07_canonical_redirects_applied(self):
        """Regla 7: Los enlaces reparados deben apuntar a sus URLs canónicas."""
        target_urls = set(b["url"] for b in self.parser.bookmarks)
        for old_u, new_u in URL_REDIRECTS.items():
            self.assertNotIn(old_u, target_urls, f"La URL inactiva {old_u} aún se encuentra en los marcadores.")
            self.assertIn(new_u, target_urls, f"La URL canónica {new_u} debería estar presente en los marcadores.")

    def test_08_no_duplicate_urls(self):
        """Regla 8: Cero URLs duplicadas en el archivo final."""
        urls = [b["url"] for b in self.parser.bookmarks]
        unique_urls = set(urls)
        self.assertEqual(len(urls), len(unique_urls), 
                         f"Existen {len(urls) - len(unique_urls)} URLs duplicadas en el archivo generado.")
        self.assertEqual(len(unique_urls), 498, f"Se esperaban 498 enlaces únicos depurados, pero hay {len(unique_urls)}")

    def test_09_url_validity(self):
        """Regla 9: Formato y validez de los esquemas de enlace."""
        valid_schemes = {"http", "https", "chrome", "file", "data", "ftp", "javascript"}
        for b in self.parser.bookmarks:
            url = b["url"]
            parsed = urlparse(url)
            self.assertIn(parsed.scheme.lower(), valid_schemes, f"URL con esquema no soportado o inválido: {url}")
            self.assertTrue(len(b["title"]) > 0, f"Marcador con título vacío para URL: {url}")

    def test_10_attribute_integrity(self):
        """Regla 10: Conservación de atributos clave (HREF, ADD_DATE, ICON)."""
        bms_with_add_date = [b for b in self.parser.bookmarks if b["attrs"].get("add_date")]
        bms_with_icon = [b for b in self.parser.bookmarks if b["attrs"].get("icon")]
        self.assertGreater(len(bms_with_add_date), 0, "Debe preservar fechas de agregado (ADD_DATE).")
        self.assertGreater(len(bms_with_icon), 0, "Debe preservar iconos embebidos (ICON).")

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestChromeBookmarkFormat)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
