# QNX6Parser 🔍

A digital forensics tool for extracting files — including **deleted files** — from QNX6 file system images.  
QNX6Parser reconstructs the full directory hierarchy and offers both a GUI and executable version for ease of use.

---

## 🔑 Key Features

- 🗂 **Extracts entire file and directory hierarchy**
- 🧹 **Recovers deleted files** — highlight of this tool
- 🖥️ GUI-based interface with real-time progress bar (PySide6)
- 🛠️ Option to parse both primary and backup superblocks
- ✅ Available as both source and Windows `.exe`

---

## 🚀 Installation & Usage

### Option 1: Clone from GitHub

```bash
git clone https://github.com/K7NGhost/QNX6Parser.git
cd QNX6Parser
pip install -r requirements.txt
python src/main.py
```

### Option 2: Download the Executable

1. Go to the [Releases](https://github.com/K7NGhost/QNX6Parser/releases) page
2. Download the latest `.exe` (e.g., `QNX6Parser.exe`)
3. Run the executable – no Python setup required

## 📂 How It Works

- Select your raw QNX6 image file via the GUI
- Choose your output directory
- QNX6Parser scans:
    - The **primary superblock**
    - Optionally, the **backup superblock**
- Extracts:
    - Valid files and folders
    - **Deleted inodes that still have recoverable data**
- Reconstructs everything in the original hierarchical structure

## 🧠 Author

Kevin Argueta  
GitHub: [@K7NGhost](https://github.com/K7NGhost)

## 📄 License

MIT License

## 🤝 Contributing

Pull requests welcome!  
If you’ve got suggestions open an issue to start the conversation.

### 🙏 Acknowledgments

This tool was built with insights and knowledge drawn from these two research paper's. Special thanks to the authors and contributors of the following works:
https://link.springer.com/content/pdf/10.1007/978-3-030-98467-0_4.pdf
https://github.com/jdbonfils/QNX6FS-Parser-Ingest-Module/blob/master/QNX6_FileSystem_FullReport_FR.pdf
