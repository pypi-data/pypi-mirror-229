import platform

from raga.exception import RagaException


class ModelExecutorFactoryException(RagaException):
    pass

class ModelExecutorFactory:
    def __init__(self) -> None:
        get_platform_details()

    @staticmethod
    def getModelExecutor(model_name="", version="", project_name=""):
        if not isinstance(model_name, str) or not model_name:
            raise ModelExecutorFactoryException("model_name is required and must be a non-empty string.")
        if not isinstance(version, str) or not version:
            raise ModelExecutorFactoryException("version is required and must be a non-empty string.")
        if not isinstance(project_name, str) or not project_name:
            raise ModelExecutorFactoryException("project_name is required and must be a non-empty string.")
        

def get_platform_details():
    os_name = platform.system().lower()
    if os_name == "darwin":
        mac_version = "11_0" if platform.release() >= "20.0.0" else "10_9"
        arch = "arm64" if platform.machine() == "arm64" else "x86_64"
        platform_name = f"macosx_{mac_version}_{arch}"
    elif os_name == "linux":
        dist_name, dist_version, dist_id = platform.linux_distribution()
        # platform_name = 

    # Get the OS release version
    os_version = platform.release()
    print("OS Version:", os_version)

    # Get the OS distribution or specific information (Linux only)
    if os_name == 'Linux':
        dist_name, dist_version, dist_id = platform.linux_distribution()
        print("Distribution:", dist_name)
        print("Distribution Version:", dist_version)
        print("Distribution ID:", dist_id)

    # Get the machine (hardware) type
    machine_type = platform.machine()
    print("Machine Type:", machine_type)

    # Get the processor architecture
    processor_arch = platform.processor()
    print("Processor Architecture:", processor_arch)
        
