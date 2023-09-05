import sys
import json
import numpy as np
import matplotlib.pyplot as plt
import pytest

from plot_serializer.serializer import Serializer


def create_benchmark_plot():
    np.random.seed(19680801)

    x = np.linspace(0.5, 3.5, 100)
    y1 = 3 + np.cos(x)
    y2 = 1 + np.cos(1 + x / 0.75) / 2

    fig = plt.figure(figsize=(7.5, 7.5))
    ax = fig.add_axes([0.2, 0.17, 0.68, 0.7], aspect=1)

    ax.set_xlim(0, 4)
    ax.set_ylim(0, 4)

    ax.tick_params(which="major", width=1.0, length=10, labelsize=14)
    ax.tick_params(which="minor", width=1.0, length=5, labelsize=10, labelcolor="0.25")

    ax.grid(linestyle="--", linewidth=0.5, color=".25", zorder=-10)

    ax.plot(x, y1, c="C0", lw=2.5, label="Blue signal", zorder=10)
    ax.plot(x, y2, c="C1", lw=2.5, label="Orange signal")
    # ax.scatter(X[::3], Y3[::3], label="scatter")

    ax.set_title("Example figure", fontsize=20, verticalalignment="bottom")
    ax.set_xlabel("TIME in s", fontsize=14)
    ax.set_ylabel("DISTANCE in m", fontsize=14)
    ax.legend(loc="upper right", fontsize=14)
    return fig, ax


def serialize_plot():
    fig, ax = create_benchmark_plot()
    s = Serializer(fig)
    s.plot.id = "id:ad0cca21"
    s.plot.axes[0].xunit = "second"
    s.plot.axes[0].yunit = "blah"
    s.add_custom_metadata({"date_created": "11.08.2023"}, s.plot)
    json_object = s.to_json()
    return json_object


@pytest.mark.skipif(not sys.platform.startswith("win"), reason="does not run on linux")
def test_to_json():
    benchmark_file = open("tests/test_plot.json")
    benchmark_dict = json.load(benchmark_file)

    dict_from_serialized = json.loads(serialize_plot())

    np.testing.assert_array_equal(
        np.array(benchmark_dict.keys()),
        np.array(dict_from_serialized.keys()),
        strict=False,
    )

    assert dict_from_serialized == pytest.approx(benchmark_dict, abs=1e-3)


def test_to_json_linux():
    benchmark_file = open("tests/test_plot.json")
    benchmark_dict = json.load(benchmark_file)

    dict_from_serialized = json.loads(serialize_plot())

    np.testing.assert_array_equal(
        np.array(benchmark_dict.keys()),
        np.array(dict_from_serialized.keys()),
        strict=False,
    )
    for key, value in dict_from_serialized.items():
        assert _recursive_search(value, benchmark_dict[key])


def _recursive_search(obj1, obj2):
    if not isinstance(obj1, dict):
        if isinstance(obj1, list):
            return _list_search(obj1, obj2)
        else:
            return obj1 == obj2
    return _nested_dict_search(obj1, obj2)


def _nested_dict_search(obj1, obj2):
    bool_list = []
    for key, value in obj1.items():
        if isinstance(value, dict):
            item1 = _recursive_search(value)
            item2 = _recursive_search(obj2[key])
            if item1 is not None:
                bool_list.append(item1 == item2)
        elif isinstance(value, list):
            bool_list.append(_list_search(value, obj2[key]))
        else:
            try:
                bool_list.append(np.allclose(value, obj2[key]))
            except (TypeError, np.exceptions.DTypePromotionError):
                bool_list.append(value == obj2[key])
    return all(bool_list)


def _list_search(l1, l2):
    bool_list = []
    for index, item in enumerate(l1):
        if isinstance(item, dict):
            bool_list.append(_nested_dict_search(item, l2[index]))
        else:
            try:
                bool_list.append(np.allclose(item, l2[index]))
            except (TypeError, np.exceptions.DTypePromotionError):
                bool_list.append(item == l2[index])
    return all(bool_list)
