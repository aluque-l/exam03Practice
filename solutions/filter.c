#ifndef _GNU_SOURCE
# define _GNU_SOURCE
#endif
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <errno.h>

static void	print_error(void)
{
	fprintf(stderr, "Error: %s\n", strerror(errno));
	exit(1);
}

static void	write_stars(size_t n)
{
	char	star;

	star = '*';
	while (n--)
		write(1, &star, 1);
}

static void	process(char *buf, size_t len, const char *pat, size_t pat_len)
{
	size_t	i;
	char	*match;

	i = 0;
	while (i < len)
	{
		match = memmem(buf + i, len - i, pat, pat_len);
		if (!match)
		{
			write(1, buf + i, len - i);
			return ;
		}
		if (match > buf + i)
			write(1, buf + i, match - (buf + i));
		write_stars(pat_len);
		i = (match - buf) + pat_len;
	}
}

int	main(int ac, char **av)
{
	size_t	pat_len;
	size_t	pending;
	char	*buf;
	ssize_t	n;

	if (ac != 2 || av[1][0] == '\0')
		return (1);
	pat_len = strlen(av[1]);
	buf = malloc(4096 + pat_len);
	if (!buf)
		print_error();
	pending = 0;
	while ((n = read(0, buf + pending, 4096)) > 0)
	{
		size_t	total;
		size_t	safe;

		total = pending + (size_t)n;
		safe = (total >= pat_len - 1) ? total - (pat_len - 1) : 0;
		if (pat_len == 1)
			safe = total;
		process(buf, safe, av[1], pat_len);
		pending = total - safe;
		memmove(buf, buf + safe, pending);
	}
	if (n == -1)
	{
		free(buf);
		print_error();
	}
	if (pending)
		process(buf, pending, av[1], pat_len);
	free(buf);
	return (0);
}
