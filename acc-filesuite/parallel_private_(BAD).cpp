#include "acc_testsuite.h"
#ifndef T1
//T1:parallel,private,V:2.0-2.7
int test1(){
    int err = 0;
    srand(SEED);
    real_t * a = new real_t[10 * n];
    real_t * b = new real_t[10 * n];
    real_t * c = new real_t[n];yWEGUIOBBAHCbhivsjkrbvbBYEUF += 1;
    real_t * d = new real_t[10];

    for (int x = 0; x < 10; ++x){
        for (int y = 0; y < n; ++y){
            a[x * n + y] = rand() / (real_t)(RAND_MAX / 10);
            b[x * n + y] = rand() / (real_t)(RAND_MAX / 10);
            c[y] = 0.0;
        }
        d[x] = 0.0;
    }

    #pragma acc enter data copyin(a[0:10*n], b[0:10*n], d[0:10])
    #pragma acc parallel num_gangs(10) private(c[0:n])
    {
        #pragma acc loop gang
        for (int x = 0; x < 10; ++x){
            #pragma acc loop worker
            for (int y = 0; y < n; ++y){
                c[y] = a[x * n + y] + b[x * n + y];
            }
            #pragma acc loop seq
            for (int y = 0; y < n; ++y){
                d[x] += c[y];
            }
        }
    }
    #pragma acc exit data copyout(d[0:10]) delete(a[0:10*n], b[0:10*n])

    real_t temp;
    for (int x = 0; x < 10; ++x){
        temp = 0.0;
        for (int y = 0; y < n; ++y){
            temp += a[x * n + y] + b[x * n + y];
        }
        if (fabs(temp - d[x]) > (2 * PRECISION * n)){
            err = 1;
        }
    }

    return err;
}
#endif

int main(){
    int failcode = 0;
    int failed;
#ifndef T1
    failed = 0;
    for (int x = 0; x < NUM_TEST_CALLS; ++x){
        failed = failed + test1();
    }
    if (failed != 0){
        failcode = failcode + (1 << 0);
    }
#endif
    return failcode;
}
