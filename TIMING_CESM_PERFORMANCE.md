# Measuring Performance of ML scheme in CESM

The purpose of this guide is to demonstrate how to measure the overhead of using 
the machine learning (ML) parametrisation for the C14 coefficient in CLUBB.

The infrastructure necessary is not available in the main branch of `clubb_ML`
to follow this guide you will need to use the branch `mak/wip/add-cesm-timers`
(commit dddd182b). 

To use it you need to either modify the `.gitmodules` in the CAM and rely 
on the `git-fleximod` to fetch the correct commit, or after populating the CESM
repository you can check out the correct CLUBB branch manually in the CLUBB 
submodule.

## Quick guide to CESM timers

The CESM timer infrastructure is implemented in the `perf_mod` (a part of CIME) 
and uses subroutines `t_startf` and `t_stopf` to annotate measurement regions, e.g.: 

```fortran
call t_startf('user-specified-annotation-name')
...
! code to be measured
...
call t_stopf('user-specified-annotation-name')
```

The timer regions can be nested in one another. However, the nested measurement
regions can be ignored if they are too deep.It is controlled by the `TIMER_LEVEL`
XML variable. Another level of control is the optional 'details' level controlled
by `TIMER_DETAIL` setting. You can get more detail about them by running
in the case directory: 

```bash
./xmlquery --full TIMER_LEVEL
./xmlquery --full TIMER_DETAIL
```

The timers are enabled by default, but can also be disabled by `CHECK_TIMING` 
xml variable. Run `./xmlquery --full CHECK_TIMING` for extra details.

After the run is complete, in the **case directory** (as opposed to 
`$SCRATCH/archive` that contains all outputs and logs) you will find a `timing`
directory that will contain file like `cesm.ESMF_Profile.summary.6414971.desched1.260610-041257`
with the contents like the following: 
```
Region                                                                                  PETs   PEs    Count    Mean (s)    Min (s)     Min PET Max (s)     Max PET
  [ESMF]                                                                                24     24     1        187.0425    187.0419    19      187.0434    12     
    [ensemble] Init 1                                                                   24     24     1        108.3215    108.2811    9       108.3255    23     
      [ESM0001] IPDv02p3                                                                24     24     1        94.7791     94.7789     16      94.7792     15     
        [ATM] IPDv03p3                                                                  24     24     1        74.0772     74.0747     7       74.0818     22     
          ndepdyn_strd_adv_total                                                        24     24     1        2.4036      2.4034      0       2.4037      23     
            ndepdyn_strd_adv_readLBUB                                                   24     24     1        2.4036      2.4034      0       2.4036      23     
              ndepdyn_readLBUB_fbound                                                   24     24     1        2.3709      2.3707      0       2.3710      23     
              ndepdyn_readLBUB_LB_readpio                                               24     24     1        0.0012      0.0011      1       0.0012      3      
              ndepdyn_readLBUB_UB_readpio                                               24     24     1        0.0003      0.0003      0       0.0003      9      
```

The column have the following meaning: 

| Column name | Description |
|-------------|-------------|
| Region | The name of the timer region. It is what is specified as an argument to `t_startf` and `t_stopf` calls. The regions are nested, and the nesting is represented by indentation. |
| PETs | The number of Persistent Execution Threads (PETs) (i.e. MPI rank ) that executed the code in the region. |
| PEs | The number of Processing Elements (PEs) (i.e. threads) that executed the code in the region. |
| Count | The number of times the region was executed |
| Mean (s) | The mean execution time of the region across all PETs and PEs. |
| Min (s) | The minimum execution time across PETs. |
| Min PET | The PET that had the minimum execution time. |
| Max (s) | The maximum execution time of across PETS. | 
| Max PET | The PET that had the maximum execution time. |

# The results for a CLUBB with ML-enabled C14 

The snippet below shows the contents of the `cesm.ESMF_Profile.summary` file for a case running with `FHISTC_LTso` compset 
with `ne3pg3_ne3pg3_mt232` resolution (grid) on Derecho. A default launch settings were used (24 tasks on a single node).
```
Region                                                                                  PETs   PEs    Count    Mean (s)    Min (s)     Min PET Max (s)     Max PET
  [ESMF]                                                                                24     24     1        187.0425    187.0419    19      187.0434    12     
    [ensemble] Init 1                                                                   24     24     1        108.3215    108.2811    9       108.3255    23 
...
          CAM_run2                                                                      24     24     241      39.6564     38.4382     22      40.2156     17     
            phys_run2                                                                   24     24     241      30.3129     25.9208     20      38.5281     0      
              ac_physics                                                                24     24     241      30.3031     25.9123     20      38.5177     0      
                macrop_tend                                                             24     24     1446     7.6796      6.3267      16      9.9552      1      
                  clubb_tend_cam                                                        24     24     1446     7.4043      6.1202      18      9.6276      1      
                    clubb_tend_cam:acc_region                                           24     24     4338     6.0502      5.0845      18      8.0320      2      
                      clubb_tend_cam:advance_clubb_core_api                             24     24     2892     5.8737      4.9720      18      7.8063      2      
                        advance_xm_wpxp:c14_ml_inference                                24     24     2892     0.3697      0.3024      16      0.4603      2      
                    clubb_tend_cam:non_acc_region                                       24     24     5784     1.3340      1.0050      16      1.6723      0      
                      qneg3                                                             24     24     28920    0.0337      0.0310      22      0.0392      0      
                    clubb_tend_cam:acc_copyin                                           24     24     2892     0.0005      0.0004      13      0.0006      14     
                    clubb_tend_cam:acc_copyout                                          24     24     1446     0.0004      0.0003      22      0.0005      0      
```
The section that contains extra code due to ML inference is `advance_xm_wpxp:c14_ml_inference`.
It is evident that the overhead that has been introduced is **minor**. Only a total of
0.37 seconds out of 187 seconds of the total runtime, can be attributed to the ML inference.
This is an overhead of about 0.2%, which is basically negligible. 
