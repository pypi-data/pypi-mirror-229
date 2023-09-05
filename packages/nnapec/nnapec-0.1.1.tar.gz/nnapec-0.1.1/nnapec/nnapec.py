from netspec import EmulatorModel


def get_apec_model() -> EmulatorModel:

    """
    return an instance of an APEC emulator

    :returns:

    """

    nn_apec = EmulatorModel("nn_apec")

    return nn_apec
