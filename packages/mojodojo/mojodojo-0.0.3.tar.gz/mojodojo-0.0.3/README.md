# The Mojo Dojo

### 1. Install LLVM

```
sudo apt install llvm
echo 'export LLVM_SYMBOLIZER_PATH=/usr/bin/llvm-symbolizer' >> ~/.bashrc
```

### 2. Find libpython path for your env

Assuming env located at `~/miniconda3`

```
python3 -c 'import pathlib; sorted({print(x) for x in (pathlib.Path.home() / "miniconda3/envs").rglob("lib/*") if "libpython" in x.name})'
```

### 3. Export env

Replace `<full_path_to_libpython.so>` with your env's libpython path

```
echo 'export MOJO_PYTHON_LIBRARY="<full_path_to_libpython.so>"' >> ~/.bashrc
source ~/.bashrc
```

### 4. Install Modular CLI / Mojo

Replace `<your key>` with key provided at [developer.modular.com/download](https://developer.modular.com/download)

```
curl https://get.modular.com | MODULAR_AUTH=<your key> sh -
modular install mojo
echo 'export MODULAR_HOME="$HOME/.modular"' >> ~/.bashrc
echo 'export PATH="$MODULAR_HOME/pkg/packages.modular.com_mojo/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### 5. Activate env and run

```python
from python import Python as py

fn main() raises:
    let np = py.import_module("numpy")
    print(np.random.randn(3,7))
```
