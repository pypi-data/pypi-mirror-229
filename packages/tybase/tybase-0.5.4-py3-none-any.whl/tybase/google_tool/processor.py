# 封装这个类
import random

from tybase.google_tool.drive import GoogleDrive
from tybase.google_tool.slides import GoogleSlides
from loguru import logger


class SlidesProcessor:
    def __init__(self, service_account_file):
        self.slides = GoogleSlides(service_account_file)
        self.drive = GoogleDrive(service_account_file)

    def process_template(self, presentation_id, template_indexes, replacements, output_filename):
        # 复制模板页面
        new_slide_id_list = self.slides.duplicate_slide(presentation_id, template_indexes)
        logger.info("复制页面完成!")

        # 进行文本替换
        self.slides.replace_placeholders(presentation_id, replacements, slide_id=new_slide_id_list[0])
        logger.info("文本替换完成!")

        # 下载图片
        self.drive.download_image(presentation_id, new_slide_id_list[0], output_filename)
        logger.info("图片下载完成!")

        # 删除复制的页面
        self.slides.delete_slide(presentation_id, new_slide_id_list[0])
        logger.info("页面删除完成!")

    def process_random_template(self, presentation_id, template_indexes, replacements_list, output_folder):
        for idx, replacements in enumerate(replacements_list):
            # 随机选择一个模板
            random_template_index = random.choice(template_indexes)

            # 复制模板页面
            new_slide_id_list = self.slides.duplicate_slide(presentation_id, [random_template_index])
            logger.info(f"复制页面 {random_template_index} 完成!")

            # 进行文本替换
            self.slides.replace_placeholders(presentation_id, replacements, slide_id=new_slide_id_list[0])
            logger.info("文本替换完成!")

            # 下载图片
            output_filename = f"{output_folder}/slide_thumbnail_{idx}.jpg"
            self.drive.download_image(presentation_id, new_slide_id_list[0], output_filename)
            logger.info(f"图片 {output_filename} 下载完成!")

            # 删除复制的页面
            self.slides.delete_slide(presentation_id, new_slide_id_list[0])
            logger.info("页面删除完成!")
