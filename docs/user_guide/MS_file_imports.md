# Mass Spectrum File Imports in CoreMS

This guide explains how to import mass spectrum data files in CoreMS, focusing on settings that control the import process and subsequent data processing.

## Basic File Import

```python
from pathlib import Path
from corems.mass_spectrum.input.massList import ReadMassList
from corems.encapsulation.factory.parameters import MSParameters

# Configure import settings
MSParameters.mass_spectrum.noise_threshold_method = "minima"
MSParameters.mass_spectrum.noise_threshold_min_std = 0

# Import mass list
file_location = Path("/path/to/your/file.pks")
mass_list_reader = ReadMassList(file_location)
mass_spectrum = mass_list_reader.get_mass_spectrum(polarity=-1, auto_process=True, loadSettings=False)
```

## File Types Supported

CoreMS supports several file formats for mass spectrometry data:

| Extension | Description | Import Method |
|-----------|-------------|--------------|
| `.pks` | Peak list format | Custom reader, skips first 8 lines, ignores last line |
| `.csv` | Comma-separated values | Uses pandas.read_csv |
| `.txt`, `.tsv` | Tab-separated values | Uses pandas.read_csv with tab delimiter |
| `.xlsx` | Excel file | Uses pandas.read_excel |
| `.xml` | Bruker XML format | Custom XML parser |
| `.xy` | Space-separated values | Uses pandas.read_csv with space delimiter |

## ReadMassList Constructor Parameters

The `ReadMassList` class accepts several parameters that control how files are imported:

* `file_location` (Path or S3Path): Path to the file
* `isCentroid` (bool): If True, assumes centroid mode; if False, assumes profile mode (default: True)
* `analyzer` (str): Analyzer used for the mass spectrum (default: "Unknown") 
* `instrument_label` (str): Instrument label (default: "Unknown")
* `sample_name` (str): Sample name (default: None)
* `header_lines` (int): Number of lines to skip at beginning of file (default: 0)
* `isThermoProfile` (bool): If True, only expects m/z and intensity columns (default: False)
* `headerless` (bool): If True, assumes no column headers, uses ["m/z", "I"] (default: False)

## MassSpectrumSetting Configuration

The `MSParameters.mass_spectrum` object controls how mass spectra are processed after import.  `MSParameters` incorporates settings for the mass spectum (`MassSpectrumSetting`), molecular formula searches (`MolecularFormulaSearchSettings`), and more. The mass spectrum is made of MassSpecCentroid objects, which contains a `process_mass_spec()` method triggered when `auto_process=True`.

### Noise Threshold Methods

```python
# Choose a noise threshold method
    """MassSpectrumSetting
    Mass spectrum processing settings class

    Selected Attributes
    ----------
    noise_threshold_method : str, optional
        Method for detecting noise threshold. Default is 'log'.
    noise_threshold_min_std : int, optional
        Minumum value for noise thresholding when using 'minima' noise threshold method. Default is 6.
    noise_threshold_min_s2n : float, optional
        Minimum value for noise thresholding when using 'signal_noise' noise threshold method. Default is 4.
    noise_threshold_min_relative_abundance : float, optional
        Minimum value for noise thresholding when using 'relative_abundance' noise threshold method. Note that this is a percentage value. Default is 6 (6%).
    noise_threshold_absolute_abundance : float, optional
        Minimum value for noise thresholding when using 'absolute_abundance' noise threshold method. Default is 1_000_000.
    noise_threshold_log_nsigma : int, optional
        Number of standard deviations to use when using 'log' noise threshold method. Default is 6.
    """
MSParameters.mass_spectrum.noise_threshold_method = "minima"  # Options: "minima", "signal_noise", "relative_abundance", "absolute_abundance", "log"
```

### Noise Thresholding Parameters

```python
# For "minima" method (use 0 to keep all peaks)
MSParameters.mass_spectrum.noise_threshold_min_std = 0

# For "signal_noise" method
MSParameters.mass_spectrum.noise_threshold_min_s2n = 4.0

# For "relative_abundance" method (percentage of max intensity)
MSParameters.mass_spectrum.noise_threshold_min_relative_abundance = 6.0

# For "absolute_abundance" method (absolute intensity value)
MSParameters.mass_spectrum.noise_threshold_absolute_abundance = 1000000

# For "log" method
MSParameters.mass_spectrum.noise_threshold_log_nsigma = 6
```

### m/z Range for Processing

```python
# Set m/z range for noise calculation and peak picking
MSParameters.mass_spectrum.noise_min_mz = 50.0
MSParameters.mass_spectrum.noise_max_mz = 1200.0
MSParameters.mass_spectrum.min_picking_mz = 50.0
MSParameters.mass_spectrum.max_picking_mz = 1200.0
```

## DataInputSetting Configuration

The `MSParameters.data_input` object controls how data is read from input files.

`.pks` files are processed using their known formats.  `.txt` files (including `.csv` files) are expected to have "m/z", "Peak Height", "Resolving Power", and "S/N" columns unless `isThermoProfile = True`.  In that case, they are expected to have "m/z" and "Peak Height" columns. 

### Header Translation

The `header_translate` dictionary maps additional column names in your input file to the standard column names used by CoreMS:

```python
# Add custom mappings for column names
MSParameters.data_input.add_mz_label("My_MZ_Column")
MSParameters.data_input.add_peak_height_label("My_Intensity_Column") 
MSParameters.data_input.add_sn_label("My_SN_Column")
MSParameters.data_input.add_resolving_power_label("My_RP_Column")
```

## Auto-Processing

When importing with `auto_process=True` (default), several steps automatically happen:

1. **Noise Threshold Calculation**: The baseline noise level is calculated based on the selected method
2. **Peak Filtering**: Peaks below the calculated noise threshold are removed
3. **Mass Range Filtering**: Peaks outside the specified mass range are filtered out
4. **Calibration** (if enabled): Mass calibration may be applied

Set `auto_process=False` to skip these steps and process data manually.

## Common Import Scenarios

### For PKS Files
```python
# PKS files are automatically handled correctly
mass_list_reader = ReadMassList(file_location)
mass_spectrum = mass_list_reader.get_mass_spectrum(polarity=-1, loadSettings=False)
```

### For CSV Files with Headers
```python
# For CSV files with headers
mass_list_reader = ReadMassList(file_location, header_lines=1)
mass_spectrum = mass_list_reader.get_mass_spectrum(polarity=-1, loadSettings=False)
```

### For CSV Files without Headers (just data)
```python
# For headerless CSV files with m/z and intensity values
mass_list_reader = ReadMassList(
    file_location,
    headerless=True,       # No headers in file
    isThermoProfile=True   # Only expect m/z and intensity columns
)
mass_spectrum = mass_list_reader.get_mass_spectrum(polarity=-1, loadSettings=False)
```

## Common Issues and Solutions

1. **Missing Columns Warning**: "Please make sure to include the columns S/N, Resolving Power"
   - Use `isThermoProfile=True` if your file only has m/z and intensity columns
   - Add header translations for your column names with `MSParameters.data_input.add_*_label()`

2. **Settings File Warning**: "Auto settings loading is enabled but could not locate the file..."
   - Use `loadSettings=False` when calling `get_mass_spectrum()` to disable this feature
   - Or create a JSON settings file with the same name as your data file

3. **PKS Files in CSV Format**:
   - Use the `prepare_pks_from_csv()` function above to convert them back to PKS format
