#!/usr/bin/env python3
import os
import time
import html
import json
from html.parser import HTMLParser

INPUT_FILE = "/home/jmro/Documents/bookmarks_9_7_26.html"
OUTPUT_FILE = "/home/jmro/Documents/bookmarks_ordenados.html"
PROJECT_OUTPUT_FILE = "/home/jmro/Documents/chrome-bookmarks/index.html"
PROJECT_BM_FILE = "/home/jmro/Documents/chrome-bookmarks/bookmarks_ordenados.html"
REPORT_FILE = "/home/jmro/Documents/chrome-bookmarks/ENLACES_ELIMINADOS.md"

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
    "https://constana.io/dashboard/home": "DNS no resuelve / Dominio inactivo",
    "https://github.com/jmrodev/practicas-iniciales": "HTTP 404 (Repositorio eliminado)",
    "https://www.aluracursos.com/challenges/challenge-one-logica": "HTTP 404 (Página eliminada)",
    "https://pornpen.ai/getpro": "DNS no resuelve / Servicio inactivo",
    "https://llava.hliu.cc/": "DNS no resuelve / Servidor caído",
    "https://www.useblackbox.io/pricing": "HTTP 404",
    "https://github.com/jmrodev/NvChad": "HTTP 404 (Fork eliminado; se conserva el repo oficial NvChad)",
    "https://github.com/jmrodev/practice-python": "HTTP 404 (Repositorio eliminado)",
    "https://github.com/jmrodev/dataStructuresAndAlgos": "HTTP 404 (Repositorio eliminado)",
    "https://github.com/jmrodev/computer-science-flash-cards": "HTTP 404 (Repositorio eliminado)",
    "https://github.com/jmrodev/code-catalog-python": "HTTP 404 (Repositorio eliminado)",
    "https://github.com/jmrodev/freecodecamp": "HTTP 404 (Repositorio eliminado)",
    "https://github.com/jmrodev/front_end_interview_questions_flashcards": "HTTP 404 (Repositorio eliminado)",
    "https://www.useblackbox.io/pricing?ref=onboarding": "HTTP 404",
    "https://helpcenter.itmplatform.com/es/project/ejemplo-de-uso-de-api-con-html-javascript/": "HTTP 404",
    "https://juanmarcelorodriguez675198.invisionapp.com/freehand/ZNQYr1QcJ?blank=": "DNS no resuelve / InVision Freehand cerrado",
    "https://windbasics.com/?fbclid=IwAR0eySmcXjEF-A41xl9-ICY7Zrk4U2EN9-zD_6pD80pdPyQoxYpAvIq3Wkc": "DNS no resuelve",
    "https://mailgolem.com/": "HTTP 521 (Servidor caído)",
    "https://wiki.manjaro.org/index.php/Build_Manjaro_ISOs_with_buildiso": "HTTP 404 (Artículo removido del wiki)",
    "https://whitestack.com/es/empleos/": "HTTP 404",
    "https://remotive.com/salaries": "HTTP 404",
    "https://carlosazaustre.es/cursos/reactjs-gratis": "HTTP 404 (Cursos reestructurados)",
    "https://carlosazaustre.es/cursos/programacion-javascript": "HTTP 404 (Cursos reestructurados)",
    "https://carlosazaustre.es/cursos/nodejs-gratis": "HTTP 404 (Cursos reestructurados)",
    "https://carlosazaustre.es/cursos/vue-gratis": "HTTP 404 (Cursos reestructurados)",
    "https://cssbuttons.io/switches": "HTTP 404",
    "https://beta.tome.app/": "HTTP 404",
    "https://worldtimeapi.org/pages/examples": "Timeout / Servicio inactivo",
    "https://www.useblackbox.io/": "HTTP 404",
    "https://stsewd.dev/es/posts/neovim-installation-configuration/": "HTTP 404 (Post de blog no disponible)",
    "https://www.evaferreira.com.ar/en/education.html": "HTTP 404",
    "https://labs.openai.com/": "DNS no resuelve (DALL-E 2 playground deprecado)",
    "https://aprendiendo.dev/react#lessons": "HTTP 404",
    "https://www.efset.org/ef-set-50/take-test/#set50-131/result": "HTTP 404 (Resultado expirado)",
    "https://www.webpagetest.org/learn/lightning-fast-web-performance/#toc": "HTTP 404",
    "https://canvas.instructure.com/courses/11637553/assignments/54036652?module_item_id=128274825": "HTTP 503 / Curso expirado",
    "https://carlcheo.com/compsci": "HTTP 404",
    "https://barbaritalara.com/oportunidad-para-estudiar-full-stack-%f0%9f%9a%80%f0%9f%94%a5/": "HTTP 404 (Campaña expirada)",
    "https://argentinaprograma.inti.gob.ar/": "Servidor inactivo / Programa gubernamental cerrado",
    "https://trabajosremotos.es/": "Servidor inactivo / Dominio caído",
    "https://trabajosremotos.es/trabajo/ingeniero-de-soporte-audible-trabajo-remoto-5838": "Servidor inactivo / Oferta caída",
    "https://www.practice-sql.com/": "Servidor inactivo / Dominio caído"
}

class BookmarkTreeParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.bookmarks = []
        self.in_h3 = False
        self.in_a = False
        self.cur_h3_text = []
        self.cur_a_text = []
        self.cur_a_attrs = {}

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        if tag == "h3":
            self.in_h3 = True
            self.cur_h3_text = []
        elif tag == "a":
            self.in_a = True
            self.cur_a_text = []
            self.cur_a_attrs = attr_dict
        elif tag == "dl":
            pass

    def handle_endtag(self, tag):
        if tag == "h3":
            self.in_h3 = False
            fname = "".join(self.cur_h3_text).strip()
            self.stack.append(fname)
        elif tag == "dl":
            if self.stack:
                self.stack.pop()
        elif tag == "a":
            self.in_a = False
            title = "".join(self.cur_a_text).strip()
            url = self.cur_a_attrs.get("href", "").strip()
            add_date = self.cur_a_attrs.get("add_date", "")
            icon = self.cur_a_attrs.get("icon", "")
            if url:
                self.bookmarks.append({
                    "url": url,
                    "title": title or url,
                    "add_date": add_date,
                    "icon": icon,
                    "path": list(self.stack)
                })

    def handle_data(self, data):
        if self.in_h3:
            self.cur_h3_text.append(data)
        elif self.in_a:
            self.cur_a_text.append(data)

def classify_granular_v2(b):
    url = b["url"].lower()
    title = b["title"].lower()
    orig_path = " / ".join(b.get("path", [])).lower()

    # 1. Personal, Ocio y Hobbies
    # Mecánica
    if "peugeot" in orig_path or "rocketbox" in url or "ecudata" in url:
        return ("🌐 Personal y Hobbies", "Mecánica & Automotriz", "Diagnóstico ECU y Repuestos")
    # Radioafición
    if "lu4dq" in url or "radio" in orig_path:
        return ("🌐 Personal y Hobbies", "Radioafición & Telecomunicaciones", "Revistas y Artículos LU4DQ")
    # Consolas & Retrogaming
    if "opentuna" in url or "ps2homebrew" in url:
        return ("🌐 Personal y Hobbies", "Gaming & Consolas", "PlayStation 2 Homebrew")
    # Matemáticas & Álgebra
    if "mathway" in url or "superprof" in url or "algebra" in orig_path or "matematicas" in orig_path or "ecuaciones" in url:
        return ("🌐 Personal y Hobbies", "Ciencias Exactas & Matemáticas", "Álgebra y Resolución de Ecuaciones")
    if "khanacademy.org" in url and "computing" not in url:
        return ("🌐 Personal y Hobbies", "Ciencias Exactas & Matemáticas", "Khan Academy General")
    # Streaming y Cine
    if "pelis" in orig_path or "pelis24" in url or "film-grab" in url:
        return ("🌐 Personal y Hobbies", "Streaming & Cine", "Películas y Fotogramas")
    if "iptv" in orig_path or "iptv-org" in url or "famelack" in url:
        return ("🌐 Personal y Hobbies", "Streaming & Cine", "TV en Vivo & Canales IPTV")
    if "nerdflix" in url or "youtube.com/watch?v=pnhjk1d7zlo" in url or "youtube.com/watch?v=libbhloefyy" in url or "youtube.com/watch?v=gqpj7re02ao" in url:
        return ("🌐 Personal y Hobbies", "Streaming & Cine", "Charlas, Charlas Nerd & YouTube")
    if "musicforprogramming" in url:
        return ("🌐 Personal y Hobbies", "Música & Concentración", "Ambiente para Programar")
    # Trámites & Finanzas Personales
    if "bcra.gob" in url:
        return ("🌐 Personal y Hobbies", "Finanzas & Trámites", "Consulta Crediticia CUIT/CUIL")
    if "kognise" in url or "sysarmy" in url or "cmal100" in orig_path or "roundyearfun" in url:
        return ("🌐 Personal y Hobbies", "Comunidad & Varios", "Comunidades y Proyectos Personales")

    # 2. Creadores y Comunidad
    if "midu.link" in url or "midudev" in orig_path or "midudev" in url or "midu.dev" in url or "midudev" in title:
        return ("👥 Creadores y Comunidad", "Desarrollo Web", "MiduDev")
    if "mouredev" in orig_path or "mouredev" in url or "moure.dev" in url or "mouredev" in title:
        return ("👥 Creadores y Comunidad", "Desarrollo Web", "MoureDev")
    if "azaustre" in orig_path or "azaustre" in url or "carlos azaustre" in title:
        return ("👥 Creadores y Comunidad", "Desarrollo Web", "Carlos Azaustre")
    if "todocode" in orig_path or "todocode" in url or "todocode" in title:
        return ("👥 Creadores y Comunidad", "Desarrollo Web", "TodoCode")
    if "coben" in url or "coben" in title or "wesbos" in url or "evaferreira" in url:
        return ("👥 Creadores y Comunidad", "Desarrollo Web", "Otros Creadores Dev")

    # 3. Formación y Cursos
    if "alura" in orig_path or "alura" in url or "oracle-one" in orig_path or "oracle one" in title:
        return ("🎓 Formación y Cursos", "Institucional & Bootcamps", "Alura - Oracle ONE")
    if "argentina-programa" in orig_path or "argentina programa" in title or "argentinaprograma" in url or "mumuki.io/argentina-programa" in url or "argentinaprograma.utn" in url:
        return ("🎓 Formación y Cursos", "Institucional & Bootcamps", "Argentina Programa")
    if "tudai" in orig_path or "tecda" in orig_path or "edi2" in orig_path or "inst_166" in url or "instituto 166" in title or "isfd166" in url:
        return ("🎓 Formación y Cursos", "Institucional & Bootcamps", "TUDAI y TECDA (ISFD 166)")
    if "propuesta de trabajo practico" in orig_path or "bezkoder.com/angular" in url or "inezpre5.wordpress" in url or "justdigital.agency" in url:
        return ("🎓 Formación y Cursos", "Proyectos Prácticos", "Spring Boot, JWT & Angular")
    if "arduino" in orig_path or "arduino" in title:
        return ("🎓 Formación y Cursos", "Hardware & Arduino", "Tutoriales y Recursos")
    if ("freecodecamp" in url or "theodinproject" in url or "scrimba" in url or "claseflix" in url or 
        "alkemy" in url or "elementsofai" in url or "fullstackopen" in url or "campusmaxiprograma" in url or 
        "barbaritalara" in url):
        return ("🎓 Formación y Cursos", "Plataformas de Aprendizaje", "Rutas y Bootcamps Web")
    if ("desafiolatam" in url or "learn.microsoft.com" in url or "coursera" in url or 
        "netacad.com" in url or "cognitiveclass.ai" in url or "aprendiendo.dev" in url or 
        "datacamp" in url or "cursos" in orig_path or "certificados" in orig_path or 
        "cobol" in title or "kubernetes de novato a pro" in title or "developer.android.com" in url or 
        "colab.research.google.com" in url or "cessi" in orig_path or "learndigital.withgoogle" in url or 
        "opensource.googleblog.com/2022/11/explore-new-learn" in url):
        return ("🎓 Formación y Cursos", "Cursos & Certificaciones", "Cloud, Datos y Certificaciones")

    # 4. Inteligencia Artificial
    if "elevenlabs" in url or "luvvoice" in url or "ttsmaker" in url or "testtospeech" in orig_path:
        return ("🤖 Inteligencia Artificial", "Multimedia y Voz", "Text-to-Speech & Audio")
    if "uncensored" in orig_path or "nsfw" in url or "undressme" in url:
        return ("🤖 Inteligencia Artificial", "Modelos & Experimentación", "Modelos Open / No Censurados")
    if "dall·e" in title or "labs.openai" in url or "ideogram" in url or "tome.app" in url or "vectorizer" in url or "escribelo" in url:
        return ("🤖 Inteligencia Artificial", "Multimedia y Voz", "Generación Visual & Creativa")
    if "notebooklm" in url or "aistudio" in url or "gemini" in url or "phind" in url or "llava" in url or "openai" in url:
        return ("🤖 Inteligencia Artificial", "Asistentes y Copilotos", "Chatbots & Asistentes Generales")
    if "codegpt" in url or "copilot" in url or "blackbox" in url or "jules.google" in url or "ecc" in url:
        return ("🤖 Inteligencia Artificial", "Asistentes y Copilotos", "Copilotos para Programación")
    if ("googleia" in orig_path or "ai" in orig_path or "ia" in orig_path or 
        "herramientas de ia" in title or "xmind.ai" in url or "markmap" in url or 
        "durable.co" in url or "ai2sql" in url or "excelformulabot" in url or 
        "botpress" in url or "flow" in url or "huggingface" in url or "vanna.ai" in url):
        return ("🤖 Inteligencia Artificial", "Herramientas de Productividad", "Utilidades y Automatización")

    # 5. Sistemas, Servidores y Seguridad
    if ("server" in orig_path or "192.168." in url or "webmin" in title or "usermin" in title or 
        "phpmyadmin" in title or "localhost" in url or "openssh" in title or "redeszone" in url):
        return ("🐧 Sistemas y Servidores", "Servidores y Redes", "Administración Local (Webmin/SSH)")
    if ("archlinux" in orig_path or "archlinux" in url or "manjaro" in url or "prebuild iso" in orig_path or 
        "recuperacion sistema" in orig_path or "linux-apps" in url or "terminaldelinux" in url or 
        "baeldung.com/linux" in url):
        return ("🐧 Sistemas y Servidores", "Linux & Entornos", "Distribuciones y ArchWiki")
    if ("hacking" in orig_path or "pentest" in url or "pentest" in title or "hack4u" in url or 
        "hack the box" in title or "cybermap" in url or "s4vitar" in url or "infosecmachines" in url):
        return ("🐧 Sistemas y Servidores", "Seguridad Informática", "Ciberseguridad & Hacking Ético")

    # 6. Empleo, Freelance y Portafolio
    if ("upwork" in url or "freelancer" in url or "fiverr" in url or "guru.com" in url or 
        "peopleperhour" in url or "toptal" in url or "aquent" in url):
        return ("💼 Empleo y Portafolio", "Oportunidades de Empleo", "Plataformas Freelance")
    if ("whitestack" in url or "nisum" in url or "masglobal" in url or "ensitech" in url or "it-talent" in url):
        return ("💼 Empleo y Portafolio", "Oportunidades de Empleo", "Empresas & Consultoras IT")
    if "portafolio" in url or "portafolio" in title or "kit de empleabilidad" in title or "kickresume" in url or "portfolio" in url:
        return ("💼 Empleo y Portafolio", "Desarrollo Profesional", "Portafolio, CV & Carrera")
    if ("getonbrd" in url or "remoteok" in url or "weworkremotely" in url or "flexjobs" in url or 
        "remote.co" in url or "workingnomads" in url or "dice.com" in url or "ziprecruiter" in url or 
        "indeed" in url or "simplyhired" in url or "virtualvocations" in url or "chumijobs" in url or 
        "hireline" in url or "bumeran" in url or "computrabajo" in url or "zonajobs" in url or 
        "web de trabajos" in orig_path or "empleo" in title or "linkedin.com/feed" in url or "linkedin.com/jobs" in url):
        return ("💼 Empleo y Portafolio", "Oportunidades de Empleo", "Bolsas Tech & Remoto")

    # 7. Desarrollo Web & Programación
    # Databases & SQL
    if ("sql" in orig_path or "sql" in url or "dbs" in orig_path or "sqlite" in title or 
        "database" in title or "mysql" in title or "sqlbolt" in url or "sqlzoo" in url or 
        "datalemur" in url or "drawdb" in url or "postgres.new" in url or "yepcode" in url):
        return ("💻 Desarrollo Web & Programación", "Backend y Datos", "Bases de Datos & SQL")
    # APIs & Mocking
    if ("api" in orig_path or "api" in title or "apis" in orig_path or "json-server" in url or 
        "jsonplaceholder" in url or "pokeapi" in url or "crudcrud" in url or "sandapi" in url or 
        "quicktype" in url or "ajv.js" in url or "apidog" in url or "clearbit" in url or "twitter developer" in title):
        return ("💻 Desarrollo Web & Programación", "Backend y Datos", "APIs, Mocking & Schemas")
    # Node.js & Javascript
    if ("js" in orig_path or "javascript" in title or "javascript" in url or 
        "entornos js" in orig_path or "node" in orig_path or "jwt" in title or 
        "pythontutor" in url or "clean-code" in url or "nodejsera" in url or 
        "digitalocean.com/community/tutorials/how-to-create-a-web-server-in-node" in url or 
        "javascript.info" in url or "dev.to/fernandochata" in url or "asabeneh/30-days" in url or 
        "elvisduru" in url or "mytinerary" in url or "configuroweb" in url):
        return ("💻 Desarrollo Web & Programación", "Backend y Datos", "JavaScript & Node.js")

    # Arquitectura & Computer Science
    if ("path-to-senior" in url or "build-your-own-x" in url or "every-programmer-should-know" in url or 
        "carlcheo.com" in url or "datastructur.es" in url or "system-design-primer" in url or 
        "awesome-design-patterns" in url or "learnxinyminutes" in url or "khanacademy.org/computing" in url or 
        "visualgo" in url or "jsv9000" in url or "lightbot" in url):
        return ("💻 Desarrollo Web & Programación", "Arquitectura & CS", "Patrones, Estructuras & Roadmaps")

    # Coding Challenges
    if ("cssbattle" in url or "frontendmentor" in url or "devchallenges" in url or 
        "acefrontend" in url or "codier" in url or "codewell" in url or 
        "frontloops" in url or "100dayscss" in url or "dailyui" in url or 
        "codepen.io/challenges" in url or "coding-interview" in url or 
        "interview" in url or "challenge" in url or "flash-cards" in url or 
        "leetcode" in url or "hackerrank" in url or "exercism" in url or "adventjs" in url or "pruebastecnicas" in url):
        return ("💻 Desarrollo Web & Programación", "Práctica y Aprendizaje", "Retos de Código & Prácticas")

    # Rendimiento
    if "webpagetest" in url or "gtmetrix" in url or "bundlephobia" in url or "packagephobia" in url or "perf.link" in url or "cruxvis" in url:
        return ("💻 Desarrollo Web & Programación", "Recursos y Referencia", "Rendimiento & Optimización Web")
    # Docs & Cheatsheets
    if ("devdocs" in url or "overapi" in url or "cheatsheet" in url or "caniuse" in url or 
        "mdn" in url or "developer.mozilla" in url or "lenguajehtml" in url or "lenguajejs" in url or 
        "lenguajecss" in url or "docs.angular" in url or "cncf" in url or "codeguide" in url or 
        "caninclude" in url):
        return ("💻 Desarrollo Web & Programación", "Recursos y Referencia", "Documentación & Cheatsheets")
    # Blogs
    if ("smashingmagazine" in url or "davidwalsh" in url or "sitepoint" in url or 
        "alistapart" in url or "scotch.io" in url or "9lessons" in url or 
        "geeksforgeeks" in url or "tutsplus" in url or "texto tecnico" in orig_path or 
        "freecodecamp.org/news/regular-expressions" in url):
        return ("💻 Desarrollo Web & Programación", "Recursos y Referencia", "Blogs & Publicaciones Dev")

    # Frontend
    if "react" in orig_path or "react" in title or "reactjs" in url or "angular" in title or "flowbite" in url or "ant.design" in url:
        return ("💻 Desarrollo Web & Programación", "Frontend", "React & Frameworks")
    if ("css" in orig_path or "css" in title or "flexbox" in title or "grid" in title or 
        "material design" in title or "htmlrev" in url or "freefrontend" in url or 
        "buttons" in url or "switch" in url or "menu" in url or "layout" in url or 
        "projectwallace" in url or "startbootstrap" in url or "comeau" in url):
        return ("💻 Desarrollo Web & Programación", "Frontend", "HTML, CSS & Layouts")

    # 8. Herramientas, Entorno & Diseño
    if ("photopea" in url or "colorspace" in url or "mycolor.space" in url or "coolsymbol" in url or 
        "symbl.cc" in url or "1001freefonts" in url or "unsplash" in url or "pexels" in url or 
        "spritegen" in url or "thegoodlineheight" in url or "uigoodies" in url or 
        "carbon.now.sh" in url or "figma" in url or "adhamdannaway" in url or 
        "shots.so" in url or "tabler-icons" in url or "tabler.io" in url or "pngegg" in url or "picsum" in url or 
        "uidesigndaily" in url or "invision" in url or "looka" in url):
        return ("🛠️ Herramientas & Entornos", "Diseño & Multimedia", "Iconos, Fuentes & UI")
    if "squoosh" in url or "compressor.io" in url or "remove.bg" in url or "unscreen" in url or "123apps" in url or "tinywow" in url or "smash" in url or "vidyard" in url:
        return ("🛠️ Herramientas & Entornos", "Diseño & Multimedia", "Compresión & Medios")
    if ("netlify" in url or "render.com" in url or "fly.io" in url or "railway" in url or 
        "northflank" in url or "stackblitz" in url or "codi.link" in url or "glitch" in url):
        return ("🛠️ Herramientas & Entornos", "Desarrollo & Terminal", "Cloud, Deploy & Playgrounds")
    if ("neovim" in orig_path or "nvchad" in url or "vscode" in title or "zsh" in url or 
        "dotfiles" in url or "filisantillan" in url or "safjan" in url or "enhancd" in url or 
        "awesomerank" in url or "linuxfacil" in url):
        return ("🛠️ Herramientas & Entornos", "Desarrollo & Terminal", "Editores, Terminal & Shell")
    if "git" in orig_path or "proyectos-seguidos" in orig_path or "github education" in orig_path or "gist.github" in url:
        return ("🛠️ Herramientas & Entornos", "Desarrollo & Terminal", "Git & GitHub")
    if "ngrok" in url or "localtunnel" in url or "resend.com/webhooks" in url or "cual-es-mi-ip" in url or "web-check" in url:
        return ("🛠️ Herramientas & Entornos", "Desarrollo & Terminal", "Redes, Túneles & Webhooks")
    if "software gestion" in orig_path or "tryton" in url or "facturascripts" in url or "kmymoney" in url or "informaticatandil" in url:
        return ("🛠️ Herramientas & Entornos", "Productividad & Gestión", "Software de Gestión & Finanzas")
    if "notion" in url or "prezi" in url or "paperme" in url or "novel.sh" in url:
        return ("🛠️ Herramientas & Entornos", "Productividad & Gestión", "Notas, Docs & Presentaciones")
    if "temp-mail" in url or "mailgolem" in url:
        return ("🛠️ Herramientas & Entornos", "Productividad & Gestión", "Correos Temporales")
    if "annas-archive" in url or "freedium" in url:
        return ("🛠️ Herramientas & Entornos", "Productividad & Gestión", "Libros & Artículos")
    if ("deepl" in url or "buscador.net" in url or "kudobox" in url or "windbasics" in url or 
        "spring" in url or "cdnjs" in url or "flags" in url or "alfred.camera" in url):
        return ("🛠️ Herramientas & Entornos", "Productividad & Gestión", "Utilidades Web & Búsqueda")

    return ("🛠️ Herramientas & Entornos", "Productividad & Gestión", "Utilidades Web & Búsqueda")

def generate():
    with open(INPUT_FILE, "r", encoding="utf-8", errors="ignore") as f:
        parser = BookmarkTreeParser()
        parser.feed(f.read())

    print(f"Total raw bookmarks parsed: {len(parser.bookmarks)}")

    purged_report_items = []
    unique_bms = {}

    for b in parser.bookmarks:
        url = b["url"].strip()
        if not url:
            continue
        
        # Check if purged
        if url in PURGED_URLS:
            purged_report_items.append({
                "title": b["title"],
                "url": url,
                "reason": PURGED_URLS[url],
                "path": b.get("path", [])
            })
            continue

        # Check if redirected / repaired
        if url in URL_REDIRECTS:
            b["url"] = URL_REDIRECTS[url]
            url = b["url"]
            if "jmrodev/" in b["title"]:
                b["title"] = b["title"].replace("jmrodev/", "")

        if url not in unique_bms:
            unique_bms[url] = b
        else:
            existing = unique_bms[url]
            if not existing.get("icon") and b.get("icon"):
                existing["icon"] = b["icon"]
            if not existing.get("add_date") and b.get("add_date"):
                existing["add_date"] = b["add_date"]
            if len(b.get("path", [])) > len(existing.get("path", [])):
                existing["path"] = b["path"]

    total_clean = len(unique_bms)
    print(f"Total clean unique bookmarks: {total_clean}")

    # Group into Arbitrary Depth Tree
    tree = {}
    for b in unique_bms.values():
        parts = classify_granular_v2(b)
        curr = tree
        for p in parts[:-1]:
            curr = curr.setdefault(p, {})
        curr.setdefault(parts[-1], []).append(b)

    now_ts = str(int(time.time()))

    interactive_enhancements = """<style>
  :root {
    --bg: #0b0f19;
    --card: #151d30;
    --card-border: #1e293b;
    --text: #f1f5f9;
    --text-muted: #94a3b8;
    --accent: #38bdf8;
    --accent-hover: #7dd3fc;
    --folder-bg: #1e293b;
    --folder-hover: #334155;
  }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    background-color: var(--bg);
    color: var(--text);
    padding: 2rem 1rem;
    max-width: 1200px;
    margin: 0 auto;
    line-height: 1.5;
  }
  .dashboard-header {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    padding: 1.5rem;
    border-radius: 12px;
    border: 1px solid var(--card-border);
    margin-bottom: 2rem;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
  }
  h1 { margin: 0; font-size: 1.8rem; color: var(--accent); display: flex; align-items: center; gap: 0.5rem; }
  .search-box {
    flex: 1;
    max-width: 400px;
    padding: 0.7rem 1rem;
    border-radius: 8px;
    border: 1px solid var(--card-border);
    background: #0f172a;
    color: var(--text);
    font-size: 0.95rem;
    outline: none;
    transition: border-color 0.2s;
  }
  .search-box:focus { border-color: var(--accent); }
  .stats-badge {
    background: #0369a1;
    color: white;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
  }
  dl { margin: 0; padding-left: 1.4rem; }
  dt { margin: 0.25rem 0; }
  dt h3 {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: var(--folder-bg);
    padding: 0.4rem 0.85rem;
    border-radius: 8px;
    margin: 0.35rem 0;
    cursor: pointer;
    font-size: 0.96rem;
    font-weight: 600;
    color: var(--text);
    border: 1px solid var(--card-border);
    transition: all 0.2s ease;
    user-select: none;
  }
  dt h3:hover {
    background: var(--folder-hover);
    color: var(--accent);
    transform: translateX(2px);
  }
  dt h3::before {
    content: "▾";
    font-size: 0.85rem;
    color: var(--accent);
    transition: transform 0.2s;
  }
  dt h3.collapsed::before {
    content: "▸";
  }
  dt h3.collapsed + dl {
    display: none;
  }
  a {
    color: #93c5fd;
    text-decoration: none;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    transition: all 0.15s ease;
    font-size: 0.92rem;
  }
  a:hover {
    background: #1e293b;
    color: var(--accent-hover);
    text-decoration: underline;
  }
</style>
<script>
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("dt > h3").forEach(h3 => {
    h3.addEventListener("click", () => {
      h3.classList.toggle("collapsed");
    });
  });

  const searchInput = document.getElementById("bookmark-search");
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      const q = e.target.value.toLowerCase().trim();
      const allLinks = document.querySelectorAll("dt > a");
      if (!q) {
        allLinks.forEach(a => a.parentElement.style.display = "");
        document.querySelectorAll("dt > h3").forEach(h3 => {
          h3.parentElement.style.display = "";
          h3.classList.remove("collapsed");
        });
        return;
      }
      allLinks.forEach(a => {
        const text = a.textContent.toLowerCase();
        const href = a.getAttribute("href").toLowerCase();
        a.parentElement.style.display = (text.includes(q) || href.includes(q)) ? "" : "none";
      });
      document.querySelectorAll("dt > h3").forEach(h3 => h3.classList.remove("collapsed"));
    });
  }
});
</script>"""

    header_markup = f"""<div class="dashboard-header">
  <h1>🔖 Mis Marcadores</h1>
  <input type="text" id="bookmark-search" class="search-box" placeholder="🔍 Buscar entre {total_clean} marcadores o temas...">
  <span class="stats-badge">{total_clean} enlaces limpios y ordenados</span>
</div>"""

    lines = [
        "<!DOCTYPE NETSCAPE-Bookmark-file-1>",
        "<!-- This is an automatically generated file.",
        "     It will be read and overwritten.",
        "     DO NOT EDIT! -->",
        '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">',
        "<TITLE>Bookmarks</TITLE>",
        interactive_enhancements,
        "<H1>Bookmarks</H1>",
        header_markup,
        "<DL><p>",
        f'    <DT><H3 ADD_DATE="{now_ts}" LAST_MODIFIED="{now_ts}" PERSONAL_TOOLBAR_FOLDER="true">Barra de marcadores</H3>',
        "    <DL><p>"
    ]

    def render_subtree(node, depth):
        indent = "    " * depth
        if isinstance(node, dict):
            for name in sorted(node.keys()):
                lines.append(f'{indent}<DT><H3 ADD_DATE="{now_ts}">{html.escape(name)}</H3>')
                lines.append(f'{indent}<DL><p>')
                render_subtree(node[name], depth + 1)
                lines.append(f'{indent}</DL><p>')
        elif isinstance(node, list):
            for b in sorted(node, key=lambda x: x["title"].lower()):
                safe_url = html.escape(b["url"], quote=True)
                safe_title = html.escape(b["title"], quote=False)
                attrs = [f'HREF="{safe_url}"']
                if b.get("add_date"):
                    attrs.append(f'ADD_DATE="{html.escape(b["add_date"], quote=True)}"')
                if b.get("icon"):
                    attrs.append(f'ICON="{html.escape(b["icon"], quote=True)}"')
                attr_str = " ".join(attrs)
                lines.append(f'{indent}<DT><A {attr_str}>{safe_title}</A>')

    render_subtree(tree, 2)

    lines.append("    </DL><p>")
    lines.append("</DL><p>")
    lines.append("")

    html_content = "\n".join(lines)

    # Write target files
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated successfully: {OUTPUT_FILE}")

    os.makedirs(os.path.dirname(PROJECT_OUTPUT_FILE), exist_ok=True)
    with open(PROJECT_OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)
    with open(PROJECT_BM_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Copied to project repo: {PROJECT_OUTPUT_FILE} & {PROJECT_BM_FILE}")

    # Write report of removed & repaired links
    report_lines = [
        "# 📋 Auditoría y Limpieza de Enlaces Caídos",
        "",
        f"Informe generado automáticamente tras auditar los **543 marcadores** únicos de la exportación original.",
        "",
        "## Resumen Ejecutivo",
        f"- **Enlaces Activos Conservados:** {total_clean}",
        f"- **Enlaces Redireccionados a Fuentes Oficiales:** {len(URL_REDIRECTS)}",
        f"- **Enlaces Caídos Depurados / Eliminados:** {len(PURGED_URLS)}",
        "",
        "---",
        "",
        "## 🔄 Enlaces Reparados / Redirigidos a Fuentes Oficiales",
        "",
        "Los siguientes marcadores apuntaban a forks personales eliminados o dominios que cambiaron su URL oficial. Se actualizaron al repositorio canónico o URL activa:",
        "",
        "| Título / Recurso | URL Original (Inactiva) | URL Actualizada (Activa) |",
        "| :--- | :--- | :--- |",
    ]

    TITLES_MAP = {
        "https://github.com/jmrodev/coding-interview-university": "Coding Interview University",
        "https://github.com/jmrodev/JavaScript30": "JavaScript 30 (Wes Bos)",
        "https://github.com/jmrodev/awesome-interview-questions": "Awesome Interview Questions",
        "https://github.com/jmrodev/superbook-tech-interview-handbook": "Tech Interview Handbook",
        "https://tabler-icons.io/": "Tabler Icons (Oficial)",
        "http://www.lu4dq.com.ar/revistas.html": "Radio Club LU4DQ Delta Quebec",
        "https://annas-archive.org/": "Anna's Archive (Espejo activo)"
    }
    for orig_u, canon_u in URL_REDIRECTS.items():
        t = TITLES_MAP.get(orig_u, orig_u)
        report_lines.append(f"| **{t}** | `{orig_u}` | [{canon_u}]({canon_u}) |")

    report_lines.extend([
        "",
        "---",
        "",
        "## ❌ Enlaces Caídos Depurados (Eliminados)",
        "",
        "Los siguientes enlaces fueron confirmados como inaccesibles (errores DNS, dominios dados de baja, HTTP 404 definitivos o servidores inactivos) y han sido depurados de la colección final:",
        "",
        "| # | Título | Motivo de Baja | URL |",
        "| :-: | :--- | :--- | :--- |"
    ])

    seen_purged = set()
    p_idx = 1
    for p_item in purged_report_items:
        u = p_item["url"]
        if u in seen_purged:
            continue
        seen_purged.add(u)
        title = p_item["title"].replace("|", "-")
        reason = p_item["reason"]
        report_lines.append(f"| {p_idx} | {title} | `{reason}` | `{u}` |")
        p_idx += 1

    for u, r in PURGED_URLS.items():
        if u not in seen_purged:
            seen_purged.add(u)
            report_lines.append(f"| {p_idx} | {u} | `{r}` | `{u}` |")
            p_idx += 1

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines) + "\n")
    print(f"Report written to: {REPORT_FILE}")

if __name__ == "__main__":
    generate()
