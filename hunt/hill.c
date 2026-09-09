#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <stdint.h>
#include <limits.h>

#define MAXN 16
typedef struct { int n; uint8_t rot[MAXN][MAXN-1]; uint8_t rnk[MAXN][MAXN]; long count; long odd; } RS;
typedef struct { double x,y; } Pt;

static uint64_t rng_s0, rng_s1;
static inline uint64_t xnext(void){ uint64_t s1=rng_s0; const uint64_t s0=rng_s1; rng_s0=s0; s1^=s1<<23; rng_s1=s1^s0^(s1>>18)^(s0>>5); return rng_s1+rng_s0; }
static void seed_rng(uint64_t s){ rng_s0=s^0x9E3779B97F4A7C15ULL; rng_s1=(s<<1)|1; for(int i=0;i<32;i++)xnext(); }
static inline uint32_t rnd(int m){ return (uint32_t)(xnext()%(uint64_t)m); }
static inline double rndf(void){ return (xnext()>>11)*(1.0/9007199254740992.0); }

static void build_rank(RS*R,int v){ for(int i=0;i<R->n-1;i++) R->rnk[v][R->rot[v][i]]=i; }
static void build_all_rank(RS*R){ for(int v=0;v<R->n;v++) build_rank(R,v); }

/* in rotation at a, starting from b going forward, is c before d? */
static inline int obit(const RS*R,int a,int b,int c,int d){
    int m=R->n-1;
    int dc=(R->rnk[a][c]-R->rnk[a][b]+m)%m;
    int dd=(R->rnk[a][d]-R->rnk[a][b]+m)%m;
    return dc<dd;
}
/* crossing parity of edges (a,b),(c,d): exact on all realizable K4 patterns */
static inline int xpar(const RS*R,int a,int b,int c,int d){
    int sa=obit(R,a,b,c,d), sb=obit(R,b,a,c,d), gc=obit(R,c,a,b,d), gd=obit(R,d,a,b,c);
    return (sa^sb) & (1^(sb^gc)) & (1^(sa^gd));
}
/* tuple oddness (Kleitman-style): 0 on every realizable K4 subsystem */
static inline int tpar(const RS*R,int i,int j,int k,int l){
    return obit(R,i,j,k,l)^obit(R,j,i,k,l)^obit(R,k,i,j,l)^obit(R,l,i,j,k);
}

static void full_eval(RS*R){
    int n=R->n; long c=0, o=0;
    for(int i=0;i<n;i++)for(int j=i+1;j<n;j++)for(int k=j+1;k<n;k++)for(int l=k+1;l<n;l++){
        c+=xpar(R,i,j,k,l)+xpar(R,i,k,j,l)+xpar(R,i,l,j,k);
        o+=tpar(R,i,j,k,l);
    }
    R->count=c; R->odd=o;
}
/* delta-exact: cross terms and odd terms over tuples containing v, canonical arg order */
static void contrib_v(const RS*R,int v,long*cx,long*od){
    int n=R->n; long c=0, o=0;
    for(int w=0;w<n;w++){ if(w==v)continue;
        for(int x=w+1;x<n;x++){ if(x==v)continue;
            for(int y=x+1;y<n;y++){ if(y==v)continue;
                int t[4]={v,w,x,y};
                for(int p=0;p<3;p++)for(int q=p+1;q<4;q++) if(t[p]>t[q]){int tt=t[p];t[p]=t[q];t[q]=tt;}
                int i=t[0],j=t[1],k=t[2],l=t[3];
                c+=xpar(R,i,j,k,l)+xpar(R,i,k,j,l)+xpar(R,i,l,j,k);
                o+=tpar(R,i,j,k,l);
            }
        }
    }
    *cx=c; *od=o;
}
static void random_rs(RS*R){
    int n=R->n;
    for(int v=0;v<n;v++){
        int i=0; for(int x=0;x<n;x++) if(x!=v) R->rot[v][i++]=x;
        for(int i=n-2;i>0;i--){ int j=rnd(i+1); uint8_t t=R->rot[v][i];R->rot[v][i]=R->rot[v][j];R->rot[v][j]=t; }
    }
    build_all_rank(R); full_eval(R);
}

static int orient(Pt a,Pt b,Pt c){ double cr=(b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x); return cr>1e-9?1:(cr<-1e-9?-1:0); }
static int seg_cross(Pt a,Pt b,Pt c,Pt d){ int o1=orient(a,b,c),o2=orient(a,b,d),o3=orient(c,d,a),o4=orient(c,d,b); return (o1*o2<0)&&(o3*o4<0); }
static long geom_crossings(Pt*p,int n){
    long c=0;
    for(int i=0;i<n;i++)for(int j=i+1;j<n;j++)for(int k=j+1;k<n;k++)for(int l=k+1;l<n;l++)
        c+=seg_cross(p[i],p[j],p[k],p[l])+seg_cross(p[i],p[k],p[j],p[l])+seg_cross(p[i],p[l],p[j],p[k]);
    return c;
}
static void rs_from_points(RS*R,Pt*p,int n){
    R->n=n; double ang[MAXN]; int idx[MAXN];
    for(int v=0;v<n;v++){
        int m=0;
        for(int x=0;x<n;x++){ if(x==v)continue; ang[m]=atan2(p[x].y-p[v].y,p[x].x-p[v].x); idx[m]=x; m++; }
        for(int i=1;i<m;i++){ double a=ang[i]; int id=idx[i]; int j=i-1; while(j>=0&&ang[j]>a){ang[j+1]=ang[j];idx[j+1]=idx[j];j--;} ang[j+1]=a;idx[j+1]=id; }
        for(int i=0;i<m;i++) R->rot[v][i]=idx[i];
    }
    build_all_rank(R);
}

static void save_rs(RS*R,const char*path){
    FILE*f=fopen(path,"w"); if(!f)return;
    fprintf(f,"%ld %ld\n",R->count,R->odd);
    for(int v=0;v<R->n;v++){ for(int i=0;i<R->n-1;i++) fprintf(f,"%d ",R->rot[v][i]); fprintf(f,"\n"); }
    fclose(f);
}
static int load_rs(RS*R,int n,int smalln,const char*path){
    FILE*f=fopen(path,"r"); if(!f)return 0;
    R->n=n; long c,o=0; if(fscanf(f,"%ld",&c)!=1){fclose(f);return 0;} fscanf(f,"%ld",&o);
    for(int v=0;v<smalln;v++) for(int i=0;i<smalln-1;i++){ int x; if(fscanf(f,"%d",&x)!=1){fclose(f);return 0;} R->rot[v][i]=x; }
    fclose(f);
    if(smalln==n){ build_all_rank(R); full_eval(R); return 1; }
    int nv=n-1;
    for(int v=0;v<nv;v++){ int pos=rnd(n-1); for(int i=n-2;i>pos;i--) R->rot[v][i]=R->rot[v][i-1]; R->rot[v][pos]=nv; }
    int i=0; for(int x=0;x<nv;x++) R->rot[nv][i++]=x;
    for(int i2=n-2;i2>0;i2--){ int j=rnd(i2+1); uint8_t t=R->rot[nv][i2];R->rot[nv][i2]=R->rot[nv][j];R->rot[nv][j]=t; }
    build_all_rank(R); full_eval(R); return 1;
}

static double now_sec(void){ struct timespec ts; clock_gettime(CLOCK_MONOTONIC,&ts); return ts.tv_sec+ts.tv_nsec*1e-9; }
static void kick(RS*R,int rows){
    for(int k=0;k<rows;k++){ int v=rnd(R->n); for(int i=R->n-2;i>0;i--){int j=rnd(i+1);uint8_t t=R->rot[v][i];R->rot[v][i]=R->rot[v][j];R->rot[v][j]=t;} }
    build_all_rank(R); full_eval(R);
}

static double LAMBDA_LO=2.0, LAMBDA_HI=50.0;
static inline int tpar_t(const RS*R,int i,int j,int k,int l){ return tpar(R,i,j,k,l); }

static void anneal(int n,double seconds,uint64_t seed,const char*logpath,const char*bestpath,const char*seedmode,int smalln){
    seed_rng(seed);
    RS cur,bestf; cur.n=n; bestf.n=n;
    if(seedmode && !strcmp(seedmode,"recti")){
        Pt p[MAXN]; for(int i=0;i<n;i++){ p[i].x=rndf()*10; p[i].y=rndf()*10; }
        rs_from_points(&cur,p,n); full_eval(&cur); kick(&cur,1);
    } else if(seedmode && seedmode[0]!='r' && load_rs(&cur,n,smalln,seedmode)){ kick(&cur,2); }
    else random_rs(&cur);
    bestf=cur; long bestfeas = (cur.odd==0)?cur.count:LONG_MAX; if(cur.odd==0) save_rs(&cur,bestpath);
    FILE*log=fopen(logpath,"a"); if(log) setvbuf(log,NULL,_IOLBF,0);
    double t0=now_sec(), tstart=t0;
    long moves=0, since_improve=0, restarts=0, accepts=0;
    long stuck_limit=3000000;
    double T0=25.0, T1=0.02;
    while(1){
        double t=now_sec();
        if(t-t0>=seconds) break;
        double frac=(t-t0)/seconds;
        double phase=frac*4.0-(double)(int)(frac*4.0);
        double T=T0*pow(T1/T0,phase);
        double LAMBDA=LAMBDA_LO*pow(LAMBDA_HI/LAMBDA_LO,phase);
        int v;
        if(cur.odd>0 && rndf()<0.6){
            /* pick a vertex of a random odd tuple */
            v=rnd(n);
            for(int tr=0;tr<25;tr++){
                int i=rnd(n),j,k,l; do{j=rnd(n);}while(j==i); do{k=rnd(n);}while(k==i||k==j); do{l=rnd(n);}while(l==i||l==j||l==k);
                int s[4]={i,j,k,l}; for(int a=0;a<3;a++)for(int b=a+1;b<4;b++) if(s[a]>s[b]){int tt=s[a];s[a]=s[b];s[b]=tt;}
                if(tpar_t(&cur,s[0],s[1],s[2],s[3])){ v=s[rnd(4)]; break; }
            }
        } else v=rnd(n);
        uint8_t oldrow[MAXN-1]; memcpy(oldrow,cur.rot[v],n-1);
        uint8_t oldrank[MAXN]; memcpy(oldrank,cur.rnk[v],n);
        long cb,ob; contrib_v(&cur,v,&cb,&ob);
        double u=rndf();
        if(u<0.03){ for(int i=n-2;i>0;i--){int j=rnd(i+1);uint8_t tt=cur.rot[v][i];cur.rot[v][i]=cur.rot[v][j];cur.rot[v][j]=tt;} }
        else if(u<0.6){ int i=rnd(n-1),j=rnd(n-1); if(i!=j){ uint8_t x=cur.rot[v][i];
            if(i<j){ for(int k=i;k<j;k++)cur.rot[v][k]=cur.rot[v][k+1]; cur.rot[v][j]=x; }
            else { for(int k=i;k>j;k--)cur.rot[v][k]=cur.rot[v][k-1]; cur.rot[v][j]=x; } } }
        else { int i=rnd(n-1),j=rnd(n-1); if(i>j){int tt=i;i=j;j=tt;} while(i<j){uint8_t tt=cur.rot[v][i];cur.rot[v][i]=cur.rot[v][j];cur.rot[v][j]=tt;i++;j--;} }
        build_rank(&cur,v);
        long ca,oa; contrib_v(&cur,v,&ca,&oa);
        long dc=ca-cb, dod=oa-ob;
        double dobj=(double)dc+LAMBDA*(double)dod;
        if(dobj<=0 || rndf()<exp(-dobj/T)){
            cur.count+=dc; cur.odd+=dod; accepts++;
            if(cur.odd==0 && cur.count<bestfeas){
                bestfeas=cur.count; bestf=cur; save_rs(&bestf,bestpath);
                if(log) fprintf(log,"NEWBEST t=%.1f best=%ld moves=%ld\n",t-t0,bestfeas,moves);
                if(n==13 && bestfeas<=223){ FILE*k=fopen("KILLER","w"); if(k){fprintf(k,"count %ld\n",bestfeas);fclose(k);} }
            }
            if(cur.odd==0 && cur.count<=bestfeas) since_improve=0;
        } else { memcpy(cur.rot[v],oldrow,n-1); memcpy(cur.rnk[v],oldrank,n); }
        moves++; since_improve++;
        if((moves&0x3FFFF)==0 && log) fprintf(log,"LOG t=%.1f cur=%ld odd=%ld best=%ld restarts=%ld acc=%.3f T=%.3g\n",t-t0,cur.count,cur.odd,bestfeas,restarts,moves?(double)accepts/moves:0.0,T);
        if(since_improve>=stuck_limit){
            if(log) fprintf(log,"RESTART t=%.1f min=%ld restarts=%ld\n",t-t0,bestfeas,restarts);
            restarts++; since_improve=0;
            if(bestfeas<LONG_MAX && rndf()<0.6){ cur=bestf; kick(&cur,1); } else { Pt p[MAXN]; for(int i=0;i<n;i++){p[i].x=rndf()*10;p[i].y=rndf()*10;} rs_from_points(&cur,p,n); full_eval(&cur); }
        }
    }
    if(log) fprintf(log,"DONE t=%.1f best=%ld moves=%ld restarts=%ld mps=%.0f\n",now_sec()-tstart,bestfeas,moves,restarts,moves/(now_sec()-tstart));
    if(bestfeas<LONG_MAX) save_rs(&bestf,bestpath);
    if(log) fclose(log);
}

static void anneal_rect(int n,double seconds,uint64_t seed,const char*logpath,const char*bestpath){
    seed_rng(seed);
    Pt p[MAXN],bp[MAXN]; RS R; R.n=n;
    for(int i=0;i<n;i++){ p[i].x=rndf()*10; p[i].y=rndf()*10; }
    rs_from_points(&R,p,n); full_eval(&R);
    long cur=R.count,best=cur; memcpy(bp,p,sizeof(p));
    FILE*log=fopen(logpath,"a"); if(log) setvbuf(log,NULL,_IOLBF,0);
    double t0=now_sec();
    long moves=0;
    while(1){
        double t=now_sec();
        if(t-t0>=seconds) break;
        double frac=(t-t0)/seconds;
        double phase=frac*4.0-(double)(int)(frac*4.0);
        double T=8.0*pow(0.005/8.0,phase);
        double step=2.0*pow(0.01/2.0,frac);
        int i=rnd(n);
        double ox=p[i].x,oy=p[i].y;
        p[i].x+=step*(rndf()*2-1); p[i].y+=step*(rndf()*2-1);
        rs_from_points(&R,p,n); full_eval(&R);
        long delta=R.count-cur;
        if(delta<=0 || rndf()<exp(-(double)delta/T)){
            cur=R.count;
            if(cur<best){ best=cur; memcpy(bp,p,sizeof(p));
                FILE*f=fopen(bestpath,"w"); if(f){ fprintf(f,"%ld 0\n",best); for(int v=0;v<n;v++){for(int k=0;k<n-1;k++)fprintf(f,"%d ",R.rot[v][k]);fprintf(f,"\n");} fclose(f); }
                if(log) fprintf(log,"NEWBEST t=%.1f best=%ld moves=%ld\n",t-t0,best,moves);
            }
        } else { p[i].x=ox; p[i].y=oy; }
        moves++;
        if((moves&0xFFFF)==0 && log) fprintf(log,"LOG t=%.1f cur=%ld best=%ld T=%.3g step=%.3g\n",t-t0,cur,best,T,step);
    }
    if(log) fprintf(log,"DONE t=%.1f best=%ld moves=%ld mps=%.0f\n",now_sec()-t0,best,moves,moves/(now_sec()-t0));
    if(log) fclose(log);
}

/* ===== allowable-sequence (pseudolinear) lane ===== */
#define MAXM 120
typedef struct { int n,M; uint8_t sw[MAXM][2]; int pos[MAXN][MAXN]; } AS;

static void as_build_pos(AS*A){
    for(int i=0;i<A->n;i++)for(int j=0;j<A->n;j++)A->pos[i][j]=-1;
    for(int t=0;t<A->M;t++){ int a=A->sw[t][0],b=A->sw[t][1]; A->pos[a][b]=t; A->pos[b][a]=t; }
}
static void as_from_points(AS*A,Pt*pt,int n){
    /* relabel points by x-order so chi rule applies */
    int ord[MAXN]; for(int i=0;i<n;i++)ord[i]=i;
    for(int i=1;i<n;i++){ int o=ord[i]; int j=i-1; while(j>=0&&pt[ord[j]].x>pt[o].x){ord[j+1]=ord[j];j--;} ord[j+1]=o; }
    double nx[MAXN],ny[MAXN];
    for(int i=0;i<n;i++){ nx[i]=pt[ord[i]].x; ny[i]=pt[ord[i]].y; }
    A->n=n; A->M=n*(n-1)/2;
    double sl[MAXM]; int m=0;
    for(int i=0;i<n;i++)for(int j=i+1;j<n;j++){ A->sw[m][0]=i; A->sw[m][1]=j; sl[m]=(ny[j]-ny[i])/(nx[j]-nx[i]); m++; }
    for(int i=1;i<m;i++){ double s=sl[i]; uint8_t a=A->sw[i][0],b=A->sw[i][1]; int j=i-1;
        while(j>=0&&sl[j]>s){ sl[j+1]=sl[j]; A->sw[j+1][0]=A->sw[j][0]; A->sw[j+1][1]=A->sw[j][1]; j--; }
        sl[j+1]=s; A->sw[j+1][0]=a; A->sw[j+1][1]=b; }
    as_build_pos(A);
}
/* chirotope sign of triple (a,b,c): antisymmetric */
static inline int chi3(AS*A,int a,int b,int c){
    int s[3]={a,b,c},inv=0;
    if(s[0]>s[1]){int t=s[0];s[0]=s[1];s[1]=t;inv++;}
    if(s[1]>s[2]){int t=s[1];s[1]=s[2];s[2]=t;inv++;}
    if(s[0]>s[1]){int t=s[0];s[0]=s[1];s[1]=t;inv++;}
    int v = A->pos[s[0]][s[1]] < A->pos[s[1]][s[2]];
    return (inv&1) ? 1-v : v;
}
static inline int ascross(AS*A,int a,int b,int c,int d){
    return (chi3(A,a,b,c)^chi3(A,a,b,d)) & (chi3(A,c,d,a)^chi3(A,c,d,b));
}
static long as_count(AS*A){
    int n=A->n; long c=0;
    for(int i=0;i<n;i++)for(int j=i+1;j<n;j++)for(int k=j+1;k<n;k++)for(int l=k+1;l<n;l++)
        c+=ascross(A,i,j,k,l)+ascross(A,i,k,j,l)+ascross(A,i,l,j,k);
    return c;
}
/* triangle flip at position t: valid iff swaps t..t+2 involve exactly 3 lines; flip reverses them */
static int as_flip(AS*A,int t){
    int x[A->M?3:3]; x[0]=A->sw[t][0];x[1]=A->sw[t][1];
    int lbl[4]; lbl[0]=A->sw[t][0];lbl[1]=A->sw[t][1];lbl[2]=A->sw[t+1][0];lbl[3]=A->sw[t+1][1];
    int u1=A->sw[t+1][0],v1=A->sw[t+1][1],u2=A->sw[t+2][0],v2=A->sw[t+2][1];
    int d[6]={A->sw[t][0],A->sw[t][1],u1,v1,u2,v2};
    int uniq[3],nu=0;
    for(int i=0;i<6;i++){ int f=0; for(int j=0;j<nu;j++) if(uniq[j]==d[i]){f=1;break;} if(!f){ if(nu>=3) return 0; uniq[nu++]=d[i]; } }
    if(nu!=3) return 0;
    uint8_t a0=A->sw[t][0],b0=A->sw[t][1],a2=A->sw[t+2][0],b2=A->sw[t+2][1];
    A->sw[t][0]=a2;A->sw[t][1]=b2;A->sw[t+2][0]=a0;A->sw[t+2][1]=b0;
    A->pos[a2][b2]=t;A->pos[b2][a2]=t;A->pos[a0][b0]=t+2;A->pos[b0][a0]=t+2;
    (void)x;(void)lbl;
    return 1;
}
static void as_save(AS*A,long best,const char*path){
    FILE*f=fopen(path,"w"); if(!f)return;
    fprintf(f,"%ld 0\n",best);
    for(int t=0;t<A->M;t++) fprintf(f,"%d %d\n",A->sw[t][0],A->sw[t][1]);
    fclose(f);
}
static void anneal_as(int n,double seconds,uint64_t seed,const char*logpath,const char*bestpath){
    seed_rng(seed);
    AS A,B; Pt p[MAXN];
    for(int i=0;i<n;i++){ p[i].x=i*3.0+rndf(); p[i].y=rndf()*10; }
    as_from_points(&A,p,n);
    long cur=as_count(&A),best=cur; B=A;
    FILE*log=fopen(logpath,"a"); if(log) setvbuf(log,NULL,_IOLBF,0);
    double t0=now_sec();
    long moves=0,since_improve=0,restarts=0;
    long stuck_limit=2000000;
    while(1){
        double t=now_sec();
        if(t-t0>=seconds) break;
        double frac=(t-t0)/seconds;
        double phase=frac*4.0-(double)(int)(frac*4.0);
        double T=6.0*pow(0.004/6.0,phase);
        int tt=rnd(A.M-2),tr;
        for(tr=0;tr<8;tr++){ tt=rnd(A.M-2); int u1=A.sw[tt][0],v1=A.sw[tt][1];
            int cnt=0; int seen[6]={u1,v1,A.sw[tt+1][0],A.sw[tt+1][1],A.sw[tt+2][0],A.sw[tt+2][1]};
            int un[3],nu=0,ok=1;
            for(int i=0;i<6;i++){ int f=0; for(int j=0;j<nu;j++) if(un[j]==seen[i]){f=1;break;} if(!f){ if(nu>=3){ok=0;break;} un[nu++]=seen[i]; } }
            if(ok&&nu==3){ cnt=1; break; }
        }
        if(!as_flip(&A,tt)){ moves++; since_improve++; continue; }
        long nc=as_count(&A);
        long delta=nc-cur;
        if(delta<=0 || rndf()<exp(-(double)delta/T)){
            cur=nc;
            if(cur<best){ best=cur; B=A; as_save(&B,best,bestpath);
                if(log) fprintf(log,"NEWBEST t=%.1f best=%ld moves=%ld\n",t-t0,best,moves);
                if(n==13 && best<=223){ FILE*k=fopen("KILLER","w"); if(k){fprintf(k,"count %ld (pseudolinear)\n",best);fclose(k);} }
            }
            since_improve=0;
        } else { /* revert flip */ as_flip(&A,tt); }
        moves++; since_improve++;
        if((moves&0x3FFFF)==0 && log) fprintf(log,"LOG t=%.1f cur=%ld best=%ld restarts=%ld T=%.3g\n",t-t0,cur,best,restarts,T);
        if(since_improve>=stuck_limit){
            if(log) fprintf(log,"RESTART t=%.1f min=%ld restarts=%ld\n",t-t0,best,restarts);
            restarts++; since_improve=0;
            if(rndf()<0.5){ A=B; cur=best; for(int k=0;k<6;k++){ int t2=rnd(A.M-2); as_flip(&A,t2);} cur=as_count(&A); }
            else { for(int i=0;i<n;i++){ p[i].x=i*3.0+rndf(); p[i].y=rndf()*10; } as_from_points(&A,p,n); cur=as_count(&A); }
        }
    }
    if(log) fprintf(log,"DONE t=%.1f best=%ld moves=%ld restarts=%ld mps=%.0f\n",now_sec()-t0,best,moves,restarts,moves/(now_sec()-t0));
    as_save(&B,best,bestpath);
    if(log) fclose(log);
}

/* ===== allowable-sequence lane v2: swap-list state, exact Ringel R3 moves ===== */
typedef struct { int n,M; uint8_t sw[MAXM][2]; int pos[MAXN][MAXN]; } AS2;
static void as2_build_pos(AS2*A){
    for(int i=0;i<A->n;i++)for(int j=0;j<A->n;j++)A->pos[i][j]=-1;
    for(int t=0;t<A->M;t++){ int a=A->sw[t][0],b=A->sw[t][1]; A->pos[a][b]=t; A->pos[b][a]=t; }
}
static void as2_from_points(AS2*A,Pt*pt,int n){
    int ord[MAXN]; for(int i=0;i<n;i++)ord[i]=i;
    for(int i=1;i<n;i++){ int o=ord[i]; int j=i-1; while(j>=0&&pt[ord[j]].x>pt[o].x){ord[j+1]=ord[j];j--;} ord[j+1]=o; }
    double nx[MAXN],ny[MAXN];
    for(int i=0;i<n;i++){ nx[i]=pt[ord[i]].x; ny[i]=pt[ord[i]].y; }
    A->n=n; A->M=n*(n-1)/2;
    double sl[MAXM]; int m=0;
    for(int i=0;i<n;i++)for(int j=i+1;j<n;j++){ A->sw[m][0]=i; A->sw[m][1]=j; sl[m]=(ny[j]-ny[i])/(nx[j]-nx[i]); m++; }
    for(int i=1;i<m;i++){ double s=sl[i]; uint8_t a=A->sw[i][0],b=A->sw[i][1]; int j=i-1;
        while(j>=0&&sl[j]>s){ sl[j+1]=sl[j]; A->sw[j+1][0]=A->sw[j][0]; A->sw[j+1][1]=A->sw[j][1]; j--; }
        sl[j+1]=s; A->sw[j+1][0]=a; A->sw[j+1][1]=b; }
    as2_build_pos(A);
}
static inline int chi3_2(AS2*A,int a,int b,int c){
    int s[3]={a,b,c},inv=0;
    if(s[0]>s[1]){int t=s[0];s[0]=s[1];s[1]=t;inv++;}
    if(s[1]>s[2]){int t=s[1];s[1]=s[2];s[2]=t;inv++;}
    if(s[0]>s[1]){int t=s[0];s[0]=s[1];s[1]=t;inv++;}
    int v = A->pos[s[0]][s[1]] < A->pos[s[1]][s[2]];
    return (inv&1) ? 1-v : v;
}
static inline int ascross2(AS2*A,int a,int b,int c,int d){
    return (chi3_2(A,a,b,c)^chi3_2(A,a,b,d)) & (chi3_2(A,c,d,a)^chi3_2(A,c,d,b));
}
static long as2_count(AS2*A){
    int n=A->n; long c=0;
    for(int i=0;i<n;i++)for(int j=i+1;j<n;j++)for(int k=j+1;k<n;k++)for(int l=k+1;l<n;l++)
        c+=ascross2(A,i,j,k,l)+ascross2(A,i,k,j,l)+ascross2(A,i,l,j,k);
    return c;
}
static long contrib3_2(AS2*A,int x,int y,int z){
    int n=A->n; long c=0;
    for(int w=0;w<n;w++){ if(w==x||w==y||w==z)continue;
        c+=ascross2(A,x,y,z,w)+ascross2(A,x,z,y,w)+ascross2(A,x,w,y,z);
    }
    return c;
}
/* check empty-triangle condition via along-line consecutiveness */
static int as2_empty(AS2*A,int x,int y,int z){
    int n=A->n;
    /* for line x: crossings with y,z must be adjacent among x-crossings, i.e. no x-w crossing
       with time between pos[x][y] and pos[x][z]; similarly cyclic */
    int txy=A->pos[x][y], txz=A->pos[x][z], tyz=A->pos[y][z];
    for(int w=0;w<n;w++){ if(w==x||w==y||w==z)continue;
        int txw=A->pos[x][w]; if((txw>txy)!=(txw>txz)) return 0;
        int tyw=A->pos[y][w]; if((tyw>txy)!=(tyw>tyz)) return 0;
        int tzw=A->pos[z][w]; if((tzw>txz)!=(tzw>tyz)) return 0;
    }
    return 1;
}
/* perform the R3 flip on the swap list: reverse the three triangle swaps, commute window spectators after them */
static void as2_flip(AS2*A,int x,int y,int z){
    int M=A->M;
    int txy=A->pos[x][y], txz=A->pos[x][z], tyz=A->pos[y][z];
    int t1=txy,t3=txy;
    if(txz<t1)t1=txz; if(tyz<t1)t1=tyz;
    if(txz>t3)t3=txz; if(tyz>t3)t3=tyz;
    uint8_t newspec[MAXM][2]; int ns=0;
    uint8_t tri[3][2]; int nt=0;
    for(int t=t1;t<=t3;t++){
        int a=A->sw[t][0],b=A->sw[t][1];
        int istri=(a==x||a==y||a==z)&&(b==x||b==y||b==z);
        if(istri){ tri[nt][0]=a; tri[nt][1]=b; nt++; }
        else { newspec[ns][0]=a; newspec[ns][1]=b; ns++; }
    }
    /* write back: reversed triple, then spectators */
    int t=t1;
    for(int i=2;i>=0;i--){ A->sw[t][0]=tri[i][0]; A->sw[t][1]=tri[i][1]; t++; }
    for(int i=0;i<ns;i++){ A->sw[t][0]=newspec[i][0]; A->sw[t][1]=newspec[i][1]; t++; }
    as2_build_pos(A);
}
static void as2_save(AS2*A,long best,const char*path){
    FILE*f=fopen(path,"w"); if(!f)return;
    fprintf(f,"%ld 0\n",best);
    for(int t=0;t<A->M;t++) fprintf(f,"%d %d\n",A->sw[t][0],A->sw[t][1]);
    fclose(f);
}
static void anneal_as2(int n,double seconds,uint64_t seed,const char*logpath,const char*bestpath){
    seed_rng(seed);
    AS2 A,B; Pt p[MAXN];
    for(int i=0;i<n;i++){ p[i].x=i*3.0+rndf(); p[i].y=rndf()*10; }
    as2_from_points(&A,p,n);
    long cur=as2_count(&A),best=cur; B=A;
    FILE*log=fopen(logpath,"a"); if(log) setvbuf(log,NULL,_IOLBF,0);
    double t0=now_sec();
    long moves=0,since_improve=0,restarts=0,flipsok=0;
    long stuck_limit=8000000;
    while(1){
        double t=now_sec();
        if(t-t0>=seconds) break;
        double frac=(t-t0)/seconds;
        double phase=frac*4.0-(double)(int)(frac*4.0);
        double T=6.0*pow(0.004/6.0,phase);
        int x=rnd(n),y,z; do{y=rnd(n);}while(y==x); do{z=rnd(n);}while(z==x||z==y);
        if(!as2_empty(&A,x,y,z)){ moves++; since_improve++; continue; }
        flipsok++;
        long cb=contrib3_2(&A,x,y,z);
        as2_flip(&A,x,y,z);
        long ca=contrib3_2(&A,x,y,z);
        long delta=ca-cb;
        if(delta<=0 || rndf()<exp(-(double)delta/T)){
            cur+=delta;
            if(cur<best){ best=cur; B=A; as2_save(&B,best,bestpath);
                if(log) fprintf(log,"NEWBEST t=%.1f best=%ld moves=%ld\n",t-t0,best,moves);
                if(n==13 && best<=223){ FILE*k=fopen("KILLER","w"); if(k){fprintf(k,"count %ld (pseudolinear ringel)\n",best);fclose(k);} }
            }
            since_improve=0;
        } else as2_flip(&A,x,y,z);
        moves++; since_improve++;
        if((moves&0x3FFFF)==0 && log) fprintf(log,"LOG t=%.1f cur=%ld best=%ld restarts=%ld fok=%ld T=%.3g\n",t-t0,cur,best,restarts,flipsok,T);
        if(since_improve>=stuck_limit){
            if(log) fprintf(log,"RESTART t=%.1f min=%ld restarts=%ld\n",t-t0,best,restarts);
            restarts++; since_improve=0;
            if(rndf()<0.5){ A=B; cur=best;
                for(int kk=0;kk<20;kk++){ int a2=rnd(n),b2,c2; do{b2=rnd(n);}while(b2==a2); do{c2=rnd(n);}while(c2==a2||c2==b2);
                    if(as2_empty(&A,a2,b2,c2)){ long d0=contrib3_2(&A,a2,b2,c2); as2_flip(&A,a2,b2,c2); cur+=contrib3_2(&A,a2,b2,c2)-d0; } }
            } else { for(int i=0;i<n;i++){ p[i].x=i*3.0+rndf(); p[i].y=rndf()*10; } as2_from_points(&A,p,n); cur=as2_count(&A); }
        }
    }
    if(log) fprintf(log,"DONE t=%.1f best=%ld moves=%ld restarts=%ld fok=%ld mps=%.0f\n",now_sec()-t0,best,moves,restarts,flipsok,moves/(now_sec()-t0));
    as2_save(&B,best,bestpath);
    if(log) fclose(log);
}

/* ===== env config helpers ===== */
static double env_d(const char*nm,double d){ const char*s=getenv(nm); return s?atof(s):d; }
static long env_l(const char*nm,long d){ const char*s=getenv(nm); return s?atol(s):d; }

static int as2_load(AS2*A,int n,const char*path){
    FILE*f=fopen(path,"r"); if(!f)return 0;
    long c,o; if(fscanf(f,"%ld %ld",&c,&o)!=2){fclose(f);return 0;}
    A->n=n; A->M=n*(n-1)/2;
    for(int t=0;t<A->M;t++){ int a,b; if(fscanf(f,"%d %d",&a,&b)!=2){fclose(f);return 0;} A->sw[t][0]=a;A->sw[t][1]=b; }
    fclose(f); as2_build_pos(A); return 1;
}

/* ===== 2-page (Harary-Hill) seed construction ===== */
static int hh_mask, hh_n;
static int page2p(int i,int j){ /* i<j; upper=1 lower=0; circular distance classes, bit c of mask = upper */
    int d=j-i; int c=d<hh_n-d?d:hh_n-d;
    return (hh_mask>>c)&1;
}
static int truth_pair(int a,int b,int c,int d){ /* edges (a,b),(c,d), a<b, c<d, distinct */
    if(page2p(a,b)!=page2p(c,d)) return 0;
    return (a<c&&c<b&&b<d)||(c<a&&a<d&&d<b);
}
static int truth_pair_g(int a,int b,int c,int d);
static int CHI[16][16][16];
static int chio(int a,int b,int c){
    int s0=a,s1=b,s2=c,inv=0,t;
    if(s0>s1){t=s0;s0=s1;s1=t;inv++;}
    if(s1>s2){t=s1;s1=s2;s2=t;inv++;}
    if(s0>s1){t=s0;s0=s1;s1=t;inv++;}
    int v=CHI[s0][s1][s2];
    return (inv&1)?1-v:v;
}
static int crossc(int a,int b,int c,int d){
    return (chio(a,b,c)^chio(a,b,d))&(chio(c,d,a)^chio(c,d,b));
}
static int tup_mis(int w,int x,int y,int z){
    int m=0;
    if(crossc(w,x,y,z)!=truth_pair_g(w,x,y,z)) m++;
    if(crossc(w,y,x,z)!=truth_pair_g(w,y,x,z)) m++;
    if(crossc(w,z,x,y)!=truth_pair_g(w,z,x,y)) m++;
    return m;
}
static long total_mis(int n){
    long m=0;
    for(int w=0;w<n;w++)for(int x=w+1;x<n;x++)for(int y=x+1;y<n;y++)for(int z=y+1;z<n;z++) m+=tup_mis(w,x,y,z);
    return m;
}
static long flip_delta(int n,int i,int j,int k){
    long before=0,after=0;
    for(int l=0;l<n;l++){ if(l==i||l==j||l==k)continue;
        int s[4]={i,j,k,l}; for(int a=0;a<3;a++)for(int b=a+1;b<4;b++) if(s[a]>s[b]){int t=s[a];s[a]=s[b];s[b]=t;}
        before+=tup_mis(s[0],s[1],s[2],s[3]);
    }
    CHI[i][j][k]^=1;
    for(int l=0;l<n;l++){ if(l==i||l==j||l==k)continue;
        int s[4]={i,j,k,l}; for(int a=0;a<3;a++)for(int b=a+1;b<4;b++) if(s[a]>s[b]){int t=s[a];s[a]=s[b];s[b]=t;}
        after+=tup_mis(s[0],s[1],s[2],s[3]);
    }
    CHI[i][j][k]^=1;
    return after-before;
}
static int PG[16][16]; static int pg_mode=0;
static int greedy_build(AS2*A,int n,uint64_t seed);
static int S1(int v){ return v+v-1; }
static int gp_viol5(int a,int b,int c,int d,int e){ /* sorted 5-tuple, 3-term GP */
    int t1=S1(chio(a,b,c))*S1(chio(a,d,e));
    int t2=-S1(chio(a,b,d))*S1(chio(a,c,e));
    int t3=S1(chio(a,b,e))*S1(chio(a,c,d));
    return (t1==t2 && t2==t3)?1:0;
}
static long gp_total(int n){
    long g=0;
    for(int a=0;a<n;a++)for(int b=a+1;b<n;b++)for(int c=b+1;c<n;c++)for(int d=c+1;d<n;d++)for(int e=d+1;e<n;e++)
        g+=gp_viol5(a,b,c,d,e);
    return g;
}
static long gp_flip_delta(int n,int i,int j,int k){
    long before=0,after=0;
    for(int l=0;l<n;l++){ if(l==i||l==j||l==k)continue;
        for(int m=l+1;m<n;m++){ if(m==i||m==j||m==k)continue;
            int s[5]={i,j,k,l,m}; for(int a=0;a<4;a++)for(int b=a+1;b<5;b++) if(s[a]>s[b]){int t=s[a];s[a]=s[b];s[b]=t;}
            before+=gp_viol5(s[0],s[1],s[2],s[3],s[4]);
        }
    }
    CHI[i][j][k]^=1;
    for(int l=0;l<n;l++){ if(l==i||l==j||l==k)continue;
        for(int m=l+1;m<n;m++){ if(m==i||m==j||m==k)continue;
            int s[5]={i,j,k,l,m}; for(int a=0;a<4;a++)for(int b=a+1;b<5;b++) if(s[a]>s[b]){int t=s[a];s[a]=s[b];s[b]=t;}
            after+=gp_viol5(s[0],s[1],s[2],s[3],s[4]);
        }
    }
    CHI[i][j][k]^=1;
    return after-before;
}
static int solve_chi(int n){
    for(int init=0;init<30;init++){
        for(int i=0;i<n;i++)for(int j=i+1;j<n;j++)for(int k=j+1;k<n;k++){
            int v;
            switch(init){
                case 0: if(pg_mode) v=!(PG[i][k]==1&&PG[j][k]==1); else v=page2p(i,k); break;
                case 1: v=!page2p(i,k); break;
                case 2: v=page2p(i,j); break;
                case 3: v=!page2p(i,j); break;
                case 4: v=page2p(j,k); break;
                case 5: v=!page2p(j,k); break;
                case 6: v=1; break;
                case 7: v=0; break;
                case 8: if(pg_mode){ v=!(PG[i][k]==1&&PG[j][k]==1); if(rnd(100)<8) v^=1; } else v=rnd(2); break;
                case 9: if(pg_mode){ v=!(PG[i][k]==1&&PG[j][k]==1); if(rnd(100)<20) v^=1; } else v=rnd(2); break;
                default: v=rnd(2); break;
            }
            CHI[i][j][k]=v;
        }
        long mis=total_mis(n);
        long gp=gp_total(n); long obj=mis+gp;
        long it=0,budget=env_l("CHI_BUDGET",3000000);
        double T0=env_d("CHI_T",1.5);
        while(!(mis==0&&gp==0) && it++<budget){
            double TT=T0*(1.0-(double)it/budget)+0.02;
            int i=rnd(n),j,k; do{j=rnd(n);}while(j==i); do{k=rnd(n);}while(k==i||k==j);
            int a=i,b=j,c=k,t; if(a>b){t=a;a=b;b=t;} if(b>c){t=b;b=c;c=t;} if(a>b){t=a;a=b;b=t;}
            long d=flip_delta(n,a,b,c)+gp_flip_delta(n,a,b,c);
            if(d<=0 || rndf()<exp(-(double)d/TT)){ CHI[a][b][c]^=1; mis=total_mis(n); gp=gp_total(n); obj=mis+gp; }
            (void)obj;
            if(mis==0){
                /* zero pattern-mismatch: check OM-realizability via greedy build */
                AS2 tmp;
                if(greedy_build(&tmp,n,9000+init*37+(long)it)){ return 0; }
                /* fake solution: perturb and continue */
                for(int q=0;q<4;q++){ int i2=rnd(n),j2,k2; do{j2=rnd(n);}while(j2==i2); do{k2=rnd(n);}while(k2==i2||k2==j2);
                    int a2=i2,b2=j2,c2=k2,t2; if(a2>b2){t2=a2;a2=b2;b2=t2;} if(b2>c2){t2=b2;b2=c2;c2=t2;} if(a2>b2){t2=a2;a2=b2;b2=t2;}
                    CHI[a2][b2][c2]^=1; }
                mis=total_mis(n); gp=gp_total(n);
            }
        }
        if(mis==0&&gp==0){ AS2 tmp; if(greedy_build(&tmp,n,77777+init)) return 0; }
    }
    return -1;
}
static int GB_n, GB_M, GB_id[16][16];
static int GB_succ[MAXM][16], GB_scnt[MAXM], GB_indeg[MAXM], GB_height[MAXM];
static int GB_perm[16], GB_done[MAXM], GB_ind[MAXM];
static uint8_t GB_sw[MAXM][2];
static long GB_nodes, GB_budget;
static int gb_dfs(int t){
    if(t==GB_M) return 1;
    if(--GB_budget<=0) return 0;
    int n=GB_n;
    /* collect adjacent free pairs */
    int cand[16],nc=0;
    for(int p=0;p<n-1;p++){
        int x=GB_perm[p],y=GB_perm[p+1]; int lo=x<y?x:y, hi=x<y?y:x;
        int e=GB_id[lo][hi];
        if(!GB_done[e] && GB_ind[e]==0) cand[nc++]=p;
    }
    if(nc==0) return 0;
    /* order by height descending, random tiebreak via shuffle */
    for(int i=0;i<nc;i++){ int r=i+rnd(nc-i); int tt=cand[i];cand[i]=cand[r];cand[r]=tt; }
    /* insertion sort by height desc (nc small) */
    for(int i=1;i<nc;i++){ int c=cand[i]; int e0=GB_id[GB_perm[c]<GB_perm[c+1]?GB_perm[c]:GB_perm[c+1]][GB_perm[c]<GB_perm[c+1]?GB_perm[c+1]:GB_perm[c]];
        int h=GB_height[e0]; int j=i-1;
        while(j>=0){ int cj=cand[j]; int ej=GB_id[GB_perm[cj]<GB_perm[cj+1]?GB_perm[cj]:GB_perm[cj+1]][GB_perm[cj]<GB_perm[cj+1]?GB_perm[cj+1]:GB_perm[cj]]; if(GB_height[ej]>=h)break; cand[j+1]=cand[j]; j--; }
        cand[j+1]=c; }
    for(int ci=0;ci<nc;ci++){
        int p=cand[ci];
        int x=GB_perm[p],y=GB_perm[p+1]; int lo=x<y?x:y, hi=x<y?y:x;
        int e=GB_id[lo][hi];
        GB_sw[t][0]=lo; GB_sw[t][1]=hi;
        GB_done[e]=1;
        for(int s=0;s<GB_scnt[e];s++) GB_ind[GB_succ[e][s]]--;
        GB_perm[p]=y; GB_perm[p+1]=x;
        if(gb_dfs(t+1)) return 1;
        GB_perm[p]=x; GB_perm[p+1]=y;
        for(int s=0;s<GB_scnt[e];s++) GB_ind[GB_succ[e][s]]++;
        GB_done[e]=0;
        GB_nodes++;
        if(GB_budget<=0) return 0;
    }
    return 0;
}
static int greedy_build(AS2*A,int n,uint64_t seed){
    int M=n*(n-1)/2;
    GB_n=n; GB_M=M;
    int m=0;
    for(int i=0;i<n;i++)for(int j=i+1;j<n;j++){ GB_id[i][j]=m; m++; }
    for(int i=0;i<M;i++){GB_scnt[i]=0;GB_indeg[i]=0;}
    for(int i=0;i<n;i++)for(int j=i+1;j<n;j++)for(int k=j+1;k<n;k++){
        int u=GB_id[i][j], v=GB_id[j][k];
        if(CHI[i][j][k]){ GB_succ[u][GB_scnt[u]++]=v; GB_indeg[v]++; }
        else { GB_succ[v][GB_scnt[v]++]=u; GB_indeg[u]++; }
    }
    /* heights: longest path to sink, via repeated relaxation on DAG (topo by BFS) */
    int topo[MAXM], nt=0; int ind0[MAXM]; memcpy(ind0,GB_indeg,sizeof(int)*M);
    /* Kahn */
    int q[MAXM],qh=0,qt=0;
    for(int i=0;i<M;i++) if(ind0[i]==0) q[qt++]=i;
    while(qh<qt){ int u=q[qh++]; topo[nt++]=u; for(int s=0;s<GB_scnt[u];s++){ int v=GB_succ[u][s]; if(--ind0[v]==0) q[qt++]=v; } }
    if(nt<M) return 0; /* cycle: chi not a valid OM */
    for(int i=0;i<M;i++) GB_height[i]=0;
    for(int i=nt-1;i>=0;i--){ int u=topo[i]; for(int s=0;s<GB_scnt[u];s++){ int v=GB_succ[u][s]; if(GB_height[v]+1>GB_height[u]) GB_height[u]=GB_height[v]+1; } }
    seed_rng(seed);
    for(int attempt=0;attempt<200;attempt++){
        for(int i=0;i<n;i++)GB_perm[i]=i;
        if(attempt>=2){ for(int i=n-1;i>0;i--){ int r=rnd(i+1); int tt=GB_perm[i];GB_perm[i]=GB_perm[r];GB_perm[r]=tt; } }
        if(attempt==1){ for(int i=0;i<n/2;i++){ int tt=GB_perm[i];GB_perm[i]=GB_perm[n-1-i];GB_perm[n-1-i]=tt; } }
        memcpy(GB_ind,GB_indeg,sizeof(int)*M);
        memset(GB_done,0,sizeof(int)*M);
        GB_budget=200000; GB_nodes=0;
        if(gb_dfs(0)){
            for(int t=0;t<M;t++){ A->sw[t][0]=GB_sw[t][0]; A->sw[t][1]=GB_sw[t][1]; }
            A->n=n; A->M=M; as2_build_pos(A); return 1;
        }
    }
    return 0;
}
static Pt GEO_P[MAXN]; static int geo_mode=0;
static int truth_pair_g(int a,int b,int c,int d){
    if(pg_mode){
        if(PG[a][b]!=PG[c][d]) return 0;
        return (a<c&&c<b&&b<d)||(c<a&&a<d&&d<b);
    }
    if(geo_mode){
        double x1=GEO_P[a].x,y1=GEO_P[a].y,x2=GEO_P[b].x,y2=GEO_P[b].y;
        double x3=GEO_P[c].x,y3=GEO_P[c].y,x4=GEO_P[d].x,y4=GEO_P[d].y;
        double d1=(x2-x1)*(y3-y1)-(y2-y1)*(x3-x1);
        double d2=(x2-x1)*(y4-y1)-(y2-y1)*(x4-x1);
        double d3=(x4-x3)*(y1-y3)-(y4-y3)*(x1-x3);
        double d4=(x4-x3)*(y2-y3)-(y4-y3)*(x2-x3);
        return ((d1>0)!=(d2>0)) && ((d3>0)!=(d4>0));
    }
    return truth_pair(a,b,c,d);
}
static void hhgeo_run(int n,int trials){
    seed_rng(31337+n);
    int solveok=0,greedyok=0,verok=0;
    for(int t=0;t<trials;t++){
        for(int i=0;i<n;i++){ GEO_P[i].x=rndf()*10; GEO_P[i].y=rndf()*10; }
        int deg=0;
        for(int i=0;i<n&&!deg;i++)for(int j=i+1;j<n&&!deg;j++)for(int k=j+1;k<n&&!deg;k++) if(!orient(GEO_P[i],GEO_P[j],GEO_P[k])) deg=1;
        if(deg){ t--; continue; }
        for(int i=1;i<n;i++){ Pt q=GEO_P[i]; int j=i-1; while(j>=0&&GEO_P[j].x>q.x){GEO_P[j+1]=GEO_P[j];j--;} GEO_P[j+1]=q; }
        geo_mode=1;
        long gc=geom_crossings(GEO_P,n);
        if(solve_chi(n)!=0){ geo_mode=0; continue; }
        geo_mode=0;
        solveok++;
        AS2 A; if(!greedy_build(&A,n,999+t)){ continue; }
        greedyok++;
        if(as2_count(&A)==gc) verok++;
    }
    printf("hhgeo n=%d trials=%d solveok=%d greedyok=%d verok=%d\n",n,trials,solveok,greedyok,verok);
}
static void geodbg_run(int n,uint64_t seed){
    seed_rng(seed);
    for(int i=0;i<n;i++){ GEO_P[i].x=rndf()*10; GEO_P[i].y=rndf()*10; }
    int deg=0;
    for(int i=0;i<n&&!deg;i++)for(int j=i+1;j<n&&!deg;j++)for(int k=j+1;k<n&&!deg;k++) if(!orient(GEO_P[i],GEO_P[j],GEO_P[k])) deg=1;
    if(deg){ printf("degenerate\n"); return; }
    for(int i=1;i<n;i++){ Pt q=GEO_P[i]; int j=i-1; while(j>=0&&GEO_P[j].x>q.x){GEO_P[j+1]=GEO_P[j];j--;} GEO_P[j+1]=q; }
    for(int i=0;i<n;i++)for(int j=i+1;j<n;j++)for(int k=j+1;k<n;k++)
        CHI[i][j][k]=orient(GEO_P[i],GEO_P[j],GEO_P[k])>0?1:0;
    AS2 A; int ok=greedy_build(&A,n,42);
    printf("greedy ok=%d\n",ok);
    if(!ok) return;
    printf("sw:"); for(int t=0;t<A.M;t++) printf(" %d%d",A.sw[t][0],A.sw[t][1]); printf("\n");
    printf("CHI012=%d CHI013=%d CHI014=%d CHI123=%d CHI345=%d\n",CHI[0][1][2],CHI[0][1][3],CHI[0][1][4],CHI[1][2][3],n>4?CHI[3][4][5]:-1);
    printf("pos01=%d pos02=%d pos12=%d pos13=%d pos23=%d\n",A.pos[0][1],A.pos[0][2],A.pos[1][2],A.pos[1][3],A.pos[2][3]);
    { long mis2=0; for(int w=0;w<n;w++)for(int x=w+1;x<n;x++)for(int y=x+1;y<n;y++)for(int z=y+1;z<n;z++){
        int cr=(chi3_2(&A,w,x,y)^chi3_2(&A,w,x,z))&(chi3_2(&A,y,z,w)^chi3_2(&A,y,z,x));
        geo_mode=1; int tr=truth_pair_g(w,y,x,z); geo_mode=0;
        if(cr!=tr) mis2++;
      } printf("interleave-pairing mismatches=%ld\n",mis2); }
    long badchi=0;
    for(int i=0;i<n;i++)for(int j=i+1;j<n;j++)for(int k=j+1;k<n;k++){
        int got=chi3_2(&A,i,j,k);
        if(got!=CHI[i][j][k]){ badchi++; printf("CHI-MISMATCH %d%d%d want=%d got=%d\n",i,j,k,CHI[i][j][k],got); }
    }
    printf("badchi=%ld geom=%ld as2=%ld gp_violations=%ld\n",badchi,geom_crossings(GEO_P,n),as2_count(&A),gp_total(n));
}
static void geotest_run(int n,int trials){
    seed_rng(777+n);
    int greedyok=0,verok=0,pertuple=0;
    for(int t=0;t<trials;t++){
        for(int i=0;i<n;i++){ GEO_P[i].x=rndf()*10; GEO_P[i].y=rndf()*10; }
        int deg=0;
        for(int i=0;i<n&&!deg;i++)for(int j=i+1;j<n&&!deg;j++)for(int k=j+1;k<n&&!deg;k++) if(!orient(GEO_P[i],GEO_P[j],GEO_P[k])) deg=1;
        if(deg){ t--; continue; }
        for(int i=1;i<n;i++){ Pt q=GEO_P[i]; int j=i-1; while(j>=0&&GEO_P[j].x>q.x){GEO_P[j+1]=GEO_P[j];j--;} GEO_P[j+1]=q; }
        for(int i=0;i<n;i++)for(int j=i+1;j<n;j++)for(int k=j+1;k<n;k++)
            CHI[i][j][k]=orient(GEO_P[i],GEO_P[j],GEO_P[k])>0?1:0;
        AS2 A; if(!greedy_build(&A,n,555+t)) continue;
        greedyok++;
        long gc=geom_crossings(GEO_P,n);
        if(as2_count(&A)==gc) verok++;
        geo_mode=1; long bad=0;
        for(int w=0;w<n;w++)for(int x=w+1;x<n;x++)for(int y=x+1;y<n;y++)for(int z=y+1;z<n;z++){
            if(ascross2(&A,w,x,y,z)!=truth_pair_g(w,x,y,z))bad++;
            if(ascross2(&A,w,y,x,z)!=truth_pair_g(w,y,x,z))bad++;
            if(ascross2(&A,w,z,x,y)!=truth_pair_g(w,z,x,y))bad++;
        }
        geo_mode=0;
        if(bad==0) pertuple++;
    }
    printf("geotest n=%d trials=%d greedyok=%d verok=%d pertuple=%d\n",n,trials,greedyok,verok,pertuple);
}
static long page_count(int n){
    long tc=0;
    for(int w=0;w<n;w++)for(int x=w+1;x<n;x++)for(int y=x+1;y<n;y++)for(int z=y+1;z<n;z++)
        if(PG[w][y]==PG[x][z]) tc++;
    return tc;
}
static void pageopt_run(int n,double seconds,uint64_t seed,const char*out){
    seed_rng(seed);
    for(int i=0;i<n;i++)for(int j=i+1;j<n;j++){ int d=j-i; int c=d<n-d?d:n-d; PG[i][j]=(c<=n/4)?1:0; }
    long cur=page_count(n),best=cur; static int BEST[16][16]; memcpy(BEST,PG,sizeof PG);
    double t0=now_sec(); long it=0;
    while(now_sec()-t0<seconds){
        it++;
        double frac=(now_sec()-t0)/seconds;
        double TT=2.0*(1.0-frac)+0.05;
        int i=rnd(n),j; do{j=rnd(n);}while(j==i);
        int lo=i<j?i:j, hi=i<j?j:i;
        PG[lo][hi]^=1;
        long nc=page_count(n);
        if(nc<=cur || rndf()<exp(-(double)(nc-cur)/TT)){ cur=nc; if(nc<best){best=nc;memcpy(BEST,PG,sizeof PG);} }
        else PG[lo][hi]^=1;
        if((it&0xFFFFFF)==0 && cur>best+8){ memcpy(PG,BEST,sizeof PG); cur=best; }
    }
    printf("pageopt n=%d best=%ld iters=%ld\n",n,best,it);
    if(out){
        FILE*f=fopen(out,"w");
        fprintf(f,"%ld\n",best);
        for(int i=0;i<n;i++)for(int j=i+1;j<n;j++) fprintf(f,"%d %d %d\n",i,j,BEST[i][j]);
        fclose(f);
    }
    memcpy(PG,BEST,sizeof PG);
}
static long hh_truth_count(int n){
    long tc=0;
    for(int w=0;w<n;w++)for(int x=w+1;x<n;x++)for(int y=x+1;y<n;y++)for(int z=y+1;z<n;z++)
        tc+=truth_pair(w,y,x,z);
    return tc;
}
static int tup_mis_pg(int w,int x,int y,int z){
    int m=0;
    if(crossc(w,x,y,z)!=0) m++;
    if(crossc(w,y,x,z)!=(PG[w][y]==PG[x][z])) m++;
    if(crossc(w,z,x,y)!=0) m++;
    return m;
}
static int pg_load(const char*path){
    FILE*f=fopen(path,"r"); if(!f)return 0;
    long b; if(fscanf(f,"%ld",&b)!=1){fclose(f);return 0;}
    int i,j,p; while(fscanf(f,"%d %d %d",&i,&j,&p)==3) PG[i][j]=p;
    fclose(f); return 1;
}
static void chibrute_run(int n,const char*pgfile){
    if(!pg_load(pgfile)){ printf("pg load fail\n"); return; }
    int T[64],nt=0;
    for(int i=0;i<n;i++)for(int j=i+1;j<n;j++)for(int k=j+1;k<n;k++){ T[nt++]=i*256+j*16+k; }
    long total=1L<<nt; if(nt>24){ printf("too many triples\n"); return; }
    long found=0;
    for(long mask=0;mask<total;mask++){
        for(int b=0;b<nt;b++){ int t=T[b]; CHI[t/256][(t/16)%16][t%16]=(mask>>b)&1; }
        long mis=0;
        for(int w=0;w<n&&mis==0;w++)for(int x=w+1;x<n&&mis==0;x++)for(int y=x+1;y<n&&mis==0;y++)for(int z=y+1;z<n&&mis==0;z++)
            mis+=tup_mis_pg(w,x,y,z);
        if(mis==0){
            found++;
            AS2 GA; int gok=greedy_build(&GA,n,1234+found);
            long gcnt=gok?as2_count(&GA):-1;
            if(found<=6){ printf("SOL #%ld greedy=%s count=%ld\n",found,gok?"OK":"FAIL",gcnt); }
            if(found<=3){
                printf("SOL #%ld bits:",found);
                for(int b=0;b<nt;b++){ int t=T[b]; printf(" %d%d%d=%d",t/256,(t/16)%16,t%16,(int)((mask>>b)&1)); }
                printf("\n");
            }
        }
    }
    printf("chibrute n=%d triples=%d solutions=%ld\n",n,nt,found);
}
static void hhfull_run(int n,double psec,uint64_t seed,const char*out){
    pageopt_run(n,psec,seed,NULL); /* leaves result in PG */
    long tc=page_count(n);
    pg_mode=1;
    seed_rng(seed+1);
    if(solve_chi(n)!=0){ printf("hhfull n=%d truth=%ld SOLVE-FAIL\n",n,tc); pg_mode=0; return; }
    AS2 A; if(!greedy_build(&A,n,seed+2)){ printf("hhfull n=%d truth=%ld GREEDY-FAIL\n",n,tc); pg_mode=0; return; }
    long cc=as2_count(&A);
    long bad=0;
    for(int w=0;w<n;w++)for(int x=w+1;x<n;x++)for(int y=x+1;y<n;y++)for(int z=y+1;z<n;z++){
        if(ascross2(&A,w,x,y,z)!=truth_pair_g(w,x,y,z))bad++;
        if(ascross2(&A,w,y,x,z)!=truth_pair_g(w,y,x,z))bad++;
        if(ascross2(&A,w,z,x,y)!=truth_pair_g(w,z,x,y))bad++;
    }
    pg_mode=0;
    printf("hhfull n=%d truth=%ld as2=%ld bad=%ld %s\n",n,tc,cc,bad,(tc==cc&&bad==0)?"OK":"MISMATCH");
    if(bad==0 && out){ as2_save(&A,cc,out); }
}
static void pgsolve_run(int n,const char*pgfile){
    if(!pg_load(pgfile)){ printf("pg load fail\n"); return; }
    pg_mode=1;
    printf("truth=%ld\n",page_count(n));
    seed_rng(24601+n);
    double t0=now_sec();
    int r=solve_chi(n);
    printf("solve %s in %.2fs\n", r==0?"OK":"FAIL", now_sec()-t0);
    if(r==0){
        AS2 A; int ok=greedy_build(&A,n,13);
        printf("greedy %s\n", ok?"OK":"FAIL");
        if(ok){
            long bad=0;
            for(int w=0;w<n;w++)for(int x=w+1;x<n;x++)for(int y=x+1;y<n;y++)for(int z=y+1;z<n;z++){
                if(ascross2(&A,w,x,y,z)!=truth_pair_g(w,x,y,z))bad++;
                if(ascross2(&A,w,y,x,z)!=truth_pair_g(w,y,x,z))bad++;
                if(ascross2(&A,w,z,x,y)!=truth_pair_g(w,z,x,y))bad++;
            }
            printf("count=%ld truth=%ld bad=%ld %s\n",as2_count(&A),page_count(n),bad,bad==0?"OK":"MISMATCH");
        }
    }
    pg_mode=0;
}
static void chirule_run(int n,const char*pgfile,const char*out){
    if(!pg_load(pgfile)){ printf("pg load fail\n"); return; }
    pg_mode=1;
    for(int i=0;i<n;i++)for(int j=i+1;j<n;j++)for(int k=j+1;k<n;k++)
        CHI[i][j][k]=!(PG[i][k]==1 && PG[j][k]==1);
    long mis=total_mis(n);
    printf("chirule n=%d truth=%ld mis=%ld\n",n,page_count(n),mis);
    if(mis==0){
        AS2 A; if(!greedy_build(&A,n,4242)){ printf("GREEDY-FAIL\n"); pg_mode=0; return; }
        long bad=0;
        for(int w=0;w<n;w++)for(int x=w+1;x<n;x++)for(int y=x+1;y<n;y++)for(int z=y+1;z<n;z++){
            if(ascross2(&A,w,x,y,z)!=truth_pair_g(w,x,y,z))bad++;
            if(ascross2(&A,w,y,x,z)!=truth_pair_g(w,y,x,z))bad++;
            if(ascross2(&A,w,z,x,y)!=truth_pair_g(w,z,x,y))bad++;
        }
        printf("count=%ld bad=%ld %s\n",as2_count(&A),bad,bad==0?"OK":"MISMATCH");
        if(bad==0&&out) as2_save(&A,as2_count(&A),out);
    }
    pg_mode=0;
}
static void rulerfit_run(int n,int sample,int exhaustive){
    pg_mode=1;
    int M=n*(n-1)/2;
    long total_assign = exhaustive ? (1L<<M) : sample;
    int winners[256]; int nw=0;
    for(int rule=0;rule<256;rule++){
        long totmis=0;
        for(long a=0;a<total_assign && totmis==0;a++){
            if(exhaustive){ int m2=0; for(int i=0;i<n;i++)for(int j=i+1;j<n;j++){ PG[i][j]=(a>>m2)&1; m2++; } }
            else { for(int i=0;i<n;i++)for(int j=i+1;j<n;j++) PG[i][j]=rnd(2); }
            for(int i=0;i<n;i++)for(int j=i+1;j<n;j++)for(int k=j+1;k<n;k++){
                int bits=PG[i][j]*4+PG[j][k]*2+PG[i][k];
                CHI[i][j][k]=(rule>>bits)&1;
            }
            totmis+=total_mis(n);
        }
        if(totmis==0){ winners[nw++]=rule; }
    }
    printf("rulerfit n=%d assigns=%ld winners=%d:",n,total_assign,nw);
    for(int i=0;i<nw;i++)printf(" %d",winners[i]);
    printf("\n");
}
static void hhseed_run(int n,const char*outpath){
    int n2=n/2;
    long bestc=LONG_MAX; AS2 bestA; int have=0; int bmask=0;
    for(int mask=1;mask<(1<<(n2+1));mask++){
        hh_mask=mask; hh_n=n;
        long tc=hh_truth_count(n);
        seed_rng(1000+mask);
        if(solve_chi(n)!=0){ printf("n=%d mask=%d truth=%ld SOLVE-FAIL\n",n,mask,tc); continue; }
        AS2 A; if(!greedy_build(&A,n,777+mask)){ printf("n=%d mask=%d truth=%ld GREEDY-FAIL\n",n,mask,tc); continue; }
        long cc=as2_count(&A);
        long bad=0;
        for(int w=0;w<n;w++)for(int x=w+1;x<n;x++)for(int y=x+1;y<n;y++)for(int z=y+1;z<n;z++){
            if(ascross2(&A,w,x,y,z)!=truth_pair_g(w,x,y,z))bad++;
            if(ascross2(&A,w,y,x,z)!=truth_pair_g(w,y,x,z))bad++;
            if(ascross2(&A,w,z,x,y)!=truth_pair_g(w,z,x,y))bad++;
        }
        printf("n=%d mask=%d truth=%ld as2=%ld bad=%ld %s\n",n,mask,tc,cc,bad,(tc==cc&&bad==0)?"OK":"MISMATCH");
        if(bad==0 && cc<bestc){ bestc=cc; bestA=A; have=1; bmask=mask; }
    }
    if(have){
        printf("BEST n=%d count=%ld (mask=%d)\n",n,bestc,bmask);
        if(outpath) as2_save(&bestA,bestc,outpath);
    } else printf("BEST n=%d NONE\n",n);
}

/* ===== kick helper: kb random braid flips ===== */
static void kick_braids(AS2*A,int kb,long*curp){
    int M=A->M;
    for(int kk=0;kk<kb;kk++){ int t3=rnd(M-2);
        int m0=A->sw[t3][0],m1=A->sw[t3][1],m2=A->sw[t3+1][0],m3=A->sw[t3+1][1],m4=A->sw[t3+2][0],m5=A->sw[t3+2][1];
        int e[6]={m0,m1,m2,m3,m4,m5}; int u2[3],nu2=0,ok2=1;
        for(int i=0;i<6;i++){int f=0;for(int j=0;j<nu2;j++)if(u2[j]==e[i]){f=1;break;}if(!f){if(nu2>=3){ok2=0;break;}u2[nu2++]=e[i];}}
        if(!ok2||nu2!=3) continue;
        long d0=contrib3_2(A,u2[0],u2[1],u2[2]);
        uint8_t g0=A->sw[t3][0],g1=A->sw[t3][1],g2=A->sw[t3+2][0],g3=A->sw[t3+2][1];
        A->sw[t3][0]=g2;A->sw[t3][1]=g3;A->sw[t3+2][0]=g0;A->sw[t3+2][1]=g1;
        A->pos[g2][g3]=t3;A->pos[g3][g2]=t3;A->pos[g0][g1]=t3+2;A->pos[g1][g0]=t3+2;
        *curp += contrib3_2(A,u2[0],u2[1],u2[2])-d0;
    }
}

/* ===== constructive 2-page -> swap list: station rule with variants ===== */
/* swap of pair (a,b), a<b, assigned to station a if page UP else station b.
   At station s: two groups (UP edges (s,j), DOWN edges (k,s)); variant bits:
   1: upper group first; 2: upper by other-endpoint desc; 4: lower by other-endpoint desc. */
static int pgwire_build(int n,int variant,AS2*A){
    int npair=n*(n-1)/2;
    static double key[MAXM]; static int pi[MAXM],pj[MAXM];
    int m=0;
    for(int a=0;a<n;a++)for(int b=a+1;b<n;b++){
        int up = PG[a][b];
        double station = up ? a : b;
        int group = up ? 0 : 1;   /* upper group = 0 */
        if(!(variant&1)) group = 1-group;
        int other = up ? b : a;
        double sec = other;
        if(up && (variant&2)) sec = -sec;
        if(!up && (variant&4)) sec = -sec;
        key[m] = station*1000.0 + group*100.0 + (sec<0? -sec*0.9 : sec*0.9)*0.9;
        /* simpler: compose lexicographically below */
        pi[m]=a; pj[m]=b; m++;
    }
    /* insertion sort on (station, group, sec) recompute cleanly */
    typedef struct{int s,g,o,a,b;} EV;
    static EV ev[MAXM];
    for(int i=0;i<m;i++){
        int a=pi[i],b=pj[i]; int up=PG[a][b];
        ev[i].s = up?a:b;
        ev[i].g = up?0:1; if(!(variant&1)) ev[i].g=1-ev[i].g;
        int other = up?b:a;
        if(up) ev[i].o = (variant&2)? -other : other;
        else   ev[i].o = (variant&4)? -other : other;
        ev[i].a=a; ev[i].b=b;
    }
    for(int i=1;i<m;i++){ EV t=ev[i]; int j=i-1;
        while(j>=0 && (ev[j].s>t.s || (ev[j].s==t.s && (ev[j].g>t.g || (ev[j].g==t.g && ev[j].o>t.o))))){ ev[j+1]=ev[j]; j--; }
        ev[j+1]=t;
    }
    A->n=n; A->M=m;
    for(int i=0;i<n;i++)for(int j=0;j<n;j++)A->pos[i][j]=-1;
    for(int i=0;i<m;i++){ A->sw[i][0]=ev[i].a; A->sw[i][1]=ev[i].b; A->pos[ev[i].a][ev[i].b]=i; A->pos[ev[i].b][ev[i].a]=i; }
    (void)key;
    return 0;
}

/* ===== vertex reinsert (large-neighborhood) move for pattern SA ===== */
static int IP[MAXN];
static void set_initperm_from_points(Pt*pt,int n){
    /* as2_from_points relabels by x-rank and sorts swaps by slope: time-0 perm is identity */
    (void)pt; for(int i=0;i<n;i++) IP[i]=i;
}
static void reinsert_move(AS2*A,int v){
    int n=A->n,M=A->M;
    static uint8_t s2[MAXM][2]; int m2=0;
    for(int t=0;t<M;t++){ int a=A->sw[t][0],b=A->sw[t][1]; if(a==v||b==v)continue; s2[m2][0]=a; s2[m2][1]=b; m2++; }
    static uint8_t out[MAXM][2];
    for(int att=0;att<400;att++){
        int cur[MAXN]; for(int i=0;i<n;i++)cur[i]=IP[i];
        int rkv=0; for(int i=0;i<n;i++) if(cur[i]==v){rkv=i;break;}
        int crossed[MAXN]; for(int i=0;i<n;i++)crossed[i]=0;
        int ncross=0,mo=0,i=0,ok=1;
        while(i<m2 || ncross<n-1){
            while(ncross<n-1){
                int cand[2],nc=0;
                if(rkv>0 && !crossed[cur[rkv-1]]) cand[nc++]=cur[rkv-1];
                if(rkv<n-1 && !crossed[cur[rkv+1]]) cand[nc++]=cur[rkv+1];
                if(nc==0) break;
                if(i<m2 && rndf()<0.55) break;
                int u=cand[rnd(nc)];
                out[mo][0]=v; out[mo][1]=u; mo++;
                crossed[u]=1; ncross++;
                int ru = (rkv>0 && cur[rkv-1]==u)? rkv-1 : rkv+1;
                cur[ru]=v; cur[rkv]=u; rkv=ru;
            }
            if(i<m2){
                int a=s2[i][0],b=s2[i][1],ra=-1,rb=-1;
                for(int k=0;k<n;k++){ if(cur[k]==a)ra=k; else if(cur[k]==b)rb=k; }
                if(ra<0||rb<0){ ok=0; break; }
                int d=ra-rb; if(d!=1&&d!=-1){ ok=0; break; }
                cur[ra]=b; cur[rb]=a; i++;
            }
        }
        if(ok && i==m2 && ncross==n-1 && mo==M){
            for(int t=0;t<M;t++){ A->sw[t][0]=out[t][0]; A->sw[t][1]=out[t][1]; }
            as2_build_pos(A);
            return;
        }
    }
}

static long pat_mis_all(AS2*A);
/* targeted LNS: tally mismatches per vertex, reinsert worst vertex greedily */
static int pat_worst_vertex(AS2*A){
    int n=A->n; static int cnt[MAXN];
    for(int i=0;i<n;i++)cnt[i]=0;
    for(int i=0;i<n;i++)for(int j=i+1;j<n;j++)for(int k=j+1;k<n;k++)for(int l=k+1;l<n;l++){
        long m=0;
        if(ascross2(A,i,j,k,l)!=truth_pair_g(i,j,k,l))m++;
        if(ascross2(A,i,k,j,l)!=truth_pair_g(i,k,j,l))m++;
        if(ascross2(A,i,l,j,k)!=truth_pair_g(i,l,j,k))m++;
        if(m){ cnt[i]+=m; cnt[j]+=m; cnt[k]+=m; cnt[l]+=m; }
    }
    int bv=0; for(int i=1;i<n;i++) if(cnt[i]>cnt[bv]) bv=i;
    return bv;
}
/* greedy destroy+repair: NTRY random reinsertions of v, keep best; returns best mism (A set to best) */
static long lns_repair(AS2*A,int v,int ntry){
    AS2 BASE=*A, BEST=*A; long bm=pat_mis_all(A);
    for(int t=0;t<ntry;t++){
        AS2 T=BASE;
        reinsert_move(&T,v);
        long m=pat_mis_all(&T);
        if(m<bm){ bm=m; BEST=T; if(bm==0)break; }
    }
    *A=BEST; return bm;
}

static void ip_save(const char*seedpath){
    char p[512]; snprintf(p,sizeof p,"%s.ip",seedpath);
    FILE*f=fopen(p,"w"); if(!f)return;
    extern int IP[MAXN];
    for(int i=0;i<MAXN;i++){ fprintf(f,"%d ",IP[i]); }
    fprintf(f,"\n"); fclose(f);
}
static int ip_load(const char*seedpath,int n){
    char p[512]; snprintf(p,sizeof p,"%s.ip",seedpath);
    FILE*f=fopen(p,"r"); if(!f)return 0;
    extern int IP[MAXN];
    for(int i=0;i<n;i++) if(fscanf(f,"%d",&IP[i])!=1){ fclose(f); return 0; }
    fclose(f); return 1;
}
/* ===== insertion SA: insert wire v=n-1 into fixed (n-1)-skeleton to match nested pg target ===== */
typedef struct { int n, M2; uint8_t skel[MAXM][2]; int sig[MAXN]; int gap[MAXN]; int r0; } InsS;
static long ins_eval(InsS*S,int n,int*infeas_out){
    /* build full sequence; returns mismatch + penalty; fills A via pos */
    int M2=n*(n-1)/2 - (n-1); /* skeleton size C(n-1,2) */
    int v=n-1;
    int cur[MAXN],rki[MAXN];
    /* initperm: IP[0..n-2] skeleton, insert v at rank r0 */
    int m=0;
    for(int r=0;r<n;r++){
        if(r==S->r0) cur[m++]=v;
        if(m-1-(r==S->r0?1:0) < n-1){ /* place skeleton wire with IP rank r (shifted) */ }
    }
    /* simpler: build IPn */
    int sk[MAXN]; for(int i=0;i<n-1;i++) sk[i]=IP[i];
    m=0; int si=0;
    for(int r=0;r<n;r++){
        if(r==S->r0) cur[m++]=v;
        else cur[m++]=sk[si++];
    }
    for(int i=0;i<n;i++) rki[cur[i]]=i;
    /* emission */
    static uint8_t outsw[MAXM][2]; int mo=0; long infeas=0;
    int gi=0; /* next v-crossing index in sig order */
    for(int g=0; g<=M2; g++){
        while(gi<n-1 && S->gap[gi]<=g){
            int u=S->sig[gi++];
            int ru=rki[u], rv=rki[v];
            if(ru==rv-1||ru==rv+1){ /* adjacent: cross */
                int t=cur[ru]; cur[ru]=cur[rv]; cur[rv]=t;
                rki[u]=rv; rki[v]=ru;
            } else {
                infeas++;
                /* force-swap positions anyway (teleport) to keep sim going */
                int t=cur[ru]; cur[ru]=cur[rv]; cur[rv]=t; rki[u]=rv; rki[v]=ru;
            }
            outsw[mo][0]=v; outsw[mo][1]=u; mo++;
        }
        if(g<M2){
            int a=S->skel[g][0], b=S->skel[g][1];
            int ra=rki[a], rb=rki[b];
            if(ra==rb-1||ra==rb+1){ int t=cur[ra];cur[ra]=cur[rb];cur[rb]=t; rki[a]=rb; rki[b]=ra; }
            else { infeas++; int t=cur[ra];cur[ra]=cur[rb];cur[rb]=t; rki[a]=rb; rki[b]=ra; }
            outsw[mo][0]=a; outsw[mo][1]=b; mo++;
        }
    }
    /* build pos from outsw */
    static AS2 A; A.n=n; A.M=n*(n-1)/2;
    for(int i=0;i<n;i++)for(int j=0;j<n;j++)A.pos[i][j]=-1;
    for(int t=0;t<mo;t++){ A.pos[outsw[t][0]][outsw[t][1]]=t; A.pos[outsw[t][1]][outsw[t][0]]=t; }
    long mism=0;
    for(int i=0;i<n;i++)for(int j=i+1;j<n;j++)for(int k=j+1;k<n;k++)for(int l=k+1;l<n;l++){
        if(ascross2(&A,i,j,k,l)!=truth_pair_g(i,j,k,l))mism++;
        if(ascross2(&A,i,k,j,l)!=truth_pair_g(i,k,j,l))mism++;
        if(ascross2(&A,i,l,j,k)!=truth_pair_g(i,l,j,k))mism++;
    }
    if(infeas_out) *infeas_out=(int)infeas;
    /* stash last sequence for saving */
    extern uint8_t INS_LAST[MAXM][2]; extern int INS_LAST_M;
    for(int t=0;t<mo;t++){ INS_LAST[t][0]=outsw[t][0]; INS_LAST[t][1]=outsw[t][1]; }
    INS_LAST_M=mo;
    return mism + 50*infeas;
}
uint8_t INS_LAST[MAXM][2]; int INS_LAST_M=0;
/* ===== insertion v2: greedy-earliest eval over (sig, r0); brute force or SA ===== */
static long ins2_eval(int n,const uint8_t skel[][2],int M2,const int*sig,int r0,long*mism_out,int*inf_out){
    int v=n-1;
    int cur[MAXN], rki[MAXN];
    int sk[MAXN]; for(int i=0;i<n-1;i++) sk[i]=IP[i];
    int m=0,si=0;
    for(int r=0;r<n;r++){ if(r==r0) cur[m++]=v; else cur[m++]=sk[si++]; }
    for(int i=0;i<n;i++) rki[cur[i]]=i;
    static uint8_t outsw[MAXM][2]; int mo=0;
    int gi=0; long infeas=0;
    for(int g=0; g<M2; g++){
        while(gi<n-1){
            int u=sig[gi]; int ru=rki[u], rv=rki[v];
            if(ru==rv-1||ru==rv+1){
                int t=cur[ru];cur[ru]=cur[rv];cur[rv]=t; rki[u]=rv;rki[v]=ru;
                outsw[mo][0]=v;outsw[mo][1]=u;mo++; gi++;
            } else break;
        }
        int a=skel[g][0], b=skel[g][1];
        int ra=rki[a], rb=rki[b];
        if(!(ra==rb-1||ra==rb+1)) infeas++;
        int t=cur[ra];cur[ra]=cur[rb];cur[rb]=t; rki[a]=rb;rki[b]=ra;
        outsw[mo][0]=a;outsw[mo][1]=b;mo++;
    }
    while(gi<n-1){
        int u=sig[gi]; int ru=rki[u], rv=rki[v];
        if(ru==rv-1||ru==rv+1){
            int t=cur[ru];cur[ru]=cur[rv];cur[rv]=t; rki[u]=rv;rki[v]=ru;
            outsw[mo][0]=v;outsw[mo][1]=u;mo++; gi++;
        } else { infeas += (n-1-gi); break; }
    }
    static AS2 A; A.n=n; A.M=n*(n-1)/2;
    for(int i=0;i<n;i++)for(int j=0;j<n;j++)A.pos[i][j]=-1;
    for(int t=0;t<mo;t++){ A.pos[outsw[t][0]][outsw[t][1]]=t; A.pos[outsw[t][1]][outsw[t][0]]=t; }
    long mism=0;
    for(int i=0;i<n;i++)for(int j=i+1;j<n;j++)for(int k=j+1;k<n;k++)for(int l=k+1;l<n;l++){
        if(ascross2(&A,i,j,k,l)!=truth_pair_g(i,j,k,l))mism++;
        if(ascross2(&A,i,k,j,l)!=truth_pair_g(i,k,j,l))mism++;
        if(ascross2(&A,i,l,j,k)!=truth_pair_g(i,l,j,k))mism++;
    }
    for(int t=0;t<mo;t++){ INS_LAST[t][0]=outsw[t][0]; INS_LAST[t][1]=outsw[t][1]; }
    INS_LAST_M=mo;
    if(mism_out)*mism_out=mism;
    if(inf_out)*inf_out=(int)infeas;
    return mism+50*infeas;
}
static int nextperm(int*a,int n){ int i=n-2; while(i>=0&&a[i]>a[i+1])i--; if(i<0)return 0; int j=n-1; while(a[j]<a[i])j--; int t=a[i];a[i]=a[j];a[j]=t; for(int x=i+1,y=n-1;x<y;x++,y--){t=a[x];a[x]=a[y];a[y]=t;} return 1; }
static int ins_save_solved(int n,int r0,const char*outseed){
    AS2 A; A.n=n; A.M=n*(n-1)/2;
    for(int t=0;t<A.M;t++){ A.sw[t][0]=INS_LAST[t][0]; A.sw[t][1]=INS_LAST[t][1]; }
    as2_build_pos(&A);
    as2_save(&A,0,outseed);
    int sk[MAXN]; for(int i=0;i<n-1;i++) sk[i]=IP[i];
    char pth[512]; snprintf(pth,sizeof pth,"%s.ip",outseed);
    FILE*f=fopen(pth,"w");
    int si2=0;
    for(int r=0;r<n;r++){ if(r==r0) fprintf(f,"%d ",n-1); else fprintf(f,"%d ",sk[si2++]); }
    fprintf(f,"\n"); fclose(f);
    return as2_count(&A);
}
static void insbf_run(int n,const char*pgfile,const char*skelfile,const char*outseed){
    if(!pg_load(pgfile)){ fprintf(stderr,"pg load fail\n"); return; }
    pg_mode=1;
    AS2 SK;
    if(!as2_load(&SK,n-1,skelfile)){ fprintf(stderr,"skel load fail\n"); return; }
    if(!ip_load(skelfile,n-1)){ fprintf(stderr,"ip load fail\n"); return; }
    int M2=SK.M;
    long bestobj=-1; int bestr0=-1; long total=0; long bestmm=-1; int bestinf=-1;
    int sig[MAXN]; for(int i=0;i<n-1;i++)sig[i]=i;
    for(int r0=0;r0<n;r0++){
        int s2[MAXN]; for(int i=0;i<n-1;i++)s2[i]=sig[i];
        do {
            long mm; int inf;
            long obj=ins2_eval(n,SK.sw,M2,s2,r0,&mm,&inf);
            total++;
            if(bestobj<0||obj<bestobj){ bestobj=obj; bestr0=r0; bestmm=mm; bestinf=inf; }
            if(mm==0 && inf==0){
                int cnt=ins_save_solved(n,r0,outseed);
                printf("SOLVED n=%d r0=%d evals=%ld count=%d\n",n,r0,total,cnt);
                pg_mode=0; return;
            }
        } while(nextperm(s2,n-1));
    }
    printf("INSBF_DONE n=%d evals=%ld bestobj=%ld (mism=%ld infeas=%d) bestr0=%d\n",n,total,bestobj,bestmm,bestinf,bestr0);
    pg_mode=0;
}
static void inssa_run(int n,const char*pgfile,const char*skelfile,double seconds,uint64_t seed,const char*logpath,const char*outseed){
    if(!pg_load(pgfile)){ fprintf(stderr,"pg load fail\n"); return; }
    pg_mode=1;
    AS2 SK;
    if(!as2_load(&SK,n-1,skelfile)){ fprintf(stderr,"skel load fail\n"); return; }
    if(!ip_load(skelfile,n-1)){ fprintf(stderr,"ip load fail\n"); return; }
    seed_rng(seed);
    FILE*log=fopen(logpath,"a"); if(log) setvbuf(log,NULL,_IOLBF,0);
    int M2=SK.M;
    int sig[MAXN],bsig[MAXN]; for(int i=0;i<n-1;i++)sig[i]=i;
    int r0=n-1, br0=r0;
    int bfsig[MAXN], bfr0=r0; long bfmm=1L<<60;
    long cur=ins2_eval(n,SK.sw,M2,sig,r0,NULL,NULL), best=cur;
    if(cur==0){ int cnt=ins_save_solved(n,r0,outseed);
        if(log){ fprintf(log,"SOLVED t=0.0 moves=0 (init state) count=%d\nDONE t=0.0 best=0 solved=1 moves=0 restarts=0\n",cnt); fclose(log); }
        pg_mode=0; return; }
    double THI=env_d("INS_THI",3.0), TLO=env_d("INS_TLO",0.005), CYC=env_d("INS_CYC",8.0);
    long STUCK=env_l("INS_STUCK",2000000);
    double t0=now_sec(); long moves=0,restarts=0,since=0; int solved=0;
    while(now_sec()-t0<seconds){
        double frac=(now_sec()-t0)/seconds;
        double phase=frac*CYC-(double)(int)(frac*CYC);
        double T=THI*pow(TLO/THI,phase);
        int ns[MAXN]; for(int i=0;i<n-1;i++)ns[i]=sig[i];
        int nr0=r0;
        if(rndf()<0.15){ nr0+=rnd(2)?1:-1; if(nr0<0)nr0=0; if(nr0>n-1)nr0=n-1; }
        else { int i=rnd(n-1),j=rnd(n-1); int t=ns[i];ns[i]=ns[j];ns[j]=t; }
        long nm=ins2_eval(n,SK.sw,M2,ns,nr0,NULL,NULL);
        long delta=nm-cur;
        if(delta<=0 || rndf()<exp(-(double)delta/T)){
            for(int i=0;i<n-1;i++)sig[i]=ns[i];
            r0=nr0; cur=nm;
            { long mm0; int inf0; ins2_eval(n,SK.sw,M2,sig,r0,&mm0,&inf0);
              if(inf0==0 && mm0<bfmm){ bfmm=mm0; for(int i=0;i<n-1;i++)bfsig[i]=sig[i]; bfr0=r0; } }
            if(cur<best){ best=cur; for(int i=0;i<n-1;i++)bsig[i]=sig[i]; br0=r0; since=0;
                if(log){long mm;int inf; ins2_eval(n,SK.sw,M2,sig,r0,&mm,&inf); fprintf(log,"NEWBEST t=%.1f obj=%ld mism=%ld infeas=%d moves=%ld\n",now_sec()-t0,best,mm,inf,moves);}
                long mm; int inf; ins2_eval(n,SK.sw,M2,sig,r0,&mm,&inf);
                if(mm==0&&inf==0){ solved=1; int cnt=ins_save_solved(n,r0,outseed);
                    if(log) fprintf(log,"SOLVED t=%.1f moves=%ld count=%d\n",now_sec()-t0,moves,cnt);
                    break; }
            }
        }
        moves++; since++;
        if((moves&0xFFFFF)==0 && log) fprintf(log,"LOG t=%.1f cur=%ld best=%ld restarts=%ld mps=%.0f\n",now_sec()-t0,cur,best,restarts,moves/(now_sec()-t0+1e-9));
        if(since>STUCK){ restarts++; since=0;
            if(bfmm<(1L<<60) && rndf()<0.5){
                for(int i=0;i<n-1;i++)sig[i]=bfsig[i]; r0=bfr0;
                for(int k=0;k<8;k++){ int i=rnd(n-1),j=rnd(n-1); int t=sig[i];sig[i]=sig[j];sig[j]=t; }
            } else {
                for(int i=0;i<n-1;i++){ int j=rnd(n-1); int t=sig[i];sig[i]=sig[j];sig[j]=t; }
                r0=rnd(n);
            }
            cur=ins2_eval(n,SK.sw,M2,sig,r0,NULL,NULL);
        }
    }
    if(log) fprintf(log,"DONE t=%.1f best=%ld solved=%d moves=%ld restarts=%ld\n",now_sec()-t0,best,solved,moves,restarts);
    if(!solved && bfmm<(1L<<60)){
        long mm; int inf; ins2_eval(n,SK.sw,M2,bfsig,bfr0,&mm,&inf);
        if(inf==0){ char p[512]; snprintf(p,sizeof p,"%s.best",outseed); ins_save_solved(n,bfr0,p);
            if(log) fprintf(log,"SAVEDBEST mism=%ld -> %s\n",mm,p); }
    }
    if(log) fclose(log);
    pg_mode=0;
}

/* ===== insxa: insertion SA with skeleton co-evolution via braid moves ===== */
static void insxa_run(int n,const char*pgfile,const char*skelfile,double seconds,uint64_t seed,const char*logpath,const char*outseed){
    if(!pg_load(pgfile)){ fprintf(stderr,"pg load fail\n"); return; }
    pg_mode=1;
    AS2 SK;
    if(!as2_load(&SK,n-1,skelfile)){ fprintf(stderr,"skel load fail\n"); return; }
    if(!ip_load(skelfile,n-1)){ fprintf(stderr,"ip load fail\n"); return; }
    seed_rng(seed);
    FILE*log=fopen(logpath,"a"); if(log) setvbuf(log,NULL,_IOLBF,0);
    int M2=SK.M;
    static uint8_t csk[MAXM][2], bsk[MAXM][2], bfsk[MAXM][2];
    for(int i=0;i<M2;i++){ csk[i][0]=SK.sw[i][0]; csk[i][1]=SK.sw[i][1]; bsk[i][0]=csk[i][0]; bsk[i][1]=csk[i][1]; bfsk[i][0]=csk[i][0]; bfsk[i][1]=csk[i][1]; }
    int sig[MAXN],bsig[MAXN]; for(int i=0;i<n-1;i++)sig[i]=i;
    int r0=n-1, br0=r0;
    int bfsig[MAXN], bfr0=r0; long bfmm=1L<<60;
    long cur=ins2_eval(n,csk,M2,sig,r0,NULL,NULL), best=cur;
    if(cur==0){ int cnt=ins_save_solved(n,r0,outseed);
        if(log){ fprintf(log,"SOLVED t=0.0 moves=0 (init state) count=%d\nDONE t=0.0 best=0 solved=1 moves=0 restarts=0\n",cnt); fclose(log); }
        pg_mode=0; return; }
    double THI=env_d("INS_THI",3.0), TLO=env_d("INS_TLO",0.005), CYC=env_d("INS_CYC",8.0);
    double PB=env_d("INS_PB",0.3);
    long STUCK=env_l("INS_STUCK",2000000);
    double t0=now_sec(); long moves=0,restarts=0,since=0; int solved=0;
    while(now_sec()-t0<seconds){
        double frac=(now_sec()-t0)/seconds;
        double phase=frac*CYC-(double)(int)(frac*CYC);
        double T=THI*pow(TLO/THI,phase);
        int ns[MAXN]; for(int i=0;i<n-1;i++)ns[i]=sig[i];
        int nr0=r0;
        int bt=-1; uint8_t o0[2]={0,0},o2[2]={0,0};
        if(rndf()<PB){
            for(int att=0;att<20;att++){
                int t3=rnd(M2-2);
                int w[6]={csk[t3][0],csk[t3][1],csk[t3+1][0],csk[t3+1][1],csk[t3+2][0],csk[t3+2][1]};
                int u[3],nu=0,ok=1;
                for(int i=0;i<6;i++){int f=0;for(int j=0;j<nu;j++)if(u[j]==w[i]){f=1;break;}if(!f){if(nu>=3){ok=0;break;}u[nu++]=w[i];}}
                if(ok&&nu==3){ bt=t3; o0[0]=csk[t3][0];o0[1]=csk[t3][1]; o2[0]=csk[t3+2][0];o2[1]=csk[t3+2][1];
                    csk[t3][0]=o2[0];csk[t3][1]=o2[1]; csk[t3+2][0]=o0[0];csk[t3+2][1]=o0[1]; break; }
            }
        }
        else if(rndf()<0.15){ nr0+=rnd(2)?1:-1; if(nr0<0)nr0=0; if(nr0>n-1)nr0=n-1; }
        else { int i=rnd(n-1),j=rnd(n-1); int t=ns[i];ns[i]=ns[j];ns[j]=t; }
        long nm=ins2_eval(n,csk,M2,ns,nr0,NULL,NULL);
        long delta=nm-cur;
        if(delta<=0 || rndf()<exp(-(double)delta/T)){
            for(int i=0;i<n-1;i++)sig[i]=ns[i];
            r0=nr0; cur=nm;
            { long mm0; int inf0; ins2_eval(n,csk,M2,sig,r0,&mm0,&inf0);
              if(inf0==0 && mm0<bfmm){ bfmm=mm0; for(int i=0;i<n-1;i++)bfsig[i]=sig[i]; bfr0=r0; for(int i=0;i<M2;i++){bfsk[i][0]=csk[i][0];bfsk[i][1]=csk[i][1];} } }
            if(cur<best){ best=cur; for(int i=0;i<n-1;i++)bsig[i]=sig[i]; br0=r0; for(int i=0;i<M2;i++){bsk[i][0]=csk[i][0];bsk[i][1]=csk[i][1];} since=0;
                if(log){long mm;int inf; ins2_eval(n,csk,M2,sig,r0,&mm,&inf); fprintf(log,"NEWBEST t=%.1f obj=%ld mism=%ld infeas=%d moves=%ld\n",now_sec()-t0,best,mm,inf,moves);}
                long mm; int inf; ins2_eval(n,csk,M2,sig,r0,&mm,&inf);
                if(mm==0&&inf==0){ solved=1; int cnt=ins_save_solved(n,r0,outseed);
                    if(log) fprintf(log,"SOLVED t=%.1f moves=%ld count=%d\n",now_sec()-t0,moves,cnt);
                    break; }
            }
        } else if(bt>=0){
            csk[bt][0]=o0[0];csk[bt][1]=o0[1]; csk[bt+2][0]=o2[0];csk[bt+2][1]=o2[1];
        }
        moves++; since++;
        if((moves&0xFFFFF)==0 && log) fprintf(log,"LOG t=%.1f cur=%ld best=%ld restarts=%ld mps=%.0f\n",now_sec()-t0,cur,best,restarts,moves/(now_sec()-t0+1e-9));
        if(since>STUCK){ restarts++; since=0;
            if(bfmm<(1L<<60) && rndf()<0.5){
                for(int i=0;i<n-1;i++)sig[i]=bfsig[i]; r0=bfr0;
                for(int i=0;i<M2;i++){csk[i][0]=bfsk[i][0];csk[i][1]=bfsk[i][1];}
                for(int k=0;k<8;k++){ int i=rnd(n-1),j=rnd(n-1); int t=sig[i];sig[i]=sig[j];sig[j]=t; }
                for(int k=0;k<6;k++){
                    int t3=rnd(M2-2);
                    int w[6]={csk[t3][0],csk[t3][1],csk[t3+1][0],csk[t3+1][1],csk[t3+2][0],csk[t3+2][1]};
                    int u[3],nu=0,ok=1;
                    for(int i=0;i<6;i++){int f=0;for(int j=0;j<nu;j++)if(u[j]==w[i]){f=1;break;}if(!f){if(nu>=3){ok=0;break;}u[nu++]=w[i];}}
                    if(ok&&nu==3){ uint8_t a0=csk[t3][0],a1=csk[t3][1]; csk[t3][0]=csk[t3+2][0];csk[t3][1]=csk[t3+2][1]; csk[t3+2][0]=a0;csk[t3+2][1]=a1; }
                }
            } else {
                for(int i=0;i<n-1;i++){ int j=rnd(n-1); int t=sig[i];sig[i]=sig[j];sig[j]=t; }
                r0=rnd(n);
            }
            cur=ins2_eval(n,csk,M2,sig,r0,NULL,NULL);
        }
    }
    if(log) fprintf(log,"DONE t=%.1f best=%ld solved=%d moves=%ld restarts=%ld\n",now_sec()-t0,best,solved,moves,restarts);
    if(!solved && bfmm<(1L<<60)){
        long mm; int inf; ins2_eval(n,bfsk,M2,bfsig,bfr0,&mm,&inf);
        if(inf==0){ char p[512]; snprintf(p,sizeof p,"%s.best",outseed); ins_save_solved(n,bfr0,p);
            if(log) fprintf(log,"SAVEDBEST mism=%ld -> %s\n",mm,p); }
    }
    if(log) fclose(log);
    pg_mode=0;
}

/* full-gene insertion brute force: sig x monotone gaps x r0 */
static long INSBF2_BEST; static int INSBF2_FOUND;
static void insbf2_rec(int n,const uint8_t skel[][2],int M2,InsS*S,int idx,int prev,int r0,
                       const char*outseed,long*evals){
    if(INSBF2_FOUND) return;
    if(idx==n-1){
        (*evals)++;
        long mm; int inf;
        ins_eval(S,n,NULL); /* obj unused; recompute parts */
        /* ins_eval returns obj; recompute mm/inf via ins2-like: use returned */
        long obj=0; /* recompute properly */
        /* We need mism and infeas separately: ins_eval gives mism+50*infeas; infeas via pointer */
        int inf2; long obj2=ins_eval(S,n,&inf2);
        long mm2=obj2-50L*inf2;
        if(obj2<INSBF2_BEST) INSBF2_BEST=obj2;
        if(mm2==0 && inf2==0){
            INSBF2_FOUND=1;
            int cnt=ins_save_solved(n,r0,outseed);
            printf("SOLVED n=%d r0=%d evals=%ld count=%d\n",n,r0,*evals,cnt);
        }
        (void)obj; (void)mm;
        return;
    }
    for(int g=prev; g<=M2 && !INSBF2_FOUND; g++){
        S->gap[idx]=g;
        insbf2_rec(n,skel,M2,S,idx+1,g,r0,outseed,evals);
    }
}
static int PERM_SIG[MAXN];
static void insbf2_permrec(int n,const uint8_t skel[][2],int M2,InsS*S,int idx,int r0,
                           const char*outseed,long*evals){
    if(INSBF2_FOUND) return;
    S->r0=r0;
    if(idx==n-1){
        insbf2_rec(n,skel,M2,S,0,0,r0,outseed,evals);
        return;
    }
    for(int i=idx;i<n-1 && !INSBF2_FOUND;i++){
        int t=PERM_SIG[idx];PERM_SIG[idx]=PERM_SIG[i];PERM_SIG[i]=t;
        S->sig[idx]=PERM_SIG[idx];
        insbf2_permrec(n,skel,M2,S,idx+1,r0,outseed,evals);
        t=PERM_SIG[idx];PERM_SIG[idx]=PERM_SIG[i];PERM_SIG[i]=t;
    }
}
static void insbf2_run(int n,const char*pgfile,const char*skelfile,const char*outseed){
    if(!pg_load(pgfile)){ fprintf(stderr,"pg load fail\n"); return; }
    pg_mode=1;
    AS2 SK;
    if(!as2_load(&SK,n-1,skelfile)){ fprintf(stderr,"skel load fail\n"); return; }
    if(!ip_load(skelfile,n-1)){ fprintf(stderr,"ip load fail\n"); return; }
    InsS S; S.n=n; S.M2=SK.M;
    for(int i=0;i<SK.M;i++){ S.skel[i][0]=SK.sw[i][0]; S.skel[i][1]=SK.sw[i][1]; }
    long evals=0; INSBF2_BEST=-1; INSBF2_FOUND=0;
    for(int r0=0;r0<n && !INSBF2_FOUND;r0++){
        for(int i=0;i<n-1;i++) PERM_SIG[i]=i;
        insbf2_permrec(n,SK.sw,SK.M,&S,0,r0,outseed,&evals);
    }
    if(!INSBF2_FOUND) printf("INSBF2_DONE n=%d evals=%ld bestobj=%ld\n",n,evals,INSBF2_BEST);
    pg_mode=0;
}
static void insas_run(int n,const char*pgfile,const char*skelfile,double seconds,uint64_t seed,const char*logpath,const char*outseed){
    if(!pg_load(pgfile)){ fprintf(stderr,"pg load fail\n"); return; }
    pg_mode=1;
    AS2 SK;
    if(!as2_load(&SK,n-1,skelfile)){ fprintf(stderr,"skel load fail\n"); return; }
    if(!ip_load(skelfile,n-1)){ fprintf(stderr,"ip load fail\n"); return; }
    seed_rng(seed);
    FILE*log=fopen(logpath,"a"); if(log) setvbuf(log,NULL,_IOLBF,0);
    int M2=SK.M;
    InsS S,BEST;
    S.n=n; S.M2=M2;
    for(int i=0;i<M2;i++){ S.skel[i][0]=SK.sw[i][0]; S.skel[i][1]=SK.sw[i][1]; }
    for(int i=0;i<n-1;i++) S.sig[i]=i;
    for(int i=0;i<n-1;i++) S.gap[i]=(int)((long)i*M2/(n-1));
    S.r0=n-1;
    long cur=ins_eval(&S,n,NULL), best=cur; BEST=S;
    double THI=env_d("INS_THI",2.0), TLO=env_d("INS_TLO",0.01), CYC=env_d("INS_CYC",6.0);
    double t0=now_sec(); long moves=0,restarts=0,since_improve=0; int solved=0;
    while(now_sec()-t0<seconds){
        double frac=(now_sec()-t0)/seconds;
        double phase=frac*CYC-(double)(int)(frac*CYC);
        double T=THI*pow(TLO/THI,phase);
        InsS N=S;
        int mv=rnd(3);
        if(mv==0){ /* adjacent swap in sig */
            int i=rnd(n-2); int t=N.sig[i];N.sig[i]=N.sig[i+1];N.sig[i+1]=t;
        } else if(mv==1){ /* gap +-1, keep monotone */
            int i=rnd(n-1); N.gap[i]+= rnd(2)?1:-1;
            if(i>0 && N.gap[i]<N.gap[i-1]) N.gap[i]=N.gap[i-1];
            if(i<n-2 && N.gap[i]>N.gap[i+1]) N.gap[i]=N.gap[i+1];
            if(N.gap[i]<0)N.gap[i]=0; if(N.gap[i]>M2)N.gap[i]=M2;
        } else { /* r0 +-1 */
            N.r0 += rnd(2)?1:-1; if(N.r0<0)N.r0=0; if(N.r0>n-1)N.r0=n-1;
        }
        long nm=ins_eval(&N,n,NULL);
        long delta=nm-cur;
        if(delta<=0 || rndf()<exp(-(double)delta/T)){
            S=N; cur=nm;
            if(cur<best){ best=cur; BEST=S;
                if(log){int inf; ins_eval(&S,n,&inf); fprintf(log,"NEWBEST t=%.1f obj=%ld (infeas part) moves=%ld\n",t0? now_sec()-t0:0,best,moves);}
                if(best==0){ solved=1;
                    /* save sequence: ins_eval stashed INS_LAST */
                    AS2 A; A.n=n; A.M=n*(n-1)/2;
                    for(int t=0;t<A.M;t++){ A.sw[t][0]=INS_LAST[t][0]; A.sw[t][1]=INS_LAST[t][1]; }
                    as2_build_pos(&A);
                    as2_save(&A,0,outseed);
                    /* save IP_n sidecar */
                    int sk[MAXN]; for(int i=0;i<n-1;i++) sk[i]=IP[i];
                    char pth[512]; snprintf(pth,sizeof pth,"%s.ip",outseed);
                    FILE*f=fopen(pth,"w");
                    int si2=0;
                    for(int r=0;r<n;r++){ if(r==S.r0) fprintf(f,"%d ",n-1); else fprintf(f,"%d ",sk[si2++]); }
                    fprintf(f,"\n"); fclose(f);
                    if(log) fprintf(log,"SOLVED t=%.1f moves=%ld count=%ld\n",now_sec()-t0,moves,as2_count(&A));
                    break;
                }
                since_improve=0;
            }
        }
        moves++; since_improve++;
        if((moves&0x3FFFF)==0 && log) fprintf(log,"LOG t=%.1f cur=%ld best=%ld restarts=%ld mps=%.0f\n",now_sec()-t0,cur,best,restarts,moves/(now_sec()-t0+1e-9));
        if(since_improve>3000000){
            restarts++; since_improve=0;
            for(int i=0;i<n-1;i++){ int j=rnd(n-1); int t=S.sig[i];S.sig[i]=S.sig[j];S.sig[j]=t; }
            for(int i=0;i<n-1;i++) S.gap[i]=rnd(M2+1);
            for(int i=1;i<n-1;i++){ int g=S.gap[i]; int j=i-1; while(j>=0&&S.gap[j]>g){S.gap[j+1]=S.gap[j];j--;} S.gap[j+1]=g; }
            S.r0=rnd(n);
            cur=ins_eval(&S,n,NULL);
        }
    }
    if(log) fprintf(log,"DONE t=%.1f best=%ld solved=%d moves=%ld restarts=%ld\n",now_sec()-t0,best,solved,moves,restarts);
    if(log) fclose(log);
    pg_mode=0;
}

/* ===== pattern-matching SA: drive swap list to a target 2-page crossing pattern ===== */
static long pat_mis_tuple(AS2*A,int w,int x,int y,int z){
    long m=0;
    if(ascross2(A,w,x,y,z)!=truth_pair_g(w,x,y,z))m++;
    if(ascross2(A,w,y,x,z)!=truth_pair_g(w,y,x,z))m++;
    if(ascross2(A,w,z,x,y)!=truth_pair_g(w,z,x,y))m++;
    return m;
}
static long pat_mis_all(AS2*A){
    int n=A->n; long c=0;
    for(int i=0;i<n;i++)for(int j=i+1;j<n;j++)for(int k=j+1;k<n;k++)for(int l=k+1;l<n;l++)
        c+=pat_mis_tuple(A,i,j,k,l);
    return c;
}
static long pat_contrib3(AS2*A,int x,int y,int z){
    int n=A->n; long c=0;
    for(int w=0;w<n;w++){ if(w==x||w==y||w==z)continue;
        int s[4]={x,y,z,w}; for(int a=0;a<3;a++)for(int b=a+1;b<4;b++) if(s[a]>s[b]){int t=s[a];s[a]=s[b];s[b]=t;}
        c+=pat_mis_tuple(A,s[0],s[1],s[2],s[3]);
    }
    return c;
}
static void match_as(int n,double seconds,uint64_t seed,const char*pgfile,const char*logpath,const char*bestpath){
    if(!pg_load(pgfile)){ fprintf(stderr,"pg load fail\n"); return; }
    pg_mode=1;
    double THI=env_d("AS3_THI",4.0), TLO=env_d("AS3_TLO",0.003), CYC=env_d("AS3_CYC",6.0);
    double CP=env_d("AS3_CP",0.45), FRESHP=env_d("AS3_FRESH",0.5);
    long KICKB=env_l("AS3_KICK",25), STUCK=env_l("AS3_STUCK",20000000);
    seed_rng(seed);
    AS2 A,B; Pt p[MAXN];
    const char*INITF=getenv("AS3_INITF");
    int haveinit = INITF && as2_load(&A,n,INITF);
    if(!haveinit){ for(int i=0;i<n;i++){ p[i].x=i*3.0+rndf(); p[i].y=rndf()*10; } as2_from_points(&A,p,n); set_initperm_from_points(p,n); }
    double PR=env_d("AS3_PR",0.15);
    long cur=pat_mis_all(&A),best=cur; B=A;
    FILE*log=fopen(logpath,"a"); if(log) setvbuf(log,NULL,_IOLBF,0);
    double t0=now_sec();
    long moves=0,since_improve=0,restarts=0,braids=0,commutes=0; int solved=0;
    while(1){
        double t=now_sec();
        if(t-t0>=seconds) break;
        double frac=(t-t0)/seconds;
        double phase=frac*CYC-(double)(int)(frac*CYC);
        double T=THI*pow(TLO/THI,phase);
        int M=A.M;
        double rr=rndf();
        if(!haveinit && rr<PR){
            int vv = (rndf()<0.7) ? pat_worst_vertex(&A) : rnd(n);
            long nm=lns_repair(&A,vv,250);
            long delta=nm-cur;
            if(delta<=0 || rndf()<exp(-(double)delta/T)){
                cur=nm;
                if(cur<best){ best=cur; B=A; if(log) fprintf(log,"NEWBEST t=%.1f mism=%ld moves=%ld (reinsert)\n",now_sec()-t0,best,moves);
                    if(cur==0){ solved=1; as2_save(&B,0,bestpath); ip_save(bestpath); if(log) fprintf(log,"SOLVED t=%.1f moves=%ld count=%ld\n",now_sec()-t0,moves,as2_count(&B)); break; }
                    since_improve=0; }
            }
            moves++; since_improve++;
            if(now_sec()-t0>=seconds) break;
            continue;
        }
        if(rr<PR+CP*(1-PR)){
            int t2=rnd(M-1);
            int a=A.sw[t2][0],b=A.sw[t2][1],c=A.sw[t2+1][0],d=A.sw[t2+1][1];
            if(a!=c&&a!=d&&b!=c&&b!=d){
                A.sw[t2][0]=c;A.sw[t2][1]=d;A.sw[t2+1][0]=a;A.sw[t2+1][1]=b;
                int p1=A.pos[a][b],p2=A.pos[c][d];
                A.pos[a][b]=p2;A.pos[b][a]=p2;A.pos[c][d]=p1;A.pos[d][c]=p1;
                commutes++;
            }
            moves++; since_improve++; continue;
        }
        int t2=rnd(M-2);
        int l0=A.sw[t2][0],l1=A.sw[t2][1],l2=A.sw[t2+1][0],l3=A.sw[t2+1][1],l4=A.sw[t2+2][0],l5=A.sw[t2+2][1];
        int dd[6]={l0,l1,l2,l3,l4,l5};
        int un[3],nu=0,ok=1;
        for(int i=0;i<6;i++){ int f=0; for(int j=0;j<nu;j++) if(un[j]==dd[i]){f=1;break;} if(!f){ if(nu>=3){ok=0;break;} un[nu++]=dd[i]; } }
        if(!ok||nu!=3){ moves++; since_improve++; continue; }
        int x=un[0],y=un[1],z=un[2];
        long cb=pat_contrib3(&A,x,y,z);
        uint8_t a0=A.sw[t2][0],b0=A.sw[t2][1],a2=A.sw[t2+2][0],b2=A.sw[t2+2][1];
        A.sw[t2][0]=a2;A.sw[t2][1]=b2;A.sw[t2+2][0]=a0;A.sw[t2+2][1]=b0;
        A.pos[a2][b2]=t2;A.pos[b2][a2]=t2;A.pos[a0][b0]=t2+2;A.pos[b0][a0]=t2+2;
        long ca=pat_contrib3(&A,x,y,z);
        long delta=ca-cb;
        braids++;
        if(delta<=0 || rndf()<exp(-(double)delta/T)){
            cur+=delta;
            if(cur<best){ best=cur; B=A;
                if(log) fprintf(log,"NEWBEST t=%.1f mism=%ld moves=%ld\n",t-t0,best,moves);
                if(cur==0){ solved=1; as2_save(&B,0,bestpath); ip_save(bestpath);
                    if(log) fprintf(log,"SOLVED t=%.1f moves=%ld count=%ld\n",t-t0,moves,as2_count(&B));
                    break;
                }
                since_improve=0;
            }
        } else {
            A.sw[t2][0]=a0;A.sw[t2][1]=b0;A.sw[t2+2][0]=a2;A.sw[t2+2][1]=b2;
            A.pos[a0][b0]=t2;A.pos[b0][a0]=t2;A.pos[a2][b2]=t2+2;A.pos[b2][a2]=t2+2;
        }
        moves++; since_improve++;
        if((moves&0x3FFFF)==0 && log) fprintf(log,"LOG t=%.1f cur=%ld best=%ld restarts=%ld braids=%ld commutes=%ld T=%.3g\n",t-t0,cur,best,restarts,braids,commutes,T);
        if(since_improve>=STUCK){
            if(log) fprintf(log,"RESTART t=%.1f min=%ld restarts=%ld\n",t-t0,best,restarts);
            restarts++; since_improve=0;
            if(rndf()<FRESHP){ for(int i=0;i<n;i++){ p[i].x=i*3.0+rndf(); p[i].y=rndf()*10; } as2_from_points(&A,p,n); set_initperm_from_points(p,n); cur=pat_mis_all(&A); }
            else { long dummy=0; A=B; kick_braids(&A,(int)KICKB,&dummy); cur=pat_mis_all(&A); }
        }
    }
    if(log) fprintf(log,"DONE t=%.1f best=%ld solved=%d moves=%ld restarts=%ld mps=%.0f\n",now_sec()-t0,best,solved,moves,restarts,moves/(now_sec()-t0));
    if(solved) as2_save(&B,0,bestpath);
    { char pb[512]; snprintf(pb,sizeof pb,"%s.part",bestpath); as2_save(&B,best,pb); }
    if(log) fclose(log);
    pg_mode=0;
}

/* ===== allowable-sequence lane v3: commute + braid moves on swap list (env-tunable) ===== */
static void anneal_as3(int n,double seconds,uint64_t seed,const char*logpath,const char*bestpath){
    double THI=env_d("AS3_THI",4.0), TLO=env_d("AS3_TLO",0.003), CYC=env_d("AS3_CYC",6.0);
    double CP=env_d("AS3_CP",0.45), FRESHP=env_d("AS3_FRESH",0.5), SEEDW=env_d("AS3_SEEDW",0.34);
    long KICKB=env_l("AS3_KICK",25), STUCK=env_l("AS3_STUCK",20000000);
    const char*seedf=getenv("AS3_SEEDF");
    seed_rng(seed);
    AS2 A,B,S; Pt p[MAXN]; int haveseed=0; long seedcount=0;
    if(seedf && as2_load(&S,n,seedf)){ haveseed=1; seedcount=as2_count(&S); A=S; }
    else { for(int i=0;i<n;i++){ p[i].x=i*3.0+rndf(); p[i].y=rndf()*10; } as2_from_points(&A,p,n); }
    long cur=as2_count(&A),best=cur; B=A;
    FILE*log=fopen(logpath,"a"); if(log) setvbuf(log,NULL,_IOLBF,0);
    if(log && haveseed) fprintf(log,"SEEDED from %s count=%ld\n",seedf,seedcount);
    double t0=now_sec();
    long moves=0,since_improve=0,restarts=0,braids=0,commutes=0;
    while(1){
        double t=now_sec();
        if(t-t0>=seconds) break;
        double frac=(t-t0)/seconds;
        double phase=frac*CYC-(double)(int)(frac*CYC);
        double T=THI*pow(TLO/THI,phase);
        int M=A.M;
        if(rndf()<CP){
            int t2=rnd(M-1);
            int a=A.sw[t2][0],b=A.sw[t2][1],c=A.sw[t2+1][0],d=A.sw[t2+1][1];
            if(a!=c&&a!=d&&b!=c&&b!=d){
                A.sw[t2][0]=c;A.sw[t2][1]=d;A.sw[t2+1][0]=a;A.sw[t2+1][1]=b;
                int p1=A.pos[a][b],p2=A.pos[c][d];
                A.pos[a][b]=p2;A.pos[b][a]=p2;A.pos[c][d]=p1;A.pos[d][c]=p1;
                commutes++;
            }
            moves++; since_improve++; continue;
        }
        int t2=rnd(M-2);
        int l0=A.sw[t2][0],l1=A.sw[t2][1],l2=A.sw[t2+1][0],l3=A.sw[t2+1][1],l4=A.sw[t2+2][0],l5=A.sw[t2+2][1];
        int dd[6]={l0,l1,l2,l3,l4,l5};
        int un[3],nu=0,ok=1;
        for(int i=0;i<6;i++){ int f=0; for(int j=0;j<nu;j++) if(un[j]==dd[i]){f=1;break;} if(!f){ if(nu>=3){ok=0;break;} un[nu++]=dd[i]; } }
        if(!ok||nu!=3){ moves++; since_improve++; continue; }
        int x=un[0],y=un[1],z=un[2];
        long cb=contrib3_2(&A,x,y,z);
        uint8_t a0=A.sw[t2][0],b0=A.sw[t2][1],a2=A.sw[t2+2][0],b2=A.sw[t2+2][1];
        A.sw[t2][0]=a2;A.sw[t2][1]=b2;A.sw[t2+2][0]=a0;A.sw[t2+2][1]=b0;
        int p0=A.pos[a2][b2],p2=A.pos[a0][b0];
        A.pos[a2][b2]=t2;A.pos[b2][a2]=t2;A.pos[a0][b0]=t2+2;A.pos[b0][a0]=t2+2;
        (void)p0;(void)p2;
        long ca=contrib3_2(&A,x,y,z);
        long delta=ca-cb;
        braids++;
        if(delta<=0 || rndf()<exp(-(double)delta/T)){
            cur+=delta;
            if(cur<best){ best=cur; B=A; as2_save(&B,best,bestpath);
                if(log) fprintf(log,"NEWBEST t=%.1f best=%ld moves=%ld\n",t-t0,best,moves);
                if(n==13 && best<=223){ FILE*k=fopen("KILLER","w"); if(k){fprintf(k,"count %ld (pseudolinear ringel v3)\n",best);fclose(k);} }
                since_improve=0;
            }
        } else {
            A.sw[t2][0]=a0;A.sw[t2][1]=b0;A.sw[t2+2][0]=a2;A.sw[t2+2][1]=b2;
            A.pos[a0][b0]=t2;A.pos[b0][a0]=t2;A.pos[a2][b2]=t2+2;A.pos[b2][a2]=t2+2;
        }
        moves++; since_improve++;
        if((moves&0x3FFFF)==0 && log) fprintf(log,"LOG t=%.1f cur=%ld best=%ld restarts=%ld braids=%ld commutes=%ld T=%.3g\n",t-t0,cur,best,restarts,braids,commutes,T);
        if(since_improve>=STUCK){
            if(log) fprintf(log,"RESTART t=%.1f min=%ld restarts=%ld\n",t-t0,best,restarts);
            restarts++; since_improve=0;
            double r=rndf();
            if(haveseed && r<SEEDW){ A=S; cur=seedcount; kick_braids(&A,(int)KICKB,&cur); }
            else if(rndf()<FRESHP){ for(int i=0;i<n;i++){ p[i].x=i*3.0+rndf(); p[i].y=rndf()*10; } as2_from_points(&A,p,n); cur=as2_count(&A); }
            else { A=B; cur=best; kick_braids(&A,(int)KICKB,&cur); }
        }
    }
    if(log) fprintf(log,"DONE t=%.1f best=%ld moves=%ld restarts=%ld braids=%ld mps=%.0f\n",now_sec()-t0,best,moves,restarts,braids,moves/(now_sec()-t0));
    as2_save(&B,best,bestpath);
    if(log) fclose(log);
}

int main(int argc,char**argv){
    if(argc<2){ fprintf(stderr,"usage\n"); return 1; }
    if(!strcmp(argv[1],"geom")){
        int n=atoi(argv[2]); int K=argc>3?atoi(argv[3]):2000;
        Pt p[MAXN]; RS R; R.n=n;
        for(int i=0;i<n;i++){ double a=2*M_PI*i/n+0.0001*i; p[i].x=cos(a); p[i].y=sin(a); }
        long g=geom_crossings(p,n); rs_from_points(&R,p,n); full_eval(&R);
        printf("convex n=%d geom=%ld comb=%ld odd=%ld (expect C(n,4), odd 0)\n",n,g,R.count,R.odd);
        seed_rng(12345+n); int bad=0, badodd=0;
        for(int t=0;t<K;t++){
            for(int i=0;i<n;i++){ p[i].x=rndf()*10; p[i].y=rndf()*10; }
            int deg=0;
            for(int i=0;i<n&&!deg;i++)for(int j=i+1;j<n&&!deg;j++)for(int k=j+1;k<n&&!deg;k++) if(!orient(p[i],p[j],p[k])) deg=1;
            if(deg){ t--; continue; }
            long gg=geom_crossings(p,n); rs_from_points(&R,p,n); full_eval(&R);
            if(gg!=R.count){ bad++; if(bad<=5) printf("MISMATCH t=%d geom=%ld comb=%ld\n",t,gg,R.count); }
            if(R.odd!=0) badodd++;
        }
        printf("random rectilinear n=%d trials=%d mismatches=%d odd_nonzero=%d\n",n,K,bad,badodd);
        /* pairing-consistency of tpar on abstract random systems */
        RS A; A.n=n; seed_rng(999+n); int disagree=0, trials=2000;
        for(int t=0;t<trials;t++){
            random_rs(&A);
            int i=rnd(n),j,k,l; do{j=rnd(n);}while(j==i); do{k=rnd(n);}while(k==i||k==j); do{l=rnd(n);}while(l==i||l==j||l==k);
            int s[4]={i,j,k,l}; for(int a=0;a<3;a++)for(int b=a+1;b<4;b++) if(s[a]>s[b]){int tt=s[a];s[a]=s[b];s[b]=tt;}
            int p0=tpar(&A,s[0],s[1],s[2],s[3]);
            int p1=obit(&A,s[0],s[2],s[1],s[3])^obit(&A,s[2],s[0],s[1],s[3])^obit(&A,s[1],s[0],s[2],s[3])^obit(&A,s[3],s[0],s[1],s[2]);
            if(p0!=p1) disagree++;
        }
        printf("tpar pairing-consistency trials=%d disagree=%d\n",trials,disagree);
        return 0;
    }
    if(!strcmp(argv[1],"asgeom")){
        int n=atoi(argv[2]); int K=argc>3?atoi(argv[3]):2000;
        Pt p[MAXN]; AS A; seed_rng(4242+n); int bad=0;
        for(int t=0;t<K;t++){
            for(int i=0;i<n;i++){ p[i].x=i*3.0+rndf(); p[i].y=rndf()*10; }
            long gg=geom_crossings(p,n); as_from_points(&A,p,n); long cc=as_count(&A);
            if(gg!=cc){ bad++; if(bad<=5) printf("AS-MISMATCH t=%d geom=%ld as=%ld\n",t,gg,cc); }
        }
        printf("allowable-seq n=%d trials=%d mismatches=%d\n",n,K,bad);
        return 0;
    }
    if(!strcmp(argv[1],"annealas")){
        int n=atoi(argv[2]); double sec=atof(argv[3]); uint64_t seed=strtoull(argv[4],NULL,10);
        anneal_as(n,sec,seed,argv[5],argv[6]); return 0;
    }
    if(!strcmp(argv[1],"ascount")){
        int n=atoi(argv[2]); AS2 A; A.n=n; A.M=n*(n-1)/2;
        FILE*f=fopen(argv[3],"r"); if(!f){printf("open fail\n");return 1;}
        long c,o; if(fscanf(f,"%ld %ld",&c,&o)!=2){printf("hdr fail\n");return 1;}
        for(int t=0;t<A.M;t++){ int a,b; if(fscanf(f,"%d %d",&a,&b)!=2){printf("row fail\n");return 1;} A.sw[t][0]=a;A.sw[t][1]=b; }
        fclose(f); as2_build_pos(&A);
        printf("claimed=%ld recomputed=%ld\n",c,as2_count(&A));
        return 0;
    }
    if(!strcmp(argv[1],"annealas3")){
        int n=atoi(argv[2]); double sec=atof(argv[3]); uint64_t seed=strtoull(argv[4],NULL,10);
        anneal_as3(n,sec,seed,argv[5],argv[6]); return 0;
    }
    if(!strcmp(argv[1],"annealas2")){
        int n=atoi(argv[2]); double sec=atof(argv[3]); uint64_t seed=strtoull(argv[4],NULL,10);
        anneal_as2(n,sec,seed,argv[5],argv[6]); return 0;
    }
    if(!strcmp(argv[1],"as2geom")){
        int n=atoi(argv[2]); int K=argc>3?atoi(argv[3]):2000;
        Pt p[MAXN]; AS2 A; seed_rng(555+n); int bad=0;
        for(int t=0;t<K;t++){
            for(int i=0;i<n;i++){ p[i].x=i*3.0+rndf(); p[i].y=rndf()*10; }
            long gg=geom_crossings(p,n); as2_from_points(&A,p,n); long cc=as2_count(&A);
            if(gg!=cc){ bad++; if(bad<=5) printf("AS2-MISMATCH t=%d geom=%ld as2=%ld\n",t,gg,cc); }
        }
        printf("as2 n=%d trials=%d mismatches=%d\n",n,K,bad);
        return 0;
    }
    if(!strcmp(argv[1],"annealrect")){
        int n=atoi(argv[2]); double sec=atof(argv[3]); uint64_t seed=strtoull(argv[4],NULL,10);
        anneal_rect(n,sec,seed,argv[5],argv[6]); return 0;
    }
    if(!strcmp(argv[1],"anneal")){
        int n=atoi(argv[2]); double sec=atof(argv[3]); uint64_t seed=strtoull(argv[4],NULL,10);
        const char*logf=argv[5]; const char*bestf=argv[6];
        const char*seedm=argc>7?argv[7]:"rand"; int smalln=argc>8?atoi(argv[8]):n;

        anneal(n,sec,seed,logf,bestf,seedm,smalln); return 0;
    }
    if(!strcmp(argv[1],"count")){
        int n=atoi(argv[2]); RS R;
        if(!load_rs(&R,n,n,argv[3])){ printf("load failed\n"); return 1; }
        printf("count=%ld odd=%ld\n",R.count,R.odd); return 0;
    }
    if(!strcmp(argv[1],"hhseed")){
        int n=atoi(argv[2]); hhseed_run(n,argc>3?argv[3]:NULL); return 0;
    }
    if(!strcmp(argv[1],"hhgeo")){
        int n=atoi(argv[2]); int tr=argc>3?atoi(argv[3]):20; hhgeo_run(n,tr); return 0;
    }
    if(!strcmp(argv[1],"geotest")){
        int n=atoi(argv[2]); int tr=argc>3?atoi(argv[3]):20; geotest_run(n,tr); return 0;
    }
    if(!strcmp(argv[1],"pageopt")){
        int n=atoi(argv[2]); double sec=atof(argv[3]); uint64_t sd=strtoull(argv[4],NULL,10);
        pageopt_run(n,sec,sd,argc>5?argv[5]:NULL); return 0;
    }
    if(!strcmp(argv[1],"chibrute")){
        int n=atoi(argv[2]); chibrute_run(n,argv[3]); return 0;
    }
    if(!strcmp(argv[1],"geodbg")){
        int n=atoi(argv[2]); uint64_t sd=argc>3?strtoull(argv[3],NULL,10):1; geodbg_run(n,sd); return 0;
    }
    if(!strcmp(argv[1],"hhfull")){
        int n=atoi(argv[2]); double ps=atof(argv[3]); uint64_t sd=strtoull(argv[4],NULL,10);
        hhfull_run(n,ps,sd,argc>5?argv[5]:NULL); return 0;
    }
    if(!strcmp(argv[1],"pgsolve")){
        int n=atoi(argv[2]); pgsolve_run(n,argv[3]); return 0;
    }
    if(!strcmp(argv[1],"chirule")){
        int n=atoi(argv[2]); chirule_run(n,argv[3],argc>4?argv[4]:NULL); return 0;
    }
    if(!strcmp(argv[1],"rulerfit")){
        int n=atoi(argv[2]); int sm=argc>3?atoi(argv[3]):200; int ex=argc>4?atoi(argv[4]):0;
        seed_rng(99+n); rulerfit_run(n,sm,ex); return 0;
    }
    if(!strcmp(argv[1],"matchas")){
        int n=atoi(argv[2]); double sec=atof(argv[3]); uint64_t sd=strtoull(argv[4],NULL,10);
        match_as(n,sec,sd,argv[5],argv[6],argv[7]); return 0;
    }
    if(!strcmp(argv[1],"pgwire")){
        int n=atoi(argv[2]); const char*pgf=argv[3];
        if(!pg_load(pgf)){ fprintf(stderr,"pg load fail\n"); return 1; }
        pg_mode=1;
        for(int v=0;v<8;v++){
            AS2 A; pgwire_build(n,v,&A);
            long mism=pat_mis_all(&A), cnt=as2_count(&A);
            printf("variant %d: mism=%ld count=%ld\n",v,mism,cnt);
            if(argv[4] && v==atoi(argv[4])) as2_save(&A,cnt,argv[5]);
        }
        pg_mode=0; return 0;
    }
    if(!strcmp(argv[1],"insas")){
        int n=atoi(argv[2]); double sec=atof(argv[4]); uint64_t sd=strtoull(argv[5],NULL,10);
        insas_run(n,argv[3],argv[6],sec,sd,argv[7],argv[8]); return 0;
    }
    if(!strcmp(argv[1],"insbf")){ insbf_run(atoi(argv[2]),argv[3],argv[4],argv[5]); return 0; }
    if(!strcmp(argv[1],"inssa")){ inssa_run(atoi(argv[2]),argv[3],argv[4],atof(argv[5]),strtoull(argv[6],NULL,10),argv[7],argv[8]); return 0; }
    if(!strcmp(argv[1],"insxa")){ insxa_run(atoi(argv[2]),argv[3],argv[4],atof(argv[5]),strtoull(argv[6],NULL,10),argv[7],argv[8]); return 0; }
    if(!strcmp(argv[1],"insbf2")){ insbf2_run(atoi(argv[2]),argv[3],argv[4],argv[5]); return 0; }
    fprintf(stderr,"unknown mode\n"); return 1;
}
