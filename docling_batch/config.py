"""Configuration helpers for the Docling batch processor."""

from docling.datamodel.pipeline_options import (
    AcceleratorDevice,
    AcceleratorOptions,
    RapidOcrOptions,
    TesseractCliOcrOptions,
    ThreadedPdfPipelineOptions,
)


def build_pdf_pipeline_options(
    device,
    enable_ocr,
    ocr_engine,
    force_full_page_ocr,
    generate_picture_images,
    generate_page_images,
    image_scale,
):
    options = ThreadedPdfPipelineOptions()
    options.accelerator_options = AcceleratorOptions(device=AcceleratorDevice(device))
    options.do_ocr = enable_ocr
    options.generate_picture_images = generate_picture_images
    options.generate_page_images = generate_page_images
    options.images_scale = image_scale
    if device == "cuda":
        options.layout_batch_size = 32
        options.ocr_batch_size = 4
        options.table_batch_size = 4

    if ocr_engine == "rapidocr":
        options.ocr_options = RapidOcrOptions(
            force_full_page_ocr=force_full_page_ocr,
            backend="torch",
        )
    else:
        options.ocr_options = TesseractCliOcrOptions(
            force_full_page_ocr=force_full_page_ocr,
        )

    return options
