import os
import logging
import shutil
import jinja2

from .config import get_link_setting

logger = logging.getLogger(__name__)


def get_all_files(target_folder):
    file_list = []
    for root, dirs, files in os.walk(target_folder):
        for file in files:
            file_list.append(file)
    return file_list


def set_tv_folder_format(data):
    tv_folder_format = get_link_setting().get("tv_folder_format")
    if tv_folder_format is None:
        tv_folder = "{name} ({year})"
    else:
        tv_folder = jinja2.Template(tv_folder_format).render(data)
    return tv_folder


def fix_filename(download_complete_data):
    title = download_complete_data.get("x_meta").get("title")
    original_title = download_complete_data.get("x_meta").get("originalTitle")
    tmdb_name = download_complete_data.get("x_meta").get("tmdb_name")
    tmdbId = download_complete_data.get("x_meta").get("tmdbId")
    target_path = download_complete_data.get("target_path")
    season_number = download_complete_data.get("season_number")
    library_path = download_complete_data.get("library_path")
    release_year = download_complete_data.get("x_meta").get("releaseYear")
    season_year = download_complete_data.get("seasonYear")

    tmpl_data = {
        "name": tmdb_name,
        "original_name": original_title,
        "year": release_year,
        "season_year": season_year,
        "tmdbid": tmdbId,
    }

    tv_folder = set_tv_folder_format(tmpl_data)

    error_folder = os.path.join(target_path, f"Season {season_number}")
    files = get_all_files(error_folder)
    for file in files:
        real_name = file.replace(title, tmdb_name)
        real_path = os.path.join(library_path, tv_folder, f"Season {season_number}")
        if not os.path.exists(real_path):
            os.makedirs(real_path)
        error_file = os.path.join(error_folder, file)
        real_file = os.path.join(str(real_path), real_name)
        if not os.path.exists(real_file):
            shutil.move(error_file, real_file)
            logger.info(f"[AutoFix事件] 文件命名修正：{error_file} -> {real_file}")
        else:
            shutil.rmtree(error_file)
            logger.info(f"[AutoFix事件] 文件{real_file} 已经存在")
    files = get_all_files(target_path)
    if len(files) > 0:
        return
    shutil.rmtree(target_path)