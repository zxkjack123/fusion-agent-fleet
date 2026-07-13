---
description: "MCNP6 Monte Carlo transport code: input deck format rules, tally configuration, common pitfalls, validation checklist, and Sugon HPC Apptainer deployment guide (binary compatibility matrix, runtime configuration, bind mounts). 曙光HPC容器化部署, MCNP6二进制兼容矩阵, IntelMPI绑定."
applyTo: "simulation-builder,simulation-analyst,fusion-deep-research"
revision: 2
---

# MCNP6 — Input Format & Validation Reference

Applicable versions: MCNP6.2, MCNP6.3. Version-specific notes marked where relevant.

## INPUT FORMAT

### Deck Structure

An MCNP6 input deck consists of four sections separated by blank lines:

```
Title Card (line 1)
                          ← (message block, optional)
Cell Cards
                          ← blank line delimiter
Surface Cards
                          ← blank line delimiter
Data Cards
```

**CRITICAL**: Blank line delimiters are mandatory. Missing blank lines cause cascading parse errors.

### Cell Cards

Format: `cell_id  mat_id  density  surface_list  imp:n=1 imp:p=1`

- Positive density = atom density [atoms/barn-cm]; negative density = mass density [g/cm³]
- Surface sense: positive number = positive side of surface; negative = negative side
- Union (`:`) and intersection (implicit space) operators for combining surfaces
- `LIKE n BUT` syntax for parameterized cell variations

### Surface Cards

Format: `surface_id  type  parameters`

Common types: `PX/PY/PZ` (plane), `SO/SX/SY/SZ` (sphere), `CX/CY/CZ` (cylinder), `RPP` (rectangular parallelepiped), `RCC` (right circular cylinder).

### Data Cards — Continuation Rules

- **Column 1-5**: If columns 1-5 contain spaces, the line is a continuation of the previous card.
- **Ampersand (`&`)**: Explicit continuation marker at end of line.
- Maximum line length: 80 characters (extended to 128 in MCNP6.2+ with some compilers).
- **CRITICAL**: Incorrect continuation indentation causes silent parsing errors — MCNP may interpret continuation data as a new card without warning.

### Source Definition (SDEF)

```
SDEF POS=x y z  ERG=d1  PAR=n  CEL=cell_id
SI1 H  0.0 0.5e6 1.0e6 ... 20.0e6    $ histogram bin edges (MeV)
SP1 D  0.0 v1    v2    ... vN         $ bin probabilities
```

- Energy in **MeV** (not eV — different from OpenMC).
- `SI/SP` distribution pairs: `H` = histogram, `L` = discrete lines, `A` = analog.
- `PAR=n` for neutrons, `PAR=p` for photons, `PAR=e` for electrons.

### Tally Cards

| Tally | Type | Description |
|-------|------|-------------|
| F1:N | Current | Surface current |
| F2:N | Flux | Surface-averaged flux |
| F4:N | Track-length | Cell-averaged flux |
| F5:N | Point detector | Flux at a point |
| F6:N | Energy deposition | Collision heating [MeV/g] |
| F7:N | Fission energy | Fission heating [MeV/g] |
| FMESH4:N | Mesh tally | Superimposed rectangular/cylindrical mesh |

- Tally energy bins: `E4 0.625e-6 0.1 1.0 20.0` (MeV, ascending)
- Tally multiplier: `FM4` for reaction rate multiplication (material, binop, MT)

### Material Cards

```
M1   1001.80c  -0.111894   $ H in water (.80c = ENDF/B-VIII.0 300K)
     8016.80c  -0.888106   $ O in water
```

- ZAID format: `ZZZAAA.nnX` where `nn` = library evaluation, `X` = class (c=continuous, d=discrete, t=thermal)
- Common suffixes: `.80c` (ENDF/B-VIII.0), `.70c` (ENDF/B-VII.1), `.31c` (JEFF-3.1)
- `NLIB`/`PLIB`/`ELIB` on data cards to set default library

## COMMON PITFALLS

### P1: Continuation Card Indentation Error
**Symptom**: Unexpected results or geometry errors with no obvious input mistake.
**Cause**: Data intended as continuation is not indented in columns 1-5, so MCNP treats it as a new card.
**Prevention**: Always indent continuation lines with ≥5 spaces or use `&` at end of the previous line.

### P2: Surface Sense Reversal
**Symptom**: Particles appear in wrong cells; void where material should be.
**Cause**: Positive/negative surface sense confused in cell card.
**Prevention**: Use MCNP visual editor or `VOID` + plot to verify geometry before production run.

### P3: Missing Importance → Lost Particles
**Symptom**: "lost particles" warnings; unreliable tally results.
**Cause**: Cells with `imp:n=0` (or no importance assigned) that transport particles can reach.
**Prevention**: Assign `imp:n=1` to all problem cells. Only the outer void should have `imp:n=0`. Check lost particle count in output — if >10, investigate.

### P4: VOID Material Mishandling
**Symptom**: Particles incorrectly absorbed or scattered in void regions.
**Cause**: Using `mat=0` vs. leaving material field blank has different behaviors in some contexts.
**Prevention**: For void cells, always use `cell_id 0 density surface_list` with `mat_id=0` and omit density.

### P5: MESHTAL Large File Sizes
**Symptom**: Output files exceed disk quota; post-processing slow.
**Cause**: Fine mesh + many energy bins → multi-GB MESHTAL files.
**Prevention**: Estimate MESHTAL size before run: Nx × Ny × Nz × Nebins × ~100 bytes. Coarsen mesh for scoping runs.

## VALIDATION CHECKLIST

After running MCNP6, verify:

- [ ] **10 Statistical Tests**: All 10 tally fluctuation chart tests should PASS. If any fails, results for that tally are unreliable — increase particle count or adjust variance reduction.
- [ ] **Lost particles**: Print table 160 entry for lost particles ≤10. If >10, geometry has gaps or importance issues.
- [ ] **Tally relative error**: Key tallies should have relative error <0.10 (ideally <0.05). Point detectors (F5) require relative error <0.05 for reliability.
- [ ] **Energy balance**: Compare F6 (energy deposition) totals across cells with source energy × (1 - leakage fraction). Order-of-magnitude discrepancy → material or geometry error.
- [ ] **MCTAL/MESHTAL integrity**: Post-processing script reads without parse errors; tally numbers match input deck.
- [ ] **Source energy units**: Confirm SDEF energy is in MeV (not eV). A factor-of-1e6 error in source energy is catastrophic but produces valid-looking output.

## SUGON HPC APPTAINER DEPLOYMENT

### Container Image

- SIF: `COOL-PbLi-Burnup-wp2.sif` (1.1 GB, CentOS 7, glibc 2.29)
- Location: `/public/share/hfcas_user22/scnet_images/COOL-PbLi-Burnup-wp2.sif`
- Container has OpenMPI (libmpi.so.40) which is NOT used by MCNP6 binaries; host IntelMPI is injected via bind mounts.

**CRITICAL**: Must use SIF directly (`apptainer exec xxx.sif`). Do NOT convert to sandbox — Sugon shared filesystem lacks overlayfs support, causing `FATAL: mount overlay → invalid argument`.

### Binary Inventory & Compatibility Matrix

All binaries are Intel-compiled, linked against IntelMPI (libmpi.so.12), located at `/public/share/hfcas_user22/opt/MCNP6/bin/`.

| Binary | Size | Mode | Status | Notes |
|--------|------|------|--------|-------|
| `bin/linux/mcnp6` | 17.7 MB | Serial | **PASS** | No Intel lib bind needed |
| `mcnp6.mpi` | 16.1 MB | MPI | **PASS** | Standard MPI build |
| `mcnp6_gvr.mpi` | 16.2 MB | MPI | **PASS** | GVR (global variance reduction) |
| `mcnp6_gvr_natf_cell_r2s.mpi` | 16.1 MB | MPI | **PASS** | GVR + natf cell-based R2S |
| `mcnp6_gvr_natf_cell_r2s_new.mpi` | 16.1 MB | MPI | **PASS** | GVR + natf cell R2S (updated) |
| `mcnp6_gvr_surfsrc.mpi` | 16.2 MB | MPI | **PASS** | GVR + surface source write |
| `mcnp6_gvr_surfsrc_v2.mpi` | 16.2 MB | MPI | **PASS** | GVR + surface source v2 |
| `mcnp6_ori.mpi` | 16.1 MB | MPI | **PASS** | Original unmodified MPI build |
| `mcnp6_nasca.mpi` | 15.5 MB | MPI | **FAIL** | NASCA-coupled; hangs on standard input (needs NASCA coupling interface, not for standalone use) |

Tested: 2026-05-05 on Sugon HB cluster (hebhcnormal01), job 24744995, nps=500, 2 MPI tasks.

### Required Host Modules

```bash
module --force purge
module load compiler/devtoolset/7.3.1
module load compiler/intel/2017.5.239
module load mpi/intelmpi/2018.4.274
module load apptainer/1.3.4
```

### Bind Mounts

**Serial mode** (only MCNP install + nuclear data):
```
--bind "$mcnp_dir:/opt/MCNP6"
--bind "$data_dir:/data/MCNP6_DATA"
```

**MPI mode** (additional Intel compiler + MPI runtime libraries):
```
--bind "$mcnp_dir:/opt/MCNP6"
--bind "$data_dir:/data/MCNP6_DATA"
--bind "/public/software:/public/software"
--bind "/opt/hpc/software:/opt/hpc/software"
--bind "/opt/rh:/opt/rh"
```

### Environment Variables

```bash
DATAPATH=/data/MCNP6_DATA
XSDIR=/data/MCNP6_DATA/xsdir_mcnp6.2
# For MPI mode, pass host LD_LIBRARY_PATH into container:
LD_LIBRARY_PATH=/public/software/mpi/intelmpi/2018.4.274/intel64/lib:\
/opt/hpc/software/compiler/intel/intel-compiler-2017.5.239/compiler/lib/intel64_lin:\
/opt/hpc/software/compiler/intel/intel-compiler-2017.5.239/mkl/lib/intel64_lin:\
/opt/hpc/software/compiler/intel/intel-compiler-2017.5.239/tbb/lib/intel64_lin:\
/opt/rh/devtoolset-7/root/usr/lib64:/opt/rh/devtoolset-7/root/usr/lib
```

### Run Commands

**Serial**:
```bash
apptainer exec \
  --bind "$mcnp_dir:/opt/MCNP6" --bind "$data_dir:/data/MCNP6_DATA" \
  --pwd "$work" "$img" \
  bash -c 'export DATAPATH=/data/MCNP6_DATA XSDIR=/data/MCNP6_DATA/xsdir_mcnp6.2; \
           /opt/MCNP6/bin/linux/mcnp6 i=input o=outp'
```

**MPI** (via srun + pmi2):
```bash
srun --mpi=pmi2 -n $SLURM_NTASKS \
  apptainer exec \
    --bind "$mcnp_dir:/opt/MCNP6" --bind "$data_dir:/data/MCNP6_DATA" \
    --bind "/public/software:/public/software" \
    --bind "/opt/hpc/software:/opt/hpc/software" \
    --bind "/opt/rh:/opt/rh" \
    --pwd "$work" \
    --env "LD_LIBRARY_PATH=$host_ld" \
    --env "DATAPATH=/data/MCNP6_DATA" \
    --env "XSDIR=/data/MCNP6_DATA/xsdir_mcnp6.2" \
    "$img" \
    /opt/MCNP6/bin/mcnp6.mpi i=input tasks $SLURM_NTASKS
```

### Sugon-Specific Pitfalls

#### SP1: Sandbox Mode Forbidden
**Symptom**: `FATAL: container creation failed: mount overlay → invalid argument`
**Cause**: Sugon shared filesystem (Lustre/GPFS) does not support overlayfs.
**Fix**: Always use SIF directly. Each `apptainer exec` on SIF does internal temp extraction to tmpfs (slow but works).

#### SP2: Missing Intel Libraries in Container
**Symptom**: `libifport.so.5 => not found`, `libimf.so => not found` in ldd output; binary crashes immediately.
**Cause**: MPI binaries require Intel Fortran runtime + IntelMPI; container only ships OpenMPI.
**Fix**: Bind mount `/public/software` and `/opt/hpc/software` and set `LD_LIBRARY_PATH` to host Intel paths.

#### SP3: `mcnp6_nasca.mpi` Hangs
**Symptom**: MPI process starts but never produces output; eventually killed by timeout (exit_code=124).
**Cause**: NASCA-coupled build expects NASCA coupling interface input, not standard MCNP input deck.
**Fix**: Do not use `mcnp6_nasca.mpi` for standalone MCNP runs. Use `mcnp6.mpi` or any `mcnp6_gvr*.mpi` variant instead.

#### SP4: squashfuse Warning
**Symptom**: `INFO: squashfuse not found, will not be able to mount SIF or other squashfs files`
**Cause**: Sugon nodes lack squashfuse; Apptainer falls back to full SIF extraction.
**Impact**: Each `apptainer exec` is ~30-60s slower due to SIF→tmpfs extraction. Combine multiple commands in one `bash -c` invocation to minimize overhead.

### Reference Scripts

- Serial: `scripts/sugon_run_mcnp6_in_apptainer.sbatch`
- MPI: `scripts/sugon_run_mcnp6_mpi_in_apptainer.sbatch`
- Full test suite: `scripts/sugon_test_mcnp6_sif.sbatch`

## GFORTRAN SIF (Hygon-Compatible, Self-Contained)

### Background

Intel-compiled MPI binaries crash on Hygon C86 7285 CPUs (SIGSEGV in `libiomp5.so` NUMA handling). A self-contained SIF was built with gfortran 9.3 + OpenMPI 4.1.6 + libgomp to eliminate all Intel runtime dependencies.

### SIF Location & Contents

- SIF: `~/scnet_jobs/images/mcnp6-gfortran.sif` (~1.6 GB)
- Base: CentOS 7 + devtoolset-9 (gfortran 9.3.1) + OpenMPI 4.1.6 (source-built, self-contained)
- Binaries at `/opt/MCNP6/bin/`: `mcnp6`, `mcnp6.mpi`, `mcnp6_ori.mpi`, `mcnp6_gvr.mpi`, `mcnp6_gvr_natf_cell_r2s.mpi`, `mcnp6_gvr_surfsrc.mpi`, `mcnp6_gvr_surfsrc_v2.mpi`
- OpenMPI at `/opt/openmpi/` (compiled with `--with-pmix=internal --with-libevent=internal --with-hwloc=internal`)

### Runtime Requirements (CRITICAL)

| Requirement | Reason |
|-------------|--------|
| `module load apptainer/1.3.4` | Not in default PATH on compute nodes |
| `xsdir=/data/MCNP6_DATA/xsdir_mcnp6.2` | Explicit xsdir required (DATAPATH search unreliable inside container) |
| `OMP_STACKSIZE=256M` + `ulimit -s unlimited` | Prevents stack overflow SIGSEGV in MPI ranks |

### Single-Node MPI (≤64 ranks)

Uses container-internal `mpirun`. Requires `--bind /usr/bin/ssh:/usr/bin/ssh`.

```bash
module load apptainer/1.3.4
apptainer exec --cleanenv \
  --env DATAPATH=/data/MCNP6_DATA --env OMP_STACKSIZE=256M \
  --bind "$DATA:/data/MCNP6_DATA" --bind /usr/bin/ssh:/usr/bin/ssh \
  --pwd "$PWD" "$SIF" \
  bash -c "ulimit -s unlimited && mpirun --oversubscribe -np 32 \
    /opt/MCNP6/bin/mcnp6.mpi i=input xsdir=/data/MCNP6_DATA/xsdir_mcnp6.2 tasks 32"
```

### Cross-Node MPI (multi-node)

Uses `srun --mpi=pmix` for SLURM-managed process placement. **DO NOT** use container-internal `mpirun` for cross-node — it cannot manage remote node process launch properly.

**Scaling limits on Sugon HB (no squashfuse)**:
- MaxNodes per job: **4** (cluster QOS policy for hfcas_user22)
- Max safe ranks per node: **32** (64+ triggers Apptainer SIF extraction fork exhaustion)
- **Maximum achievable: 4 nodes × 32 ranks = 128 total**

```bash
#!/bin/bash
#SBATCH -N 4 --ntasks-per-node=32 -n 128 -t 120
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

**Key differences from single-node**:
- `srun --mpi=pmix` replaces container `mpirun` — SLURM manages cross-node process placement
- No `--bind /usr/bin/ssh` needed — srun handles remote launch
- No `--oversubscribe` needed — SLURM allocates exact slots
- No `--cleanenv` — PMIx environment variables must pass through; use explicit `--env` overrides instead
- `OPAL_PREFIX=/opt/openmpi` prevents host HPC-X OpenMPI from hijacking container OpenMPI config

### gfortran SIF Pitfalls

#### GP1: Cross-Node with Container mpirun
**Symptom**: `plm_rsh_agent: ssh : rsh — not found` or only launches on first node.
**Cause**: Container-internal mpirun tries ssh to remote nodes but can't wrap in apptainer on remote side.
**Fix**: Use `srun --mpi=pmix` for cross-node. Container mpirun only works for single-node.

#### GP2: MCNP6 Exit Code 2 (False SLURM FAILED)
**Symptom**: SLURM reports job as FAILED, but `outp` contains "run terminated when N particle histories were done."
**Cause**: MCNP6 MPI master rank exits with code 2 (normal termination signal), which mpirun/srun reports as non-zero.
**Fix**: Ignore SLURM exit status for MCNP6; check `outp` for "run terminated when" + "mcrun is done" as success markers.

#### GP3: Multiple outp Files
**Symptom**: `outp`, `outq`, `outr`, ... files generated.
**Cause**: Previous run files exist in the working directory. MCNP6 auto-increments output filenames.
**Fix**: Always use a clean working directory (`mktemp -d`), or clean up before runs (`rm -f outp* runtpe* mctal*`).

#### GP4: Host OPAL_PREFIX Interference
**Symptom**: `WARNING: Environment variable OPAL_PREFIX already has value [/opt/hpc/software/mpi/hpcx/...]`
**Cause**: Host HPC-X OpenMPI sets OPAL_PREFIX which leaks into container when not using `--cleanenv`.
**Fix**: Explicitly set `--env OPAL_PREFIX=/opt/openmpi` to override with container path.

#### GP5: High Rank Density Fork Exhaustion (≥64 ranks/node)
**Symptom**: `FATAL: root filesystem extraction failed: fork/exec .../apptainer: resource temporarily unavailable`
**Cause**: Cluster lacks squashfuse, so each srun task triggers a full SIF→sandbox extraction. 64+ simultaneous extractions exhaust per-user nproc limits.
**Fix**: Limit to ≤32 ranks per node. Sandbox conversion doesn't help (cluster lacks overlay support too). Pre-warm step helps slightly but is insufficient for 64+.

### Validation Results (2026-05-05/06, Sugon HB, Hygon C86 7285)

| Test | Ranks | Nodes | Result |
|------|-------|-------|--------|
| Serial | 1 | 1 | ✅ PASS |
| MPI-32 | 32 | 1 | ✅ PASS |
| All 6 variants | 2 each | 1 | ✅ ALL PASS |
| Cross-node | 64 | 2 | ✅ PASS (srun --mpi=pmix) |
| Cross-node max | 128 | 4 | ✅ PASS (4×32, 213 M hist/hr) |
| ~~Cross-node 256~~ | ~~256~~ | ~~4~~ | ❌ FAIL (64/node fork limit) |

## mcnp-lint MCP Server — 输入文件验证工具

`mcnp-lint` MCP server 提供 MCNP6 输入文件的确定性静态检查。已注册在 OpenCode MCP servers 中。

### 可用工具

| Tool | Purpose |
|------|---------|
| `full_scan` | 运行所有检查（推荐首选） |
| `deck_structure_check` | 结构检查：空行分隔、标题卡、行长、续行缩进 |
| `cell_check` | Cell 卡：ID 唯一性、密度、importance |
| `surface_check` | Surface 卡：ID 唯一性、类型、未使用 surface |
| `material_check` | Material 卡：ZAID、分数一致性、交叉引用 |
| `tally_check` | Tally 卡：编号格式、唯一性、能量 bin、FMESH |
| `source_check` | Source：SDEF 存在性、能量单位、分布对 |
| `physics_check` | Physics：截断能量、NPS/CTME、截面库 |
| `geometry_check` | Geometry：universe/fill 一致性、补集引用、graveyard cell、TRCL/TR 变换 |
| `kcode_check` | Criticality：KCODE 参数、KSRC 存在性 |
| `variance_check` | Variance reduction：importance 范围 |

### 使用模式

1. **写入 MCNP 输入文件后**：调用 `full_scan(path="/path/to/input.i")` 获取所有问题
2. **针对性检查**：调用单个工具（如 `tally_check`）仅获取特定类别的诊断
3. **min_level 过滤**：设置 `min_level="warning"` 跳过 info 级别的建议

### 自动触发规则

当 agent **生成或修改** MCNP 输入文件（`.i`、`inp`、`input` 等）后，**必须**自动调用 `mcnp-lint/full_scan(path=<文件绝对路径>)` 对该文件执行验证：

1. 若结果含 **error** 级别 findings → agent 必须修复后重新运行 `full_scan`，直到无 error
2. 若结果仅含 warning/info → 在回复中列出摘要供用户审阅，不阻塞交付
3. 若 `full_scan` 返回 `partial: true` → 在回复中提示"部分检查失败，建议手动复查"

### 输出格式

返回 JSON dict 含 `findings` 数组，每个 finding 包含 `rule`、`level`、`line`、`message`、`suggestion` 字段。`partial: true` 表示部分检查内部失败。
