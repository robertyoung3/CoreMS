__author__ = "Yuri E. Corilo"
__date__ = "Nov 11, 2019"

import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Thread

import h5py
import toml
from numpy import NaN, empty
from pandas import DataFrame

from corems.encapsulation.constant import Atoms, Labels #Labels is accessed in the eval() function
from corems.encapsulation.output import parameter_to_dict
from corems.mass_spectrum.factory.MassSpectrumClasses import MassSpecfromFreq


class HighResMassSpecExport(Thread):
    """A class for exporting high-resolution mass spectra.

    Parameters
    ----------
    out_file_path : str
        The output file path.
    mass_spectrum : MassSpectrum
        The mass spectrum to export.
    output_type : str, optional
        The type of output file. Defaults to 'excel'. Can be 'excel', 'csv', 'pandas' or 'hdf5'.

    Attributes
    ----------
    output_file : Path
        The output file path.
    output_type : str
        The type of output file.
    mass_spectrum : MassSpectrum
        The mass spectrum to export.
    atoms_order_list : list
        The list of assigned atoms in the order specified by Atoms.atoms_order list.
    columns_label : list
        The column labels in order.

    Methods
    -------
    * save().
        Save the mass spectrum data to the output file.
    * run().
        Run the export process.
    * get_pandas_df().
        Returns the mass spectrum data as a pandas DataFrame.
    * write_settings(output_path, mass_spectrum).
        Writes the settings of the mass spectrum to a JSON file.
    * to_pandas(write_metadata=True).
        Exports the mass spectrum data to a pandas DataFrame and saves it as a pickle file.
    * to_excel(write_metadata=True).
        Exports the mass spectrum data to an Excel file.
    * to_csv(write_metadata=True).
        Exports the mass spectrum data to a CSV file.
    * to_json().
        Exports the mass spectrum data to a JSON string.
    * to_hdf().
        Exports the mass spectrum data to an HDF5 file.
    * parameters_to_toml().
        Converts the mass spectrum parameters to a TOML string.
    * parameters_to_json().
        Converts the mass spectrum parameters to a JSON string.
    * get_mass_spec_attrs(mass_spectrum).
        Returns the mass spectrum attributes as a dictionary.
    * get_all_used_atoms_in_order(mass_spectrum).
        Returns the list of assigned atoms in the order specified by Atoms.atoms_order list.
    * list_dict_to_list(mass_spectrum, is_hdf5=False).
        Returns the mass spectrum data as a list of dictionaries.
    * get_list_dict_data(mass_spectrum, include_no_match=True, include_isotopologues=True, isotopologue_inline=True, no_match_inline=False, is_hdf5=False).
        Returns the mass spectrum data as a list of dictionaries.

    """

    def __init__(self, out_file_path, mass_spectrum, output_type="excel"):
        Thread.__init__(self)

        self.output_file = Path(out_file_path)

        # 'excel', 'csv' or 'pandas'
        self.output_type = output_type

        self.mass_spectrum = mass_spectrum

        # collect all assigned atoms and order them accordingly to the Atoms.atoms_order list
        self.atoms_order_list = self.get_all_used_atoms_in_order(self.mass_spectrum)

        self._init_columns()

    def _init_columns(self):
        """Initialize the columns for the mass spectrum output."""
        # column labels in order
        self.columns_label = [
            "Index",
            "m/z",
            "Calibrated m/z",
            "Calculated m/z",
            "Peak Height",
            "Peak Area",
            "Resolving Power",
            "S/N",
            "Ion Charge",
            "m/z Error (ppm)",
            "m/z Error Score",
            "Isotopologue Similarity",
            "Confidence Score",
            "DBE",
            "O/C",
            "H/C",
            "Heteroatom Class",
            "Ion Type",
            "Adduct",
            "Is Isotopologue",
            "Mono Isotopic Index",
            "Molecular Formula",
        ]

    @property
    def output_type(self):
        """Returns the output type of the mass spectrum."""
        return self._output_type

    @output_type.setter
    def output_type(self, output_type):
        output_types = ["excel", "csv", "pandas", "hdf5"]
        if output_type in output_types:
            self._output_type = output_type
        else:
            raise TypeError(
                'Supported types are "excel", "csv" or "pandas", %s entered'
                % output_type
            )

    def save(self):
        """Save the mass spectrum data to the output file.

        Raises
        ------
        ValueError
            If the output type is not supported.
        """

        if self.output_type == "excel":
            self.to_excel()
        elif self.output_type == "csv":
            self.to_csv()
        elif self.output_type == "pandas":
            self.to_pandas()
        elif self.output_type == "hdf5":
            self.to_hdf()
        else:
            raise ValueError(
                "Unkown output type: %s; it can be 'excel', 'csv' or 'pandas'"
                % self.output_type
            )

    def run(self):
        """Run the export process.

        This method is called when the thread starts.
        It calls the save method to perform the export."""
        self.save()

    def get_pandas_df(self, additional_columns=None):
        """Returns the mass spectrum data as a pandas DataFrame.

        Parameters
        ----------
        additional_columns : list, optional
            Additional columns to include in the DataFrame. Defaults to None.
            Suitable additional columns are: 'Aromaticity Index', 'NOSC', 'Aromaticity Index (modified)'.

        Returns
        -------
        DataFrame
            The mass spectrum data as a pandas DataFrame.
        """
        if additional_columns is not None:
            possible_additional_columns = [
                "Aromaticity Index",
                "NOSC",
                "Aromaticity Index (modified)",
            ]
            if additional_columns:
                for column in additional_columns:
                    if column not in possible_additional_columns:
                        raise ValueError("Invalid additional column: %s" % column)
            columns = (
                self.columns_label
                + additional_columns
                + self.get_all_used_atoms_in_order(self.mass_spectrum)
            )
        else:
            columns = self.columns_label + self.get_all_used_atoms_in_order(
                self.mass_spectrum
            )
        dict_data_list = self.get_list_dict_data(
            self.mass_spectrum, additional_columns=additional_columns
        )
        df = DataFrame(dict_data_list, columns=columns)
        df.name = self.output_file
        return df

    def write_settings(self, output_path, mass_spectrum):
        """Writes the settings of the mass spectrum to a JSON file.

        Parameters
        ----------
        output_path : str
            The output file path.
        mass_spectrum : MassSpectrum
            The mass spectrum to export.
        """

        import json

        dict_setting = parameter_to_dict.get_dict_data_ms(mass_spectrum)

        dict_setting["MassSpecAttrs"] = self.get_mass_spec_attrs(mass_spectrum)
        dict_setting["analyzer"] = mass_spectrum.analyzer
        dict_setting["instrument_label"] = mass_spectrum.instrument_label
        dict_setting["sample_name"] = mass_spectrum.sample_name

        with open(
            output_path.with_suffix(".json"),
            "w",
            encoding="utf8",
        ) as outfile:
            output = json.dumps(
                dict_setting, sort_keys=True, indent=4, separators=(",", ": ")
            )
            outfile.write(output)

    def to_pandas(self, write_metadata=True):
        """Exports the mass spectrum data to a pandas DataFrame and saves it as a pickle file.

        Parameters
        ----------
        write_metadata : bool, optional
            Whether to write the metadata to a JSON file. Defaults to True.
        """

        columns = self.columns_label + self.get_all_used_atoms_in_order(
            self.mass_spectrum
        )

        dict_data_list = self.get_list_dict_data(self.mass_spectrum)

        df = DataFrame(dict_data_list, columns=columns)

        df.to_pickle(self.output_file.with_suffix(".pkl"))

        if write_metadata:
            self.write_settings(self.output_file, self.mass_spectrum)

    def to_excel(self, write_metadata=True):
        """Exports the mass spectrum data to an Excel file.

        Parameters
        ----------
        write_metadata : bool, optional
            Whether to write the metadata to a JSON file. Defaults to True.
        """

        columns = self.columns_label + self.get_all_used_atoms_in_order(
            self.mass_spectrum
        )

        dict_data_list = self.get_list_dict_data(self.mass_spectrum)

        df = DataFrame(dict_data_list, columns=columns)

        df.to_excel(self.output_file.with_suffix(".xlsx"))

        if write_metadata:
            self.write_settings(self.output_file, self.mass_spectrum)

    def to_csv(self, write_metadata=True):
        """Exports the mass spectrum data to a CSV file.

        Parameters
        ----------
        write_metadata : bool, optional
            Whether to write the metadata to a JSON file. Defaults to True.
        """

        columns = self.columns_label + self.get_all_used_atoms_in_order(
            self.mass_spectrum
        )

        dict_data_list = self.get_list_dict_data(self.mass_spectrum)

        import csv

        try:
            with open(self.output_file.with_suffix(".csv"), "w", newline="") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=columns)
                writer.writeheader()
                for data in dict_data_list:
                    writer.writerow(data)
            if write_metadata:
                self.write_settings(self.output_file, self.mass_spectrum)

        except IOError as ioerror:
            print(ioerror)

    def to_json(self):
        """Exports the mass spectrum data to a JSON string."""

        columns = self.columns_label + self.get_all_used_atoms_in_order(
            self.mass_spectrum
        )

        dict_data_list = self.get_list_dict_data(self.mass_spectrum)

        df = DataFrame(dict_data_list, columns=columns)

        # for key, values in dict_data.items():
        #    if not values: dict_data[key] = NaN

        # output = json.dumps(dict_data, sort_keys=True, indent=4, separators=(',', ': '))
        return df.to_json(orient="records")

    def add_mass_spectrum_to_hdf5(
        self,
        hdf_handle,
        mass_spectrum,
        group_key,
        mass_spectra_group=None,
        export_raw=True,
    ):
        """Adds the mass spectrum data to an HDF5 file.

        Parameters
        ----------
        hdf_handle : h5py.File
            The HDF5 file handle.
        mass_spectrum : MassSpectrum
            The mass spectrum to add to the HDF5 file.
        group_key : str
            The group key (where to add the mass spectrum data within the HDF5 file).
        mass_spectra_group : h5py.Group, optional
            The mass spectra group. Defaults to None (no group, mass spectrum is added to the root).
        export_raw : bool, optional
            Whether to export the raw data. Defaults to True.
            If False, only the processed data (peaks) is exported (essentially centroided data).
        """
        if mass_spectra_group is None:
            # Check if the file has the necessary attributes and add them if not
            # This assumes that if there is a mass_spectra_group, these attributes were already added to the file
            if not hdf_handle.attrs.get("date_utc"):
                timenow = str(
                    datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S %Z")
                )
                hdf_handle.attrs["date_utc"] = timenow
                hdf_handle.attrs["file_name"] = mass_spectrum.filename.name
                hdf_handle.attrs["data_structure"] = "mass_spectrum"
                hdf_handle.attrs["analyzer"] = mass_spectrum.analyzer
                hdf_handle.attrs["instrument_label"] = mass_spectrum.instrument_label
                hdf_handle.attrs["sample_name"] = mass_spectrum.sample_name

        list_results = self.list_dict_to_list(mass_spectrum, is_hdf5=True)

        dict_ms_attrs = self.get_mass_spec_attrs(mass_spectrum)

        setting_dicts = parameter_to_dict.get_dict_data_ms(mass_spectrum)

        columns_labels = json.dumps(
            self.columns_label + self.get_all_used_atoms_in_order(mass_spectrum),
            sort_keys=False,
            indent=4,
            separators=(",", ": "),
        )

        group_key = group_key

        if mass_spectra_group is not None:
            hdf_handle = mass_spectra_group

        if group_key not in hdf_handle.keys():
            scan_group = hdf_handle.create_group(group_key)

            # If there is raw data (from profile data) save it
            if not mass_spectrum.is_centroid and export_raw:
                mz_abun_array = empty(shape=(2, len(mass_spectrum.abundance_profile)))

                mz_abun_array[0] = mass_spectrum.abundance_profile
                mz_abun_array[1] = mass_spectrum.mz_exp_profile

                raw_ms_dataset = scan_group.create_dataset(
                    "raw_ms", data=mz_abun_array, dtype="f8"
                )
                
                # Add metadata to the raw_ms dataset when it exists
                raw_ms_dataset.attrs["MassSpecAttrs"] = json.dumps(dict_ms_attrs)

                if isinstance(mass_spectrum, MassSpecfromFreq):
                    raw_ms_dataset.attrs["TransientSetting"] = json.dumps(
                        setting_dicts.get("TransientSetting"),
                        sort_keys=False,
                        indent=4,
                        separators=(",", ": "),
                    )
            else:
                # For centroided data, store metadata directly on the scan group
                scan_group.attrs["MassSpecAttrs"] = json.dumps(dict_ms_attrs)
                
                if isinstance(mass_spectrum, MassSpecfromFreq):
                    scan_group.attrs["TransientSetting"] = json.dumps(
                        setting_dicts.get("TransientSetting"),
                        sort_keys=False,
                        indent=4,
                        separators=(",", ": "),
                    )

        else:
            scan_group = hdf_handle.get(group_key)

        # if there is not processed data len = 0, otherwise len() will return next index
        index_processed_data = str(len(scan_group.keys()))

        timenow = str(datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S %Z"))

        processed_dset = scan_group.create_dataset(
            index_processed_data, data=list_results
        )

        processed_dset.attrs["date_utc"] = timenow

        processed_dset.attrs["ColumnsLabels"] = columns_labels

        processed_dset.attrs["MoleculaSearchSetting"] = json.dumps(
            setting_dicts.get("MoleculaSearch"),
            sort_keys=False,
            indent=4,
            separators=(",", ": "),
        )

        processed_dset.attrs["MassSpecPeakSetting"] = json.dumps(
            setting_dicts.get("MassSpecPeak"),
            sort_keys=False,
            indent=4,
            separators=(",", ": "),
        )

        processed_dset.attrs["MassSpectrumSetting"] = json.dumps(
            setting_dicts.get("MassSpectrum"),
            sort_keys=False,
            indent=4,
            separators=(",", ": "),
        )

    def to_hdf(self):
        """Exports the mass spectrum data to an HDF5 file."""

        with h5py.File(self.output_file.with_suffix(".hdf5"), "a") as hdf_handle:
            self.add_mass_spectrum_to_hdf5(
                hdf_handle, self.mass_spectrum, str(self.mass_spectrum.scan_number)
            )

    def parameters_to_toml(self):
        """Converts the mass spectrum parameters to a TOML string.

        Returns
        -------
        str
            The TOML string of the mass spectrum parameters.
        """

        dict_setting = parameter_to_dict.get_dict_data_ms(self.mass_spectrum)

        dict_setting["MassSpecAttrs"] = self.get_mass_spec_attrs(self.mass_spectrum)
        dict_setting["analyzer"] = self.mass_spectrum.analyzer
        dict_setting["instrument_label"] = self.mass_spectrum.instrument_label
        dict_setting["sample_name"] = self.mass_spectrum.sample_name

        output = toml.dumps(dict_setting)

        return output

    def parameters_to_json(self):
        """Converts the mass spectrum parameters to a JSON string.

        Returns
        -------
        str
            The JSON string of the mass spectrum parameters.
        """

        dict_setting = parameter_to_dict.get_dict_data_ms(self.mass_spectrum)

        dict_setting["MassSpecAttrs"] = self.get_mass_spec_attrs(self.mass_spectrum)
        dict_setting["analyzer"] = self.mass_spectrum.analyzer
        dict_setting["instrument_label"] = self.mass_spectrum.instrument_label
        dict_setting["sample_name"] = self.mass_spectrum.sample_name

        output = json.dumps(dict_setting)

        return output

    def get_mass_spec_attrs(self, mass_spectrum):
        """Returns the mass spectrum attributes as a dictionary.

        Parameters
        ----------
        mass_spectrum : MassSpectrum
            The mass spectrum to export.

        Returns
        -------
        dict
            The mass spectrum attributes.
        """

        dict_ms_attrs = {}
        dict_ms_attrs["polarity"] = mass_spectrum.polarity
        dict_ms_attrs["rt"] = mass_spectrum.retention_time
        dict_ms_attrs["tic"] = mass_spectrum.tic
        dict_ms_attrs["mobility_scan"] = mass_spectrum.mobility_scan
        dict_ms_attrs["mobility_rt"] = mass_spectrum.mobility_rt
        dict_ms_attrs["Aterm"] = mass_spectrum.Aterm
        dict_ms_attrs["Bterm"] = mass_spectrum.Bterm
        dict_ms_attrs["Cterm"] = mass_spectrum.Cterm
        dict_ms_attrs["baseline_noise"] = mass_spectrum.baseline_noise
        dict_ms_attrs["baseline_noise_std"] = mass_spectrum.baseline_noise_std

        return dict_ms_attrs

    def get_all_used_atoms_in_order(self, mass_spectrum):
        """Returns the list of assigned atoms in the order specified by Atoms.atoms_order list.

        Parameters
        ----------
        mass_spectrum : MassSpectrum
            The mass spectrum to export.

        Returns
        -------
        list
            The list of assigned atoms in the order specified by Atoms.atoms_order list.
        """

        atoms_in_order = Atoms.atoms_order
        all_used_atoms = set()
        if mass_spectrum:
            for ms_peak in mass_spectrum:
                if ms_peak:
                    for m_formula in ms_peak:
                        for atom in m_formula.atoms:
                            all_used_atoms.add(atom)

        def sort_method(atom):
            return [atoms_in_order.index(atom)]

        return sorted(all_used_atoms, key=sort_method)

    def list_dict_to_list(self, mass_spectrum, is_hdf5=False):
        """Returns the mass spectrum data as a list of dictionaries.

        Parameters
        ----------
        mass_spectrum : MassSpectrum
            The mass spectrum to export.
        is_hdf5 : bool, optional
            Whether the mass spectrum is being exported to an HDF5 file. Defaults to False.

        Returns
        -------
        list
            The mass spectrum data as a list of dictionaries.
        """

        column_labels = self.columns_label + self.get_all_used_atoms_in_order(
            mass_spectrum
        )

        dict_list = self.get_list_dict_data(mass_spectrum, is_hdf5=is_hdf5)

        all_lines = []
        for dict_res in dict_list:
            result_line = [NaN] * len(column_labels)

            for label, value in dict_res.items():
                label_index = column_labels.index(label)
                result_line[label_index] = value

            all_lines.append(result_line)

        return all_lines

    def get_list_dict_data(
        self,
        mass_spectrum,
        include_no_match=True,
        include_isotopologues=True,
        isotopologue_inline=True,
        no_match_inline=False,
        is_hdf5=False,
        additional_columns=None,
    ):
        """Returns the mass spectrum data as a list of dictionaries.

        Parameters
        ----------
        mass_spectrum : MassSpectrum
            The mass spectrum to export.
        include_no_match : bool, optional
            Whether to include unassigned (no match) data. Defaults to True.
        include_isotopologues : bool, optional
            Whether to include isotopologues. Defaults to True.
        isotopologue_inline : bool, optional
            Whether to include isotopologues inline. Defaults to True.
        no_match_inline : bool, optional
            Whether to include unassigned (no match) data inline. Defaults to False.
        is_hdf5 : bool, optional
            Whether the mass spectrum is being exported to an HDF5 file. Defaults to False.

        Returns
        -------
        list
            The mass spectrum data as a list of dictionaries.
        """

        dict_data_list = []

        if is_hdf5:
            encode = ".encode('utf-8')"
        else:
            encode = ""

        def add_no_match_dict_data(index, ms_peak):
            """
            Export dictionary of mspeak info for unassigned (no match) data
            """
            dict_result = {
                "Index": index,
                "m/z": ms_peak._mz_exp,
                "Calibrated m/z": ms_peak.mz_exp,
                "Peak Height": ms_peak.abundance,
                "Peak Area": ms_peak.area,
                "Resolving Power": ms_peak.resolving_power,
                "S/N": ms_peak.signal_to_noise,
                "Ion Charge": ms_peak.ion_charge,
                "Heteroatom Class": eval("Labels.unassigned{}".format(encode)),
            }

            dict_data_list.append(dict_result)

        def add_match_dict_data(index, ms_peak, mformula, additional_columns=None):
            """
            Export dictionary of mspeak info for assigned (match) data
            """
            formula_dict = mformula.to_dict()

            dict_result = {
                "Index": index,
                "m/z": ms_peak._mz_exp,
                "Calibrated m/z": ms_peak.mz_exp,
                "Calculated m/z": mformula.mz_calc,
                "Peak Height": ms_peak.abundance,
                "Peak Area": ms_peak.area,
                "Resolving Power": ms_peak.resolving_power,
                "S/N": ms_peak.signal_to_noise,
                "Ion Charge": ms_peak.ion_charge,
                "m/z Error (ppm)": mformula.mz_error,
                "Confidence Score": mformula.confidence_score,
                "Isotopologue Similarity": mformula.isotopologue_similarity,
                "m/z Error Score": mformula.average_mz_error_score,
                "DBE": mformula.dbe,
                "Heteroatom Class": eval("mformula.class_label{}".format(encode)),
                "H/C": mformula.H_C,
                "O/C": mformula.O_C,
                "Ion Type": eval("mformula.ion_type.lower(){}".format(encode)),
                "Is Isotopologue": int(mformula.is_isotopologue),
                "Molecular Formula": eval("mformula.string{}".format(encode)),
            }
            if additional_columns is not None:
                possible_dict = {
                    "Aromaticity Index": mformula.A_I,
                    "NOSC": mformula.nosc,
                    "Aromaticity Index (modified)": mformula.A_I_mod,
                }
                for column in additional_columns:
                    dict_result[column] = possible_dict.get(column)

            if mformula.adduct_atom:
                dict_result["Adduct"] = eval("mformula.adduct_atom{}".format(encode))

            if mformula.is_isotopologue:
                dict_result["Mono Isotopic Index"] = mformula.mspeak_index_mono_isotopic

            if self.atoms_order_list is None:
                atoms_order_list = self.get_all_used_atoms_in_order(mass_spectrum)
            else:
                atoms_order_list = self.atoms_order_list

            for atom in atoms_order_list:
                if atom in formula_dict.keys():
                    dict_result[atom] = formula_dict.get(atom)

            dict_data_list.append(dict_result)

        score_methods = mass_spectrum.molecular_search_settings.score_methods
        selected_score_method = (
            mass_spectrum.molecular_search_settings.output_score_method
        )

        if selected_score_method in score_methods:
            # temp set score method as the one chosen in the output
            current_method = mass_spectrum.molecular_search_settings.score_method
            mass_spectrum.molecular_search_settings.score_method = selected_score_method

            for index, ms_peak in enumerate(mass_spectrum):
                # print(ms_peak.mz_exp)

                if ms_peak:
                    m_formula = ms_peak.best_molecular_formula_candidate

                    if m_formula:
                        if not m_formula.is_isotopologue:
                            add_match_dict_data(
                                index,
                                ms_peak,
                                m_formula,
                                additional_columns=additional_columns,
                            )

                            for (
                                iso_mspeak_index,
                                iso_mf_formula,
                            ) in m_formula.mspeak_mf_isotopologues_indexes:
                                iso_ms_peak = mass_spectrum[iso_mspeak_index]
                                add_match_dict_data(
                                    iso_mspeak_index,
                                    iso_ms_peak,
                                    iso_mf_formula,
                                    additional_columns=additional_columns,
                                )
                else:
                    if include_no_match and no_match_inline:
                        add_no_match_dict_data(index, ms_peak)

            if include_no_match and not no_match_inline:
                for index, ms_peak in enumerate(mass_spectrum):
                    if not ms_peak:
                        add_no_match_dict_data(index, ms_peak)
            # reset score method as the one chosen in the output
            mass_spectrum.molecular_search_settings.score_method = current_method

        else:
            for index, ms_peak in enumerate(mass_spectrum):
                # check if there is a molecular formula candidate for the msPeak

                if ms_peak:
                    # m_formula = ms_peak.molecular_formula_lowest_error
                    for m_formula in ms_peak:
                        if mass_spectrum.molecular_search_settings.output_min_score > 0:
                            if (
                                m_formula.confidence_score
                                >= mass_spectrum.molecular_search_settings.output_min_score
                            ):
                                if m_formula.is_isotopologue:  # isotopologues inline
                                    if include_isotopologues and isotopologue_inline:
                                        add_match_dict_data(
                                            index,
                                            ms_peak,
                                            m_formula,
                                            additional_columns=additional_columns,
                                        )
                                else:
                                    add_match_dict_data(
                                        index,
                                        ms_peak,
                                        m_formula,
                                        additional_columns=additional_columns,
                                    )  # add monoisotopic peak

                            # cutoff because of low score
                            else:
                                add_no_match_dict_data(index, ms_peak)

                        else:
                            if m_formula.is_isotopologue:  # isotopologues inline
                                if include_isotopologues and isotopologue_inline:
                                    add_match_dict_data(
                                        index,
                                        ms_peak,
                                        m_formula,
                                        additional_columns=additional_columns,
                                    )
                            else:
                                add_match_dict_data(
                                    index,
                                    ms_peak,
                                    m_formula,
                                    additional_columns=additional_columns,
                                )  # add monoisotopic peak
                else:
                    # include not_match
                    if include_no_match and no_match_inline:
                        add_no_match_dict_data(index, ms_peak)

            if include_isotopologues and not isotopologue_inline:
                for index, ms_peak in enumerate(mass_spectrum):
                    for m_formula in ms_peak:
                        if m_formula.is_isotopologue:
                            if (
                                m_formula.confidence_score
                                >= mass_spectrum.molecular_search_settings.output_min_score
                            ):
                                add_match_dict_data(
                                    index,
                                    ms_peak,
                                    m_formula,
                                    additional_columns=additional_columns,
                                )

            if include_no_match and not no_match_inline:
                for index, ms_peak in enumerate(mass_spectrum):
                    if not ms_peak:
                        add_no_match_dict_data(index, ms_peak)

        # remove duplicated add_match data possibly introduced on the output_score_filter step
        res = []
        [res.append(x) for x in dict_data_list if x not in res]

        return res
