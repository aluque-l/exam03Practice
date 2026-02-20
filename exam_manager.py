#!/usr/bin/env python3
"""
exam_manager.py — Simulador de examen Rank03 para la Escuela 42.
Uso:
    python exam_manager.py start   → Asigna un ejercicio aleatorio
    python exam_manager.py grade   → Corrige el ejercicio actual
    python exam_manager.py status  → Muestra el ejercicio activo
    python exam_manager.py reset   → Reinicia sin cambiar de ejercicio
"""

import os
import subprocess
import shutil
import sys
import random
import json
import time

# ─── RUTAS ────────────────────────────────────────────────────────────────────

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
SOLUTIONS_DIR = os.path.join(BASE_DIR, "solutions")
SUBJECTS_DIR  = os.path.join(BASE_DIR, "subjects")
RENDU_DIR     = os.path.join(BASE_DIR, "rendu")
STATE_FILE    = os.path.join(BASE_DIR, ".current_ex")
TMP_DIR       = os.path.join(BASE_DIR, ".tmp")

# ─── COLORES ANSI ─────────────────────────────────────────────────────────────

class C:
    RED    = "\033[91m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    BLUE   = "\033[94m"
    PURPLE = "\033[95m"
    CYAN   = "\033[96m"
    BOLD   = "\033[1m"
    RESET  = "\033[0m"

def red(s):    return f"{C.RED}{s}{C.RESET}"
def green(s):  return f"{C.GREEN}{s}{C.RESET}"
def yellow(s): return f"{C.YELLOW}{s}{C.RESET}"
def blue(s):   return f"{C.BLUE}{s}{C.RESET}"
def purple(s): return f"{C.PURPLE}{s}{C.RESET}"
def bold(s):   return f"{C.BOLD}{s}{C.RESET}"

# ─── CONFIGURACIÓN DE EJERCICIOS ──────────────────────────────────────────────

EXAMS = {
    "broken_GNL": {
        "files":        ["get_next_line.c"],
        "ref_file":     "broken_GNL.c",
        "is_program":   False,
        "buffer_sizes": [1, 5, 32, 1024, 9999],
        "tests": [
            {"stdin": "Hola\n42\nEscuela\n",                "name": "Básico"},
            {"stdin": "Linea sin salto final",              "name": "EOF sin newline"},
            {"stdin": "\n\n\n",                             "name": "Solo saltos de línea"},
            {"stdin": "",                                   "name": "Entrada vacía"},
            {"stdin": "A" * 2000 + "\n" + "B" * 2000,      "name": "Líneas muy largas"},
            {"stdin": "uno\ndos\ntres\ncuatro\ncinco\n",    "name": "Múltiples líneas"},
        ],
    },
    "filter": {
        "files":      ["filter.c"],
        "ref_file":   "filter.c",
        "is_program": True,
        "extra_flags": ["-D_GNU_SOURCE"],
        "tests": [
            {"args": ["abc"],   "stdin": "abcdefaaaabcdeabcabcdabc\n", "desc": "Subject 1"},
            {"args": ["ababc"], "stdin": "ababcabababc\n",              "desc": "Subject 2"},
            {"args": ["a"],     "stdin": "aaaaa\n",                    "desc": "Repetición simple"},
            {"args": [" "],     "stdin": "hola mundo \n",              "desc": "Patrón con espacio"},
            {"args": ["xyz"],   "stdin": "abcdefgh\n",                 "desc": "Sin coincidencias"},
            {"args": ["ab"],    "stdin": "ab",                         "desc": "EOF sin newline"},
            {"args": [],        "exit": 1,                             "desc": "Sin argumentos"},
            {"args": [""],      "exit": 1,                             "desc": "Argumento vacío"},
            {"args": ["a","b"], "exit": 1,                             "desc": "Demasiados argumentos"},
        ],
    },
    "n_queens": {
        "files":      ["n_queens.c"],
        "ref_file":   "nqueens.c",
        "is_program": True,
        "sort":       True,
        "tests": [
            {"args": ["1"], "desc": "n=1"},
            {"args": ["2"], "desc": "n=2 (sin solución)"},
            {"args": ["4"], "desc": "n=4"},
            {"args": ["6"], "desc": "n=6"},
            {"args": ["8"], "desc": "n=8"},
        ],
    },
    "permutations": {
        "files":      ["permutations.c"],
        "ref_file":   "permutations.c",
        "is_program": True,
        "sort":       False,   # El output ya debe estar ordenado
        "tests": [
            {"args": ["a"],    "desc": "Un carácter"},
            {"args": ["ab"],   "desc": "Dos caracteres"},
            {"args": ["abc"],  "desc": "Tres caracteres"},
            {"args": ["dcba"], "desc": "Cuatro caracteres (desordenado)"},
            {"args": ["123"],  "desc": "Dígitos"},
        ],
    },
    "powerset": {
        "files":      ["powerset.c"],
        "ref_file":   "powerset.c",
        "is_program": True,
        "sort":       True,
        "tests": [
            {"args": ["5", "1", "2", "3", "4", "5"],                  "desc": "Subject básico"},
            {"args": ["3", "1", "0", "2", "4", "5", "3"],             "desc": "Subject con cero"},
            {"args": ["0", "1", "-1"],                                 "desc": "Target 0 con negativos"},
            {"args": ["12", "5", "2", "1", "8", "4", "3", "7", "11"], "desc": "Subject grande"},
            {"args": ["7", "3", "8", "2"],                            "desc": "Sin solución"},
            {"args": ["0", "0"],                                       "desc": "Subconjunto vacío"},
        ],
    },
    "rip": {
        "files":      ["rip.c"],
        "ref_file":   "rip.c",
        "is_program": True,
        "sort":       True,
        "tests": [
            {"args": ["(()"],         "desc": "Subject 1"},
            {"args": ["()())()"],     "desc": "Subject 2"},
            {"args": ["(()(()(" ],    "desc": "Subject 3"},
            {"args": ["((()()())())"],"desc": "Ya balanceado"},
            {"args": ["((("],         "desc": "Solo abre"},
            {"args": [")))"],         "desc": "Solo cierra"},
        ],
    },
    "ft_scanf": {
        "files":      ["ft_scanf.c"],
        "ref_file":   "scanf.c",
        "is_program": False,
        "is_scanf":   True,
        # Cada test define:
        #   format → string de formato pasado a ft_scanf
        #   stdin  → input que leerá ft_scanf
        #   desc   → descripción del test
        #   vars   → lista de {type, name}
        #            tipos: "int", "char", "str" (char[256])
        "tests": [
            # ── %c básico ────────────────────────────────────────────────────
            {"desc": "%c lee un carácter",
             "format": "%c", "stdin": "A\n",
             "vars": [{"type": "char", "name": "c"}]},
            {"desc": "%c no salta espacios",
             "format": "%c", "stdin": " A\n",
             "vars": [{"type": "char", "name": "c"}]},
            {"desc": "%c lee espacio como carácter",
             "format": "%c", "stdin": "  \n",
             "vars": [{"type": "char", "name": "c"}]},
            {"desc": "dos %c consecutivos",
             "format": "%c%c", "stdin": "AB\n",
             "vars": [{"type": "char", "name": "c1"}, {"type": "char", "name": "c2"}]},
            {"desc": "%c en EOF devuelve EOF",
             "format": "%c", "stdin": "",
             "vars": [{"type": "char", "name": "c"}]},
            # ── %d básico ────────────────────────────────────────────────────
            {"desc": "%d entero positivo",
             "format": "%d", "stdin": "42\n",
             "vars": [{"type": "int", "name": "n"}]},
            {"desc": "%d entero negativo",
             "format": "%d", "stdin": "-7\n",
             "vars": [{"type": "int", "name": "n"}]},
            {"desc": "%d con signo +",
             "format": "%d", "stdin": "+15\n",
             "vars": [{"type": "int", "name": "n"}]},
            {"desc": "%d salta espacios previos",
             "format": "%d", "stdin": "   99\n",
             "vars": [{"type": "int", "name": "n"}]},
            {"desc": "%d cero",
             "format": "%d", "stdin": "0\n",
             "vars": [{"type": "int", "name": "n"}]},
            {"desc": "%d falla con letra → retorna 0",
             "format": "%d", "stdin": "abc\n",
             "vars": [{"type": "int", "name": "n"}]},
            {"desc": "%d número seguido de letra",
             "format": "%d", "stdin": "42abc\n",
             "vars": [{"type": "int", "name": "n"}]},
            {"desc": "%d en EOF devuelve EOF",
             "format": "%d", "stdin": "",
             "vars": [{"type": "int", "name": "n"}]},
            # ── %s básico ────────────────────────────────────────────────────
            {"desc": "%s palabra simple",
             "format": "%s", "stdin": "hola\n",
             "vars": [{"type": "str", "name": "s"}]},
            {"desc": "%s salta espacios previos",
             "format": "%s", "stdin": "   mundo\n",
             "vars": [{"type": "str", "name": "s"}]},
            {"desc": "%s para en espacio",
             "format": "%s", "stdin": "hola mundo\n",
             "vars": [{"type": "str", "name": "s"}]},
            {"desc": "%s en EOF devuelve EOF",
             "format": "%s", "stdin": "",
             "vars": [{"type": "str", "name": "s"}]},
            {"desc": "%s solo espacios devuelve 0",
             "format": "%s", "stdin": "   ",
             "vars": [{"type": "str", "name": "s"}]},
            # ── combinaciones ────────────────────────────────────────────────
            {"desc": "%d %s combinados",
             "format": "%d %s", "stdin": "42 hola\n",
             "vars": [{"type": "int", "name": "n"}, {"type": "str", "name": "s"}]},
            {"desc": "%s %d combinados",
             "format": "%s %d", "stdin": "hola 42\n",
             "vars": [{"type": "str", "name": "s"}, {"type": "int", "name": "n"}]},
            {"desc": "%d %d dos enteros",
             "format": "%d %d", "stdin": "10 20\n",
             "vars": [{"type": "int", "name": "a"}, {"type": "int", "name": "b"}]},
            {"desc": "%c %d carácter y entero",
             "format": "%c %d", "stdin": "A 99\n",
             "vars": [{"type": "char", "name": "c"}, {"type": "int", "name": "n"}]},
            {"desc": "%d %c entero y carácter",
             "format": "%d %c", "stdin": "5 X\n",
             "vars": [{"type": "int", "name": "n"}, {"type": "char", "name": "c"}]},
            {"desc": "%s %s dos palabras",
             "format": "%s %s", "stdin": "foo bar\n",
             "vars": [{"type": "str", "name": "a"}, {"type": "str", "name": "b"}]},
            {"desc": "%d %s %c tres conversiones",
             "format": "%d %s %c", "stdin": "7 test Z\n",
             "vars": [{"type": "int",  "name": "n"},
                      {"type": "str",  "name": "s"},
                      {"type": "char", "name": "c"}]},
            # ── literales en formato ──────────────────────────────────────────
            {"desc": "literal entre conversiones",
             "format": "%d-%d", "stdin": "3-7\n",
             "vars": [{"type": "int", "name": "a"}, {"type": "int", "name": "b"}]},
            {"desc": "literal no coincide → para",
             "format": "%d-%d", "stdin": "3x7\n",
             "vars": [{"type": "int", "name": "a"}, {"type": "int", "name": "b"}]},
            # ── segunda conversión falla ──────────────────────────────────────
            {"desc": "primera OK segunda falla → retorna 1",
             "format": "%d %d", "stdin": "42 abc\n",
             "vars": [{"type": "int", "name": "a"}, {"type": "int", "name": "b"}]},
            {"desc": "primera falla → retorna 0",
             "format": "%d %s", "stdin": "abc hola\n",
             "vars": [{"type": "int", "name": "n"}, {"type": "str", "name": "s"}]},
            # ── espacios en formato ───────────────────────────────────────────
            {"desc": "espacio en formato consume múltiples espacios",
             "format": "%d %d", "stdin": "1    2\n",
             "vars": [{"type": "int", "name": "a"}, {"type": "int", "name": "b"}]},
            {"desc": "espacio en formato consume tabs",
             "format": "%d %d", "stdin": "1\t2\n",
             "vars": [{"type": "int", "name": "a"}, {"type": "int", "name": "b"}]},
            # ── valores extremos ─────────────────────────────────────────────
            {"desc": "%d INT_MAX",
             "format": "%d", "stdin": "2147483647\n",
             "vars": [{"type": "int", "name": "n"}]},
            {"desc": "%d número grande negativo",
             "format": "%d", "stdin": "-2147483648\n",
             "vars": [{"type": "int", "name": "n"}]},
        ],
    },
}

# ─── NIVELES ──────────────────────────────────────────────────────────────────

LEVELS = {
    "lvl1": ["broken_GNL", "filter", "ft_scanf"],
    "lvl2": ["n_queens", "permutations", "powerset", "rip"],
}

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def ensure_dirs():
    os.makedirs(TMP_DIR, exist_ok=True)
    os.makedirs(SOLUTIONS_DIR, exist_ok=True)
    os.makedirs(SUBJECTS_DIR, exist_ok=True)
    os.makedirs(RENDU_DIR, exist_ok=True)

def tmp(name):
    return os.path.join(TMP_DIR, name)

def load_state():
    """Devuelve dict {ex, graded} o None si no hay estado."""
    if not os.path.exists(STATE_FILE):
        return None
    with open(STATE_FILE) as f:
        try:
            return json.load(f)
        except (json.JSONDecodeError, ValueError):
            # Compatibilidad con formato antiguo (texto plano)
            raw = f.read().strip()
            return {"ex": raw, "graded": False} if raw else None

def save_state(ex, graded=False, level=None):
    with open(STATE_FILE, "w") as f:
        json.dump({"ex": ex, "graded": graded, "level": level}, f)

def mark_graded():
    """Marca el ejercicio actual como superado."""
    state = load_state()
    if state:
        save_state(state["ex"], graded=True, level=state.get("level"))

def check_valgrind():
    return shutil.which("valgrind") is not None

def run(cmd, stdin_text="", timeout=15):
    """Ejecuta un comando y devuelve (stdout, stderr, returncode)."""
    try:
        res = subprocess.run(
            cmd,
            input=stdin_text,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return res.stdout, res.stderr, res.returncode
    except subprocess.TimeoutExpired:
        return "", "TIMEOUT", -1
    except Exception as e:
        return "", str(e), -1

def compile_src(sources, out, extra_flags=None):
    """Compila fuentes C. Devuelve True si OK."""
    flags = ["-Wall", "-Wextra", "-Werror"] + (extra_flags or [])
    cmd = ["gcc"] + flags + sources + ["-o", out]
    _, stderr, code = run(cmd)
    if code != 0:
        print(red(f"  Error de compilación:\n{stderr}"))
    return code == 0

def check_memory(cmd, stdin_text=""):
    """Valgrind check. Devuelve (ok, stderr)."""
    if not check_valgrind():
        return True, "(valgrind no disponible)"
    v_cmd = ["valgrind", "--leak-check=full", "--error-exitcode=42", "-q"] + cmd
    _, stderr, code = run(v_cmd, stdin_text, timeout=20)
    return (code != 42), stderr

def normalize(text, sort_lines=False):
    lines = text.strip().split("\n")
    if sort_lines:
        lines = sorted(lines)
    return "\n".join(lines)

def print_diff(expected, obtained):
    exp_lines = expected.split("\n")
    obt_lines = obtained.split("\n")
    max_len   = max(len(exp_lines), len(obt_lines))
    print(f"  {'ESPERADO':<35} {'OBTENIDO':<35}")
    print(f"  {'-'*35} {'-'*35}")
    for i in range(max_len):
        e = exp_lines[i] if i < len(exp_lines) else "<vacío>"
        o = obt_lines[i] if i < len(obt_lines) else "<vacío>"
        mark = "" if e == o else " ← DIFF"
        color = C.RESET if e == o else C.RED
        print(f"  {color}{repr(e):<35} {repr(o):<35}{mark}{C.RESET}")

# ─── LÓGICA DE CORRECCIÓN ─────────────────────────────────────────────────────

def grade_gnl(conf, user_src, ref_src):
    """Corrección especial para broken_GNL con múltiples BUFFER_SIZE."""
    main_c = tmp("gnl_main.c")
    with open(main_c, "w") as f:
        f.write(
            '#include <stdio.h>\n'
            '#include <stdlib.h>\n'
            'char *get_next_line(int fd);\n'
            'int main(void) {\n'
            '    char *l;\n'
            '    while ((l = get_next_line(0))) {\n'
            '        printf("%s", l);\n'
            '        free(l);\n'
            '    }\n'
            '    return 0;\n'
            '}\n'
        )

    all_ok = True
    for bs in conf["buffer_sizes"]:
        print(f"\n  {blue(f'BUFFER_SIZE = {bs}')}")
        bs_flag = f"-DBUFFER_SIZE={bs}"

        u_ok = compile_src([user_src, main_c], tmp("u.out"), [bs_flag])
        r_ok = compile_src([ref_src,  main_c], tmp("r.out"), [bs_flag])
        if not u_ok:
            return False
        if not r_ok:
            print(yellow("  (referencia no compiló, saltando comparación)"))

        for t in conf["tests"]:
            label = t["name"]
            u_out, _, u_code = run([tmp("u.out")], t["stdin"])
            r_out, _, _      = run([tmp("r.out")], t["stdin"]) if r_ok else ("", "", 0)

            if r_ok and u_out != r_out:
                print(red(f"  ✗ FAIL [{label}]"))
                print_diff(r_out, u_out)
                all_ok = False
                continue

            ok_mem, mem_log = check_memory([tmp("u.out")], t["stdin"])
            if not ok_mem:
                print(red(f"  ✗ LEAKS [{label}]\n{mem_log}"))
                all_ok = False
                continue

            print(green(f"  ✓ [{label}]"))

    return all_ok


def grade_program(conf, user_src, ref_src):
    """Corrección genérica para programas compilables."""
    extra = conf.get("extra_flags", [])

    u_ok = compile_src([user_src], tmp("u.out"), extra)
    if not u_ok:
        return False

    r_ok = compile_src([ref_src], tmp("r.out"), extra)
    if not r_ok:
        print(yellow("  (solución de referencia no disponible, solo se valida exit code)"))

    do_sort = conf.get("sort", False)
    all_ok  = True

    for t in conf["tests"]:
        args  = t.get("args", [])
        stdin = t.get("stdin", "")
        desc  = t.get("desc", str(args))
        expected_exit = t.get("exit", 0)

        u_out, _, u_code = run([tmp("u.out")] + args, stdin)

        # Verificar exit code cuando se espera error
        if expected_exit != 0:
            if u_code == expected_exit:
                print(green(f"  ✓ [{desc}] → exit {u_code}"))
            else:
                print(red(f"  ✗ [{desc}] → exit esperado {expected_exit}, obtenido {u_code}"))
                all_ok = False
            continue

        if r_ok:
            r_out, _, _ = run([tmp("r.out")] + args, stdin)
            u_norm = normalize(u_out, do_sort)
            r_norm = normalize(r_out, do_sort)

            if u_norm != r_norm:
                print(red(f"  ✗ FAIL [{desc}]"))
                print_diff(r_norm, u_norm)
                all_ok = False
                continue

        # Valgrind solo si el programa tiene stdin o es determinista
        ok_mem, mem_log = check_memory([tmp("u.out")] + args, stdin)
        if not ok_mem:
            print(red(f"  ✗ LEAKS [{desc}]\n{mem_log}"))
            all_ok = False
            continue

        print(green(f"  ✓ [{desc}]"))

    return all_ok

def grade_scanf(conf, user_src, ref_src):
    """
    Corrección especial para ft_scanf.
    Por cada test genera un main.c que:
      1. Llama a ft_scanf con el formato y variables del test
      2. Imprime ret= + los valores capturados
    Compara contra la misma lógica con scanf del sistema (o ref_src si existe).
    """

    def type_decl(v):
        t, n = v["type"], v["name"]
        if t == "int":  return f"    int {n} = 0;"
        if t == "char": return f"    char {n} = 0;"
        if t == "str":  return f'    char {n}[256]; {n}[0] = \'\\0\';'
        return ""

    def print_stmt(v):
        t, n = v["type"], v["name"]
        if t == "int":  return f'    printf(" {n}=%d", {n});'
        # char como entero para detectar diferencias en no-imprimibles
        if t == "char": return f'    printf(" {n}=%d", (int)(unsigned char){n});'
        if t == "str":  return f'    printf(" {n}=%s", {n});'
        return ""

    def make_main(fmt, variables, func_name):
        decls  = "\n".join(type_decl(v) for v in variables)
        args   = ", ".join(f"&{v['name']}" for v in variables)
        prints = "\n".join(print_stmt(v) for v in variables)
        fmt_e  = fmt.replace('\\', '\\\\').replace('"', '\\"')
        return (
            '#include <stdio.h>\n'
            '#include <stdarg.h>\n'
            '#include <ctype.h>\n'
            f'int {func_name}(const char *, ...);\n'
            'int main(void) {\n'
            f'{decls}\n'
            f'    int ret = {func_name}("{fmt_e}", {args});\n'
            '    printf("ret=%d", ret);\n'
            f'{prints}\n'
            '    printf("\\n");\n'
            '    return 0;\n'
            '}\n'
        )

    ref_available = os.path.exists(ref_src)
    all_ok = True

    for t in conf["tests"]:
        desc      = t["desc"]
        fmt       = t["format"]
        sin       = t["stdin"]
        variables = t["vars"]

        # ── binario usuario ───────────────────────────────────────────────────
        u_main = tmp("scanf_u_main.c")
        with open(u_main, "w") as f:
            f.write(make_main(fmt, variables, "ft_scanf"))

        if not compile_src([user_src, u_main], tmp("scanf_u.out")):
            return False
        u_out, _, _ = run([tmp("scanf_u.out")], sin)

        # ── binario referencia ────────────────────────────────────────────────
        r_main = tmp("scanf_r_main.c")
        if ref_available:
            with open(r_main, "w") as f:
                f.write(make_main(fmt, variables, "ft_scanf"))
            r_ok = compile_src([ref_src, r_main], tmp("scanf_r.out"))
        else:
            # Sin ref_src: comparar contra scanf real del sistema
            with open(r_main, "w") as f:
                f.write(make_main(fmt, variables, "scanf"))
            r_ok = compile_src([r_main], tmp("scanf_r.out"))

        if not r_ok:
            print(yellow(f"  ⚠ [{desc}] referencia no compiló, saltando"))
            continue

        r_out, _, _ = run([tmp("scanf_r.out")], sin)

        if u_out.strip() != r_out.strip():
            print(red(f"  ✗ FAIL [{desc}]"))
            print_diff(r_out.strip(), u_out.strip())
            all_ok = False
            continue

        print(green(f"  ✓ [{desc}]"))

    return all_ok


# ─── COMANDOS PRINCIPALES ─────────────────────────────────────────────────────

def cmd_status():
    state = load_state()
    if not state:
        print(yellow("No hay ejercicio activo. Usa: python exam_manager.py start [lvl1|lvl2]"))
        return
    ex     = state["ex"]
    graded = state.get("graded", False)
    level  = state.get("level")
    conf   = EXAMS.get(ex, {})
    dest   = os.path.join(RENDU_DIR, ex)
    estado = green("✓ SUPERADO") if graded else yellow("⏳ pendiente de grade")
    print(f"\n  Ejercicio activo : {bold(ex)}")
    if level:
        print(f"  Nivel            : {purple(level.upper())}")
    print(f"  Estado           : {estado}")
    print(f"  Entregar en      : {dest}/")
    print(f"  Archivos pedidos : {', '.join(conf['files'])}")
    # Mostrar qué archivos ya existen
    for f in conf["files"]:
        path = os.path.join(dest, f)
        exists = green("✓ presente") if os.path.exists(path) else red("✗ falta")
        print(f"    {f}: {exists}")


def cmd_grade():
    ensure_dirs()
    state = load_state()
    if not state:
        print(red("No hay ejercicio activo. Usa: python exam_manager.py start"))
        return

    ex       = state["ex"]
    conf     = EXAMS[ex]
    ref_file = conf.get("ref_file", f"{ex}.c")
    ref_src  = os.path.join(SOLUTIONS_DIR, ref_file)
    user_src = os.path.join(RENDU_DIR, ex, conf["files"][0])

    print(f"\n{blue('─' * 50)}")
    print(f"  {bold('Corrigiendo:')} {purple(ex)}")
    print(f"{blue('─' * 50)}")

    if not os.path.exists(user_src):
        print(red(f"\n  Archivo no encontrado: {conf['files'][0]}"))
        print(yellow(f"  Entrégalo en: {os.path.dirname(user_src)}/"))
        return

    if not os.path.exists(ref_src):
        print(yellow(f"  Solución de referencia no encontrada: {ref_src}"))
        print(yellow("  Se validará solo compilación, exit codes y memoria."))

    t0 = time.time()

    if conf.get("is_scanf"):
        ok = grade_scanf(conf, user_src, ref_src)
    elif not conf.get("is_program"):
        ok = grade_gnl(conf, user_src, ref_src)
    else:
        ok = grade_program(conf, user_src, ref_src)

    elapsed = time.time() - t0
    print(f"\n{blue('─' * 50)}")
    if ok:
        print(green(f"  ✓ SUCCESS — {ex} superado en {elapsed:.1f}s"))
        print(f"{blue('─' * 50)}\n")
        mark_graded()
        cmd_setup(level=state.get("level"))
    else:
        print(red(f"  ✗ FAILED — revisa los errores anteriores"))
        print(f"{blue('─' * 50)}\n")


def cmd_setup(specific=None, level=None):
    ensure_dirs()
    if specific and specific not in EXAMS:
        print(red(f"Ejercicio desconocido: {specific}"))
        print(f"Disponibles: {', '.join(EXAMS.keys())}")
        return

    # Determinar pool de ejercicios según nivel
    if level and level in LEVELS:
        pool = LEVELS[level]
    else:
        pool = list(EXAMS.keys())

    # Bloquear si hay ejercicio activo que no se ha superado con grade
    state = load_state()
    if state and not state.get("graded", False):
        active_ex = state["ex"]
        sep = yellow("─" * 50)
        print("\n" + sep)
        print(yellow("  ⚠ Ejercicio activo sin superar: ") + bold(active_ex))
        print(yellow("  Debes pasarlo con 'grade' antes de continuar."))
        print(yellow("  Si quieres cancelarlo todo: 'cancel'"))
        print(sep + "\n")
        return

    ex   = specific or random.choice(pool)
    conf = EXAMS[ex]
    dest = os.path.join(RENDU_DIR, ex)

    save_state(ex, graded=False, level=level)

    if os.path.exists(dest):
        shutil.rmtree(dest)
    os.makedirs(dest)

    # Copia el subject.txt en el directorio de entrega si existe
    subject_src = os.path.join(SUBJECTS_DIR, f"{ex}.txt")
    subject_dst = os.path.join(dest, "subject.txt")
    if os.path.exists(subject_src):
        shutil.copy(subject_src, subject_dst)
        subject_status = green("✓ subject.txt copiado")
    else:
        subject_status = yellow(f"⚠ no encontrado en subjects/{ex}.txt")

    level_tag = f" {purple('[' + level.upper() + ']')}" if level else ""
    print(f"\n{purple('─' * 50)}")
    print(f"  {bold('NUEVO EJERCICIO:')}{level_tag} {purple(ex)}")
    print(f"  Entrega en      : {dest}/")
    print(f"  Archivos pedidos: {', '.join(conf['files'])}")
    print(f"  Subject         : {subject_status}")
    print(f"{purple('─' * 50)}\n")


def cmd_reset():
    """Regenera el directorio de entrega sin cambiar de ejercicio."""
    state = load_state()
    if not state:
        print(red("No hay ejercicio activo. Usa: python exam_manager.py start"))
        return
    ex   = state["ex"]
    conf = EXAMS[ex]
    dest = os.path.join(RENDU_DIR, ex)
    if os.path.exists(dest):
        shutil.rmtree(dest)
    os.makedirs(dest)
    save_state(ex, graded=False)
    print(green(f"  Directorio reiniciado: {dest}/"))
    print(yellow("  Estado de grade reiniciado. Deberás superar el ejercicio de nuevo."))

def cmd_cancel():
    """Elimina todo lo generado por start: rendu, state y tmp."""
    state = load_state()
    if not state:
        print(red("No hay ejercicio activo. Nada que cancelar."))
        return

    ex   = state["ex"]
    dest = os.path.join(RENDU_DIR, ex)

    sep = red("─" * 50)
    print("\n" + sep)
    print(red(f"  ✗ Cancelando ejercicio: ") + bold(ex))

    if os.path.exists(dest):
        shutil.rmtree(dest)
        print(red(f"  ✗ Eliminado: {dest}/"))

    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
        print(red(f"  ✗ Estado eliminado"))

    if os.path.exists(TMP_DIR):
        shutil.rmtree(TMP_DIR)
        print(red(f"  ✗ Temporales eliminados"))

    print(sep)
    print(yellow("\n  Puedes lanzar 'start' para comenzar un nuevo ejercicio.\n"))


# ─── ENTRY POINT ──────────────────────────────────────────────────────────────

COMMANDS = {
    "start":  lambda: cmd_setup(),
    "grade":  cmd_grade,
    "status": cmd_status,
    "reset":  cmd_reset,
    "cancel": cmd_cancel,
}

def usage():
    print(f"\n{bold('exam_manager.py')} — Simulador Rank03 (42 School)")
    print("\nUso:")
    descs = {
        "start":  "Asigna un ejercicio aleatorio (todos los niveles)",
        "grade":  "Corrige el ejercicio actual",
        "status": "Muestra el estado del ejercicio activo",
        "reset":  "Limpia el rendu sin cambiar de ejercicio",
        "cancel": "Cancela el ejercicio activo y borra todo",
    }
    for cmd in COMMANDS:
        print(f"  python exam_manager.py {cmd:<8} — {descs[cmd]}")
    print(f"  python exam_manager.py {'start lvl1':<8} — Solo ejercicios de nivel 1 (broken_GNL, filter, ft_scanf)")
    print(f"  python exam_manager.py {'start lvl2':<8} — Solo ejercicios de nivel 2 (nqueens, permutations, powerset, rip)")
    print()

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        usage()
        sys.exit(1)

    if sys.argv[1] == "start":
        if len(sys.argv) == 3:
            arg = sys.argv[2]
            if arg in LEVELS:
                cmd_setup(level=arg)
            else:
                # Nombre de ejercicio concreto (comportamiento original)
                cmd_setup(specific=arg)
        else:
            cmd_setup()
    else:
        COMMANDS[sys.argv[1]]()
