from .portfolio_entry import PortfolioEntry

DENOISING = "denoising"


class N2V_BSD68(PortfolioEntry):
    """BSD68 dataset.

    Attributes
    ----------
        portfolio (str): Name of the portfolio to which the dataset belong.
        name (str): Name of the dataset.
        url (str): URL of the dataset.
        description (str): Description of the dataset.
        license (str): License of the dataset.
        citation (str): Citation to use when referring to the dataset.
        file_name (str): Name of the downloaded file.
        hash (str): SHA256 hash of the downloaded file.
        files (list[str]): List of files in the dataset.
        size (int): Size of the dataset in MB.
        tags (list[str]): List of tags associated to the dataset.
        is_zip (bool): Whether the dataset is a zip file.
    """

    def __init__(self) -> None:
        super().__init__(
            portfolio=DENOISING,
            name="N2V_BSD68",
            url="https://download.fht.org/jug/n2v/BSD68_reproducibility_data.zip",
            file_name="BSD68_reproducibility_data.zip",
            sha256="32c66d41196c9cafff465f3c7c42730f851c24766f70383672e18b8832ea8e55",
            description="This dataset is taken from K. Zhang et al (TIP, 2017). \n"
            "It consists of 400 gray-scale 180x180 images (cropped from the "
            "BSD dataset) and splitted between training and validation, and "
            "68 gray-scale test images (BSD68).\n"
            "All images were corrupted with Gaussian noise with standard "
            "deviation of 25 pixels. The test dataset contains the uncorrupted "
            "images as well.\n"
            "Original dataset: "
            "https://www2.eecs.berkeley.edu/Research/Projects/CS/vision/bsds/",
            license="Unknown",
            citation='D. Martin, C. Fowlkes, D. Tal and J. Malik, "A database of '
            "human segmented natural images and its application to "
            "evaluating segmentation algorithms and measuring ecological "
            'statistics," Proceedings Eighth IEEE International '
            "Conference on Computer Vision. ICCV 2001, Vancouver, BC, "
            "Canada, 2001, pp. 416-423 vol.2, doi: "
            "10.1109/ICCV.2001.937655.",
            files=[
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_1.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_2.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_3.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_4.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_5.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_6.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_7.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_8.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_9.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_10.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_11.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_12.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_13.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_14.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_15.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_16.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_17.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_18.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_19.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_20.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_21.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_22.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_23.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_24.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_25.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_26.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_27.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_28.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_29.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_30.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_31.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_32.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_33.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_34.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_35.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_36.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_37.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_38.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_39.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_40.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_41.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_42.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_43.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_44.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_45.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_46.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_47.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_48.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_49.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_50.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_51.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_52.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_53.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_54.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_55.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_56.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_57.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_58.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_59.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_60.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_61.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_62.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_63.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_64.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_65.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_66.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_67.tiff",
                "BSD68_reproducibility_data/test/images/bsd68_gaussian25_68.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_1.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_2.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_3.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_4.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_5.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_6.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_7.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_8.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_9.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_10.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_11.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_12.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_13.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_14.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_15.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_16.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_17.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_18.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_19.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_20.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_21.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_22.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_23.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_24.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_25.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_26.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_27.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_28.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_29.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_30.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_31.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_32.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_33.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_34.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_35.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_36.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_37.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_38.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_39.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_40.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_41.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_42.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_43.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_44.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_45.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_46.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_47.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_48.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_49.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_50.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_51.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_52.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_53.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_54.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_55.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_56.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_57.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_58.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_59.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_60.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_61.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_62.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_63.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_64.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_65.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_66.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_67.tiff",
                "BSD68_reproducibility_data/test/gt/bsd68_groundtruth_68.tiff",
                "BSD68_reproducibility_data/train/DCNN400_train_gaussian25.tiff",
                "BSD68_reproducibility_data/val/DCNN400_validation_gaussian25.tiff",
            ],
            size=395.0,
            tags=["denoising", "natural images"],
        )


class N2V_SEM(PortfolioEntry):
    """SEM dataset.

    Attributes
    ----------
        portfolio (str): Name of the portfolio to which the dataset belong.
        name (str): Name of the dataset.
        url (str): URL of the dataset.
        description (str): Description of the dataset.
        license (str): License of the dataset.
        citation (str): Citation to use when referring to the dataset.
        file_name (str): Name of the downloaded file.
        hash (str): SHA256 hash of the downloaded file.
        files (list[str]): List of files in the dataset.
        size (int): Size of the dataset in MB.
        tags (list[str]): List of tags associated to the dataset.
        is_zip (bool): Whether the dataset is a zip file.
    """

    def __init__(self) -> None:
        super().__init__(
            portfolio=DENOISING,
            name="N2V_SEM",
            url="https://download.fht.org/jug/n2v/SEM.zip",
            file_name="SEM.zip",
            sha256="7600a17c3dbd4992ea547be12458640c21e797eef6a9f776f36ba5890f26855d",
            description="Cropped images from a SEM dataset from T.-O. Buchholz et al "
            "(Methods Cell Biol, 2020).",
            license="CC-BY-4.0",
            citation="T.-O. Buchholz, A. Krull, R. Shahidi, G. Pigino, G. Jékely, "
            'F. Jug, "Content-aware image restoration for electron '
            'microscopy", Methods Cell Biol 152, 277-289',
            files=["train.tif", "validation.tif"],
            size=13.0,
            tags=["denoising", "electron microscopy"],
        )


class N2V_RGB(PortfolioEntry):
    """RGB dataset.

    Attributes
    ----------
        portfolio (str): Name of the portfolio to which the dataset belong.
        name (str): Name of the dataset.
        url (str): URL of the dataset.
        description (str): Description of the dataset.
        license (str): License of the dataset.
        citation (str): Citation to use when referring to the dataset.
        file_name (str): Name of the downloaded file.
        hash (str): SHA256 hash of the downloaded file.
        files (list[str]): List of files in the dataset.
        size (int): Size of the dataset in MB.
        tags (list[str]): List of tags associated to the dataset.
        is_zip (bool): Whether the dataset is a zip file.
    """

    def __init__(self) -> None:
        super().__init__(
            portfolio=DENOISING,
            name="N2V_RGB",
            url="https://download.fht.org/jug/n2v/RGB.zip",
            file_name="RGB.zip",
            sha256="4c2010c6b5c253d3a580afe744cbff969d387617c9dde29fea4463636d285657",
            description="Banner of the CVPR 2019 conference with extra noise.",
            license="CC-BY-4.0",
            citation='A. Krull, T.-O. Buchholz and F. Jug, "Noise2Void - Learning '
            'Denoising From Single Noisy Images," 2019 IEEE/CVF '
            "Conference on Computer Vision and Pattern Recognition (CVPR),"
            " 2019, pp. 2124-2132",
            files=[
                "longBeach.png",
            ],
            size=10.4,
            tags=["denoising", "natural images", "RGB"],
        )


class Flywing(PortfolioEntry):
    """Flywing dataset.

    Attributes
    ----------
        portfolio (str): Name of the portfolio to which the dataset belong.
        name (str): Name of the dataset.
        url (str): URL of the dataset.
        description (str): Description of the dataset.
        license (str): License of the dataset.
        citation (str): Citation to use when referring to the dataset.
        file_name (str): Name of the downloaded file.
        hash (str): SHA256 hash of the downloaded file.
        files (list[str]): List of files in the dataset.
        size (int): Size of the dataset in MB.
        tags (list[str]): List of tags associated to the dataset.
        is_zip (bool): Whether the dataset is a zip file.
    """

    def __init__(self) -> None:
        super().__init__(
            portfolio=DENOISING,
            name="Flywing",
            url="https://download.fht.org/jug/n2v/flywing-data.zip",
            file_name="flywing-data.zip",
            sha256="01106b6dc096c423babfca47ef27059a01c2ca053769da06e8649381089a559f",
            description="Image of a membrane-labeled fly wing (35x692x520 pixels).",
            license="CC-BY-4.0",
            citation="Buchholz, T.O., Prakash, M., Schmidt, D., Krull, A., Jug, "
            "F.: Denoiseg: joint denoising and segmentation. In: European "
            "Conference on Computer Vision (ECCV). pp. 324-337. Springer (2020) 8, 9",
            files=[
                "flywing.tif",
            ],
            size=10.2,
            tags=["denoising", "membrane", "fluorescence"],
        )


class Convallaria(PortfolioEntry):
    """Convallaria dataset.

    Attributes
    ----------
        portfolio (str): Name of the portfolio to which the dataset belong.
        name (str): Name of the dataset.
        url (str): URL of the dataset.
        description (str): Description of the dataset.
        license (str): License of the dataset.
        citation (str): Citation to use when referring to the dataset.
        file_name (str): Name of the downloaded file.
        hash (str): SHA256 hash of the downloaded file.
        files (list[str]): List of files in the dataset.
        size (int): Size of the dataset in MB.
        tags (list[str]): List of tags associated to the dataset.
        is_zip (bool): Whether the dataset is a zip file.
    """

    def __init__(self) -> None:
        super().__init__(
            portfolio=DENOISING,
            name="Convallaria",
            url="https://cloud.mpi-cbg.de/index.php/s/BE8raMtHQlgLDF3/download",
            file_name="Convallaria_diaphragm.zip",
            sha256="8a2ac3e2792334c833ee8a3ca449fc14eada18145f9d56fa2cb40f462c2e8909",
            description="Image of a convallaria flower (35x692x520 pixels).\n"
            "The image also comes with a defocused image in order to allow \n"
            "estimating the noise distribution.",
            license="CC-BY-4.0",
            citation="Krull, A., Vičar, T., Prakash, M., Lalit, M., & Jug, F. (2020). "
            "Probabilistic noise2void: Unsupervised content-aware denoising. Frontiers"
            " in Computer Science, 2, 5.",
            files=[
                "Convallaria_diaphragm/20190520_tl_25um_50msec_05pc_488_130EM_Conv.tif",
                "Convallaria_diaphragm/20190726_tl_50um_500msec_wf_130EM_FD.tif",
            ],
            size=344.0,
            tags=["denoising", "membrane", "fluorescence"],
        )
