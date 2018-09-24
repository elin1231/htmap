"""
Copyright 2018 HTCondor Team, Computer Sciences Department,
University of Wisconsin-Madison, WI.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import time

import pytest

import htmap


def test_rename_new_name_in_map_ids(mapped_doubler):
    result = mapped_doubler.map('old', range(2))
    result.wait()

    time.sleep(.1)

    result.rename('new')

    assert 'new' in htmap.map_ids()


def test_rename_removes_old_map(mapped_doubler):
    result = mapped_doubler.map('old', range(2))

    result.wait()
    time.sleep(.1)

    result.rename('new')

    assert 'old' not in htmap.map_ids()


def test_rename_raises_if_jobs_running(mapped_sleepy_double):
    result = mapped_sleepy_double.map('old', range(2))

    with pytest.raises(htmap.exceptions.CannotRenameMap):
        result.rename('new')


def test_rename_raises_if_jobs_held(mapped_doubler):
    result = mapped_doubler.map('old', range(2))
    result.hold()

    with pytest.raises(htmap.exceptions.CannotRenameMap):
        result.rename('new')


def test_rename_raises_if_new_map_id_already_exists(mapped_doubler):
    result = mapped_doubler.map('old', range(2))
    result.wait()

    existing = mapped_doubler.map('target', range(2))
    existing.hold()  # doesn't matter, just speeds things up

    with pytest.raises(htmap.exceptions.MapIdAlreadyExists):
        result.rename('target')


def test_complete_then_rename_then_rerun(mapped_doubler):
    result = mapped_doubler.map('old', range(2))
    result.wait()
    time.sleep(.1)

    new_result = result.rename('new')

    new_result.rerun()

    assert list(new_result) == [0, 2]


def test_can_be_recovered_after_rename(mapped_doubler):
    result = mapped_doubler.map('old', range(2))
    result.wait()
    time.sleep(.1)

    result.rename('new')
    time.sleep(.1)

    htmap.recover('new')


def test_can_be_renamed_if_nothing_running(mapped_doubler):
    result = mapped_doubler.map('old', range(2))
    result._remove_from_queue()

    result.rename('new')


def test_can_be_renamed_and_rerun_if_nothing_running(mapped_doubler):
    result = mapped_doubler.map('old', range(2))
    result._remove_from_queue()

    new_result = result.rename('new')
    new_result.rerun()

    assert list(new_result) == [0, 2]