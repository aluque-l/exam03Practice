#include <unistd.h>

static int	invalid(char *s)
{
	int	open;
	int	close;
	int	i;

	open = 0;
	close = 0;
	i = 0;
	while (s[i])
	{
		if (s[i] == '(')
			open++;
		else if (s[i] == ')')
		{
			if (open > 0)
				open--;
			else
				close++;
		}
		i++;
	}
	return (open + close);
}

static void	ft_puts(char *s)
{
	while (*s)
		write(1, s++, 1);
	write(1, "\n", 1);
}

static void	solve(char *s, int start, int to_remove)
{
	int		i;
	char	c;

	if (to_remove == 0)
	{
		if (!invalid(s))
			ft_puts(s);
		return ;
	}
	i = start;
	while (s[i])
	{
		if (s[i] == '(' || s[i] == ')')
		{
			if (i > start && s[i] == s[i - 1])
			{
				i++;
				continue ;
			}
			c = s[i];
			s[i] = ' ';
			solve(s, i + 1, to_remove - 1);
			s[i] = c;
		}
		i++;
	}
}

int	main(int ac, char **av)
{
	if (ac != 2)
		return (1);
	solve(av[1], 0, invalid(av[1]));
	return (0);
}
