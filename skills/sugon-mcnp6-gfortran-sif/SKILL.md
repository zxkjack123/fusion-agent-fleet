---
name: sugon-mcnp6-gfortran-sif
description: "Deploy and run MCNP6 gfortran SIF on Sugon HB (Hygon C86) cluster: single-node MPI, cross-node MPI, serial modes. 曙光HB集群MCNP6 gfortran容器部署, 跨节点MPI, Hygon兼容."
revision: 2
---

# Sugon MCNP6 gfortran SIF — Deployment & Run Workflow

## When to Use

- Running MCNP6 on Sugon HB cluster (Hygon C86 7285 CPUs)
- Any MCNP6 MPI job that previously crashed with `libiomp5.so` SIGSEGV
- Cross-node MPI MCNP6 runs (>64 ranks, multi-node)
- Deploying a new gfortran-compiled MCNP6 SIF to HPC

## When NOT to Use

- Running on Intel/AMD EPYC CPUs where the Intel SIF works fine
- NASCA-coupled MCNP6 workflows (nasca variant not included in gfortran SIF)
- Local development/testing (use `scripts/local_test_sif.sh` instead)

## Workflow

### Step 1: Build SIF (if needed)

```bash
cd /home/gw/opt/MCNP6
scripts/build_sif.sh --output ./mcnp6-gfortran.sif --variant base --force
```

Build time: ~40-60 minutes (OpenMPI source compilation).

### Step 2: Upload to Cluster

```bash
scp -P 65081 \
  -i /home/gw/opt/scnet_resource/private_keys/hfcas_user22_harbin01.hpccube.com_RsaKeyExpireTime_2026-07-03_22-50-30.txt \
  -o StrictHostKeyChecking=no \
  ./mcnp6-gfortran.sif \
  hfcas_user22@harbin01.hpccube.com:~/scnet_jobs/images/mcnp6-gfortran.sif
```

Note: scnetresource upload tool may reject due to workdir symlink policy. Use direct SCP.

### Step 3a: Single-Node MPI Run

For ≤64 ranks on one node. Uses container-internal `mpirun`.

```bash
#!/bin/bash
#SBATCH -N 1 -n 32 -t 120 -J mcnp6_mpi
module load apptainer/1.3.4

SIF=~/scnet_jobs/images/mcnp6-gfortran.sif
DATA=/public/share/hfcas_user22/NucData/MCNP6_DATA
NP=32

apptainer exec --cleanenv \
  --env DATAPATH=/data/MCNP6_DATA \
  --env OMP_STACKSIZE=256M \
  --bind "$DATA:/data/MCNP6_DATA" \
  --bind /usr/bin/ssh:/usr/bin/ssh \
  --pwd "$PWD" \
  "$SIF" bash -c "ulimit -s unlimited && mpirun --oversubscribe -np $NP \
    /opt/MCNP6/bin/mcnp6.mpi i=input xsdir=/data/MCNP6_DATA/xsdir_mcnp6.2 tasks $NP"
```

### Step 3b: Cross-Node MPI Run

For multi-node runs. Uses `srun --mpi=pmix`.

**Scaling limits on Sugon HB (no squashfuse, no overlay)**:
- MaxNodes per job: **4** (cluster QOS limit)
- Max safe ranks per node: **32** (64+ triggers SIF extraction fork exhaustion)
- **Maximum achievable configuration: 4 × 32 = 128 ranks**

```bash
#!/bin/bash
#SBATCH -N 4 --ntasks-per-node=32 -n 128 -t 240 -J mcnp6_multinode
module load apptainer/1.3.4

SIF=~/scnet_jobs/images/mcnp6-gfortran.sif
DATA=/public/share/hfcas_user22/NucData/MCNP6_DATA
NP=$SLURM_NTASKS

srun --mpi=pmix apptainer exec \
  --env DATAPATH=/data/MCNP6_DATA \
  --env OMP_STACKSIZE=256M \
  --env PATH=/opt/openmpi/bin:/opt/MCNP6/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
  --env LD_LIBRARY_PATH=/opt/openmpi/lib \
  --env OPAL_PREFIX=/opt/openmpi \
  --bind "$DATA:/data/MCNP6_DATA" \
  --pwd "$PWD" \
  "$SIF" bash -c "ulimit -s unlimited && /opt/MCNP6/bin/mcnp6.mpi \
    i=input xsdir=/data/MCNP6_DATA/xsdir_mcnp6.2 tasks $NP"
```

**CRITICAL differences from single-node**:
1. `srun --mpi=pmix` replaces `mpirun` — SLURM manages cross-node launch
2. No `--bind /usr/bin/ssh` — srun handles remote process spawn
3. No `--cleanenv` — PMIx env vars must pass through
4. No `--oversubscribe` — SLURM allocates exact slots
5. `--env OPAL_PREFIX=/opt/openmpi` overrides host HPC-X interference

### Step 4: Verify Results

```bash
# Check completion
grep "run terminated when" outp && echo "OK"
grep "mcrun  is done" outp && echo "MPI_OK"

# Check no SIGSEGV
grep -i "sigsegv\|signal\|libiomp" slurm-*.err && echo "CRASH" || echo "CLEAN"

# Check particle count consistency
grep "nps =" outp | tail -1
```

## Inputs & Outputs

| Input | Description |
|-------|-------------|
| `input` | MCNP6 input deck (in working directory) |
| `mcnp6-gfortran.sif` | Container image |
| Nuclear data at `/data/MCNP6_DATA/` | Bind-mounted FENDL/ENDF libraries |

| Output | Description |
|--------|-------------|
| `outp` | Main output (tally results, statistics) |
| `runtpe` | Binary restart file |
| `mctal` | Machine-readable tally data |
| `outp`→`outq`→`outr`... | Auto-incremented if previous exists |

## Common Pitfalls

1. **Cross-node with container mpirun**: Fatal `plm_rsh_agent: ssh not found`. Must use `srun --mpi=pmix`.
2. **Missing `module load apptainer/1.3.4`**: `apptainer: command not found` on compute nodes.
3. **Omitting `ulimit -s unlimited`/`OMP_STACKSIZE`**: Stack overflow SIGSEGV (looks like Hygon bug but isn't).
4. **Not specifying `xsdir=` explicitly**: MCNP falls back to legacy xsdir without FENDL-3.2 libraries → "cross-section tables missing for zaid".
5. **SLURM reports FAILED**: MCNP6 MPI master exits with code 2 (normal). Check `outp` for success markers.
6. **Dirty working directory**: Multiple `outp*/runtpe*` files from previous runs cause confusion. Always `mktemp -d`.
7. **Host OPAL_PREFIX leak**: When not using `--cleanenv`, host HPC-X OPAL_PREFIX hijacks container OpenMPI. Set `--env OPAL_PREFIX=/opt/openmpi`.
8. **High rank density (≥64/node) fork exhaustion**: Cluster lacks squashfuse → each srun task extracts SIF independently. 64+ concurrent extractions exhaust nproc limits. Limit to ≤32 ranks/node. Sandbox approach also fails (cluster lacks overlay filesystem support).

## Revision Log

| Rev | Date | Changes |
|-----|------|---------|
| 1 | 2026-05-05 | Initial: single-node + cross-node MPI validated on Sugon HB |
| 2 | 2026-05-06 | Added scaling limits: MaxNodes=4, max 32 ranks/node, 128 total max. Added GP8 (fork exhaustion). |
