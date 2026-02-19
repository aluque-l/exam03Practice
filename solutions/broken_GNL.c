#include <unistd.h>
#include <stdlib.h>

#ifndef BUFFER_SIZE
# define BUFFER_SIZE 42
#endif

static char	*append(char *line, char *buf, int n)
{
	char	*tmp;
	int		len;
	int		i;

	len = 0;
	while (line && line[len])
		len++;
	tmp = malloc(len + n + 1);
	if (!tmp)
		return (free(line), NULL);
	i = 0;
	while (i < len)
	{
		tmp[i] = line[i];
		i++;
	}
	i = 0;
	while (i < n)
	{
		tmp[len + i] = buf[i];
		i++;
	}
	tmp[len + n] = '\0';
	free(line);
	return (tmp);
}

char	*get_next_line(int fd)
{
	static char	buf[BUFFER_SIZE];
	static int	start = 0;
	static int	end = 0;
	char		*line;
	int			i;

	if (fd < 0 || BUFFER_SIZE <= 0)
		return (NULL);
	line = NULL;
	while (1)
	{
		if (start >= end)
		{
			end = read(fd, buf, BUFFER_SIZE);
			start = 0;
			if (end <= 0)
				break ;
		}
		i = start;
		while (i < end && buf[i] != '\n')
			i++;
		if (i < end)
		{
			line = append(line, buf + start, i - start + 1);
			start = i + 1;
			return (line);
		}
		line = append(line, buf + start, end - start);
		if (!line)
			return (NULL);
		start = 0;
		end = 0;
	}
	if (line && line[0])
		return (line);
	free(line);
	return (NULL);
}
