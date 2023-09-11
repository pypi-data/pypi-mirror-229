import fdlayout as fd


def test_basic_functionality():
    n_nodes = 3
    layout = fd.layout(3, [(0, 1), (1, 2), (2, 0)])

    for x in layout:
        assert isinstance(x, list)
        assert len(x) == n_nodes
        for i in x:
            assert isinstance(i, float)


test_basic_functionality()
