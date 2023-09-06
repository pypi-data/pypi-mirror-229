import pytest
from gwcloud_python.utils import file_filters
from gwcloud_python import FileReference, FileReferenceList


@pytest.fixture
def png_data():
    return FileReferenceList([
        FileReference(
            path='data/dir/test1.png',
            file_size='1',
            download_token='test_token_1',
            job_id='id'
        ),
        FileReference(
            path='data/dir/test2.png',
            file_size='1',
            download_token='test_token_2',
            job_id='id'
        ),
    ])


@pytest.fixture
def png_result():
    return FileReferenceList([
        FileReference(
            path='result/dir/test1.png',
            file_size='1',
            download_token='test_token_3',
            job_id='id'
        ),
        FileReference(
            path='result/dir/test2.png',
            file_size='1',
            download_token='test_token_4',
            job_id='id'
        ),
    ])


@pytest.fixture
def png_extra_no_dir():
    return FileReferenceList([
        FileReference(
            path='test1.png',
            file_size='1',
            download_token='test_token_5',
            job_id='id'
        ),
        FileReference(
            path='test2.png',
            file_size='1',
            download_token='test_token_6',
            job_id='id'
        ),
    ])


@pytest.fixture
def png_extra_dir():
    return FileReferenceList([
        FileReference(
            path='arbitrary/dir/test1.png',
            file_size='1',
            download_token='test_token_7',
            job_id='id'
        ),
        FileReference(
            path='arbitrary/dir/test2.png',
            file_size='1',
            download_token='test_token_8',
            job_id='id'
        ),
    ])


@pytest.fixture
def corner():
    return FileReferenceList([
        FileReference(
            path='test1_corner.png',
            file_size='1',
            download_token='test_token_9',
            job_id='id'
        ),
        FileReference(
            path='test2_corner.png',
            file_size='1',
            download_token='test_token_10',
            job_id='id'
        ),
    ])


@pytest.fixture
def index():
    return FileReferenceList([
        FileReference(
            path='index.html',
            file_size='1',
            download_token='test_token_11',
            job_id='id'
        ),
    ])


@pytest.fixture
def config():
    return FileReferenceList([
        FileReference(
            path='a_config_complete.ini',
            file_size='1',
            download_token='test_token_12',
            job_id='id'
        ),
    ])


@pytest.fixture
def merge():
    return FileReferenceList([
        FileReference(
            path='result/dir/a_merge_result.json',
            file_size='1',
            download_token='test_token_13',
            job_id='id'
        ),
    ])


@pytest.fixture
def unmerge():
    return FileReferenceList([
        FileReference(
            path='result/dir/a_result.json',
            file_size='1',
            download_token='test_token_14',
            job_id='id'
        ),
    ])


@pytest.fixture
def png(png_data, png_result, png_extra_no_dir, png_extra_dir, corner):
    return png_data + png_result + png_extra_no_dir + png_extra_dir + corner


@pytest.fixture
def default_with_merge(png_data, png_result, index, config, merge):
    return png_data + png_result + index + config + merge


@pytest.fixture
def full_with_merge(png, index, config, merge, unmerge):
    return png + index + config + merge + unmerge


@pytest.fixture
def default_without_merge(png_data, png_result, index, config, unmerge):
    return png_data + png_result + index + config + unmerge


@pytest.fixture
def full_without_merge(png, index, config, unmerge):
    return png + index + config + unmerge


def test_default_file_filter(full_with_merge, default_with_merge, full_without_merge, default_without_merge):
    sub_list = file_filters.default_filter(full_with_merge)
    assert file_filters.sort_file_list(sub_list) == file_filters.sort_file_list(default_with_merge)

    sub_list = file_filters.default_filter(full_without_merge)
    assert file_filters.sort_file_list(sub_list) == file_filters.sort_file_list(default_without_merge)


def test_png_file_filter(full_with_merge, png):
    sub_list = file_filters.png_filter(full_with_merge)
    assert file_filters.sort_file_list(sub_list) == file_filters.sort_file_list(png)


def test_config_file_filter(full_with_merge, config):
    sub_list = file_filters.config_filter(full_with_merge)
    assert file_filters.sort_file_list(sub_list) == file_filters.sort_file_list(config)


def test_corner_file_filter(full_with_merge, corner):
    sub_list = file_filters.corner_plot_filter(full_with_merge)
    assert file_filters.sort_file_list(sub_list) == file_filters.sort_file_list(corner)


def test_result_json_file_filter(full_with_merge, full_without_merge, merge, unmerge):
    sub_list = file_filters.result_json_filter(full_with_merge)
    assert file_filters.sort_file_list(sub_list) == file_filters.sort_file_list(merge)
    assert file_filters.sort_file_list(sub_list) != file_filters.sort_file_list(unmerge)

    sub_list = file_filters.result_json_filter(full_without_merge)
    assert file_filters.sort_file_list(sub_list) != file_filters.sort_file_list(merge)
    assert file_filters.sort_file_list(sub_list) == file_filters.sort_file_list(unmerge)
