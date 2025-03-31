import psutil

def get_processes():
    """
    Retorna un iterador de procesos con la información requerida.
    """
    return psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'status'])

def terminate_process(pid):
    """
    Termina el proceso indicado por pid.
    """
    proc = psutil.Process(pid)
    proc.terminate()
    proc.wait(timeout=3)

def suspend_process(pid):
    """
    Suspende el proceso indicado por pid.
    """
    proc = psutil.Process(pid)
    proc.suspend()

def resume_process(pid):
    """
    Reanuda el proceso indicado por pid.
    """
    proc = psutil.Process(pid)
    proc.resume()
