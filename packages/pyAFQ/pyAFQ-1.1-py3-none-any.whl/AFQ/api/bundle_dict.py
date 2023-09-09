import logging
from collections.abc import MutableMapping, Mapping

import AFQ.data.fetch as afd
import AFQ.utils.volume as auv
from AFQ.tasks.utils import get_fname, str_to_desc
from AFQ.definitions.utils import find_file

import numpy as np
import nibabel as nib

from dipy.io.streamline import load_tractogram

logging.basicConfig(level=logging.INFO)


__all__ = ["PediatricBundleDict", "BundleDict"]


def do_preprocessing():
    raise NotImplementedError


def append_l_r(bundle_list, no_lr_list):
    new_bundle_list = []
    for bundle in bundle_list:
        if bundle in no_lr_list:
            new_bundle_list.append(bundle)
        else:
            new_bundle_list.append(bundle + "_L")
            new_bundle_list.append(bundle + "_R")
    return new_bundle_list


BUNDLES = ["ATR", "CGC", "CST", "IFO", "ILF", "SLF", "ARC", "UNC",
           "FA", "FP", "pARC", "VOF"]
BUNDLES = append_l_r(BUNDLES, ["FA", "FP"])

CALLOSUM_BUNDLES = ["AntFrontal", "Motor", "Occipital", "Orbital",
                    "PostParietal", "SupFrontal", "SupParietal",
                    "Temporal"]

# See: https://www.cmu.edu/dietrich/psychology/cognitiveaxon/documents/yeh_etal_2018.pdf  # noqa

RECO_UNIQUE = [
    'CCMid', 'CC_ForcepsMajor', 'CC_ForcepsMinor', 'MCP', 'AC', 'PC', 'SCP',
    'V', 'CC', 'F_L_R']

RECO_BUNDLES_16 = [
    'CST', 'C', 'F', 'UF', 'MCP', 'AF', 'CCMid',
    'CC_ForcepsMajor', 'CC_ForcepsMinor', 'IFOF']
RECO_BUNDLES_16 = append_l_r(RECO_BUNDLES_16, RECO_UNIQUE)

RECO_BUNDLES_80 = ["AC", "AF", "AR", "AST", "C", "CB", "CC_ForcepsMajor",
                   "CC_ForcepsMinor", "CC", "CCMid", "CNII", "CNIII",
                   "CNIV", "CNV", "CNVII", "CNVIII", "CS", "CST", "CT",
                   "CTT", "DLF", "EMC", "F_L_R", "FPT", "ICP", "IFOF", "ILF",
                   "LL", "MCP", "MdLF", "ML", "MLF", "OPT", "OR", "PC", "PPT",
                   "RST", "SCP", "SLF", "STT", "TPT", "UF", "V", "VOF"]
RECO_BUNDLES_80 = append_l_r(RECO_BUNDLES_80, RECO_UNIQUE)

PEDIATRIC_BUNDLES = [
    "ARC", "ATR", "CGC", "CST", "FA", "FP", "IFO", "ILF", "MdLF", "SLF", "UNC"]
PEDIATRIC_BUNDLES = append_l_r(PEDIATRIC_BUNDLES, ["FA", "FP"])

DIPY_GH = "https://github.com/dipy/dipy/blob/master/dipy/"


class _BundleEntry(Mapping):
    """Describes how to recognize a single bundle, immutable"""

    def __init__(self, data):
        self._data = data

    def __getitem__(self, key):
        return self._data[key]

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __setitem__(self, key, value):
        raise RuntimeError((
            "You cannot modify the properties of a bundle's definition. "
            "To modify a bundle's definition, replace that bundle's entry "
            "in the BundleDict."))


class BundleDict(MutableMapping):
    """
    Create a bundle dictionary, needed for the segmentation.

    Parameters
    ----------
    bundle_info : list or dict, optional
        A list of the bundles to be used, or a dictionary defining
        custom bundles. See `Defining Custom Bundle Dictionaries`
        in the `usage` section of pyAFQ's documentation for details.
        Default: AFQ.api.bundle_dict.BUNDLES

    seg_algo: One of {"afq", "reco", "reco16", "reco80"}
        The bundle segmentation algorithm to use.
            "afq" : Use waypoint ROIs + probability maps, as described
            in [Yeatman2012]_
            "reco" / "reco16" : Use Recobundles [Garyfallidis2017]_
            with a 16-bundle set.
            "reco80": Use Recobundles with an 80-bundle set.

    resample_to : Nifti1Image or bool, optional
        If there are bundles in bundle_info with the 'space' attribute
        set to 'template', or with no 'space' attribute,
        their images (all ROIs and probability maps)
        will be resampled to the affine and shape of this image.
        If None, the MNI template will be used.
        If False, no resampling will be done.
        Default: None

    resample_subject_to : Nifti1Image or bool, optional
        If there are bundles in bundle_info with the 'space' attribute
        set to 'subject', their images (all ROIs and probability maps)
        will be resampled to the affine and shape of this image.
        If False, no resampling will be done.
        Default: None

    keep_in_memory : bool, optional
        Whether, once loaded, all ROIs and probability maps will stay
        loaded in memory within this object. By default, ROIs are loaded
        into memory on demand and no references to ROIs are kept, other
        than their paths. The default 18 bundles use ~6GB when all loaded.
        Default: False

    Examples
    --------
    # import OR ROIs and create a custom bundle dict
    # from them
    import AFQ.data.fetch as afd
    or_rois = afd.read_or_templates()

    bundles = BundleDict({
        "L_OR": {
            "include": [
                or_rois["left_OR_1"],  # these can be paths to Nifti files
                or_rois["left_OR_2"]],  # or they can Nifti images
            "exclude": [
                or_rois["left_OP_MNI"],
                or_rois["left_TP_MNI"],
                or_rois["left_pos_thal_MNI"]],
            "start": or_rois['left_thal_MNI'],
            "end": or_rois['left_V1_MNI'],
            "cross_midline": False,
        },
        "R_OR": {
            "include": [
                or_rois["right_OR_1"],
                or_rois["right_OR_2"]],
            "exclude": [
                or_rois["right_OP_MNI"],
                or_rois["right_TP_MNI"],
                or_rois["right_pos_thal_MNI"]],
            "start": or_rois['right_thal_MNI'],
            "end": or_rois['right_V1_MNI'],
            "cross_midline": False
        }
    })
    """

    def __init__(self,
                 bundle_info=BUNDLES,
                 seg_algo="afq",
                 resample_to=None,
                 resample_subject_to=False,
                 keep_in_memory=False):
        if not (isinstance(bundle_info, dict)
                or isinstance(bundle_info, list)):
            raise TypeError((
                f"bundle_info must be a dict or a list,"
                f" currently a {type(bundle_info)}"))
        self.seg_algo = seg_algo.lower()
        if resample_to is None:
            resample_to = afd.read_mni_template()
        self.resample_to = resample_to
        self.resample_subject_to = resample_subject_to
        self.keep_in_memory = keep_in_memory
        self.has_bids_info = False
        self.max_includes = 3

        self._dict = {}
        self.bundle_names = []
        self.templates_loaded = False
        if isinstance(bundle_info, dict):
            for key, item in bundle_info.items():
                self.__setitem__(key, item)
        else:
            for bundle_name in bundle_info:
                self.bundle_names.append(bundle_name)

        self.logger = logging.getLogger('AFQ')

        if self.seg_algo == "afq":
            if "FP" in self.bundle_names\
                    and "Occipital" in self.bundle_names:
                self.logger.warning((
                    "FP and Occipital bundles are co-located, and AFQ"
                    " assigns each streamline to only one bundle."
                    " Only Occipital will be used."))
                self.bundle_names.remove("FP")
            if "FA" in self.bundle_names\
                    and "Orbital" in self.bundle_names:
                self.logger.warning((
                    "FA and Orbital bundles are co-located, and AFQ"
                    " assigns each streamline to only one bundle."
                    " Only Orbital will be used."))
                self.bundle_names.remove("FA")
            if "FA" in self.bundle_names\
                    and "AntFrontal" in self.bundle_names:
                self.logger.warning((
                    "FA and AntFrontal bundles are co-located, and AFQ"
                    " assigns each streamline to only one bundle."
                    " Only AntFrontal will be used."))
                self.bundle_names.remove("FA")

    def update_max_includes(self, new_max):
        if new_max > self.max_includes:
            self.max_includes = new_max

    def load_templates(self):
        """
        Loads templates for generating bundle dictionaries
        from bundle names.
        """
        if self.seg_algo == "afq":
            self.templates =\
                afd.read_templates(as_img=False)
            # For the arcuate, we need to rename a few of these
            # and duplicate the SLF ROI:
            self.templates['ARC_roi1_L'] = self.templates['SLF_roi1_L']
            self.templates['ARC_roi1_R'] = self.templates['SLF_roi1_R']
            self.templates['ARC_roi2_L'] = self.templates['SLFt_roi2_L']
            self.templates['ARC_roi2_R'] = self.templates['SLFt_roi2_R']
            callosal_templates =\
                afd.read_callosum_templates(as_img=False)
            self.templates = {
                **self.templates,
                **callosal_templates}
        elif self.seg_algo.startswith("reco"):
            if self.seg_algo.endswith("80"):
                self.templates = afd.read_hcp_atlas(80, as_file=True)
            else:
                self.templates = afd.read_hcp_atlas(16, as_file=True)
        else:
            raise ValueError(
                "Input: %s is not a valid input`seg_algo`" % self.seg_algo)
        self.templates_loaded = True

    def _gen(self, bundle_name):
        """
        Given a bundle name, load its
        bundle's dictionary describing the bundle.
        """
        if self.seg_algo == "afq":
            name = bundle_name[:-2]
            hemi = bundle_name[-2:]
            if bundle_name in CALLOSUM_BUNDLES:
                roi_name1 = "L_" + bundle_name
                roi_name2 = "R_" + bundle_name
            elif bundle_name in ["FA", "FP"]:
                roi_name1 = bundle_name + "_L"
                roi_name2 = bundle_name + "_R"
            else:
                roi_name1 = name + '_roi1' + hemi
                roi_name2 = name + '_roi2' + hemi

            roi_dict = {}
            if name == "pARC":
                roi_dict['cross_midline'] = False
                roi_dict['include'] = [self.templates["SLFt_roi2" + hemi]]
                roi_dict['exclude'] = [self.templates["SLF_roi1" + hemi]]
                roi_dict['space'] = 'template'
                roi_dict['start'] = self.templates[bundle_name + "_start"]
                roi_dict['primary_axis'] = 2
                roi_dict["primary_axis_percentage"] = 40
                self._dict[bundle_name] = roi_dict
            elif name == "VOF":
                roi_dict['cross_midline'] = False
                roi_dict['space'] = 'template'
                roi_dict['start'] = self.templates[bundle_name + "_start"]
                roi_dict['end'] = self.templates[bundle_name + "_end"]
                roi_dict["inc_addtol"] = [4, 0]
                roi_dict['primary_axis'] = 2
                roi_dict["primary_axis_percentage"] = 40
                self._dict[bundle_name] = roi_dict
            elif (roi_name1 in self.templates
                    and roi_name2 in self.templates):
                roi_dict['cross_midline'] = False
                roi_dict['include'] = [
                    self.templates[roi_name1],
                    self.templates[roi_name2]]
                roi_dict['exclude'] = []
                roi_dict['space'] = 'template'
                if name + '_roi3' + hemi in self.templates:
                    roi_dict['include'].append(
                        self.templates[name + '_roi3' + hemi])
                if name == "SLF":
                    roi_dict['exclude'].append(
                        self.templates["SLFt_roi2" + hemi])
                if bundle_name in CALLOSUM_BUNDLES\
                        or bundle_name in ["FA", "FP"]:
                    roi_dict['include'].append(
                        self.templates["Callosum_midsag"])
                    roi_dict['cross_midline'] = True
                if bundle_name + '_prob_map' in self.templates:
                    roi_dict['prob_map'] = self.templates[
                        bundle_name + '_prob_map']
                if bundle_name + "_start" in self.templates and self.templates[
                        bundle_name + "_start"] is not None:
                    roi_dict['start'] = self.templates[
                        bundle_name + "_start"]
                if bundle_name + "_end" in self.templates and self.templates[
                        bundle_name + "_end"] is not None:
                    roi_dict['end'] = self.templates[
                        bundle_name + "_end"]
                self._dict[bundle_name] = roi_dict
            else:
                raise ValueError(f"{bundle_name} is not in AFQ templates")
        elif self.seg_algo.startswith("reco"):
            self._dict[bundle_name] = self.templates[bundle_name]

    def gen_all(self):
        """
        If bundle_info is a list of names, this will load
        each bundle's dictionary describing the bundle.
        """
        for bundle_name in self.bundle_names:
            if bundle_name not in self._dict:
                if not self.templates_loaded:
                    self.load_templates()
                self._gen(bundle_name)
        if self.templates_loaded:
            del self.templates
        self.templates_loaded = False

    def set_bids_info(self, bids_layout, bids_path, subject, session):
        """
        Provide the bids_layout, a nearest path,
        and the subject and session information
        to load ROIS from BIDS
        """
        self.has_bids_info = True
        self._bids_info = bids_layout
        self._bids_path = bids_path
        self._subject = subject
        self._session = session

    def _cond_load(self, roi_or_sl, resample_to):
        """
        Load ROI or streamline if not already loaded
        """
        if isinstance(roi_or_sl, dict):
            if not self.has_bids_info:
                raise ValueError((
                    "Attempted to load an ROI using BIDS description without "
                    "First providing BIDS information."))
            suffix = roi_or_sl.get("suffix", "dwi")
            roi_or_sl = find_file(
                self._bids_info, self._bids_path,
                roi_or_sl,
                suffix,
                self._session, self._subject)
        if isinstance(roi_or_sl, str):
            if self.seg_algo == "afq":
                return afd.read_resample_roi(
                    roi_or_sl,
                    resample_to=resample_to)
            elif self.seg_algo.startswith("reco"):
                return load_tractogram(
                    roi_or_sl,
                    'same',
                    bbox_valid_check=False).streamlines
        else:
            return roi_or_sl

    def get_b_info(self, b_name):
        if b_name not in self._dict and b_name in self.bundle_names:
            # generate all in one go, so templates are not kept in memory
            self.gen_all()
        return self._dict[b_name]

    def __getitem__(self, key):
        if key not in self._dict and key in self.bundle_names:
            # generate all in one go, so templates are not kept in memory
            self.gen_all()
        if not self.keep_in_memory:
            _item = self._dict[key].copy()
            _res = self._cond_load_bundle(key, dry_run=True)
            if _res is not None:
                _item.update(_res)
            _item = _BundleEntry(_item)
        else:
            if "loaded" not in self._dict[key] or\
                    not self._dict[key]["loaded"]:
                self._cond_load_bundle(key)
                self._dict[key]["loaded"] = True
            if "resampled" not in self._dict[key] or not self._dict[
                    key]["resampled"]:
                self._resample_roi(key)
            _item = _BundleEntry(self._dict[key].copy())
        return _item

    def __setitem__(self, key, item):
        self._dict[key] = item
        if hasattr(item, "get"):
            self.update_max_includes(len(item.get("include", [])))
        if key not in self.bundle_names:
            self.bundle_names.append(key)

    def __len__(self):
        return len(self.bundle_names)

    def __delitem__(self, key):
        if key not in self._dict and key not in self.bundle_names:
            raise KeyError(f"{key} not found")
        if key in self._dict:
            del self._dict[key]
        else:
            raise RuntimeError((
                f"{key} not found in internal dictionary, "
                f"but found in bundle_names"))
        if key in self.bundle_names:
            self.bundle_names.remove(key)
        else:
            raise RuntimeError((
                f"{key} not found in bundle_names, "
                f"but found in internal dictionary"))

    def __iter__(self):
        self.gen_all()
        return iter(self._dict)

    def copy(self):
        """
        Generates a copy of this BundleDict where the internal dictionary
        is a copy of this BundleDict's internal dictionary.
        Useful if you want to add or remove bundles from a copy
        of a BundleDict.

        Returns
        ---------
        bundle_dict : BundleDict
            Euclidean norms of vectors.
        """
        self.gen_all()
        return self.__class__(
            self._dict.copy(),
            seg_algo=self.seg_algo,
            resample_to=self.resample_to,
            resample_subject_to=self.resample_subject_to,
            keep_in_memory=self.keep_in_memory)

    def apply_to_rois(self, b_name, func, *args,
                      dry_run=False,
                      **kwargs):
        """
        Applies some transformation to all ROIs (include, exclude, end, start)
        and the prob_map in a given bundle.

        Parameters
        ----------
        b_name : name
            bundle name of bundle whose ROIs will be transformed.
        func : function
            function whose first argument must be a Nifti1Image and which
            returns a Nifti1Image
        dry_run : bool
            Whether to actually apply changes returned by `func` to the ROIs.
            If has_return is False, dry_run is not used.
        *args :
            Additional arguments for func
        **kwargs
            Optional arguments for func

        Returns
        -------
        A dictionary where keys are
        the roi type and values are the transformed ROIs.
        """
        return_vals = {}
        if self.seg_algo == "afq":
            for roi_type in ["include", "exclude", "start", "end", "prob_map"]:
                if roi_type in self._dict[b_name]:
                    if roi_type in ["start", "end", "prob_map"]:
                        return_vals[roi_type] = func(
                            self._dict[b_name][roi_type], *args, **kwargs)
                    else:
                        changed_rois = []
                        for _roi in self._dict[b_name][roi_type]:
                            changed_rois.append(func(
                                _roi, *args, **kwargs))
                        return_vals[roi_type] = changed_rois
        elif self.seg_algo.startswith("reco"):
            if b_name == "whole_brain":
                return_vals = func(
                    self._dict[b_name], *args, **kwargs)
            else:
                for sl_type in ["sl", "centroid"]:
                    return_vals[sl_type] = func(
                        self._dict[b_name][sl_type],
                        *args, **kwargs)
        if not dry_run:
            for roi_type, roi in return_vals.items():
                self._dict[b_name][roi_type] = roi
        return return_vals

    def _cond_load_bundle(self, b_name, dry_run=False):
        """
        Given a bundle name, resample all ROIs and prob maps
        into either template or subject space for that bundle,
        depending on its "space" attribute.

        Parameters
        ----------
        b_name : str
            Name of the bundle to be resampled.
        """
        if self.seg_algo == "afq":
            if self.is_bundle_in_template(b_name):
                resample_to = self.resample_to
            else:
                resample_to = self.resample_subject_to
        else:
            resample_to = None
        return self.apply_to_rois(
            b_name,
            self._cond_load,
            resample_to,
            dry_run=dry_run)

    def is_bundle_in_template(self, bundle_name):
        return "space" not in self._dict[bundle_name]\
            or self._dict[bundle_name]["space"] == "template"

    def _roi_transform_helper(self, roi, mapping, new_affine, bundle_name):
        roi = afd.read_resample_roi(roi, self.resample_to)
        warped_img = auv.transform_inverse_roi(
            roi.get_fdata(),
            mapping,
            bundle_name=bundle_name)
        warped_img = nib.Nifti1Image(warped_img, new_affine)
        return warped_img

    def transform_rois(self, bundle_name, mapping, new_affine,
                       base_fname=None):
        """
        Get the bundle definition with transformed ROIs
        for a given bundle into a
        given subject space using a given mapping.
        Will only run on bundles which are in template
        space, otherwise will just return the bundle
        definition without transformation.

        Parameters
        ----------
        bundle_name : str
            Name of the bundle to be transformed.
        mapping : DiffeomorphicMap object
            A mapping between DWI space and a template.
        new_affine : array
            Affine of space transformed into.
        base_fname : str, optional
            Base file path to save ROIs too. Additional BIDS
            descriptors will be added to this file path. If None, 
            do not save the ROIs.

        Returns
        -------
        If base_fname is None, a dictionary where keys are
        the roi type and values are the transformed ROIs.
        Otherwise, a list of file names where the transformed
        ROIs are saved.
        """
        if self.is_bundle_in_template(bundle_name):
            transformed_rois = self.apply_to_rois(
                bundle_name,
                self._roi_transform_helper,
                mapping,
                new_affine,
                bundle_name,
                dry_run=True)
        else:
            transformed_rois = self.apply_to_rois(
                bundle_name,
                self._cond_load,
                self.resample_subject_to,
                dry_run=True)

        if base_fname is not None:
            fnames = []
            for roi_type, rois in transformed_rois.items():
                if not isinstance(rois, list):
                    rois = [rois]
                for ii, roi in enumerate(rois):
                    fname = get_fname(
                        base_fname,
                        '_space-subject_desc-'
                        f'{str_to_desc(bundle_name)}{roi_type}{ii}'
                        '_mask.nii.gz')
                    nib.save(
                        nib.Nifti1Image(
                            roi.get_fdata().astype(np.float32),
                            roi.affine), fname)
                    fnames.append(fname)
            return fnames
        else:
            return transformed_rois

    def __add__(self, other):
        self.gen_all()
        other.gen_all()
        if self.seg_algo != other.seg_algo:
            raise ValueError((
                "Adding BundleDicts where seg_algo do not match."
                f"seg_algo's are {self.seg_algo} and {other.seg_algo}"))
        for resample in ["resample_to", "resample_subject_to"]:
            if not getattr(self, resample)\
                    or not getattr(other, resample)\
                    or getattr(self, resample) is None\
                    or getattr(other, resample) is None:
                if getattr(self, resample) != getattr(other, resample):
                    raise ValueError((
                        f"Adding BundleDicts where {resample} do not match."
                        f"{resample}'s are {getattr(self, resample)} and "
                        f"{getattr(other, resample)}"))
            else:
                if not np.allclose(
                        getattr(self, resample).affine,
                        getattr(other, resample).affine):
                    raise ValueError((
                        f"Adding BundleDicts where {resample} affines"
                        f" do not match. {resample} affines are"
                        f"{getattr(self, resample).affine} and "
                        f"{getattr(other, resample).affine}"))
                if not np.allclose(
                        getattr(self, resample).header['dim'],
                        getattr(other, resample).header['dim']):
                    raise ValueError((
                        f"Adding BundleDicts where {resample} dimensions"
                        f" do not match. {resample} dimensions are"
                        f"{getattr(self, resample).header['dim']} and "
                        f"{getattr(other, resample).header['dim']}"))
        return self.__class__(
            {**self._dict, **other._dict},
            self.seg_algo,
            self.resample_to,
            self.resample_subject_to,
            self.keep_in_memory)


class PediatricBundleDict(BundleDict):
    def __init__(self,
                 bundle_info=PEDIATRIC_BUNDLES,
                 seg_algo="afq",
                 resample_to=None,
                 resample_subject_to=False,
                 keep_in_memory=False):
        """
        Create a pediatric bundle dictionary, needed for the segmentation

        Parameters
        ----------
        bundle_info : list or dict, optional
            A list of the bundles to be used, or a dictionary defining
            custom bundles.
            Default: AFQ.api.bundle_dict.PEDIATRIC_BUNDLES

        seg_algo: only "afq" is supported
            The bundle segmentation algorithm to use.
                "afq" : Use waypoint ROIs + probability maps, as described
                in [Yeatman2012]_

        resample_to : Nifti1Image or bool, optional
            If set, templates will be resampled to the affine and shape of this
            image. If None, this will be used:
            afd.read_pediatric_templates()['UNCNeo-withCerebellum-for-babyAFQ']
            If False, no resampling will be done.
            Default: None

        resample_subject_to : Nifti1Image or bool, optional
            If there are ROIs with the 'space' attribute
            set to 'subject', those ROIs will be resampled to the affine
            and shape of this image.
            If False, no resampling will be done.
            Default: None

        keep_in_memory : bool, optional
            Whether, once loaded, all ROIs and probability maps will stay
            loaded in memory within this object. By default, ROIs are loaded
            into memory on demand and no references to ROIs are kept, other
            than their paths. The default 18 bundles use ~6GB when all loaded.
            Default: False

        """
        if resample_to is None:
            resample_to = afd.read_pediatric_templates()[
                'UNCNeo-withCerebellum-for-babyAFQ']
        self.resample_to = resample_to
        BundleDict.__init__(
            self, bundle_info, seg_algo,
            resample_to, resample_subject_to)

    def load_templates(self):
        # Pediatric bundles differ from adult bundles:
        #   - A third ROI has been introduced for curvy tracts:
        #     ARC, ATR, CGC, IFO, and UCI
        #   - ILF posterior ROI has been split into two
        #     to separate ILF and mdLF
        #   - Addition of pAF and VOF ROIs
        #   - SLF ROIs are restricted to parietal cortex
        self.templates = afd.read_pediatric_templates()

        # pediatric probability maps
        prob_map_order = [
            "ATR_L", "ATR_R", "CST_L", "CST_R", "CGC_L", "CGC_R",
            "FP", "FA", "IFO_L", "IFO_R", "ILF_L",
            "ILF_R", "SLF_L", "SLF_R", "UNC_L", "UNC_R",
            "ARC_L", "ARC_R", "MdLF_L", "MdLF_R"]

        prob_maps = self.templates[
            'UNCNeo_JHU_tracts_prob-for-babyAFQ']
        prob_map_data = prob_maps.get_fdata()

        self.templates["Callosum_midsag"] = self.templates["mid-saggital"]

        for bundle_name in PEDIATRIC_BUNDLES:
            self.templates[bundle_name + "_prob_map"] = nib.Nifti1Image(
                prob_map_data[
                    ...,
                    prob_map_order.index(bundle_name)], prob_maps.affine)

        # reuse probability map from ILF
        self.templates["MdLF_L_prob_map"] = self.templates["ILF_L_prob_map"]
        self.templates["MdLF_R_prob_map"] = self.templates["ILF_R_prob_map"]

    def _gen(self, bundle_name):
        if bundle_name == "OR_L":
            self._dict["OR_L"] = {
                "include": [self.templates["OR_left_roi3"]],
                "start": self.templates["OR_leftThal"],
                "end": self.templates["OR_leftV1"],
                "cross_midline": False
            }
        elif bundle_name == "OR_R":
            self._dict["OR_R"] = {
                "include": [self.templates["OR_right_roi3"]],
                "start": self.templates["OR_rightThal"],
                "end": self.templates["OR_rightV1"],
                "cross_midline": False
            }
        elif bundle_name == "pARC_L":
            self._dict["pARC_L"] = {
                "include": [self.templates["SLFt_roi2_L"]],
                "exclude": [self.templates["SLF_roi1_L"]],
                "start": self.templates["pARC_L_start"],
                "end": self.templates["VOF_box_small_L"],
                "primary_axis": 2,
                "primary_axis_percentage": 40,
                "cross_midline": False
            }
        elif bundle_name == "pARC_R":
            self._dict["pARC_R"] = {
                "include": [self.templates["SLFt_roi2_R"]],
                "exclude": [self.templates["SLF_roi1_R"]],
                "start": self.templates["pARC_R_start"],
                "end": self.templates["VOF_box_small_R"],
                "primary_axis": 2,
                "primary_axis_percentage": 40,
                "cross_midline": False
            }
        elif bundle_name == "VOF_L":
            self._dict["VOF_L"] = {
                "start": self.templates["VOF_L_start"],
                "end": self.templates["VOF_box_small_L"],
                "primary_axis": 2,
                "primary_axis_percentage": 40,
                "cross_midline": False
            }
        elif bundle_name == "VOF_R":
            self._dict["VOF_R"] = {
                "start": self.templates["VOF_R_start"],
                "end": self.templates["VOF_box_small_R"],
                "primary_axis": 2,
                "primary_axis_percentage": 40,
                "cross_midline": False
            }
        else:
            super()._gen(bundle_name)
