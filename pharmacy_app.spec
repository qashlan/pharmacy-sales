# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Pharmacy Sales Analytics
This file defines how to bundle the application into a Windows executable.
"""

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Define the base directory
BASE_DIR = Path('.').absolute()

# Collect all necessary data files
datas = []

# Add Streamlit data files
datas += collect_data_files('streamlit')
datas += collect_data_files('streamlit_extras')
datas += collect_data_files('plotly')
datas += collect_data_files('altair')

# Add application Python modules
app_modules = [
    'dashboard.py',
    'data_loader.py',
    'sales_analysis.py',
    'customer_analysis.py',
    'product_analysis.py',
    'inventory_management.py',
    'rfm_analysis.py',
    'refill_prediction.py',
    'cross_sell_analysis.py',
    'ai_query.py',
    'openai_integration.py',
    'config.py',
    'utils.py',
]

for module in app_modules:
    if (BASE_DIR / module).exists():
        datas.append((str(module), '.'))

# Add data directories
data_dirs = ['data', 'output', 'output/charts', 'output/reports', 'output/inventory']
for data_dir in data_dirs:
    dir_path = BASE_DIR / data_dir
    if dir_path.exists():
        datas.append((str(data_dir), data_dir))

# Add sample data files if they exist
data_files = ['pharmacy_sales.xlsx', 'inventory.xlsx', 'total_sales.xlsx']
for data_file in data_files:
    file_path = BASE_DIR / data_file
    if file_path.exists():
        datas.append((str(data_file), '.'))

# Add .env file if it exists
env_file = BASE_DIR / '.env'
if env_file.exists():
    datas.append(('.env', '.'))

# Collect all submodules for key packages
hiddenimports = []
hiddenimports += collect_submodules('streamlit')
hiddenimports += collect_submodules('plotly')
hiddenimports += collect_submodules('pandas')
hiddenimports += collect_submodules('numpy')
hiddenimports += collect_submodules('scipy')
hiddenimports += collect_submodules('sklearn')
hiddenimports += collect_submodules('mlxtend')
hiddenimports += collect_submodules('openpyxl')
hiddenimports += collect_submodules('openai')

# Add specific hidden imports that PyInstaller might miss
hiddenimports += [
    'sklearn.utils._cython_blas',
    'sklearn.neighbors._typedefs',
    'sklearn.neighbors._partition_nodes',
    'sklearn.tree._utils',
    'scipy.special._ufuncs_cxx',
    'scipy.linalg.cython_blas',
    'scipy.linalg.cython_lapack',
    'scipy.integrate._odepack',
    'scipy.integrate._quadpack',
    'scipy.integrate._vode',
    'scipy.integrate._dop',
    'scipy.integrate._lsoda',
    'scipy.special._ufuncs',
    'scipy.special.cython_special',
    'streamlit.runtime.scriptrunner.magic_funcs',
    'streamlit.web.bootstrap',
    'altair',
    'pyarrow',
    'pytz',
    'tzdata',
]

a = Analysis(
    ['launcher.py'],
    pathex=[str(BASE_DIR)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'tkinter', 'test', 'unittest'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PharmacySalesAnalytics',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Show console window for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # You can add an .ico file here if you have one
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PharmacySalesAnalytics',
)



