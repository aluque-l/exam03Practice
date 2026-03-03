#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <float.h>

typedef struct s_city
{
	float x;
	float y;
}	t_city;

static float	dist(t_city a, t_city b)
{
	float dx = a.x - b.x;
	float dy = a.y - b.y;
	return sqrtf(dx * dx + dy * dy);
}

static float	path_length(t_city *cities, int *order, int n)
{
	float	total = 0.0f;
	int		i = 0;

	while (i < n - 1)
	{
		total += dist(cities[order[i]], cities[order[i + 1]]);
		i++;
	}
	total += dist(cities[order[n - 1]], cities[order[0]]);
	return total;
}

static void	swap(int *a, int *b)
{
	int tmp = *a;
	*a = *b;
	*b = tmp;
}

static float	permute(t_city *cities, int *order, int start, int n, float best)
{
	float	current;
	int		i;

	if (start == n)
	{
		current = path_length(cities, order, n);
		if (current < best)
			best = current;
		return best;
	}
	i = start;
	while (i < n)
	{
		swap(&order[start], &order[i]);
		best = permute(cities, order, start + 1, n, best);
		swap(&order[start], &order[i]);
		i++;
	}
	return best;
}

int	main(void)
{
	t_city	cities[11];
	int		order[11];
	int		n;
	int		i;
	float	best;

	n = 0;
	while (n < 11 && fscanf(stdin, "%f, %f\n", &cities[n].x, &cities[n].y) == 2)
		n++;
	if (n == 0)
		return 1;
	i = 0;
	while (i < n)
	{
		order[i] = i;
		i++;
	}
	best = permute(cities, order, 1, n, FLT_MAX);
	fprintf(stdout, "%.2f\n", best);
	return 0;
}
