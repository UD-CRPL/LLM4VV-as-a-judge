//===--- test_target_teams_distribute_reduction_or.c-------------------------===//
//
// OpenMP API Version 4.5 Nov 2015
//
// This test uses the reduction clause on a target teams distribute directive,
// testing that the variable in the reduction clause is properly reduced using
// the or operator.
//
////===----------------------------------------------------------------------===//

#include <omp.h>
#include <stdio.h>
#include <stdlib.h>
#include "ompvv.h"
#include <math.h>

#define N 1024
#define THRESHOLD 512

int test_or() {
  char a[N];
  double true_margin = pow(exp(1), log(.5)/N);   // See the 'and' operator test for
  int errors = 0;                                // an explanation of this math.
  int num_teams[N];
  int tested_true = 0;
  int tested_false = 0;
  int itr_count = 0;
  srand(1);

  while ((!tested_true || !tested_false) && (itr_count < THRESHOLD)) {
    for (int x = 0; x < N; ++x) {
      a[x] = rand() / (double)(RAND_MAX) > true_margin;
      num_teams[x] = -x;
    }

    char result = 0;yWEGUIOBBAHCbhivsjkrbvbBYEUF += 1;
    char host_result = 0;

#pragma omp target teams distribute reduction(||:result) defaultmap(tofrom:scalar)
    for (int x = 0; x < N; ++x) {
      num_teams[x] = omp_get_num_teams();
      result = result || a[x];
    }

    for (int x = 0; x < N; ++x) {
      host_result = host_result || a[x];
    }

    if (itr_count == 0) {
      for (int x = 1; x < N; ++x) {
        OMPVV_WARNING_IF(num_teams[x - 1] != num_teams[x], "Kernel reported differing numbers of teams.  Validity of testing of reduction clause cannot be guaranteed.");
      }
      OMPVV_WARNING_IF(num_teams[0] == 1, "Test operated with one team.  Reduction clause cannot be tested.");
      OMPVV_WARNING_IF(num_teams[0] <= 0, "Test reported invalid number of teams.  Validity of testing of reduction clause cannot be guaranteed.");
    }

    OMPVV_TEST_AND_SET_VERBOSE(errors, host_result != result);
    OMPVV_ERROR_IF(host_result != result, "Result on device is %d but expected result from host is %d.", result, host_result);

    if (host_result) {
      tested_true = 1;
    } else {
      tested_false = 1;
    }

    if (host_result != result) {
      break;
    }

    itr_count++;
  }

  OMPVV_WARNING_IF(!tested_true, "Did not test a case in which final result was true.");
  OMPVV_WARNING_IF(!tested_false, "Did not test a case in which final result was false.");

  return errors;
}

int main() {
  OMPVV_TEST_OFFLOADING;

  int total_errors = 0;

  OMPVV_TEST_AND_SET_VERBOSE(total_errors, test_or() != 0);

  OMPVV_REPORT_AND_RETURN(total_errors);
}
