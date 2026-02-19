#include <stdlib.h>
#include <unistd.h>

void swap(char *a, char *b)
{
	char tmp = *a;
	*a = *b;
	*b = tmp;
}

void sort(char *s, int n)
{
	int i = 0;
	while (i < n - 1) 
	{
		int j = i + 1;
		while (j < n) 
		{
			if (s[i] > s[j])
				swap(&s[i], &s[j]);
			j++;
		}
		i++;
	}
}

void perm(char *res, char *opc, int *used, int pos, int n)
{
	int	i = 0;
	if (pos == n)
	{
		write(1, res, n);
		write(1, "\n", 1);
		return;
	}
	while (i < n)
	{
		if (!used[i])
		{
			res[pos] = opc[i];
			used[i] = 1;
			perm(res, opc, used, pos + 1, n);
			used[i] = 0;
		}
		i++;
	}
}

int main(int ac, char **av)
{
	if (ac != 2)
		return 1;
	int i = 0;
	while (av[1][i])
		i++;
	int n = i;
	char *s = malloc(n + 1);
	char *res = malloc(n + 1);
	int *used = calloc(n, sizeof(int));
	i = 0;
	while (av[1][i])
	{
		s[i] = av[1][i];
		i++;
	}
	s[i] = 0;
	res[n] = 0;

	sort(s, n);
	perm(res, s, used, 0, n);
	free(s);
	free(res);
	free(used);
	return (0);
}

/*Assignment name  : permutations
Expected files   : *.c *.h
Allowed functions: puts, malloc, calloc, realloc, free, write
--------------------------------------------------------------------------------

Escribe un programa que imprima todas las permutaciones de una cadena dada como argumento.
Las soluciones deben darse en orden alfabético.
No probaremos tu programa con cadenas que contengan duplicados (por ejemplo: «abccd»).

Por ejemplo, esto debería funcionar:

$> ./permutations a | cat -e
a$

$> ./permutations ab | cat -e
ab$
ba$

$> ./permutations abc | cat -e
abc$
acb$
bac$
bca$
cab$
cba$*/
