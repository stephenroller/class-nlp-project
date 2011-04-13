nawk '
{
for (i=1;i<=NF;i++)
count[$i]++
}
END {
for (i in count)
print count[i], i
}' $* |
sort -rn
