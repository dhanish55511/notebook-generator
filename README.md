# 📓 Notebook Generator

A simple Python-based tool to generate `.dsnb` notebooks dynamically from the published Use Case docs.  

---

## 📦 Installation

### 1. Install Python

#### For Windows
1. Go to the official Python website: [https://www.python.org/downloads/](https://www.python.org/downloads/).
2. Click **"Download Python [version]"** for Windows.
3. Once the file finishes downloading, double-click it to run the installer.
4. **Important:** On the first installation screen, check the box that says **"Add Python to PATH"** — this makes it easier to use Python from the Command Prompt.
5. Click **"Install Now"** and follow the prompts.

#### For macOS
1. Open the Terminal app (you can find it in **Applications → Utilities**).
2. Run the following command to download Python (replace `<python_download_link>` with the actual link):
   ```bash
   wget <python_download_link>
   ````

3. Follow the instructions to install it.

💡 *Tip:* You can also install Python on Mac using **Homebrew**:

```bash
brew install python
```

#### Verify the Python Installation

```bash
python --version
```

If installed correctly, you should see something like:

```
Python 3.x.x
```

---

### 2. Clone the Repository

```bash
git clone git@github.com:dhanish55511/notebook-generator.git
cd notebook-generator
```

---

### 3. Install Required Python Packages

This project requires **BeautifulSoup4** and **Requests**. Install them by running:

```bash
pip install beautifulsoup4 requests
```

#### Verify the Package Installation

```bash
pip show beautifulsoup4
pip show requests
```

---

## 🧪 Usage

To generate a notebook, run:

```bash
python main.py
```

The generated `.dsnb` notebook will appear in the `output` directory.

---

## 🤝 Contributing

1. Fork the repository.
2. Create your feature branch:

   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:

   ```bash
   git commit -m "Add new feature"
   ```
4. Push to the branch:

   ```bash
   git push origin feature-name
   ```
5. Open a Pull Request.

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

```

This layout:  
- Follows the **standard GitHub README structure**.  
- Groups installation, usage, and contribution logically.  
- Uses **clear step-by-step formatting** so beginners won’t get lost.  

If you want, I can also **add a "Quick Start" section at the very top** so advanced users can install & run in just two commands without reading the full instructions. That way, both beginners and pros are happy.
```
