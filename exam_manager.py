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
}

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def ensure_dirs():
    os.makedirs(TMP_DIR, exist_ok=True)
    os.makedirs(SOLUTIONS_DIR, exist_ok=True)
    os.makedirs(RENDU_DIR, exist_ok=True)

def tmp(name):
    return os.path.join(TMP_DIR, name)

def load_state():
    if not os.path.exists(STATE_FILE):
        return None
    with open(STATE_FILE) as f:
        return f.read().strip()

def save_state(ex):
    with open(STATE_FILE, "w") as f:
        f.write(ex)

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

# ─── COMANDOS PRINCIPALES ─────────────────────────────────────────────────────

def cmd_status():
    ex = load_state()
    if not ex:
        print(yellow("No hay ejercicio activo. Usa: python exam_manager.py start"))
        return
    conf = EXAMS[ex]
    dest = os.path.join(RENDU_DIR, ex)
    print(f"\n  Ejercicio activo : {bold(ex)}")
    print(f"  Entregar en      : {dest}/")
    print(f"  Archivos pedidos : {', '.join(conf['files'])}")
    # Mostrar qué archivos ya existen
    for f in conf["files"]:
        path = os.path.join(dest, f)
        exists = green("✓ presente") if os.path.exists(path) else red("✗ falta")
        print(f"    {f}: {exists}")


def cmd_grade():
    ensure_dirs()
    ex = load_state()
    if not ex:
        print(red("No hay ejercicio activo. Usa: python exam_manager.py start"))
        return

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

    if not conf.get("is_program"):
        ok = grade_gnl(conf, user_src, ref_src)
    else:
        ok = grade_program(conf, user_src, ref_src)

    elapsed = time.time() - t0
    print(f"\n{blue('─' * 50)}")
    if ok:
        print(green(f"  ✓ SUCCESS — {ex} superado en {elapsed:.1f}s"))
        print(f"{blue('─' * 50)}\n")
        cmd_setup()
    else:
        print(red(f"  ✗ FAILED — revisa los errores anteriores"))
        print(f"{blue('─' * 50)}\n")


def cmd_setup(specific=None):
    ensure_dirs()
    if specific and specific not in EXAMS:
        print(red(f"Ejercicio desconocido: {specific}"))
        print(f"Disponibles: {', '.join(EXAMS.keys())}")
        return

    ex   = specific or random.choice(list(EXAMS.keys()))
    conf = EXAMS[ex]
    dest = os.path.join(RENDU_DIR, ex)

    save_state(ex)

    if os.path.exists(dest):
        shutil.rmtree(dest)
    os.makedirs(dest)

    print(f"\n{purple('─' * 50)}")
    print(f"  {bold('NUEVO EJERCICIO:')} {purple(ex)}")
    print(f"  Entrega en      : {dest}/")
    print(f"  Archivos pedidos: {', '.join(conf['files'])}")
    print(f"{purple('─' * 50)}\n")


def cmd_reset():
    """Regenera el directorio de entrega sin cambiar de ejercicio."""
    ex = load_state()
    if not ex:
        print(red("No hay ejercicio activo. Usa: python exam_manager.py start"))
        return
    conf = EXAMS[ex]
    dest = os.path.join(RENDU_DIR, ex)
    if os.path.exists(dest):
        shutil.rmtree(dest)
    os.makedirs(dest)
    print(green(f"  Directorio reiniciado: {dest}/"))

# ─── ENTRY POINT ──────────────────────────────────────────────────────────────

COMMANDS = {
    "start":  lambda: cmd_setup(),
    "grade":  cmd_grade,
    "status": cmd_status,
    "reset":  cmd_reset,
}

def usage():
    print(f"\n{bold('exam_manager.py')} — Simulador Rank03 (42 School)")
    print("\nUso:")
    for cmd, _ in COMMANDS.items():
        descs = {
            "start":  "Asigna un ejercicio aleatorio",
            "grade":  "Corrige el ejercicio actual",
            "status": "Muestra el estado del ejercicio activo",
            "reset":  "Limpia el rendu sin cambiar de ejercicio",
        }
        print(f"  python exam_manager.py {cmd:<8} — {descs[cmd]}")
    print()

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        usage()
        sys.exit(1)

    # Opción: start <nombre> para elegir ejercicio concreto
    if sys.argv[1] == "start" and len(sys.argv) == 3:
        cmd_setup(specific=sys.argv[2])
    else:
        COMMANDS[sys.argv[1]]()
