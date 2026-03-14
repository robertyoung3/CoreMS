import os
import pytest

from corems.mass_spectrum.input.numpyArray import ms_from_array_centroid
from corems.molecular_id.search.molecularFormulaSearch import SearchMolecularFormulas
from corems.mass_spectrum.output.export import HighResMassSpecExport
from corems.mass_spectrum.input.coremsHDF5 import ReadCoreMSHDF_MassSpectrum


@pytest.fixture
def mass_spectrum_silico(postgres_database):
    # Test for generating accurate molecular formula from a single mass using the local sql database
    # Now also tests that it is handling isotopes correctly (for non-adducts)
    mz = [760.58156938877, 761.58548]
    abundance = [1000, 400]
    rp, s2n = [[1, 1], [10, 10]]

    mass_spectrum_obj = ms_from_array_centroid(
        mz, abundance, rp, s2n, "single mf search", polarity=1, auto_process=False
    )

    # Set the settings for the molecular search on the mass spectrum object
    mass_spectrum_obj.settings.noise_threshold_method = "relative_abundance"
    mass_spectrum_obj.settings.noise_threshold_absolute_abundance = 0

    mass_spectrum_obj.molecular_search_settings.url_database = postgres_database
    mass_spectrum_obj.molecular_search_settings.error_method = "None"
    mass_spectrum_obj.molecular_search_settings.min_ppm_error = -5
    mass_spectrum_obj.molecular_search_settings.max_ppm_error = 5
    mass_spectrum_obj.molecular_search_settings.mz_error_range = 1
    mass_spectrum_obj.molecular_search_settings.isProtonated = True
    mass_spectrum_obj.molecular_search_settings.isRadical = False
    mass_spectrum_obj.molecular_search_settings.isAdduct = False
    mass_spectrum_obj.molecular_search_settings.use_min_peaks_filter = False
    mass_spectrum_obj.molecular_search_settings.use_isotopologue_filter = False

    usedatoms = {"C": (1, 57), "H": (4, 200), "N": (0, 1)}
    mass_spectrum_obj.molecular_search_settings.usedAtoms = usedatoms

    mass_spectrum_obj.process_mass_spec()

    return mass_spectrum_obj


def test_molecular_formula_search(mass_spectrum_silico):
    SearchMolecularFormulas(
        mass_spectrum_silico, find_isotopologues=True
    ).run_worker_ms_peaks([mass_spectrum_silico[0]])

    ms_df1 = mass_spectrum_silico.to_dataframe()
    assert mass_spectrum_silico[0][0].string == "C56 H73 N1"
    assert ms_df1.shape == (2, 26)
    assert mass_spectrum_silico[1][0].string == "C55 H73 N1 13C1"


def test_kmd_columns_in_dataframe(mass_spectrum_silico):
    """Test KMD and Formula KMD additional columns with configurable n_digits."""
    SearchMolecularFormulas(
        mass_spectrum_silico, find_isotopologues=True
    ).run_worker_ms_peaks([mass_spectrum_silico[0]])

    # Set custom n_digits parameters
    mass_spectrum_silico.mspeaks_settings.kmd_n_digits = 3
    mass_spectrum_silico.mspeaks_settings.formula_kmd_n_digits = 4

    df = mass_spectrum_silico.to_dataframe(additional_columns=["KMD", "Formula KMD"])

    # Both columns should be present
    assert "KMD" in df.columns
    assert "Formula KMD" in df.columns

    # KMD should be a float rounded to n decimal places, between -1 and 1
    kmd_values = df["KMD"].dropna()
    assert len(kmd_values) > 0
    for val in kmd_values:
        assert -1 <= val <= 1, f"KMD value {val} is not between -1 and 1"
        scaled = val * 10**3
        assert abs(scaled - round(scaled)) < 1e-9, (
            f"KMD value {val} not rounded to 3 decimal places"
        )

    # Formula KMD should be a float rounded to n decimal places, between -1 and 1
    formula_kmd_values = df["Formula KMD"].dropna()
    assert len(formula_kmd_values) > 0
    for val in formula_kmd_values:
        assert -1 <= val <= 1, f"Formula KMD value {val} is not between -1 and 1"
        scaled = val * 10**4
        assert abs(scaled - round(scaled)) < 1e-9, (
            f"Formula KMD value {val} not rounded to 4 decimal places"
        )

    # Test with different n_digits
    mass_spectrum_silico.mspeaks_settings.kmd_n_digits = 2
    mass_spectrum_silico.mspeaks_settings.formula_kmd_n_digits = 2

    df2 = mass_spectrum_silico.to_dataframe(additional_columns=["KMD", "Formula KMD"])
    kmd_values_2 = df2["KMD"].dropna()
    for val in kmd_values_2:
        scaled = val * 10**2
        assert abs(scaled - round(scaled)) < 1e-9, (
            f"KMD value {val} not rounded to 2 decimal places"
        )
    formula_kmd_values_2 = df2["Formula KMD"].dropna()
    for val in formula_kmd_values_2:
        scaled = val * 10**2
        assert abs(scaled - round(scaled)) < 1e-9, (
            f"Formula KMD value {val} not rounded to 2 decimal places"
        )


def test_mass_spec_export_import_with_annote(mass_spectrum_silico):
    SearchMolecularFormulas(
        mass_spectrum_silico, find_isotopologues=True
    ).run_worker_ms_peaks([mass_spectrum_silico[0]])

    exportMS = HighResMassSpecExport("my_mass_spec", mass_spectrum_silico)
    exportMS._output_type = "hdf5"
    exportMS.save()

    parser = ReadCoreMSHDF_MassSpectrum("my_mass_spec.hdf5")
    mass_spectrum_obj2 = parser.get_mass_spectrum(auto_process=True, load_settings=True)

    ms_df2 = mass_spectrum_obj2.to_dataframe()
    assert mass_spectrum_obj2[0][0].string == "C56 H73 N1"
    assert ms_df2.shape == (2, 26)
    assert mass_spectrum_obj2[1][0].string == "C55 H73 N1 13C1"
    assert mass_spectrum_obj2._mz_exp[0] == 760.58156938877

    # Remove the file
    os.remove("my_mass_spec.hdf5")