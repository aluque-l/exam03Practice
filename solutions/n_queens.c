#include <stdlib.h>
#include <unistd.h>

static int	is_valid(int *board, int col, int row)
{
	int	i;

	i = 0;
	while (i < row)
	{
		if (board[i] == col
			|| board[i] - i == col - row
			|| board[i] + i == col + row)
			return (0);
		i++;
	}
	return (1);
}

static void	print_board(int *board, int n)
{
	int		i;
	char	c;

	i = 0;
	while (i < n)
	{
		c = board[i] + '0';
		write(1, &c, 1);
		if (i < n - 1)
			write(1, " ", 1);
		i++;
	}
	write(1, "\n", 1);
}

static void	solve(int *board, int row, int n)
{
	int	col;

	if (row == n)
	{
		print_board(board, n);
		return ;
	}
	col = 0;
	while (col < n)
	{
		if (is_valid(board, col, row))
		{
			board[row] = col;
			solve(board, row + 1, n);
		}
		col++;
	}
}

int	main(int ac, char **av)
{
	int	n;
	int	*board;

	if (ac != 2)
		return (1);
	n = atoi(av[1]);
	if (n <= 0)
		return (1);
	board = malloc(sizeof(int) * n);
	if (!board)
		return (1);
	solve(board, 0, n);
	free(board);
	return (0);
}
