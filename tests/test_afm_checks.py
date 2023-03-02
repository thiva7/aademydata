import afm_checks as afmc


def test_can_be_afm1():
    assert afmc.can_be_afm('046948583') == False


def test_can_be_afm2():
    assert afmc.can_be_afm('046948586') == True


def test_can_be_afm3():
    assert afmc.can_be_afm('12312') == False


def test_can_be_afm4():
    assert afmc.can_be_afm('12312312a') == False
