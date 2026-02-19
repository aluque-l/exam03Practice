#include <stdio.h>
#include <stdlib.h>

void  print_subset(int *arr, int *path,int len)
{
	int i = -1;
	int first = 1;

	while (++i < len)
	{
		if (path[i])
		{
			if (!first)
				printf(" ");
			printf("%d", arr[i]);
			first = 0;
		}
	}
	printf("\n");
}

void  backtrack(int *arr, int *path, int len, int idx, int sum, int target)
{
	if (idx == len)
	{
		if (sum == target)
			print_subset(arr, path, len);
		return ;
	}
	path[idx] = 1;
	backtrack(arr, path, len, idx + 1, sum + arr[idx], target);
	path[idx] = 0;
	backtrack(arr, path, len, idx + 1, sum, target);
}


int main(int argc, char **argv)
{
	if (argc < 2)
		return (1);
	int i = -1;
	int target = atoi(argv[1]);
	int len = argc - 2;
	int *arr = malloc(sizeof(int) * len);
	int *path = calloc(len, sizeof(int));
	if (!arr || !path)
		return (1);
	while (++i < len)
		arr[i] = atoi(argv[i + 2]);
	backtrack(arr, path, len, 0, 0, target);
	free(arr);
	free(path);
	return (0);
}

/*contador para recorrer los argumentos y llenar el array nums
av1 es un string, lo convertimos a int y lo guardamos en target
reservo memoria para nums, reservo - 2 porque no necesito reservar para el ejecutor ni para el target
mientras i sea menos que el numero de argumentos
almaceno en nums cada argumento
llamo a la funcion recursiva
pos_num = 0; size = ac-2; p_act; suma = 0;
libero memoria
salgo

Assignment name  : powerset
Expected files   : *.c *.h
Allowed functions: atoi, printf, fprintf, malloc, calloc, realloc, free, stdout,
write
--------------------------------------------------------------------------------

Escribe un programa que tome como argumento un entero n seguido de un conjunto s de
enteros distintos.
Tu programa debe mostrar todos los subconjuntos de s cuya suma de elementos sea n.

El orden de las líneas no es importante, pero el orden de los elementos en un subconjunto sí lo es:
debe coincidir con el orden en el conjunto inicial s.
De esta manera, no debe haber duplicados (por ejemplo: «1 2» y «2 1»).

Por ejemplo, utilizando el comando ./powerset 5 1 2 3 4 5,
esta salida es válida:
1 4
2 3
5
esta salida es válida:
2 3
5
1 4
pero esta no:
4 1
3 2
5

En caso de error de malloc, tu programa se cerrará con el código 1.
No realizaremos pruebas con conjuntos no válidos (por ejemplo, «1 1 2»).
Pista: el subconjunto vacío es un subconjunto válido de cualquier conjunto. Se mostrará como una línea vacía.

Por ejemplo, esto debería funcionar:
$> ./powerset 3 1 0 2 4 5 3 | cat -e
3$
0 3$
1 2$
1 0 2$
$> ./powerset 12 5 2 1 8 4 3 7 11 | cat -e
8 4$
1 11$
1 4 7$
1 8 3$
2 3 7$
5 7$
5 4 3$
5 2 1 4$
$> ./powerset 0 1 -1 | cat -e
$
1 -1$
$> ./powerset 7 3 8 2 | cat -e

// Other tests:
$> ./powerset 100 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 | cat -e
...
$> ./powerset -1 1 2 3 4 5 -10 | cat -e
...
$> ./powerset 0 -1 1 2 3 -2 | cat -e
...
$> ./powerset 13 65 23 3 4 6 7 1 2 | cat -e
...
$> ./powerset 10 0 1 2 3 4 5 6 7 8 9 | cat -e
...*/