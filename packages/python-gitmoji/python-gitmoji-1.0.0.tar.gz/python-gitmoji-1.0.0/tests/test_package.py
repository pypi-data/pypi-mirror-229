def test_version(mocker):
    mocker.patch("gitmoji.__version__", "0.1.0")

    from gitmoji import __version__

    assert __version__ == "0.1.0"
