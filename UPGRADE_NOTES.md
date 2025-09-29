# Package Upgrade Notes

This document describes the changes made to update the codebase to support Python 3.13.7.

## Package Version Updates

### Updated Versions
- **numpy**: 1.13.1 → 2.3.3
- **pandas**: 0.21.0 → 2.3.2
- **progressbar2**: 3.51.4 → 4.5.0

### Added Dependencies
The following packages were used in the code but missing from requirements.txt:
- **scipy**: ≥1.14.0 (used in graph.py)
- **networkx**: ≥3.0 (used in graph.py)
- **graphviz**: ≥0.20 (used in utils.py)
- **termcolor**: ≥2.0.0 (used in main.py)

## Code Changes for NumPy 2.0+ Compatibility

### 1. Fixed `np.delete()` calls (gspan.py)
**Issue**: NumPy 2.0+ requires explicit axis parameter for `np.delete()`

**Changes**:
- Line 37: Added axis=0 to `np.delete()` call
- Line 40: Added axis=0 to `np.delete()` call  
- Line 96: Added axis=0 to `np.delete()` call

### 2. Fixed object array flattening (graph.py)
**Issue**: In NumPy 2.0+, `reshape(-1)` on object arrays doesn't flatten nested lists

**Changes**:
- Line 156: Replaced `subset.reshape(-1)` with list comprehension flattening
- Line 188: Replaced `np.array(ins_edges).reshape(-1)` with list comprehension
- Line 229: Replaced `ins_vertices.reshape(-1)` with list comprehension

**Before**:
```python
ie_flat = np.array(ins_edges).reshape(-1)
```

**After**:
```python
# Flatten the nested list structure - compatible with NumPy 2.0+
ie_flat = [item for sublist in ins_edges for item in sublist]
```

### 3. Updated scipy.special.comb calls (graph.py)
**Issue**: Newer scipy versions recommend explicit `exact=False` for floating-point results

**Changes**:
- Line 237: Added `exact=False` parameter to `comb()` call
- Line 256: Added `exact=False` parameter to `comb()` call

**Before**:
```python
s += log2(comb(v_num, sn))
```

**After**:
```python
s += log2(comb(v_num, sn, exact=False))
```

### 4. Updated networkx imports and function calls (graph.py)
**Issue**: In networkx 3.x, `independent_set` module was renamed to `maximum_independent_set`

**Changes**:
- Line 12: Updated import from `independent_set` to `maximum_independent_set`
- Line 76: Updated function call from `independent_set.maximum_independent_set()` to `maximum_independent_set()`

**Before**:
```python
from networkx.algorithms.approximation import independent_set
...
mis = independent_set.maximum_independent_set(NG)
```

**After**:
```python
from networkx.algorithms.approximation import maximum_independent_set
...
mis = maximum_independent_set(NG)
```

## Verification

Run the compatibility test:
```bash
python test_compatibility.py
```

To install all dependencies:
```bash
pip install -r requirements.txt
```

## Breaking Changes Summary

The main breaking changes from NumPy 2.0+ that affected this codebase:
1. Stricter requirements for axis parameters in array operations
2. Changed behavior for operations on object arrays (ragged arrays)
3. Object array reshaping no longer flattens nested structures

### 5. Fixed pickle file structure handling (utils.py)
**Issue**: Different pickle files have different data structures - some contain tuples with (graph, value), others contain graphs directly

**Changes**:
- Lines 32-38: Added conditional logic to handle both tuple and direct graph structures

**Before**:
```python
# g is the networkx graph itself
networkx_graph = g
```

**After**:
```python
# Handle different pickle file structures
if isinstance(g, tuple):
    # Some pickle files contain tuples with (graph, value)
    networkx_graph = g[0]
else:
    # Other pickle files contain the graph directly
    networkx_graph = g
```

### 6. Fixed edge weight data type conversion (utils.py)
**Issue**: Edge weights were being converted to integers, causing decimal weights (0.6, 0.7) to become 0, leading to math domain errors in log2(0)

**Changes**:
- Line 45: Removed `int()` conversion for edge weights to preserve decimal values

**Before**:
```python
tgraph.add_edge(AUTO_EDGE_ID, int(e[0]), int(e[1]), 1, int(networkx_graph.edges[e]['weight']))
```

**After**:
```python
tgraph.add_edge(AUTO_EDGE_ID, int(e[0]), int(e[1]), 1, networkx_graph.edges[e]['weight'])
```

### 7. Fixed indentation bug in eliminate_incorrect_pattern (gspan.py)
**Issue**: `UnboundLocalError` when checking `ufs.instances` - the check was incorrectly outside the for loop

**Changes**:
- Lines 38-39: Moved the min_support check inside the for loop

**Before**:
```python
for idx1, ufs in enumerate(progressbar.progressbar(undir_freq_subs)):
    # ... process instances ...
    ufs.instances = list(np.delete(np.array(ufs.instances), del_ins, 0))
if len(ufs.instances) < min_support:  # Wrong: outside loop
    del_idx.append(idx1)
```

**After**:
```python
for idx1, ufs in enumerate(progressbar.progressbar(undir_freq_subs)):
    # ... process instances ...
    ufs.instances = list(np.delete(np.array(ufs.instances), del_ins, 0))
    if len(ufs.instances) < min_support:  # Correct: inside loop
        del_idx.append(idx1)
```

### 8. Fixed division by zero in anomaly score calculation (main.py)
**Issue**: `ZeroDivisionError` when calculating anomaly scores for graphs with zero MDL

**Changes**:
- Lines 124-127: Added check to prevent division by zero

**Before**:
```python
if idx in max_arr:
    g_old_mdl, g_new_mdl = max_mdl[idx]
    a_score[idx].append((g_old_mdl - g_new_mdl) / graph_ori_mdl[idx])
```

**After**:
```python
if idx in max_arr:
    g_old_mdl, g_new_mdl = max_mdl[idx]
    # Avoid division by zero for graphs with zero MDL
    if graph_ori_mdl[idx] > 0:
        a_score[idx].append((g_old_mdl - g_new_mdl) / graph_ori_mdl[idx])
    else:
        a_score[idx].append(0)
```

### 9. Fixed array index dtype in np.delete calls (gspan.py)
**Issue**: `IndexError: arrays used as indices must be of integer (or boolean) type` - NumPy 2.0+ requires explicit integer dtype for index arrays

**Changes**:
- Lines 37, 40, 96: Added `dtype=int` to ensure index arrays are integers

**Before**:
```python
ufs.instances = list(np.delete(np.array(ufs.instances), del_ins, 0))
return np.delete(undir_freq_subs, del_idx, 0)
tmp.instances = np.delete(np.array(tmp.instances), np.array(del_idx), 0)
```

**After**:
```python
ufs.instances = list(np.delete(np.array(ufs.instances), np.array(del_ins, dtype=int), 0))
return np.delete(undir_freq_subs, np.array(del_idx, dtype=int), 0)
tmp.instances = np.delete(np.array(tmp.instances), np.array(del_idx, dtype=int), 0)
```

## Compatibility Notes

- All changes are backward compatible with NumPy 1.x if needed
- The code now properly handles ragged arrays (arrays of lists with different lengths)
- scipy.special.comb now explicitly uses floating-point arithmetic for better precision with large numbers
- The code now handles different pickle file formats automatically
- Edge weights are now preserved as decimal values instead of being truncated to integers
- Fixed variable scope issues in pattern elimination
- Added safety checks for edge cases (zero MDL graphs)
- Index arrays for np.delete now explicitly use integer dtype for NumPy 2.0+ compatibility
