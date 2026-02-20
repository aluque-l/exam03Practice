#include <stdarg.h>
#include <stdio.h>
#include <ctype.h>

/*
** Consume todos los espacios del stream.
** Devuelve 1 siempre (EOF durante espacios no es error de matching).
** Devuelve -1 solo si ferror.
*/
int     match_space(FILE *f)
{
    int ch;

    ch = fgetc(f);
    while (ch != EOF && isspace(ch))
        ch = fgetc(f);
    if (ch != EOF)
        ungetc(ch, f);
    if (ferror(f))
        return (-1);
    return (1);
}

/*
** Lee un carácter del stream y comprueba si coincide con c.
** Si no coincide, lo devuelve al stream.
** Devuelve 1 si coincide, -1 si no.
*/
int     match_char(FILE *f, char c)
{
    int ch;

    ch = fgetc(f);
    if (ch == (int)c)
        return (1);
    if (ch != EOF)
        ungetc(ch, f);
    return (-1);
}

/*
** %c — lee exactamente un carácter sin saltar espacios.
** El puntero se obtiene antes de leer para mantener va_list consistente.
*/
int     scan_char(FILE *f, va_list ap)
{
    char    *cp;
    int     ch;

    cp = va_arg(ap, char *);
    ch = fgetc(f);
    if (ch == EOF)
        return (-1);
    *cp = (char)ch;
    return (1);
}

/*
** %d — lee un entero con signo opcional.
** Los espacios previos ya fueron consumidos por match_conv.
** Devuelve 1 si leyó al menos un dígito, -1 si no.
*/
int     scan_int(FILE *f, va_list ap)
{
    int     *ip;
    int     ch;
    int     sign;
    int     value;

    ip    = va_arg(ap, int *);
    sign  = 1;
    value = 0;
    ch    = fgetc(f);
    if (ch == EOF)
        return (-1);
    if (ch == '-' || ch == '+')
    {
        if (ch == '-')
            sign = -1;
        ch = fgetc(f);
    }
    if (!isdigit(ch))
    {
        if (ch != EOF)
            ungetc(ch, f);
        return (-1);
    }
    while (isdigit(ch))
    {
        value = value * 10 + (ch - '0');
        ch = fgetc(f);
    }
    if (ch != EOF)
        ungetc(ch, f);
    *ip = value * sign;
    return (1);
}

/*
** %s — lee caracteres no-espacio hasta whitespace o EOF.
** Los espacios previos ya fueron consumidos por match_conv.
** Añade '\0' al final. Devuelve 1 si leyó al menos un carácter.
*/
int     scan_string(FILE *f, va_list ap)
{
    char    *sp;
    int     ch;
    int     i;

    sp = va_arg(ap, char *);
    i  = 0;
    ch = fgetc(f);
    if (ch == EOF)
        return (-1);
    while (ch != EOF && !isspace(ch))
    {
        sp[i++] = (char)ch;
        ch = fgetc(f);
    }
    sp[i] = '\0';
    if (ch != EOF)
        ungetc(ch, f);
    if (i == 0)
        return (-1);
    return (1);
}

/*
** Dispatcher de conversiones.
** Responsable único del salto de espacios para %d y %s.
*/
int     match_conv(FILE *f, const char **format, va_list ap)
{
    switch (**format)
    {
        case 'c':
            return (scan_char(f, ap));
        case 'd':
            match_space(f);
            return (scan_int(f, ap));
        case 's':
            match_space(f);
            return (scan_string(f, ap));
        case '\0':
            return (-1);
        default:
            return (-1);
    }
}

/*
** Bucle principal de parseo del formato.
** Itera carácter a carácter:
**   '%X' → conversión
**   espacio → consume whitespace del stream
**   literal → debe coincidir exactamente
*/
int     ft_vfscanf(FILE *f, const char *format, va_list ap)
{
    int nconv;
    int c;

    nconv = 0;
    c = fgetc(f);
    if (c == EOF)
        return (EOF);
    ungetc(c, f);
    while (*format)
    {
        if (*format == '%')
        {
            format++;
            if (match_conv(f, &format, ap) != 1)
                break ;
            nconv++;
        }
        else if (isspace(*format))
        {
            match_space(f);
        }
        else if (match_char(f, *format) != 1)
            break ;
        format++;
    }
    if (ferror(f))
        return (EOF);
    return (nconv);
}

/*
** Wrapper público: inicializa la va_list y delega en ft_vfscanf.
*/
int     ft_scanf(const char *format, ...)
{
    va_list ap;
    int     ret;

    va_start(ap, format);
    ret = ft_vfscanf(stdin, format, ap);
    va_end(ap);
    return (ret);
}
