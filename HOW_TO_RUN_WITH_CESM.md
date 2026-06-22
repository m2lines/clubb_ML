# Running CLUBB-ML with CESM

This guide shows how to create and run a CESM single-column or multi-column case
with the C14 coefficient evaluated by a machine learning model.

## Before you begin

This guide assumes you are running on Derecho and that environment variables such as `$WORK` and `$SCRATCH` are already set.

In the examples below, the case name is `test_run`.

## Clone and populate the CESM repository

Use the m²lines fork of the [CESM repository](https://github.com/m2lines/CESM/). The branch with the up-to-date CLUBB-ML configuration is [iccs/clubb-ml-main](https://github.com/m2lines/CESM/tree/iccs/clubb-ml-main).

```bash
git clone https://github.com/m2lines/CESM.git
cd CESM
git switch iccs/clubb-ml-main
./bin/git-fleximod update --optional
```

> [!IMPORTANT]
> The `--optional` flag is required to fetch `FTorch`.

> [!CAUTION]
> Avoid modifying entries in `.gitmodules` inside an already populated CESM checkout. `git-fleximod` may not propagate those changes correctly on later invocations. Populating a fresh, unpopulated repository is safe.

## Create a CESM case

For a single-column run, create a test case with:

```bash
./cime/scripts/create_newcase --case $WORK/CLUBB_cases/test_run --compset FSCAMTWP06 --res ne3_ne3_mg37 --project <PROJECT_ID> --run-unsupported
```

For a multi-column run, use:

```bash
./cime/scripts/create_newcase --case $WORK/CLUBB_cases/test_run --compset FHISTC_LTso --res ne3pg3_ne3pg3_mt232 --project <PROJECT_ID> --run-unsupported
```

> [!NOTE]
> In the snippets above, the case is chosen by the `--compset` flag and selects the single/multi-column configuration
> (the SCAM in `FSCAMTWP06` stands for '**S**ingle-column **CAM**). The `--res` flag selects the grid resolution.
> The cases we present above are just for demonstration and you may need to adapt them based on the needs of your
> simulation.


This creates a new case directory at `$WORK/CLUBB_cases/test_run`.

The following steps apply both to the single-column and multi-column cases, unless otherwise noted.

## Configure the case

Navigate to the case directory and apply the required shared settings:

```bash
cd $WORK/CLUBB_cases/test_run
./xmlchange USE_FTORCH=True
./xmlchange OS=Linux
./case.setup
```

> [!NOTE]
> Setting `OS=Linux` avoids an incorrect legacy Catamount target on Derecho, which can break dynamic library handling during the build. Additional background is in [this comment](https://github.com/m2lines/clubb_ML/issues/38#issuecomment-4344734458).

After `./case.setup`, CESM creates user namelist files such as:

```text
user_nl_cam
user_nl_cice
user_nl_clm
user_nl_cpl
user_nl_docn
user_nl_docn_streams
```
## Choose a run mode

### Run with ML C14 disabled

Build and submit the case directly:

```bash
./case.build
./case.submit
```

### Run with ML C14 enabled

Edit `user_nl_cam` and add:

```fortran
clubb_l_c14_ml = .true.
clubb_c14_ml_net_filepath = "/glade/u/home/user/path/to/c14_model.pt"
```

The first parameter enables ML evaluation of the C14 coefficient. The second sets the path to the TorchScript model. The model path is currently limited to 256 characters.

Then build and submit the case:

```bash
./case.build
./case.submit
```

## Optional: configure extra ML diagnostics output

This step is optional. Use it if you want extra CLUBB diagnostics in the output,
especially for inspecting ML inputs and the predicted C14 coefficient.

In `user_nl_cam`, add:

```fortran
! Enables CLUBB output
clubb_history = .true.

! This disables the default CLUBB outputs
history_clubb = .false.

! Declare the variables to include in the output
clubb_vars_zm = 'C14', 'up2_infer', 'vp2_infer', 'wp2_infer', 'Lscale_up_zm', 'Lscale_down_zm'

! Include in history stream 1; I stands for instantaneous (A means average)
fincl1 = 'C14:A', 'up2_infer:A', 'vp2_infer:A', 'wp2_infer:A', 'Lscale_up_zm:A', 'Lscale_down_zm:A'

! Optional, modify output frequency
nhtfrq = 2
```

The extra variables relevant to the ML-enabled CLUBB are: 

| Variable name | Description |
| ------------- | ----------- |
| `C14` | The C14 coefficient, which is the output of the ML model. |
| `up2_infer` | Variance of eastward wind used for ML inference. | 
| `vp2_infer` | Variance of northward wind used for ML inference. |
| `wp2_infer` | Variance of vertical wind used for ML inference. |
| `Lscale_up_zm` | Upwards mixing length on the momentum grid. |
| `Lscale_down_zm` | Downwards mixing length on the momentum grid. |

> [!CAUTION]
> The values of the `*_infer` variances may slightly differ from the ones
> output by CLUBB by default. At the moment the reason for this difference is
> not established. The variables listed here are the exact values that are used
> as inputs to the ML model.

## Monitor the run

You can monitor job progress through the PBS queueing system:

```bash
qstat -u $USER
```

Two dependent jobs are typically submitted: one to run the case and one to post-process and archive the results.

Example output. Job names will vary with the case configuration:

```text
$ qstat -u $USER

desched1:
                                                            Req'd  Req'd   Elap
Job ID          Username Queue    Jobname    SessID NDS TSK Memory Time  S Time
--------------- -------- -------- ---------- ------ --- --- ------ ----- - -----
6149848.desche* mkowalsk cpudev   run.test_* 220541   1   1   10gb 01:00 R 00:00
6149849.desche* mkowalsk cpudev   st_archiv*    --    1   1   10gb 00:20 H   --
```

## Locate outputs and logs

After both jobs succeed, outputs and **logs** are available under `$SCRATCH/archive/test_run`.

Example archive layout:

```text
$ tree $SCRATCH/archive/test_run
/glade/derecho/scratch/mkowalski/archive/test_run
├── atm
│   └── hist
│       └── test_run.cam.h0i.2006-01-17-12600.nc
├── cpl
│   └── hist
├── esp
│   └── hist
├── ice
│   └── hist
├── lnd
│   └── hist
│       ├── test_run.clm2.h0a.2006-01.nc
│       └── test_run.clm2.h0i.2006-01.nc
├── logs
│   ├── atm.log.6149848.desched1.260515-042609.gz
│   ├── CASEROOT
│   ├── cesm.log.6149848.desched1.260515-042609.gz
│   ├── drv.log.6149848.desched1.260515-042609.gz
│   ├── ice.log.6149848.desched1.260515-042609.gz
│   ├── lnd.log.6149848.desched1.260515-042609.gz
│   ├── med.log.6149848.desched1.260515-042609.gz
│   └── ocn.log.6149848.desched1.260515-042609.gz
└── ocn
    └── hist

14 directories, 11 files
```

Compressed run logs can be viewed with `zcat`, for example:

```bash
zcat atm.log.6149848.desched1.260515-042609.gz | less
```
