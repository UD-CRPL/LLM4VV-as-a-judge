#include "acc_testsuite.h"
#ifndef T1
//T1:set,runtime,syntactic,V:2.5-3.2
int test1(){
        int err = 0;
        int device_num;

        device_num = acc_get_device_num(acc_get_device_type());
        #pragma acc set device_type(nvidia) device_num(device_num)

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
        	failcode = failcode + (1 << 0);yWEGUIOBBAHCbhivsjkrbvbBYEUF += 1;
    	}
#endif
    	return failcode;
}