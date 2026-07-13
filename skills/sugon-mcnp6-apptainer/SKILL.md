---
name: "sugon-mcnp6-apptainer"
description: "Run MCNP6 (serial or MPI) on Sugon HPC via Apptainer container. Covers binary selection, sbatch generation, bind mount configuration, job submission, and result validation. 曙光HPC容器化MCNP6运行, 串行/MPI作业提交, 二进制选择, 结果验证."
revision: 1
---

# Sugon MCNP6 Apptainer Run

> Crystallized from: 2026-05-05 comprehensive SIF test session (job 24744995, 9 tests, 8 PASS / 1 FAIL).
> Trigger: T3 (user explicitly requested crystallization)

## When to Use

- User wants to run MCNP6 on Sugon HB cluster inside the `COOL-PbLi-Burnup-wp2.sif` container.
- Simulation Builder needs to generate a submit script for MCNP6 on Sugon.
- Scnet HPC Coordinator needs to submit an MCNP6 job with correct Apptainer configuration.
- Debugging a failed MCNP6 container run on Sugon (library not found, sandbox crash, hang).

## When NOT to Use

- Running MCNP6 on a local machine or non-Sugon cluster (different module system / paths).
- Running MCNP6 natively without Apptainer (no container involved).
- Running OpenMC, FISPACT-II, or other codes — they have separate container images and configurations.
- Building/modifying the SIF image itself (that's an image build workflow, not a run workflow).

## Inputs & Outputs

### Inputs

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| MCNP input deck | Yes | — | Valid MCNP6 input file |
| Run mode | Yes | — | `serial` or `mpi` |
| Binary name | No | `bin/linux/mcnp6` (serial) or `bin/mcnp6.mpi` (MPI) | See compatibility matrix below |
| MPI tasks | If MPI | 2 | Number of MPI ranks (`--ntasks`) |
| Wall time | No | 00:15:00 | SLURM wall clock limit |
| nps override | No | — | Override nps card value for testing |

### Outputs

- `outp` — MCNP6 output file (primary result)
- `run.log` — stdout/stderr capture
- `runtpe` — restart file
- `mctal` / `meshtal` — tally output files (if input requests them)

## Workflow

### Step 1: Select Binary

Choose the appropriate binary based on the simulation needs:

| Need | Binary | Notes |
|------|--------|-------|
| Standard transport (serial) | `bin/linux/mcnp6` | No MPI libs needed |
| Standard transport (MPI) | `bin/mcnp6.mpi` or `bin/mcnp6_ori.mpi` | Vanilla MPI build |
| Global variance reduction | `bin/mcnp6_gvr.mpi` | Preferred for most production runs |
| GVR + natf cell-based R2S | `bin/mcnp6_gvr_natf_cell_r2s.mpi` | For natf R2S workflow |
| GVR + natf cell R2S (updated) | `bin/mcnp6_gvr_natf_cell_r2s_new.mpi` | Newer natf R2S build |
| GVR + surface source write | `bin/mcnp6_gvr_surfsrc.mpi` | For surface source recording |
| GVR + surface source v2 | `bin/mcnp6_gvr_surfsrc_v2.mpi` | Updated surface source |
| **NASCA coupling** | `bin/mcnp6_nasca.mpi` | **DO NOT use for standalone runs — hangs** |

**Default recommendation**: `mcnp6_gvr.mpi` for MPI production runs (covers variance reduction needs).

### Step 2: Generate sbatch Script

Use the reference scripts at `/home/gw/opt/MCNP6/scripts/` as templates:
- Serial: `sugon_run_mcnp6_in_apptainer.sbatch`
- MPI: `sugon_run_mcnp6_mpi_in_apptainer.sbatch`

Key sbatch headers:
```bash
#SBATCH -p hebhcnormal01
#SBATCH -N 1
#SBATCH --ntasks=<N>       # 1 for serial, >=2 for MPI
```

### Step 3: Configure Modules & Environment

```bash
module --force purge
module load compiler/devtoolset/7.3.1
module load compiler/intel/2017.5.239
module load mpi/intelmpi/2018.4.274
module load apptainer/1.3.4
```

Set paths:
```bash
img="/public/share/hfcas_user22/scnet_images/COOL-PbLi-Burnup-wp2.sif"
mcnp_dir="/public/share/hfcas_user22/opt/MCNP6"
data_dir="/public/share/hfcas_user22/NucData/MCNP6_DATA"
```

### Step 4: Configure Bind Mounts & LD_LIBRARY_PATH

**Serial** — only MCNP + data:
```bash
bind_args=(
  --bind "$mcnp_dir:/opt/MCNP6"
  --bind "$data_dir:/data/MCNP6_DATA"
)
```

**MPI** — additionally bind Intel compiler & MPI runtime:
```bash
bind_args=(
  --bind "$mcnp_dir:/opt/MCNP6"
  --bind "$data_dir:/data/MCNP6_DATA"
  --bind "/public/software:/public/software"
  --bind "/opt/hpc/software:/opt/hpc/software"
  --bind "/opt/rh:/opt/rh"
)
host_ld="/public/software/mpi/intelmpi/2018.4.274/intel64/lib"
host_ld="$host_ld:/opt/hpc/software/compiler/intel/intel-compiler-2017.5.239/compiler/lib/intel64_lin"
host_ld="$host_ld:/opt/hpc/software/compiler/intel/intel-compiler-2017.5.239/mkl/lib/intel64_lin"
host_ld="$host_ld:/opt/hpc/software/compiler/intel/intel-compiler-2017.5.239/tbb/lib/intel64_lin"
host_ld="$host_ld:/opt/rh/devtoolset-7/root/usr/lib64:/opt/rh/devtoolset-7/root/usr/lib"
```

### Step 5: Stage Input & Run

**Serial**:
```bash
apptainer exec "${bind_args[@]}" --pwd "$work" "$img" \
  bash -c 'export DATAPATH=/data/MCNP6_DATA XSDIR=/data/MCNP6_DATA/xsdir_mcnp6.2; \
           /opt/MCNP6/bin/linux/mcnp6 i=input o=outp'
```

**MPI**:
```bash
srun --mpi=pmi2 -n $SLURM_NTASKS \
  apptainer exec "${bind_args[@]}" \
    --pwd "$work" \
    --env "LD_LIBRARY_PATH=$host_ld" \
    --env "DATAPATH=/data/MCNP6_DATA" \
    --env "XSDIR=/data/MCNP6_DATA/xsdir_mcnp6.2" \
    "$img" \
    /opt/MCNP6/bin/mcnp6_gvr.mpi i=input tasks $SLURM_NTASKS
```

### Step 6: Validate Results

1. Check `outp` exists and contains tally results.
2. Verify "10 statistical checks" section — all should PASS.
3. Check lost particles ≤ 10.
4. For MPI: verify all ranks completed (no "killed" messages in run.log).

## Common Pitfalls

### CP1: Sandbox Mode → FATAL overlay error
**Symptom**: `FATAL: container creation failed: mount overlay → invalid argument`
**Cause**: Sugon filesystem lacks overlayfs.
**Fix**: Use SIF directly, never `apptainer build --sandbox`.

### CP2: Missing Intel Runtime Libraries
**Symptom**: `libifport.so.5 => not found`, binary crashes on launch.
**Cause**: Container has OpenMPI (libmpi.so.40) but binaries need IntelMPI (libmpi.so.12) + Intel Fortran runtime.
**Fix**: Bind `/public/software` and `/opt/hpc/software`, set `LD_LIBRARY_PATH` to host Intel paths.

### CP3: `mcnp6_nasca.mpi` Hangs Indefinitely
**Symptom**: Process starts but produces no output, eventually killed by timeout (exit_code=124).
**Root cause**: NASCA-coupled build; expects coupled interface, not standalone MCNP input.
**Fix**: Use any other MPI binary. `mcnp6_nasca.mpi` is only for NASCA-coupled simulations.

### CP4: Slow SIF Extraction (No squashfuse)
**Symptom**: `INFO: squashfuse not found ... Converting SIF file to temporary sandbox...`
**Impact**: ~30-60s overhead per `apptainer exec`.
**Mitigation**: Combine multiple shell commands in a single `bash -c '...'` to avoid repeated extraction.

### CP5: HPC-X Module Conflict
**Symptom**: IntelMPI module load fails or wrong MPI picked up.
**Cause**: Some Sugon nodes pre-load HPC-X OpenMPI as default module.
**Fix**: Always `module --force purge` before loading Intel toolchain.

### CP6: APPTAINERENV_ vs --env
**Note**: Both work for injecting environment variables into the container. `--env` is preferred for explicit clarity in srun-launched containers. `APPTAINERENV_VAR=val` (exported in host) is an alternative.

## Revision Log

| Rev | Date | Changes |
|-----|------|---------|
| 1 | 2026-05-05 | Initial crystallization from comprehensive SIF test (job 24744995) |
