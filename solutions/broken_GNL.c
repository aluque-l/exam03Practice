#ifndef BUFFER_SIZE
# define BUFFER_SIZE 10
#endif

#include <unistd.h>
#include <stdlib.h>

char *ft_strchr(char *s, int c)
{
	int i = 0;
	if (!s)
		return NULL;
	while (s[i] && s[i] != (char)c)
		i++;
	if (s[i] == (char)c)
		return s + i;
	else
		return NULL;
}

void *ft_memcpy(void *dest, const void *src, size_t n)
{
	size_t i = 0;
	if (!dest && !src)
		return NULL;
	while (i < n)
	{
		((char *)dest)[i] = ((char *)src)[i];
		i++;
	}
	return dest;
}

size_t ft_strlen(char *s)
{
	size_t res = 0;
	if (!s)
		return 0;
	while (*s)
	{
		s++;
		res++;
	}
	return res;
}

int str_append_mem(char **s1, char *s2, size_t size2)
{
	size_t size1 = ft_strlen(*s1);
	char *tmp = malloc(size2 + size1 + 1);
	if (!tmp)
		return 0;
	if (*s1)
		ft_memcpy(tmp, *s1, size1);
	ft_memcpy(tmp + size1, s2, size2);
	tmp[size1 + size2] = '\0';
	if (*s1)
		free(*s1);
	*s1 = tmp;
	return 1;
}

int str_append_str(char **s1, char *s2)
{
	return str_append_mem(s1, s2, ft_strlen(s2));
}

void *ft_memmove(void *dest, const void *src, size_t n)
{
	char *d = (char *)dest;
	const char *s = (const char *)src;

	if (!dest && !src)
		return NULL;
	if (d > s)
	{
		while (n--)
			d[n] = s[n];
	}
	else
	{
		size_t i = 0;
		while (i < n)
		{
			d[i] = s[i];
			i++;
		}
	}
	return dest;
}

char *get_next_line(int fd)
{
	static char b[BUFFER_SIZE + 1] = "";
	char *ret = NULL;
	char *tmp;
	int read_ret;

	if (fd < 0 || BUFFER_SIZE <= 0)
		return NULL;
	while (!(tmp = ft_strchr(b, '\n')))
	{
		if (*b)
		{
			if (!str_append_str(&ret, b))
				return NULL;
		}
		read_ret = read(fd, b, BUFFER_SIZE);
		if (read_ret == -1)
		{
			free(ret);
			b[0] = '\0';
			return NULL;		
		}
		if (read_ret == 0)
		{
			b[0] = '\0';
			return ret;
		}
		b[read_ret] = '\0';
	}

	if (!str_append_mem(&ret, b, tmp - b + 1))
	{
		free(ret);
		return NULL;
	}

	ft_memmove(b, tmp + 1, ft_strlen(tmp + 1) + 1);

	return ret;
}
