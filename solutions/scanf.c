#include <stdarg.h>   // va_start, va_arg, va_end
#include <stdio.h>    // FILE, fgetc, ungetc, stdin
#include <ctype.h>    // isspace, isdigit

/***************** helpers para saltar espacios y casillas ******************/

int match_space(FILE *f)
{
    int c;
    // Leer mientras haya espacios
    while ((c = fgetc(f)) != EOF && isspace(c))
        ;                                 // consumir
    if (c == EOF)                          // si EOF antes de encontrar no-espacio
        return -1;
    ungetc(c, f);                          // devolver el primer no-espacio
    return 1;                              // éxito
}

int match_char(FILE *f, char expected)
{
    int c = fgetc(f);                      // leer siguiente carácter
    if (c == EOF)                          // si EOF, error
        return -1;
    if (c != expected)                     // si no coincide, devolver al flujo
    {
        ungetc(c, f);
        return 0;                          // fallo de coincidencia
    }
    return 1;                              // coincidencia correcta
}

/************************* conversión %c *************************/

int scan_char(FILE *f, va_list ap)
{
    int c = fgetc(f);                      // leer un carácter tal cual
    if (c == EOF)                          // si EOF, error
        return -1;
    char *dst = va_arg(ap, char *);        // obtener puntero destino
    *dst = (char)c;                        // guardar carácter
    return 1;                              // una asignación realizada
}

/************************* conversión %d *************************/

int scan_int(FILE *f, va_list ap)
{
    int c, sign = 1, value = 0, read = 0;

    c = fgetc(f);                          // leer primer carácter
    if (c == EOF)                          // EOF inmediato → error
        return -1;
    if (c == '+' || c == '-')              // signo opcional
    {
        sign = (c == '-') ? -1 : 1;
        c = fgetc(f);                      // leer siguiente tras signo
    }
    while (c != EOF && isdigit(c))         // acumular dígitos
    {
        read = 1;                          // hemos leído al menos un dígito
        value = value * 10 + (c - '0');    // construir entero
        c = fgetc(f);                      // siguiente carácter
    }
    if (c != EOF)                          // devolver el primer no-dígito
        ungetc(c, f);
    if (!read)                             // si no hubo dígitos, fallo de coincidencia
        return 0;
    int *dst = va_arg(ap, int *);          // obtener puntero destino
    *dst = value * sign;                   // guardar resultado con signo
    return 1;                              // una asignación realizada
}

/************************* conversión %s *************************/

int scan_string(FILE *f, va_list ap)
{
    int c;
    char *dst = va_arg(ap, char *);        // destino de la cadena
    int read = 0;

    // saltar espacios iniciales
    while ((c = fgetc(f)) != EOF && isspace(c))
        ;
    if (c == EOF)                          // EOF antes de datos
        return -1;
    // leer hasta siguiente espacio o EOF
    while (c != EOF && !isspace(c))
    {
        dst[read++] = (char)c;             // copiar carácter
        c = fgetc(f);                      // siguiente
    }
    if (c != EOF)                          // devolver el separador
        ungetc(c, f);
    if (read == 0)                         // nada leído → fallo de coincidencia
        return 0;
    dst[read] = '\0';                      // terminar cadena
    return 1;                              // una asignación realizada
}

/*********************** despachador de conversiones ************************/

int match_conv(FILE *f, const char **format, va_list ap)
{
    switch (**format)                      // mirar letra de conversión
    {
        case 'c': return scan_char(f, ap);               // %c
        case 'd': match_space(f); return scan_int(f, ap); // %d (saltando espacios)
        case 's': match_space(f); return scan_string(f, ap); // %s (saltando espacios)
        case EOF: return -1;                              // fin inesperado
        default: return -1;                               // conversión no soportada
    }
}

/************************** núcleo tipo scanf *******************************/

int ft_vfscanf(FILE *f, const char *format, va_list ap)
{
    int nconv = 0;                         // contador de asignaciones
    int c = fgetc(f);                      // mirar si hay algo en el flujo
    if (c == EOF)                          // si vacío, devolver EOF
        return EOF;
    ungetc(c, f);                          // devolverlo para el proceso real

    while (*format)                        // recorrer cadena de formato
    {
        if (*format == '%')                // encontramos una conversión
        {
            format++;                      // pasar el '%'
            if (match_conv(f, &format, ap) != 1) // si falla conversión
                break;
            nconv++;                       // contar asignación exitosa
        }
        else if (isspace(*format))         // espacio en formato
        {
            if (match_space(f) == -1)      // saltar espacios de entrada
                break;
        }
        else if (match_char(f, *format) != 1) // literal debe coincidir
            break;
        format++;                          // avanzar formato
    }

    if (ferror(f))                         // si ocurrió error de lectura
        return EOF;
    return nconv;                          // devolver asignaciones realizadas
}

/**************************** interfaz pública ******************************/

int ft_scanf(const char *format, ...)
{
    va_list ap;
    va_start(ap, format);                  // iniciar lista variable
    int ret = ft_vfscanf(stdin, format, ap); // delegar en núcleo sobre stdin
    va_end(ap);                            // cerrar lista variable
    return ret;                            // devolver resultado
}

