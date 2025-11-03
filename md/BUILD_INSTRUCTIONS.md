# Building Pharmacy Sales Analytics as Windows Executable

This guide explains how to bundle the Pharmacy Sales Analytics application into a standalone Windows executable (.exe) that can run without requiring Python or any dependencies to be installed.

## 📋 Prerequisites

### On the Build Machine (Where you create the .exe)

- **Windows 10/11** (64-bit recommended)
- **Python 3.8 or higher** installed
  - Download from: https://www.python.org/downloads/
  - ⚠️ **Important**: Check "Add Python to PATH" during installation
- **At least 2GB free disk space** for the build process

## 🛠️ Building the Executable

### Method 1: Automated Build (Recommended)

1. **Open Command Prompt** in the project directory
   ```cmd
   cd C:\path\to\pharmacy_sales
   ```

2. **Run the build script**
   ```cmd
   build_exe.bat
   ```

3. **Wait for the build to complete** (5-15 minutes depending on your PC)

4. **Find your executable** in:
   ```
   dist\PharmacySalesAnalytics\
   ```

### Method 2: Manual Build

If the automated script doesn't work, follow these steps:

1. **Create a virtual environment**
   ```cmd
   python -m venv build_venv
   ```

2. **Activate the virtual environment**
   ```cmd
   build_venv\Scripts\activate.bat
   ```

3. **Install build dependencies**
   ```cmd
   pip install -r build_requirements.txt
   ```

4. **Run PyInstaller**
   ```cmd
   pyinstaller pharmacy_app.spec --clean
   ```

5. **Check the output** in `dist\PharmacySalesAnalytics\`

## 📦 Distributing the Application

### What Gets Created

After building, you'll have a folder:
```
dist\PharmacySalesAnalytics\
├── PharmacySalesAnalytics.exe    (Main executable)
├── _internal\                     (Required libraries)
├── dashboard.py
├── config.py
├── (all other Python modules)
└── data\                          (Sample data if included)
```

### How to Distribute

**Option 1: Compress the Folder**
1. Right-click the `PharmacySalesAnalytics` folder
2. Select "Send to" → "Compressed (zipped) folder"
3. Share the `.zip` file

**Option 2: Create an Installer (Advanced)**
- Use tools like Inno Setup or NSIS to create a proper installer
- This provides a more professional installation experience

## 🚀 Running the Application

### For End Users (No Installation Required!)

1. **Extract/Copy** the `PharmacySalesAnalytics` folder to any location
2. **Double-click** `PharmacySalesAnalytics.exe`
3. **Wait** for the console window to show "Starting server..."
4. **Browser opens automatically** with the dashboard
5. **To close**: Close the console window or press Ctrl+C

### First Run Notes

- Windows Defender might ask for permission - click "Allow"
- The first run might take 10-20 seconds to start
- Subsequent runs will be faster

## 📁 Data Files

### Including Sample Data

The build script includes any existing data files:
- `pharmacy_sales.xlsx`
- `inventory.xlsx`
- `total_sales.xlsx`

### User Data Directory

The application creates these folders:
```
PharmacySalesAnalytics\
├── data\           (Input data)
├── output\
    ├── charts\     (Generated charts)
    ├── reports\    (Exported reports)
    └── inventory\  (Inventory analysis)
```

Users can upload their own data files through the dashboard interface.

## 🔧 Customization

### Change the Application Icon

1. Create or find a `.ico` file (256x256 recommended)
2. Edit `pharmacy_app.spec`, find the line:
   ```python
   icon=None,
   ```
3. Change it to:
   ```python
   icon='path/to/your/icon.ico',
   ```
4. Rebuild

### Hide Console Window

To hide the console window (for a cleaner look):

1. Edit `pharmacy_app.spec`, find:
   ```python
   console=True,
   ```
2. Change to:
   ```python
   console=False,
   ```
3. Rebuild

⚠️ **Note**: Hiding the console makes troubleshooting harder if issues occur.

### Include API Keys

To pre-configure OpenAI API key:

1. Create a `.env` file with:
   ```
   OPENAI_API_KEY=your_key_here
   ```
2. The build script will include it automatically
3. Users won't need to configure it

## ❓ Troubleshooting

### Build Fails with "Module not found"

**Solution**: Add the missing module to `hiddenimports` in `pharmacy_app.spec`

### Executable is Very Large (>500MB)

**Normal**: Due to Pandas, NumPy, Scikit-learn, and Streamlit
- Expected size: 300-600 MB
- Use compression to reduce distribution size

### "Failed to execute script" Error

**Causes**:
1. Missing dependencies in spec file
2. Antivirus blocking
3. Corrupted build

**Solution**:
```cmd
pyinstaller pharmacy_app.spec --clean --debug all
```
Check the generated warnings.

### Streamlit Not Starting

**Check**:
1. Console window shows errors?
2. Port already in use?
3. Missing Streamlit files?

**Solution**: Run with `console=True` to see error messages

### Application Crashes on Startup

**Debug Mode**:
1. Edit `pharmacy_app.spec`: `debug=True`
2. Rebuild
3. Run from command prompt to see errors:
   ```cmd
   PharmacySalesAnalytics.exe
   ```

## 🔒 Security Notes

### Antivirus False Positives

PyInstaller executables sometimes trigger antivirus warnings:

**For Distribution**:
1. Sign the executable (requires code signing certificate)
2. Upload to VirusTotal and share the report
3. Build on a clean Windows VM

**For Users**:
- Add exception in Windows Defender
- Right-click exe → Properties → Unblock

### Data Privacy

- All data stays local (no cloud uploads)
- OpenAI API key (if used) is for AI features only
- Users control what data they load

## 📊 Performance Notes

### Startup Time

- First run: 10-20 seconds
- Subsequent runs: 5-10 seconds
- Loading large datasets: Additional time

### Memory Usage

- Base: ~200-300 MB
- With large dataset: Up to 1-2 GB
- Recommend minimum 4GB RAM for end users

## 🆕 Updating the Application

### For Developers

1. Make code changes
2. Test locally
3. Run `build_exe.bat` again
4. Distribute new version

### Version Management

Add version info in `launcher.py`:
```python
VERSION = "1.0.0"
print(f"Pharmacy Sales Analytics v{VERSION}")
```

## 📝 Deployment Checklist

Before distributing:

- [ ] Test the exe on a clean Windows machine (no Python installed)
- [ ] Verify all features work (AI query, reports, exports)
- [ ] Check that sample data loads correctly
- [ ] Test with real pharmacy data
- [ ] Verify charts and exports work
- [ ] Create a simple user guide
- [ ] Test on Windows 10 and Windows 11
- [ ] Check file size is reasonable (<600MB)
- [ ] Scan with antivirus (ensure no false positives)
- [ ] Create a README for end users

## 🎯 Quick Reference

### Build Command
```cmd
build_exe.bat
```

### Output Location
```
dist\PharmacySalesAnalytics\PharmacySalesAnalytics.exe
```

### Rebuild from Scratch
```cmd
rmdir /s /q build dist
pyinstaller pharmacy_app.spec --clean
```

## 🤝 Support

If you encounter issues:

1. Check the console output (keep `console=True`)
2. Review PyInstaller warnings
3. Verify all dependencies are in `build_requirements.txt`
4. Test on a different Windows machine
5. Check antivirus isn't blocking files

## 📄 License Note

Ensure you comply with all package licenses when distributing:
- Streamlit (Apache 2.0)
- Pandas (BSD 3-Clause)
- NumPy (BSD 3-Clause)
- Plotly (MIT)
- Scikit-learn (BSD 3-Clause)

Include licenses in your distribution if required.

---

**Success!** 🎉 You should now have a fully functional Windows executable that anyone can run without installing Python or dependencies!



