import os
import pretty_errors
import rich

# from .widgets import timer


class Cli:
    def __init__(self):
        ...

    @staticmethod
    def install_node(version=16):
        from .cli.script import install_node_with_nvm
        install_node_with_nvm(version=version)

    @staticmethod
    def install_nvim(version='0.9.2'):
        from .cli.script import install_nvim
        install_nvim(version=version)
    @staticmethod
    def uninstall_nvim():
        from .cli.script import uninstall_nvim
        uninstall_nvim()
    @staticmethod
    def save_docker_images(filedir='.', skip_exists=True, use_stream=False):
        kwargs = locals()
        from .docker import save_docker_images
        return save_docker_images(**kwargs)

    @staticmethod
    def load_docker_images(filename_pattern="./*", skip_exists=True):
        kwargs = locals()
        from .docker import load_docker_images
        return load_docker_images(**kwargs)

    @staticmethod
    def docker_gpu_stat():
        from .docker.nvidia_stat import docker_gpu_stat
        return docker_gpu_stat()

    @staticmethod
    def pack(source_path: str, target_path=None, format='gztar'):
        kwargs = locals()
        from .utils.compress import pack
        return pack(**kwargs)

    @staticmethod
    def unpack(filename: str, extract_dir=None, format=None):
        kwargs = locals()
        from .utils.compress import unpack
        return unpack(**kwargs)

    @staticmethod
    def start_server(port=50001, deque_maxlen=None):
        kwargs = locals()
        from .multiprocess import start_server
        return start_server(**kwargs)

    @staticmethod
    def kill(*ports: int, view=False):
        from .multiprocess import kill
        return kill(*ports, view)

    @staticmethod
    def clone(url: str, save_path=None, branch=None, proxy=False):
        kwargs = locals()
        from .cli.git import clone
        return clone(**kwargs)

    @staticmethod
    def get_ip(env="inner"):
        kwargs = locals()
        from .utils.net import get_ip
        return get_ip(**kwargs)

    @staticmethod
    def create(project_name: str, out=None):
        """创建项目
        Parameter
        ---------
        project_name : str
            package name
        out : str | None
            项目生成路径
        """
        if out is None:
            out = project_name
        from .template.scaffold.core import create_project
        return create_project(project_name, out)

    @staticmethod
    def milvus(flag='start'):
        kwargs = locals()
        from .ann import milvus
        return milvus(**kwargs)

    @staticmethod
    def latexocr():
        os.system("latexocr")

    @staticmethod
    def test_torch():
        from sparrow.experimental import test_torch

    @staticmethod
    def gen_key(rsa_name:str, email='beidongjiedeguang@gmail.com'):
        from pathlib import Path
        rsa_path = str(Path.home() / '.ssh' / f'id_rsa_{rsa_name}')
        command = f"ssh-keygen -t rsa -C {email} -f {rsa_path}"
        os.system(command)

        with open(rsa_path + '.pub', 'r', encoding='utf8') as f:
            rich.print("pub key:\n")
            print(f.read())

        config_path = str(Path.home() / '.ssh' / 'config')
        rich.print(f"""你可能需要将新添加的key 写入 {config_path}文件中，内容大概是：
# 如果是远程服务器
Host {rsa_name}
  HostName 198.211.51.254
  User root
  Port 22
  IdentityFile {rsa_path}
  
# 或者 git
Host {rsa_name}
  HostName github.com
  User git
  IdentityFile {rsa_path}
  IdentitiesOnly yes
""")




def fire_commands():
    import fire
    fire.Fire(Cli)


def typer_commands():
    import typer
    app = typer.Typer()
    # [app.command()(i) for i in func_list]
    # app()


def main():
    use_fire = 1
    if use_fire:
        fire_commands()
    else:
        # Fixme *形参 传入会出错，参考这里 https://typer.tiangolo.com/tutorial/multiple-values/arguments-with-multiple-values/
        typer_commands()
