/* EP617 impl A: exhaustive search for balanced r-colorings of K_n.
 * Every (r+1)-set of vertices must see all r colors on its internal edges.
 * SAT <=> erdos_617's conclusion FAILS at (r,n). Recursive DFS, star edge order,
 * forward checking (seen-mask + uncolored count per set), first-occurrence color
 * symmetry breaking. Usage: ep617_c N R [minutes] */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

static int n, r, m, nsets, ksz, fullmask;
static int *eid;                 /* eid[u*n+v] */
static int (*ks)[15];            /* per set: its C(r+1,2) <= 15 edge ids (r<=5) */
static int *soe_cnt;
static int **soe;
static unsigned char *seen, *uncol;
static signed char *col;
static int *order;
static unsigned long long nodes = 0, node_cap = 20000000000ULL;
static time_t deadline;

static void die(const char *s) { fprintf(stderr, "%s\n", s); exit(1); }

static int dfs(int depth, int maxcolor) {
    if (depth == m) return 1;
    if ((++nodes & 0xFFFFF) == 0 && time(NULL) > deadline) return -1;
    if (nodes > node_cap) return -1;
    int x = order[depth];
    int hi = maxcolor + 2; if (hi > r) hi = r;
    unsigned char ssave[64]; unsigned char usave[64];
    for (int c = 0; c < hi; c++) {
        col[x] = c;
        int bad = 0, cnt = soe_cnt[x], *lst = soe[x];
        for (int j = 0; j < cnt; j++) {
            int a = lst[j];
            ssave[j] = seen[a]; usave[j] = uncol[a];   /* snapshot */
            unsigned char ns = seen[a] | (unsigned char)(1u << c);
            unsigned char nu = uncol[a] - 1;
            seen[a] = ns; uncol[a] = nu;
            if (nu == 0) { if (ns != fullmask) bad = 1; }
            else if (__builtin_popcount(ns) + nu < r) bad = 1;
        }
        if (!bad) {
            int ret = dfs(depth + 1, c > maxcolor ? c : maxcolor);
            if (ret != 0) { if (ret < 0) return -1; return 1; }
        }
        for (int j = 0; j < cnt; j++) {                /* restore snapshots */
            int a = lst[j];
            seen[a] = ssave[j]; uncol[a] = usave[j];
        }
        col[x] = -1;
    }
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 3) die("usage: ep617_c N R [minutes]");
    n = atoi(argv[1]); r = atoi(argv[2]);
    int minutes = argc > 3 ? atoi(argv[3]) : 30;
    deadline = time(NULL) + (time_t)minutes * 60;
    m = n * (n - 1) / 2;
    eid = calloc(n * n, sizeof(int));
    col = malloc(m);
    for (int i = 0, u = 0; u < n; u++)
        for (int v = u + 1; v < n; v++) eid[u * n + v] = i++;

    /* enumerate (r+1)-combinations */
    nsets = 1;
    for (int i = 1; i <= r + 1; i++) nsets = nsets * (n - i + 1) / i;
    ksz = (r + 1) * r / 2;
    ks = malloc((size_t)nsets * sizeof(*ks));
    seen = calloc(nsets, 1); uncol = malloc(nsets);
    memset(uncol, ksz, nsets);
    fullmask = (1 << r) - 1;

    int *comb = malloc((r + 2) * sizeof(int));
    long si = 0;
    for (int i = 0; i <= r + 1; i++) comb[i] = i;
    while (1) {
        int e = 0;
        for (int a = 0; a <= r; a++)
            for (int b = a + 1; b <= r; b++)
                ks[si][e++] = eid[comb[a] * n + comb[b]];
        si++;
        int p = r;
        while (p >= 0 && comb[p] == n - 1 - (r - p)) p--;
        if (p < 0) break;
        comb[p]++;
        for (int q = p + 1; q <= r; q++) comb[q] = comb[q - 1] + 1;
    }

    soe_cnt = calloc(m, sizeof(int));
    for (long a = 0; a < nsets; a++)
        for (int e = 0; e < ksz; e++) soe_cnt[ks[a][e]]++;
    soe = malloc(m * sizeof(void *));
    for (int i = 0; i < m; i++) {
        soe[i] = malloc(soe_cnt[i] * sizeof(int));
        soe_cnt[i] = 0;
    }
    for (long a = 0; a < nsets; a++)
        for (int e = 0; e < ksz; e++) {
            int x = ks[a][e];
            soe[x][soe_cnt[x]++] = (int)a;
        }

    order = malloc(m * sizeof(int));
    {   /* star order: edges of vertex 0 first, then vertex 1, ... */
        int i = 0;
        for (int u = 0; u < n - 1; u++)
            for (int v = u + 1; v < n; v++)
                order[i++] = eid[u * n + v];
    }

    col[order[0]] = 0;                       /* WLOG color permutation */
    for (int j = 0; j < soe_cnt[order[0]]; j++) {
        int a = soe[order[0]][j];
        seen[a] |= 1; uncol[a]--;
    }
    int res = dfs(1, 0);
    printf("BAL(%d,%d) verdict=%s nodes=%llu\n", n, r,
           res == 1 ? "SAT" : res == 0 ? "UNSAT" : "TIMEOUT", nodes);
    if (res == 1)
        for (int u = 0; u < n; u++)
            for (int v = u + 1; v < n; v++)
                printf("%d %d %d\n", u, v, col[eid[u * n + v]]);
    return 0;
}
