#ifndef _GNU_SOURCE
# define _GNU_SOURCE
#endif

#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#define BUF_SIZE 4096

int main (int ac, char **av)
{
	char buf[BUF_SIZE]; // Cada ejecución del read se almacena aquí
	char *accumulator = NULL; // Se acumula la stdin aquí
	int acc_len = 0;
	int pat_len;
	int read_ret; // Cuantos bytes ha leido read

	if (ac != 2 || !av[1][0]) // Protección ante argumentos invalidos
		return (perror("Error: invalid arguments."), 1);
	
	pat_len = strlen(av[1]); // inicializamos variable tras comprobación de argumentos para evitar segfault

	while ((read_ret = read(0, buf, BUF_SIZE)) > 0) // Leo BUF_SIZE bytes de stdin y los guardo en buf
	{
		
		//funcion ACCUMULATE: aumenta el tamaño de accumulator, y almacena el read.
		
		char *tmp = realloc(accumulator, acc_len + read_ret + 1); // aumentar tamaño del acumulador la lectura de esta iteración
		if (!tmp)
			return (free(accumulator), perror("Error: memory allocation failed."), 1); // protección del realloc
		accumulator = tmp;
		memmove(accumulator + acc_len, buf, read_ret); // añadimos el bloque al acumulador
		acc_len += read_ret; // actualiza la longitud del accumulator
		accumulator[acc_len] = '\0';

		//funcion PROCESS: sustituye las coincidencias del patron pat = argv[1] en accumulator. Se divide el accumulator en
		//prefijo (prefix), coincidencia con el patron (hit), y sufijo. se imprime el prefijo y se cambia la coincidencia por
		//asteriscos, en bucle hasta que no haya mas coincidencias.

		while (1)
		{
			char *hit = memmem(accumulator, acc_len, av[1], pat_len); // busca el patron en accumulator
			if (!hit)
				break ; // si no encuentra coincidencia, se rompe el bucle
			int prefix = (int)(hit - accumulator); // tamaño en bytes del prefijo
			if (prefix)
				write (1, accumulator, prefix); // si existe, escribe el prefijo
			int i = 0;
			while (i++ < pat_len)
				write(1, "*", 1); // escribe  "*" [pat_len] veces.
			int rest = acc_len - (prefix + pat_len);
			memmove(accumulator, hit + pat_len, rest + 1); /* se pasan los [rest + 1] bytes al inicio de accumulator. 
									  (hit + len = byte justo después del match)*/
			acc_len = rest; // se acualiza la longitud de accumulator
		}
	}
	if (read_ret < 0)
		return (perror("Error: read failed"), 1); // si falla el read, imprime error
	if (acc_len)
		write(1, accumulator, acc_len); // imprime el sufijo restante tras la ultima iteracion
	free(accumulator); // libera la memoria allocada para accumulator
	return (0);
}
